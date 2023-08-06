import os

import click
import yaml

from cnvrgv2.utils.url_utils import urljoin


def parse_parameters_from_file(path):
    """
    Parse parameters from command line
    :param parameters: parameters yaml
    :return: parameters list of dicts
    """
    if not os.path.exists(path):
        raise ValueError("The provided parameters yaml path does not exist.")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not data.get("parameters"):
        raise ValueError("The provided parameters yaml is missing the parameters key")

    return data.get("parameters")


def build_grid_url(cnvrg, project, grid_slug):
    """
    Build Grid url
    :param cnvrg: cnvrg object
    :param project: project object
    :param grid_slug: grid slug
    :return: grid url
    """
    grid_path = "{}/experiments?grid={}".format(project._route, grid_slug)
    route = urljoin(cnvrg._proxy._domain, "api", grid_path)
    return route


def callback_log(experiment, log=False):
    if not log:
        return

    end_pos = 0

    def callback():
        nonlocal end_pos
        nonlocal log
        try:
            resp = experiment.info(end_pos=end_pos)
            end_pos = resp.attributes["info"][experiment.slug]["end_pos"]
            logs = resp.attributes["info"][experiment.slug]["logs"]
            for log in logs:
                click.echo(log["message"])
        except Exception as e:
            click.echo("Failed to get logs, error: {}".format(e))

    return callback


def pretty_print_predictions(predictions):
    """
    Pretty print predictions of endpoint
    :@predictions: list of predictions dict
    :return: None
    """
    click.echo("{:<5} {:<20} {:<20} {:<20} {:<13}".format('Model',
                                                          'Time',
                                                          'Input',
                                                          'Output',
                                                          'Elapsed_time'))
    for prediction in predictions:
        click.echo("{:<5} {:<20} {:<20} {:<20} {:<13}".format(prediction["model"],
                                                              prediction["start_time"],
                                                              prediction["input"][:20],
                                                              prediction["output"][:20],
                                                              prediction["elapsed_time"]))
