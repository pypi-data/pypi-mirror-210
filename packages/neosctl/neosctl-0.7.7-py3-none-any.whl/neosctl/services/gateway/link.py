import httpx
import typer

from neosctl import util
from neosctl.auth import ensure_login
from neosctl.util import process_response

app = typer.Typer()


def _link_url(ctx: typer.Context) -> str:
    return "{}/link".format(ctx.obj.gateway_api_url.rstrip("/"))


@app.command(name="list")
def list_links(
    ctx: typer.Context,
) -> None:
    """List all links."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            url=_link_url(ctx),
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def link_product_product(
    ctx: typer.Context,
    parent: str = typer.Argument(..., help="Parent data product identifier", callback=util.sanitize),
    child: str = typer.Argument(..., help="Child data product identifier", callback=util.sanitize),
) -> None:
    """Link data products."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            url=f"{_link_url(ctx)}/product/{parent}/product/{child}",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def unlink_product_product(
    ctx: typer.Context,
    parent: str = typer.Argument(..., help="Parent data product identifier", callback=util.sanitize),
    child: str = typer.Argument(..., help="Child data product identifier", callback=util.sanitize),
) -> None:
    """Unlink data products."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            url=f"{_link_url(ctx)}/product/{parent}/product/{child}",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def link_source_product(
    ctx: typer.Context,
    parent: str = typer.Argument(..., help="Parent source identifier", callback=util.sanitize),
    child: str = typer.Argument(..., help="Child data product identifier", callback=util.sanitize),
) -> None:
    """Link source and data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            url=f"{_link_url(ctx)}/source/{parent}/product/{child}",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def unlink_source_product(
    ctx: typer.Context,
    parent: str = typer.Argument(..., help="Parent source identifier", callback=util.sanitize),
    child: str = typer.Argument(..., help="Child data product identifier", callback=util.sanitize),
) -> None:
    """Unlink source and data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            url=f"{_link_url(ctx)}/source/{parent}/product/{child}",
        )

    r = _request(ctx)
    process_response(r)
