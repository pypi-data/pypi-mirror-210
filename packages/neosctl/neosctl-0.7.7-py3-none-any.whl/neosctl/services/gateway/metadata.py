import httpx
import typer

from neosctl import util
from neosctl.auth import ensure_login
from neosctl.services.gateway import schema
from neosctl.util import process_response

app = typer.Typer()

product_app = typer.Typer()
tag_app = typer.Typer()
pipeline_app = typer.Typer()
browse_app = typer.Typer()

app.add_typer(product_app, name="product", help="Manage product metadata.")
app.add_typer(tag_app, name="tag", help="Manage tags.")
app.add_typer(browse_app, name="browse", help="Browse external data source metadata.")
app.add_typer(pipeline_app, name="pipeline", help="Manage data source pipelines.")


def _metadata_url(ctx: typer.Context, postfix: str = "") -> str:
    return "{}/metadata{}".format(ctx.obj.get_gateway_api_url().rstrip("/"), postfix)


@product_app.command()
def get(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Get data product metadata."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            _metadata_url(ctx, f"/product/{product_identifier}"),
        )

    r = _request(ctx)

    process_response(r)


@tag_app.command("add")
def add_tag(
    ctx: typer.Context,
    tag: str = typer.Argument(..., callback=util.sanitize),
    scope: str = typer.Option("field", "--scope", "-s", callback=util.sanitize),
) -> None:
    """Add a tag."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            _metadata_url(ctx, "/tag"),
            json={
                "tag": tag.lower(),
                "scope": scope.upper(),
            },
        )

    r = _request(ctx)

    process_response(r)


@tag_app.command("remove")
def remove_tag(
    ctx: typer.Context,
    tag: str = typer.Argument(..., callback=util.sanitize),
    scope: str = typer.Option("field", "--scope", "-s", callback=util.sanitize),
) -> None:
    """Remove a tag."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            url=_metadata_url(ctx, "/tag"),
            json={
                "tag": tag.lower(),
                "scope": scope.upper(),
            },
        )

    r = _request(ctx)

    process_response(r)


@tag_app.command("list")
def list_tags(
    ctx: typer.Context,
    *,
    tag_filter: str = typer.Option(None, "--tag-filter", "-t", callback=util.sanitize),
    scope: str = typer.Option("field", "--scope", "-s", callback=util.sanitize),
    system_defined: bool = typer.Option(False, "--system-defined"),
) -> None:
    """List tags.

    Tag list can be filtered using `-t/--tag-filter`, and the tag scope can be
    defined using `-s/--scope [PRODUCT|FIELD]`.
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        params = {"scope": scope.upper(), "system_defined": system_defined}
        if tag_filter:
            params["tag_filter"] = tag_filter
        return util.get(
            ctx,
            url=_metadata_url(ctx, "/tag"),
            params=params,
        )

    r = _request(ctx)

    process_response(r)


@browse_app.command()
def source_types(ctx: typer.Context) -> None:
    """List source types."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            url=_metadata_url(ctx, "/browse"),
        )

    r = _request(ctx)

    process_response(r)


@browse_app.command("databases")
def browse_databases(
    ctx: typer.Context,
    source_type: str = typer.Option(..., "--source-type", "-s", callback=util.sanitize),
) -> None:
    """List databases by source type."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            url=_metadata_url(ctx, f"/browse/{source_type}"),
        )

    r = _request(ctx)

    process_response(r)


@browse_app.command("datasets")
def browse_datasets(
    ctx: typer.Context,
    source_type: str = typer.Option(..., "--source-type", "-s", callback=util.sanitize),
    database: str = typer.Option(..., "--database", "-d", callback=util.sanitize),
) -> None:
    """List datasets by source type and database."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            url=_metadata_url(ctx, f"/browse/{source_type}/{database}"),
        )

    r = _request(ctx)

    process_response(r)


@browse_app.command("dataset-metadata")
def browse_dataset_metadata(
    ctx: typer.Context,
    source_type: str = typer.Option(..., "--source-type", "-s", callback=util.sanitize),
    database: str = typer.Option(..., "--database", "-d", callback=util.sanitize),
    dataset_urn: str = typer.Option(..., "--dataset-urn", "-du", callback=util.sanitize),
) -> None:
    """Get dataset metadata by source type, database and dataset urn."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            url=_metadata_url(ctx, f"/browse/{source_type}/{database}/{dataset_urn}"),
        )

    r = _request(ctx)

    process_response(r)


@pipeline_app.command("add")
def add_pipeline(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", callback=util.sanitize),
    *,
    schedule: str = typer.Option(
        ...,
        "--schedule",
        "-s",
        help='Pipeline schedule in crontab format (e.g. "* * * * *")',
        callback=util.sanitize,
    ),
    schedule_timezone: str = typer.Option(..., "--schedule-timezone", "-st", callback=util.sanitize),
    source: str = typer.Option(
        ...,
        "--source",
        "-sr",
        help="Data source DSN (e.g. mysql://user:pass@host:3306/dbname)",
        callback=util.sanitize,
    ),
    include_tables: bool = typer.Option(True, "--include-tables", "-it", help="Applies only to relational DBs"),
    include_views: bool = typer.Option(True, "--include-views", "-iv", help="Applies only to relational DBs"),
) -> None:
    """Add an ingestion pipeline."""
    source_url = httpx.URL(source)
    request_data = {
        "pipeline_type": source_url.scheme,
        "pipeline_name": name,
        "schedule": schedule,
        "schedule_timezone": schedule_timezone,
        "source": {
            "host": source_url.netloc.decode(),
            "database": source_url.path.lstrip("/"),
            "username": source_url.username,
            "password": source_url.password,
            "include_tables": include_tables,
            "include_views": include_views,
        },
    }

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            _metadata_url(ctx, "/pipeline"),
            json=request_data,
        )

    r = _request(ctx)

    process_response(r)


@pipeline_app.command("remove")
def remove_pipeline(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", callback=util.sanitize),
) -> None:
    """Remove an ingestion pipeline."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            _metadata_url(ctx, "/pipeline"),
            json={
                "pipeline_name": name,
            },
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("description")
def product_description(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    description: str = typer.Option(..., "--description", "-d", callback=util.sanitize),
) -> None:
    """Add a product description."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            _metadata_url(ctx, f"/product/{product_identifier}/description"),
            json={
                "description": description,
            },
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("tag")
def product_tag(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    tag: str = typer.Option(..., "--tag", "-t", callback=util.sanitize),
) -> None:
    """Add a product tag."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            _metadata_url(ctx, f"/product/{product_identifier}/tag"),
            json={
                "tag": tag.lower(),
            },
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("remove-tag")
def remove_product_tag(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    tag: str = typer.Option(..., "--tag", "-t", callback=util.sanitize),
) -> None:
    """Remove a product tag."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            url=_metadata_url(ctx, f"/product/{product_identifier}/tag"),
            json={
                "tag": tag.lower(),
            },
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("field-tag")
def product_field_tag(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    field: str = typer.Option(..., "--field", "-f", callback=util.sanitize),
    tag: str = typer.Option(..., "--tag", "-t", callback=util.sanitize),
) -> None:
    """Add a product field tag."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            _metadata_url(ctx, f"/product/{product_identifier}/{field}/tag"),
            json={
                "tag": tag.lower(),
            },
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("remove-field-tag")
def remove_product_field_tag(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    field: str = typer.Option(..., "--field", "-f", callback=util.sanitize),
    tag: str = typer.Option(..., "--tag", "-t", callback=util.sanitize),
) -> None:
    """Remove a product field tag."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            url=_metadata_url(ctx, f"/product/{product_identifier}/{field}/tag"),
            json={
                "tag": tag.lower(),
            },
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("field-description")
def product_field_description(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    field: str = typer.Option(..., "--field", "-f", callback=util.sanitize),
    description: str = typer.Option(..., "--description", "-d", callback=util.sanitize),
) -> None:
    """Add a product field description."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            _metadata_url(ctx, f"/product/{product_identifier}/{field}/description"),
            json={
                "description": description,
            },
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("quality-rules")
def quality_rules(
    ctx: typer.Context,
) -> None:
    """Get quality expectations rules."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            _metadata_url(ctx, "/quality/rules"),
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("edit-quality-expectations")
def edit_product_quality_expectations(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    filepath: str = typer.Option(
        ...,
        "--filepath",
        "-f",
        help="Filepath of the details json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Update data product quality expectations."""

    @ensure_login
    def _request(ctx: typer.Context, uqe: schema.UpdateQualityExpectations) -> httpx.Response:
        return util.put(
            ctx,
            _metadata_url(ctx, f"/product/{product_identifier}/quality/expectation"),
            json=uqe.dict(exclude_none=True, by_alias=True),
        )

    fp = util.get_file_location(filepath)
    details = util.load_object_file(fp, "")

    uqe = schema.UpdateQualityExpectations(
        custom_details=details["custom_details"],  # type: ignore[reportGeneralTypeIssues]
        weights=details["weights"],  # type: ignore[reportGeneralTypeIssues]
        thresholds=details["thresholds"],  # type: ignore[reportGeneralTypeIssues]
    )

    r = _request(ctx, uqe)

    process_response(r)


@product_app.command("quality-expectations")
def product_quality_expectations(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Get data product quality expectations."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            _metadata_url(ctx, f"/product/{product_identifier}/quality/expectations"),
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("quality-profiling")
def product_quality_profiling(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Get data product quality profiling."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            _metadata_url(ctx, f"/product/{product_identifier}/quality/profiling"),
        )

    r = _request(ctx)

    process_response(r)


@product_app.command("quality-validations")
def product_quality_validations(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Get data product quality validations."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            _metadata_url(ctx, f"/product/{product_identifier}/quality/validations"),
        )

    r = _request(ctx)

    process_response(r)
