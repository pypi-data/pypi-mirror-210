import asyncio
import os
from pathlib import Path
from typing import cast

import click
import yaml
from metablock import Metablock, Space

METABLOCK_SPACE = os.environ.get("METABLOCK_SPACE", "")
METABLOCK_API_TOKEN = os.environ.get("METABLOCK_API_TOKEN", "")


def manifest(file_path: Path) -> dict:
    return yaml.safe_load(file_path.read_text())


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--space", "space_name", help="Space name", default=METABLOCK_SPACE)
@click.option("--token", help="metablock API token", default=METABLOCK_API_TOKEN)
def apply(path: str, space_name: str, token: str) -> None:
    """Apply metablock manifest"""
    asyncio.get_event_loop().run_until_complete(_apply(path, space_name, token))


async def _apply(path: str, space_name: str, token: str) -> None:
    if not token:
        click.echo("metablock API token is required", err=True)
        raise click.Abort()
    if not space_name:
        click.echo("metablock space is required", err=True)
        raise click.Abort()
    p = Path(path)
    blocks = []
    for file_path in p.glob("*.yaml"):
        name = file_path.name.split(".")[0]
        blocks.append((name, manifest(file_path)))
    async with Metablock(auth_key=token) as mb:
        space: Space = cast(Space, await mb.spaces.get(space_name))
        svc = await space.blocks.get_list()
        click.echo(f"space {space.name} has {len(svc)} blocks")
        by_name = {s["name"]: s for s in svc}
        for name, config in blocks:
            block = by_name.get(name)
            if block:
                # update
                await mb.services.update(block.id, **config)
                click.echo(f"updated block {name}")
            else:
                # create
                await space.services.create(name=name, **config)
                click.echo(f"created new block {name}")


if __name__ == "__main__":
    cli()
