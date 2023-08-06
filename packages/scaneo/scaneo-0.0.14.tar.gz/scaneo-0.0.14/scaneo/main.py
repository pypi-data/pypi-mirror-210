import typer
import os

app = typer.Typer()


@app.command()
def run(
    port: int = typer.Option(8000, help="Port to run the server on"),
    reload: bool = typer.Option(False, help="Reload the server when files change"),
    host: str = typer.Option("localhost", help="Host to run the server on"),
):
    # we run the cli from some directory, but run the api from the directory where this file is
    # operation done by the api will have the same working directory as the one from which the cli is run
    os.system(
        f"uvicorn api:app --port {port} --host {host} {'--reload' if reload else ''} --app-dir {os.path.dirname(os.path.realpath(__file__))}"
    )


if __name__ == "__main__":
    app()
