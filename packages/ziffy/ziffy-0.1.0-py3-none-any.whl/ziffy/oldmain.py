import logging
import re
import sqlite3
import click

from rich.tree import Tree
from tqdm import tqdm

from db import init_db
from datasets import get_datasets, update_datasets, print_datasets
from regex import RE_ATTRIBUTES
from tree import update_tree
from utils import execute

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

con = sqlite3.connect("/tmp/ziffy.db")
con.row_factory = sqlite3.Row
init_db(con)

@click.group()
def cli():
    return

@cli.command()
@click.argument("pool")
@click.option("--force-update", is_flag=True, default=False, show_default=True)
def datasets(pool, force_update):
    if force_update:
        update_datasets(con, pool)

    print_datasets(get_datasets(con, pool))

@cli.command()
@click.argument("dataset")
@click.option("--force-update", is_flag=True, default=False, show_default=True)
def tree(dataset, force_update):
    if force_update:
        update_tree(dataset)

    sql_query = f"SELECT * FROM tree WHERE tree.dataset = '{dataset}'"

    with con:
        entries = con.execute(sql_query).fetchall()
        logging.debug(entries)

        if len(entries) == 0:
            entries = update_tree(dataset)

            for entry in tqdm(entries):
                if entry[8] == "ZFS plain file" or entry[8] == "ZFS directory":
                    obj = execute(["zdb", "-P", "-ddddd", "-AAA", dataset, entry[0]]).replace("\t", " ")
                    logging.debug(obj)

                    properties = re.search(RE_ATTRIBUTES, obj).groupdict()
                    logging.debug(properties)
                    sql = f"""
                        INSERT OR REPLACE INTO tree (
                            dataset,
                            id,
                            path,
                            {'target,' if properties['target'] else ''}
                            uid,
                            gid,
                            atime,
                            mtime,
                            ctime,
                            crtime,
                            gen,
                            mode,
                            size,
                            parent
                        ) VALUES(
                            '{dataset}',
                            {entry[0]},
                            '{properties['path']}',
                            {'"' + properties['target'] + '"' if properties['target'] else ''}
                            {properties['uid']},
                            {properties['gid']},
                            '{properties['atime']}',
                            '{properties['mtime']}',
                            '{properties['ctime']}',
                            '{properties['crtime']}',
                            {properties['gen']},
                            '{properties['mode']}',
                            {properties['size']},
                            {properties['parent']}
                        )"""
                    logging.debug(sql)
                    con.execute(sql)
            con.commit()

    entries = con.execute(sql_query).fetchall()
    for entry in entries:
        print(entry["path"])

@cli.command()
@click.argument("dataset")
@click.argument("path")
@click.argument("destination", type=click.Path())
def recover(dataset, path, destination):
    sql_query = f"SELECT * FROM tree WHERE tree.dataset = '{dataset}' AND tree.path LIKE '{path}%'"

    if path.startswith("/"):
        path = path[1:]

    # Get directories
    with con:
        directories = con.execute(f"{sql_query} AND tree.mode LIKE '4%' ORDER BY tree.path").fetchall()

    # Create directories
    for directory in directories:
        logging.debug({key: directory[key] for key in directory.keys()})
        dir_path = directory['path'][1:]
        execute(["mkdir", "-p", f"{destination}/{dataset}/{dir_path}"])
        execute(["chmod", directory["mode"][-4:], f"{destination}/{dataset}/{dir_path}"])
        execute(["chown", f"{directory['uid']}:{directory['gid']}", f"{destination}/{dataset}/{dir_path}"])

    # Get files
    with con:
        files = con.execute(f"{sql_query} AND tree.mode LIKE '10%'").fetchall()

    # Create files
    for file in files:
        logging.debug({key: file[key] for key in file.keys()})
        file_path = file['path'][1:]

        if file["size"]:
            execute(["zdb", "-r", dataset, file_path, f"{destination}/{dataset}/{file_path}"])
        execute(["touch", "-a", "-d", file["atime"], f"{destination}/{dataset}/{file_path}"])
        execute(["touch", "-m" "-d", file["mtime"], f"{destination}/{dataset}/{file_path}"])
        execute(["chmod", file["mode"][-4:], f"{destination}/{dataset}/{file_path}"])
        execute(["chown", f"{file['uid']}:{file['gid']}", f"{destination}/{dataset}/{file_path}"])

    # Get symbolic links
    with con:
        symlinks = con.execute(f"{sql_query} AND tree.mode LIKE '12%'").fetchall()

    # Create symbolic links
    for symlink in symlinks:
        logging.debug({key: symlink[key] for key in symlink.keys()})
        file_path = symlink['path'][1:]
        target_path = symlink['target'][1:]

        execute(f"""
            ln -s {destination}/{dataset}/{file_path} {destination}/{dataset}/{target_path}
            touch -a -d '{file['atime']}' {destination}/{dataset}/{file_path} &&
            touch -m -d '{file['mtime']}' {destination}/{dataset}/{file_path} &&
            chmod {file['mode'][-4:]} {destination}/{dataset}/{file_path} &&
            chown {file['uid']}:{file['gid']} {destination}/{dataset}/{file_path}
        """)

    # Update access and modification time for directories here to preserve the original value
    for directory in directories:
        logging.debug({key: directory[key] for key in directory.keys()})
        dir_path = directory['path'][1:]
        execute(f"""
            touch -a -d '{directory['atime']}' {destination}/{dataset}/{dir_path} &&
            touch -m -d '{directory['mtime']}' {destination}/{dataset}/{dir_path}
        """)

if __name__ == "__main__":
    cli()
