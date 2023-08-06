import typing

import httpx
import typer

from neosctl import util
from neosctl.auth import ensure_login
from neosctl.util import process_response

app = typer.Typer(name="secret", help="Manage secrets.")


def _secret_url(gateway_api_url: str, identifier: typing.Optional[str] = None) -> str:
    if identifier:
        return "{}/secret/{}".format(gateway_api_url.rstrip("/"), identifier)
    return "{}/secret".format(gateway_api_url.rstrip("/"))


@app.command()
def add(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Secret name", callback=util.sanitize),
    secrets: typing.List[str] = typer.Option(..., "--secret", "-s", help="Secret in the form key:value"),
    product_identifier: typing.Optional[str] = typer.Option(None, help="Data Product identifier"),
) -> None:
    """Add a set of secrets."""

    @ensure_login
    def _request(ctx: typer.Context, payload: typing.Dict) -> httpx.Response:
        return util.post(
            ctx,
            _secret_url(ctx.obj.gateway_api_url),
            json=payload,
        )

    payload = {"data": {}, "identifier": product_identifier, "name": name}
    for s in secrets:
        key, value = s.split(":", 1)
        payload["data"][key] = value

    r = _request(ctx, payload)

    process_response(r)


@app.command()
def update(
    ctx: typer.Context,
    identifier: str = typer.Argument(..., help="Secret identifier"),
    secrets: typing.List[str] = typer.Option(..., "--secret", "-s", help="Secret in the form key:value"),
) -> None:
    """Update existing secrets.

    This will overwrite existing keys, and add new keys, any keys that already
    exist but aren't provided will remain.
    """

    @ensure_login
    def _request(ctx: typer.Context, payload: typing.Dict) -> httpx.Response:
        return util.patch(
            ctx,
            _secret_url(ctx.obj.gateway_api_url, identifier),
            json=payload,
        )

    payload = {"data": {}}
    for s in secrets:
        name, value = s.split(":", 1)
        payload["data"][name] = value

    r = _request(ctx, payload)

    process_response(r)


@app.command()
def remove(
    ctx: typer.Context,
    identifier: str = typer.Argument(
        ...,
        help="Secret identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Remove secret."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            _secret_url(ctx.obj.gateway_api_url, identifier),
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def remove_key(
    ctx: typer.Context,
    identifier: str = typer.Argument(
        ...,
        help="Secret identifier",
        callback=util.sanitize,
    ),
    keys: typing.List[str] = typer.Option(
        ...,
        "--key",
        "-k",
        help="Key name you wish to remove from secret",
        callback=util.sanitize,
    ),
) -> None:
    """Remove a set of keys from a secret."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            f"{_secret_url(ctx.obj.gateway_api_url, identifier)}/key",
            json={"keys": keys},
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def get(
    ctx: typer.Context,
    identifier: str = typer.Argument(
        ...,
        help="Secret identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Get existing secret keys."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            _secret_url(ctx.obj.gateway_api_url, identifier),
        )

    r = _request(ctx)

    process_response(r)


@app.command("list")
def list_secrets(
    ctx: typer.Context,
) -> None:
    """Get existing secret keys."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            _secret_url(ctx.obj.gateway_api_url),
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def add_connection_secret(
    ctx: typer.Context,
    secret_identifier: str,
    connection_id: str,
) -> None:
    """Add a secret to a connection."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            f"{_secret_url(ctx.obj.gateway_api_url, secret_identifier)}/connection/{connection_id}",
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def remove_connection_secret(
    ctx: typer.Context,
    secret_identifier: str,
    connection_id: str,
) -> None:
    """Remove a secret from a connection."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            f"{_secret_url(ctx.obj.gateway_api_url, secret_identifier)}/connection/{connection_id}",
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def add_product_secret(
    ctx: typer.Context,
    secret_identifier: str,
    product_identifier: str,
) -> None:
    """Add a secret from a data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            f"{_secret_url(ctx.obj.gateway_api_url, secret_identifier)}/product/{product_identifier}",
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def remove_product_secret(
    ctx: typer.Context,
    secret_identifier: str,
    product_identifier: str,
) -> None:
    """Remove a secret from a data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            f"{_secret_url(ctx.obj.gateway_api_url, secret_identifier)}/product/{product_identifier}",
        )

    r = _request(ctx)

    process_response(r)
