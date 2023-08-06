import sys
import typing

import httpx

if sys.platform != "win32":
    import jq
else:
    jq = None

import typer

from neosctl import util
from neosctl.auth import ensure_login
from neosctl.services.gateway import schema
from neosctl.util import process_response

app = typer.Typer()


def _product_url(ctx: typer.Context) -> str:
    return "{}/product".format(ctx.obj.get_gateway_api_url().rstrip("/"))


@app.command(name="create")
def create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Data Product name", callback=util.sanitize),
    description: typing.Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="Data Product description",
        callback=util.sanitize,
    ),
    filepath: str = typer.Option(
        ...,
        "--filepath",
        "-f",
        help="Filepath of the details and info json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Create a data product."""

    @ensure_login
    def _request(ctx: typer.Context, dpc: schema.CreateDataProduct) -> httpx.Response:
        return util.post(
            ctx,
            f"{_product_url(ctx)}",
            json=dpc.dict(exclude_none=True, by_alias=True),
        )

    fp = util.get_file_location(filepath)
    content = util.load_object_file(fp, "details")
    details = content["details"]
    info = content["info"]

    dpc = schema.CreateDataProduct(
        name=name,
        description=description or "",
        info=info,  # type: ignore[reportGeneralTypeIssues]
        details=details,  # type: ignore[reportGeneralTypeIssues]
    )

    r = _request(ctx, dpc)
    process_response(r)


@app.command(name="add-schema")
def add_schema(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(..., help="Data Product identifier", callback=util.sanitize),
    filepath: str = typer.Option(
        ...,
        "--filepath",
        "-f",
        help="Filepath of the table schema json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Add a schema to a stored data product."""

    @ensure_login
    def _request(ctx: typer.Context, dps: schema.UpdateDataProductSchema) -> httpx.Response:
        return util.post(
            ctx,
            f"{_product_url(ctx)}/{product_identifier}/schema",
            json=dps.dict(exclude_none=True, by_alias=True),
        )

    fp = util.get_file_location(filepath)
    details = util.load_object_file(fp, "details")

    dps = schema.UpdateDataProductSchema(details=details)  # type: ignore[reportGeneralTypeIssues]

    r = _request(ctx, dps)
    process_response(r)


@app.command(name="update-info")
def update_info(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(..., help="Data Product identifier", callback=util.sanitize),
    filepath: str = typer.Option(
        ...,
        "--filepath",
        "-f",
        help="Filepath of the info json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Update data product info."""

    @ensure_login
    def _request(ctx: typer.Context, dps: schema.UpdateDataProductInfo) -> httpx.Response:
        return util.put(
            ctx,
            f"{_product_url(ctx)}/{product_identifier}/info",
            json=dps.dict(exclude_none=True, by_alias=True),
        )

    fp = util.get_file_location(filepath)
    info = util.load_object_file(fp, "info")

    dps = schema.UpdateDataProductInfo(info=info)  # type: ignore[reportGeneralTypeIssues]

    r = _request(ctx, dps)
    process_response(r)


@app.command(name="list")
def list_products(
    ctx: typer.Context,
    filter_: typing.Optional[str] = typer.Option(
        None,
        "--filter",
        "-f",
        help="jq filter to apply to data_products.",
        callback=util.sanitize,
    ),
    name: typing.Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Filter products for a specific name. (Overrides --filter if provided)",
        callback=util.sanitize,
    ),
) -> None:
    """List data products.

    Provide a filter to access specific elements in the returned list.
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(ctx, _product_url(ctx))

    if jq is None and (name or filter_):
        raise util.exit_with_output(
            msg=f"--filter and --name are not supported on '{sys.platform}'",
            exit_code=1,
        )
    if name:
        filter_ = f'{{data_products: [.data_products[] | select(.name | contains("{name}"))]}}'

    def _filter_products(payload: typing.Dict) -> str:
        """Filter response with an optional jq filter."""
        if filter_:
            output = jq.compile(filter_).input(payload)
            payload = output.all()
            if name:
                payload = output.first()

        return util.prettify_json(payload)

    r = _request(ctx)

    process_response(r, _filter_products)  # type: ignore[reportGeneralTypeIssues]


@app.command()
def delete_data(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(..., help="Data Product identifier", callback=util.sanitize),
) -> None:
    """Delete data from a data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            f"{_product_url(ctx)}/{product_identifier}/data",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def delete(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(..., help="Data Product identifier", callback=util.sanitize),
    *,
    force: bool = typer.Option(
        False,
        "--force",
        help="Force remove even if attached spark application is still running.",
    ),
) -> None:
    """Delete a data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            f"{_product_url(ctx)}/{product_identifier}",
            params={"force": force},
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def publish(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(..., help="Data Product identifier", callback=util.sanitize),
) -> None:
    """Publish a data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            f"{_product_url(ctx)}/{product_identifier}/publish",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def unpublish(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(..., help="Data Product identifier", callback=util.sanitize),
) -> None:
    """Unpublish a product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            f"{_product_url(ctx)}/{product_identifier}/publish",
        )

    r = _request(ctx)
    process_response(r)


@app.command(name="get")
def get_product(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Get data product schema."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            f"{_product_url(ctx)}/{product_identifier}",
        )

    r = _request(ctx)
    process_response(r)


@app.command(name="get-links")
def get_product_links(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Get data product links."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            f"{_product_url(ctx)}/{product_identifier}/link",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def preview(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Preview data product data.

    Get the first 25 rows of a data product's data.
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            "{product_url}/{name}/data".format(
                product_url=_product_url(ctx),
                name=product_identifier,
            ),
        )

    r = _request(ctx)
    process_response(r)
