import typer
import os
import sys

# add scaneo to path
# scaneo_dir = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.join(scaneo_dir))

app = typer.Typer()


@app.command()
def run(port: int = typer.Option(8000, help="Port to run the server on")):
    os.system(f"uvicorn api:app --reload --port {port}")


if __name__ == "__main__":
    app()
