#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "typer",
# ]
# ///
from pathlib import Path
from typing import Annotated, Optional

import typer

from app import consolidate, has_date

app = typer.Typer(help="foo bar baz")


@app.command()
def main(
    csv_files: list[Path],
    out: Annotated[Optional[Path], typer.Option("--out", "-o", help="Write output to a file")] = None,
):
    if all(has_date(f.name) for f in csv_files):
        csv_files = sorted(csv_files, key=lambda f: f.name)
    result = consolidate(*csv_files)
    if out:
        out.write_text(result)
        return
    typer.echo(result)


if __name__ == "__main__":
    app()
