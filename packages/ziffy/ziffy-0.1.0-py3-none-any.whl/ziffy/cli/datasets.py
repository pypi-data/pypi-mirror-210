from rich.console import Console
from rich.table import Table

from ..utils import order_of_magnitude


def print_datasets(datasets):
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Dataset")
    table.add_column("Size", justify="right")
    table.add_column("Objects", justify="right")

    for dataset in sorted(datasets, key=lambda d: d["dataset"]):
        table.add_row(
            dataset["dataset"],
            order_of_magnitude(float(dataset["size"])),
            str(dataset["objects"]),
        )

    console = Console()
    console.print(table)
