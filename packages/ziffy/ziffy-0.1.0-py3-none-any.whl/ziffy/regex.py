import re

RE_DATASETS = re.compile(
    r"Dataset (?P<dataset>[\w._\-\/@]+) \[ZPL\], ID (?P<id>\d+), cr_txg (?P<cr_txg>\d+), (?P<size>\d+), (?P<objects>\d+) objects"
)

RE_TREE = re.compile(
    r"\s+([\-\d]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\w\s]+)\n"
)

RE_ATTRIBUTES = re.compile(
    r"path\s+(?P<path>[^\n]+)\n(?:\s+target\s+(?P<target>[^\n]+)\n)?\s+uid\s+(?P<uid>\d+)\n\s+gid\s+(?P<gid>\d+)\n\s+atime\s+(?P<atime>[^\n]+)\n\s+mtime\s+(?P<mtime>[^\n]+)\n\s+ctime\s+(?P<ctime>[^\n]+)\n\s+crtime\s+(?P<crtime>[^\n]+)\n\s+gen\s+(?P<gen>\d+)\n\s+mode\s+(?P<mode>\d+)\n\s+size\s+(?P<size>\d+)\n\s+parent\s+(?P<parent>\d+)\n\s+links\s+(?P<links>\d+)\n\s+pflags\s+(?P<pflags>\d+)\n"
)
