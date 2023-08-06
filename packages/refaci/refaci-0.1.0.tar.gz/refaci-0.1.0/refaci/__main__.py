from pathlib import Path

import typer

app = typer.Typer(add_completion=False)


@app.command()
def gather(
    old: list[Path] = typer.Option([], "-o", "--old-packages", help="Old packages", exists=True),
    new: list[Path] = typer.Option([], "-n", "--new-packages", help="New packages", exists=True),
):
    from .gather import main

    main(old, new)


@app.callback()
def main():
    ...


if __name__ == "__main__":
    app()
