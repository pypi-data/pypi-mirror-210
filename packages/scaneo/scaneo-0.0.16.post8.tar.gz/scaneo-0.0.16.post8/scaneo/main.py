import typer
import os
import sys

# Add the cli directory to the Python path
scaneo_cli_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(scaneo_cli_dir))

from cli import hello

app = typer.Typer()
app.add_typer(hello.app, name="hello")


@app.command()
def run(
    port: int = typer.Option(8000, help="Port to run the server on"),
    reload: bool = typer.Option(False, help="Reload the server when files change"),
    host: str = typer.Option("localhost", help="Host to run the server on"),
    data: str = typer.Option("data", help="Path to data directory"),
):
    # we run the cli from some directory, but run the api from the directory where this file is
    # operation done by the api will have the same working directory as the one from which the cli is run
    # pass environment variable to the api before the command, parse in api settings object
    os.system(
        f"DATA={data} uvicorn api:app --port {port} --host {host} {'--reload' if reload else ''} --app-dir {os.path.dirname(os.path.realpath(__file__))}"
    )


if __name__ == "__main__":
    app()
