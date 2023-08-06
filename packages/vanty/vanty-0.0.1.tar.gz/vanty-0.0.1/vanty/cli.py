import typer

from vanty.auth import app as auth
from vanty.dev import app as dev
from vanty.ops import app as ops
from vanty.project import app as project

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="markdown",
    help="""
    Vanty is the fastest way to launch new SaaS & AI products.

    Visit https://www.advantch.com/ for documentation and more information

    """,
)
app.add_typer(auth)
app.add_typer(dev)
app.add_typer(ops)
app.add_typer(project)
