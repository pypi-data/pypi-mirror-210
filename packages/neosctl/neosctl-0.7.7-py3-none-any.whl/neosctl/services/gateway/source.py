import json
from typing import Optional

import httpx
import typer

from neosctl import util
from neosctl.auth import ensure_login
from neosctl.services.gateway import schema
from neosctl.util import process_response

app = typer.Typer()


def _source_url(ctx: typer.Context) -> str:
    return "{}/source".format(ctx.obj.gateway_api_url.rstrip("/"))


def _connection_url(ctx: typer.Context) -> str:
    return "{}/connection".format(ctx.obj.gateway_api_url.rstrip("/"))


def _source_connection_url(ctx: typer.Context, source_id: int, connection_id: int) -> str:
    return "{url}/source/{source_id}/connection/{connection_id}".format(
        url=ctx.obj.gateway_api_url.rstrip("/"),
        source_id=source_id,
        connection_id=connection_id,
    )


@app.command()
def create_source(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Source name", callback=util.sanitize),
    description: str = typer.Option(..., "--description", "-d", help="Source description", callback=util.sanitize),
    filepath: str = typer.Option(
        ...,
        "--filepath",
        "-f",
        help="Filepath of the info json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Create a new source."""

    @ensure_login
    def _request(ctx: typer.Context, content: schema.CreateSource) -> httpx.Response:
        return util.post(
            ctx,
            url=_source_url(ctx),
            json=content.dict(exclude_none=True, by_alias=True),
        )

    fp = util.get_file_location(filepath)
    info = util.load_object_file(fp, "info")
    payload = schema.CreateSource(
        name=name,
        description=description,
        info=info,  # type: ignore[reportGeneralTypeIssues]
    )
    r = _request(ctx, payload)
    process_response(r)


@app.command()
def list_sources(
    ctx: typer.Context,
) -> None:
    """List sources."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            url=_source_url(ctx),
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def get_source(
    ctx: typer.Context,
    source_identifier: int = typer.Argument(..., help="Source identifier", callback=util.sanitize),
) -> None:
    """Get a source."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            url=f"{_source_url(ctx)}/{source_identifier}",
        )

    r = _request(ctx)
    process_response(r)


@app.command(name="get-source-links")
def get_source_links(
    ctx: typer.Context,
    source_identifier: int = typer.Argument(..., help="Source identifier", callback=util.sanitize),
) -> None:
    """Get source links."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            f"{_source_url(ctx)}/{source_identifier}/link",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def update_source(
    ctx: typer.Context,
    source_identifier: int = typer.Argument(..., help="Source identifier", callback=util.sanitize),
    filepath: str = typer.Option(
        ...,
        "--filepath",
        "-f",
        help="Filepath of the source json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Update a source."""

    @ensure_login
    def _request(ctx: typer.Context, content: schema.UpdateSource) -> httpx.Response:
        return util.put(
            ctx,
            url=f"{_source_url(ctx)}/{source_identifier}",
            json=content.dict(exclude_none=True, by_alias=True),
        )

    fp = util.get_file_location(filepath)
    file_content: dict = util.load_json_file(fp, "json")  # type: ignore[reportGeneralTypeIssues]
    payload = schema.UpdateSource(**file_content)
    r = _request(ctx, payload)
    process_response(r)


@app.command()
def update_source_info(
    ctx: typer.Context,
    source_identifier: int = typer.Argument(..., help="Source identifier", callback=util.sanitize),
    filepath: str = typer.Option(
        ...,
        "--filepath",
        "-f",
        help="Filepath of the source info json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Update a source info."""

    @ensure_login
    def _request(ctx: typer.Context, content: schema.UpdateSourceInfo) -> httpx.Response:
        return util.put(
            ctx,
            url=f"{_source_url(ctx)}/{source_identifier}/info",
            json=content.dict(exclude_none=True, by_alias=True),
        )

    fp = util.get_file_location(filepath)
    file_content: dict = util.load_json_file(fp, "info")  # type: ignore[reportGeneralTypeIssues]
    payload = schema.UpdateSourceInfo(**file_content)
    r = _request(ctx, payload)
    process_response(r)


@app.command()
def delete_source(
    ctx: typer.Context,
    source_identifier: int = typer.Argument(..., help="Source identifier", callback=util.sanitize),
) -> None:
    """Delete a source."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            url=f"{_source_url(ctx)}/{source_identifier}",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def create_connection(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Connection name", callback=util.sanitize),
    filepath: str = typer.Option(
        ...,
        "--filepath",
        "-f",
        help="Filepath of the connection json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Create a new connection."""

    @ensure_login
    def _request(ctx: typer.Context, content: schema.CreateConnection) -> httpx.Response:
        return util.post(
            ctx,
            url=_connection_url(ctx),
            json=content.dict(exclude_none=True, by_alias=True),
        )

    fp = util.get_file_location(filepath)
    details: dict = util.load_object_file(fp, "connection")
    payload = schema.CreateConnection(
        name=name,
        details=details,  # type: ignore[reportGeneralTypeIssues]
    )
    r = _request(ctx, payload)
    process_response(r)


@app.command()
def list_connections(
    ctx: typer.Context,
) -> None:
    """List connections."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            url=_connection_url(ctx),
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def get_connection(
    ctx: typer.Context,
    connection_identifier: int = typer.Argument(..., help="Connection identifier", callback=util.sanitize),
) -> None:
    """Get a connection."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            url=f"{_connection_url(ctx)}/{connection_identifier}",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def update_connection(
    ctx: typer.Context,
    connection_identifier: int = typer.Argument(..., help="Connection identifier", callback=util.sanitize),
    filepath: str = typer.Option(
        ...,
        "--filepath",
        "-f",
        help="Filepath of the connection json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Update a connection."""

    @ensure_login
    def _request(ctx: typer.Context, content: schema.CreateConnection) -> httpx.Response:
        return util.put(
            ctx,
            url=f"{_connection_url(ctx)}/{connection_identifier}",
            json=content.dict(exclude_none=True, by_alias=True),
        )

    fp = util.get_file_location(filepath)
    file_content: dict = util.load_json_file(fp, "json")  # type: ignore[reportGeneralTypeIssues]
    payload = schema.CreateConnection(**file_content)
    r = _request(ctx, payload)
    process_response(r)


@app.command()
def delete_connection(
    ctx: typer.Context,
    connection_identifier: int = typer.Argument(..., help="Connection identifier", callback=util.sanitize),
) -> None:
    """Delete a connection."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            url=f"{_connection_url(ctx)}/{connection_identifier}",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def create_source_connection(
    ctx: typer.Context,
    source_identifier: int = typer.Option(
        ...,
        "--source",
        "-s",
        help="Source identifier",
        callback=util.sanitize,
    ),
    connection_identifier: int = typer.Option(
        ...,
        "--connection",
        "-c",
        help="Connection identifier",
        callback=util.sanitize,
    ),
    filepath: Optional[str] = typer.Option(
        None,
        "--filepath",
        "-f",
        help="Filepath of the connected source json payload",
        callback=util.sanitize,
    ),
    raw_json: Optional[str] = typer.Option(
        None,
        "--json",
        "-j",
        help="Connected source json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Create a linkage between source and connection."""

    @ensure_login
    def _request(ctx: typer.Context, content: schema.CreateSourceConnection) -> httpx.Response:
        return util.post(
            ctx,
            url=_source_connection_url(ctx, source_id=source_identifier, connection_id=connection_identifier),
            json=content.dict(exclude_none=True, by_alias=True),
        )

    if filepath:
        fp = util.get_file_location(filepath)
        details: dict = util.load_object_file(fp, "source_connection")  # type: ignore[reportGeneralTypeIssues]
    else:
        details: dict = json.loads(raw_json)  # type: ignore[reportGeneralTypeIssues]

    payload = schema.CreateSourceConnection(details=details)  # type: ignore[reportGeneralTypeIssues]
    r = _request(ctx, payload)
    process_response(r)


@app.command()
def update_source_connection(
    ctx: typer.Context,
    source_identifier: int = typer.Option(
        ...,
        "--source",
        "-s",
        help="Source identifier",
        callback=util.sanitize,
    ),
    connection_identifier: int = typer.Option(
        ...,
        "--connection",
        "-c",
        help="Connection identifier",
        callback=util.sanitize,
    ),
    filepath: Optional[str] = typer.Option(
        None,
        "--filepath",
        "-f",
        help="Filepath of the connected source json payload",
        callback=util.sanitize,
    ),
    raw_json: Optional[str] = typer.Option(
        None,
        "--json",
        "-j",
        help="Connected source json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Update a linkage between source and connection."""

    @ensure_login
    def _request(ctx: typer.Context, content: schema.CreateSourceConnection) -> httpx.Response:
        return util.put(
            ctx,
            url=_source_connection_url(ctx, source_id=source_identifier, connection_id=connection_identifier),
            json=content.details.dict(exclude_none=True, by_alias=True),
        )

    if filepath:
        fp = util.get_file_location(filepath)
        details: dict = util.load_object_file(fp, "source_connection")  # type: ignore[reportGeneralTypeIssues]
    else:
        details: dict = json.loads(raw_json)  # type: ignore[reportGeneralTypeIssues]

    payload = schema.CreateSourceConnection(details=details)  # type: ignore[reportGeneralTypeIssues]
    r = _request(ctx, payload)
    process_response(r)


@app.command()
def delete_source_connection(
    ctx: typer.Context,
    source_identifier: int = typer.Option(
        ...,
        "--source",
        "-s",
        help="Source identifier",
        callback=util.sanitize,
    ),
    connection_identifier: int = typer.Option(
        ...,
        "--connection",
        "-c",
        help="Connection identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Delete a linkage between source and and connection."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            url=f"{_source_connection_url(ctx, source_id=source_identifier, connection_id=connection_identifier)}",
        )

    r = _request(ctx)
    process_response(r)
