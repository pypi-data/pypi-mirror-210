import typer

app = typer.Typer()


@app.command()
def hello():
    typer.echo("hello")


if __name__ == "__main__":
    app()
