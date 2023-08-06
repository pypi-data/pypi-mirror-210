import typer
import os
import sys

# add scaneo to path
# scaneo_dir = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.join(scaneo_dir))

app = typer.Typer()


@app.command()
def run(
    port: int = typer.Option(8000, help="Port to run the server on"),
    reload: bool = typer.Option(False, help="Reload the server when files change"),
    host: str = typer.Option("localhost", help="Host to run the server on"),
):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    print(os.getcwd())
    print(os.listdir())
    os.system(
        f"python api.py --port {port} --host {host} {'--reload' if reload else ''}"
    )


if __name__ == "__main__":
    app()
