import httpx
import typer

from neosctl import util
from neosctl.auth import ensure_login
from neosctl.util import process_response

app = typer.Typer()


def _consume_url(ctx: typer.Context) -> str:
    return "{}/consume".format(ctx.obj.gateway_api_url.rstrip("/"))


@app.command()
def query(
    ctx: typer.Context,
    statement: str = typer.Argument(..., callback=util.sanitize),
) -> None:
    """Query a published data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            url=_consume_url(ctx),
            json={
                "statement": statement,
            },
        )

    r = _request(ctx)
    process_response(r)
