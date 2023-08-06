import click

from cnvrgv2.cli.utils import messages
from cnvrgv2.cli.utils.decorators import prepare_command


@click.group(name='webapp')
def webapp_group():
    pass


@webapp_group.command()
@click.option('-s', '--slug', default=None, help=messages.WEBAPP_HELP_SLUG)
@click.option('-f', '--frequency', default=5, help=messages.WEBAPP_HELP_FREQUENCY)
@prepare_command()
def compare_experiments(webapp, logger, slug, frequency):
    """
      start a compare experiments in webapp for tensorboard
    """
    logger.log_and_echo("Compare is running")
    webapp.compare_experiments(frequency=frequency)
