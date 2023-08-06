import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from ..utils import read, write, STATIC_DIR

console = Console(width=88)


################################################################
# init package
################################################################
def init_package(root):
    from PyInquirer import prompt

    # get project name from input
    fp = Path(root)
    project = fp.absolute().name

    # get private pypi url
    private_pypi = os.getenv("PIP_INDEX_URL") or ""

    # set setup configuration
    setup_conf = [
        {"type": "input", "name": "project", "default": project, "message": "Project Name"},
        {"type": "input", "name": "author", "message": "Author"},
        {"type": "input", "name": "author_email", "message": "Author Email"},
        {"type": "input", "name": "description", "message": "Description"},
        {"type": "input", "name": "long_description", "default": "file: README.md", "message": "Long Description"},
        {"type": "input", "name": "keywords", "message": "Keywords"},
        {"type": "input", "name": "license", "default": "MIT License", "message": "License"},
        {"type": "input", "name": "python_requires", "default": ">= 3.8", "message": "Python Requires"},
        {
            "type": "input",
            "name": "install_requires",
            "message": "Install Requires (e.g., pandas, numpy)",
            "filter": lambda x: [_.strip() for _ in x.split(",")],
        },
        {
            "type": "input",
            "name": "dependency_links",
            "default": private_pypi,
            "message": "Your Private PyPI",
        },
        {"type": "confirm", "name": "confirm", "message": "Confirm Initializer"},
    ]

    # user input
    conf = prompt(setup_conf)
    confirm = conf.pop("confirm")
    if not confirm:
        print("[EXIT] Nothing Happened!")
        return

    # correct install requires
    if conf["install_requires"] is not None:
        if "" not in conf["install_requires"]:
            conf["install_requires"] = ["", *conf["install_requires"]]
        TAB = "    "
        conf["install_requires"] = f"\n{TAB}".join(conf["install_requires"])

    # [WRITE FILES]
    # pyproject.toml
    PYPROJECT_TOML_FILE = "pyproject.toml"
    write(
        dst_fp=fp / PYPROJECT_TOML_FILE,
        content=read(PYPROJECT_TOML_FILE),
    )

    # setup.cfg
    SETUP_CFG_FILE = "setup.cfg"
    write(
        dst_fp=fp / SETUP_CFG_FILE,
        content=read(SETUP_CFG_FILE).format(**conf),
    )

    # make src directory
    (fp / "src").mkdir(exist_ok=True)
    (fp / "src" / conf["project"]).mkdir(exist_ok=True)
    _init = fp / "src" / conf["project"] / "__init__.py"
    if not _init.exists():
        _init.touch()
    (fp / "src" / conf["project"] / STATIC_DIR).mkdir(exist_ok=True)
    _init = fp / "src" / conf["project"] / STATIC_DIR / "__init__.py"
    if not _init.exists():
        _init.touch()

    # [LOGGING]
    summary = "\n".join(
        [
            f"[bold]Python project '{project}' is ready.[/bold]",
            " - Build Package: 'python -m build', python package 'build' is required.",
            " - Upload to PyPI: 'twine upload dist/*', python package 'twine is required.",
        ]
    )
    print()
    console.print(Panel(summary))
