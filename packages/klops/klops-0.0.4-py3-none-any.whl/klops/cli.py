import click

from .deployment import gke, default

@click.group(help="CLI tool to manage full development cycle of machine learning projects.")
def deployment():
    pass

@click.group(help="[Under development] CLI tool to start and manage our experiments.")
def experiment():
    pass

@click.group(help="[Under development] CLI tool to manage data versioning.")
def versioning():
    pass


@click.group(help="Klops: KoinMLOps. Build Your End to End Machine Learning Projects.")
def cli():
    pass


deployment.add_command(default)
deployment.add_command(gke)

cli.add_command(deployment)
cli.add_command(experiment)
cli.add_command(versioning)

if __name__ == '__main__':
    cli()
