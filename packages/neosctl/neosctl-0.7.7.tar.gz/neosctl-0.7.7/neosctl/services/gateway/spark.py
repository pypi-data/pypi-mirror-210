import typing

import httpx
import typer

from neosctl import util
from neosctl.auth import ensure_login
from neosctl.util import process_response

app = typer.Typer()


def _spark_url(name: str, gateway_api_url: str) -> str:
    return "{}/spark/{}".format(gateway_api_url.rstrip("/"), name)


@app.command()
def add_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    job_filepath: str = typer.Option(..., "--job-filepath", "-f", callback=util.sanitize),
) -> None:
    """Assign a spark job.

    Assign and configure a spark job for a data product. This will result in a
    one off run of the spark job.
    """

    @ensure_login
    def _request(ctx: typer.Context, f: typing.IO) -> httpx.Response:
        return util.post(
            ctx,
            _spark_url(product_identifier, ctx.obj.gateway_api_url),
            files={"spark_file": f},
        )

    fp = util.get_file_location(job_filepath)

    with fp.open("rb") as f:
        r = _request(ctx, f)

    process_response(r)


@app.command()
def generate_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    json_filepath: str = typer.Option(..., "--json-filepath", "-f", callback=util.sanitize),
    *,
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Generate spark code, but don't save the output.",
    ),
    reassign: bool = typer.Option(
        False,
        "--reassign",
        help="Generate spark code and replace existing spark job.",
    ),
) -> None:
    """Generate and assign a spark job.

    Generate a spark job from source/transformations configuration for a data product. This will result in a
    one off run of the spark job but no output.
    """

    @ensure_login
    def _request(ctx: typer.Context, data: typing.Dict) -> httpx.Response:
        return util.post(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/generate",
            json=data,
        )

    fp = util.get_file_location(json_filepath)
    data = util.load_object_file(fp, "builder")
    data["preview"] = dry_run
    data["reassign"] = reassign

    r = _request(ctx, data)

    process_response(r)


@app.command()
def fetch_job_preview(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Fetch output of generate dry-run."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/preview",
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def job_history(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Get history of spark applications."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/history",
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def run_history(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    suffix: str = typer.Option(None, "--suffix", "-s", callback=util.sanitize),
) -> None:
    """Get history of spark application runs."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            "{spark_url}/history/{suffix}/run".format(
                spark_url=_spark_url(product_identifier, ctx.obj.gateway_api_url),
                suffix=suffix,
            ),
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def job_status(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    suffix: str = typer.Option(None, "--suffix", "-s", callback=util.sanitize),
    run: str = typer.Option(None, "--run", "-r", callback=util.sanitize),
) -> None:
    """Get status of a spark job.

    Defaults to current application status, previous application status or a
    specific scheduled run can be requested.
    """
    params = {
        k: v
        for k, v in {
            "suffix": suffix,
            "run": run,
        }.items()
        if v is not None
    }

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}",
            params=params,
        )

    r = _request(ctx)

    process_response(r)


def _render_logs(payload: typing.Union[typing.Dict, typing.List]) -> str:
    """Render response logs as a string for display in terminal."""
    logs = payload["logs"] if isinstance(payload, dict) else payload
    return "\n".join(logs)


@app.command()
def job_logs(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    suffix: str = typer.Option(None, "--suffix", "-s", callback=util.sanitize),
    run: str = typer.Option(None, "--run", "-r", callback=util.sanitize),
) -> None:
    """Get logs for a spark job.

    Defaults to current application logs, previous application logs or a
    specific scheduled run can be requested.
    """
    params = {
        k: v
        for k, v in {
            "suffix": suffix,
            "run": run,
        }.items()
        if v is not None
    }

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/log",
            params=params,
        )

    r = _request(ctx)

    process_response(r, _render_logs)


@app.command()
def update_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    job_filepath: str = typer.Option(None, "--job-filepath", "-f", callback=util.sanitize),
) -> None:
    """Update an assigned spark job.

    Update the assigned spark job file and/or the spark job configuration values.
    """

    @ensure_login
    def _request(
        ctx: typer.Context,
        f: typing.Optional[typing.IO],
    ) -> httpx.Response:
        files = {"spark_file": f} if f else {}

        return util.put(
            ctx,
            _spark_url(product_identifier, ctx.obj.gateway_api_url),
            files=files,
        )

    if job_filepath:
        fp = util.get_file_location(job_filepath)

        with fp.open("rb") as f:
            r = _request(ctx, f)
    else:
        r = _request(ctx, None)

    process_response(r)


@app.command()
def remove_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    *,
    force: bool = typer.Option(
        False,
        "--force",
        help="Force remove even if application is still running.",
    ),
) -> None:
    """Remove assigned spark job."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            _spark_url(product_identifier, ctx.obj.gateway_api_url),
            params={"force": force},
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def trigger_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Trigger assigned spark job.

    Trigger an additional run of a spark job.
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/trigger",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def schedule_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    schedule: str = typer.Option(
        ...,
        "--schedule",
        "-s",
        help='Schedule in crontab format (e.g. "* * * * *")',
        callback=util.sanitize,
    ),
) -> None:
    """Schedule an assigned spark job.

    Schedule a spark job once it is configured correctly to run periodically.
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.post(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/scheduled",
            json={
                "cron_expression": schedule,
            },
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def reschedule_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    schedule: str = typer.Option(
        ...,
        "--schedule",
        "-s",
        help='Schedule in crontab format (e.g. "* * * * *")',
        callback=util.sanitize,
    ),
) -> None:
    """Reschedule an assigned spark job.

    Update existing scheduled spark job run schedule.
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.put(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/scheduled",
            json={
                "cron_expression": schedule,
            },
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def unschedule_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Unschedule a scheduled spark job.

    Remove existing scheduled spark job.
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/scheduled",
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def stream_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    trigger_interval: str = typer.Option(
        ...,
        "--trigger",
        "-t",
        help='Trigger interval in spark format (e.g. "30 seconds")',
    ),
) -> None:
    """Run an infinite spark job.

    For streaming data product spark job will be created with given trigger interval.
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        params = {"trigger_interval": trigger_interval}

        return util.post(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/streaming",
            params=params,
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def restream_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    trigger_interval: str = typer.Option(
        ...,
        "--trigger",
        "-t",
        help='Trigger interval in spark format (e.g. "30 seconds")',
    ),
) -> None:
    """Update an infinite spark job.

    For streaming data product spark job will be removed and recreated with given trigger interval.
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        params = {"trigger_interval": trigger_interval}

        return util.put(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/streaming",
            params=params,
        )

    r = _request(ctx)
    process_response(r)


@app.command()
def unstream_job(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Pause an infinite spark job.

    For streaming data product spark job will be removed and recreated with trigger interval "once".
    """

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            f"{_spark_url(product_identifier, ctx.obj.gateway_api_url)}/streaming",
        )

    r = _request(ctx)
    process_response(r)
