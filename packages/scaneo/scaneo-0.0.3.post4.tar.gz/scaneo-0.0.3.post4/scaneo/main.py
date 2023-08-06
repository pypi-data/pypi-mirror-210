import typer
import os

app = typer.Typer()


@app.command()
def run(port: int = typer.Option(8000, help="Port to run the server on")):
    os.system(f"uvicorn api:app --reload --port {port}")


if __name__ == "__main__":
    app()
