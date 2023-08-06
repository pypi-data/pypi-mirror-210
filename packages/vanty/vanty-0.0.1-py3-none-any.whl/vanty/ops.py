from subprocess import call, run

import environ
import rich
import sh
import typer
from rich import print as rprint

app = typer.Typer(
    name="ops",
    help="Operations commands for interacting with providers such as fly.io. "
    "\n this will be moved to plugins in the future.",
    no_args_is_help=True,
)


@app.command()
def set_flyctl_vars():
    """
    Fly.io
    Fetch env vars flyctl environment variables
    """
    env = environ.Env(
        # set casting, default value
        DEBUG=(bool, False),
    )

    # Set the project base directory
    environ.Env.read_env(".envs/.production/.django")

    export_envs = [
        "DJANGO_AWS_SECRET_ACCESS_KEY",
        "DJANGO_ACCOUNT_ALLOW_REGISTRATION",
        "DJANGO_SECRET_KEY",
        "STRIPE_TEST_SECRET_KEY",
        "STRIPE_LIVE_SECRET_KEY",
        "DJSTRIPE_WEBHOOK_SECRET",
        "SINGLESTORE_DB_PASSWORD",
        "TWITTER_ACCESS_TOKEN_SECRET",
        "TWITTER_CLIENT_SECRET",
    ]

    for e in export_envs:
        rich.print(f"exporting {e}={env(e)}")

    call(["fly", "secrets", "set", f"{e}={env(e)}"])


@app.command()
def check_app_status(app_name="demo-app"):
    """Check the app status on fly.io"""
    rich.print("Checking app status")
    sh.fly("status", app=app_name)


@app.command()
def fly_deploy(skip_tests: bool = False):
    """Run tests and deploy to fly.io"""
    rich.print("[green]Checking app status[/green]")
    run(["make", "tests"])
    run(["flyctl", "deploy"])


def process_output(line, stdin, process):
    rprint(line)
    if "ERROR" in line:
        process.kill()
        return True


@app.command()
def fly_db_connect(app_name="demo-app", bg=True):
    """
    Connect to the database
    """
    rprint("[green] Connecting to the database")
    return sh.fly("proxy", "5433:5432", app=app_name, _out=rprint, _bg=bg)
