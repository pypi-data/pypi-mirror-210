def get_datasets(con, pool):
    sql_query = f"SELECT dataset, size, objects FROM datasets WHERE datasets.dataset LIKE '{pool}%' AND datasets.dataset NOT LIKE '%@%'"

    with con:
        datasets = con.execute(sql_query).fetchall()
        logging.debug(datasets)

    if len(datasets) == 0:
        update_datasets(con, pool)

        with con:
            datasets = con.execute(sql_query).fetchall()
            logging.debug(datasets)

    return datasets

def update_datasets(con, pool):
    command = ["zdb", "-P", "-d", pool]
    result = execute(command)

    #result = execute(command.insert(1, "-e"))

    datasets = re.findall(RE_DATASETS, result)
    logger.debug(datasets)

    with con:
        con.executemany("INSERT OR REPLACE INTO datasets VALUES(?,?,?,?,?)", datasets)
        con.commit()
