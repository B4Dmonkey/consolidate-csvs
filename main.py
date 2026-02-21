#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "typer",
# ]
# ///
from pathlib import Path

import typer

from app import consolidate

app = typer.Typer(help="foo bar baz")


@app.command()
def main(csv_files: list[Path]):
    typer.echo(consolidate(*csv_files))


if __name__ == "__main__":
    app()
