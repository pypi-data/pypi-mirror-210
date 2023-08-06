import os
import yaml

import click

from .main import main, CONTEXT_SETTINGS
from .config import config, banner


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def get(env):
    # banner("User", env.__dict__)
    pass
