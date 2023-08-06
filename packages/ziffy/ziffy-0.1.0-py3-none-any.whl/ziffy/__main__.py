"""
The `python -m ziffy` entrypoint.
"""

if __name__ == "__main__":
    import logging
    import click

    from .datasets import get_datasets
    from .cli.datasets import print_datasets

    logger = logging.getLogger(__name__)

    @click.group()
    def cli():
        return

    @cli.command()
    @click.argument("pool")
    @click.option("--force-update", is_flag=True, default=False, show_default=True)
    def datasets(pool, force_update):
        print_datasets(get_datasets(pool))

    cli()
