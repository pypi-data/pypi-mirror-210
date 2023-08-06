from __future__ import print_function, unicode_literals

import click


################################################################
# CLIs
################################################################
@click.group()
def bibigo():
    pass


################
# init
################
@bibigo.group()
def init():
    pass


@init.command()
@click.argument("root")
def settings(root):
    from .init.settings import init_settings

    init_settings(root, verbose=True)


@init.command()
@click.argument("root")
def package(root):
    from .init.package import init_package
    from .init.settings import init_settings

    init_settings(root)
    init_package(root)
    
@init.command()
@click.argument("root")
def docker_compose(root):
    from .init.docker_compose import init_stack
    
    init_stack(root)


################
# debug
################
@bibigo.group()
def debug():
    pass


@debug.command()
@click.argument("filename")
@click.option("--version", default="default")
def file(filename, version):
    from .utils import read

    content = read(fn=filename, version=version)
    print(content)
