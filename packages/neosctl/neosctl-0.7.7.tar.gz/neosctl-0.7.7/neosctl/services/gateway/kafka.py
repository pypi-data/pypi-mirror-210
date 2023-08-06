import typing

import httpx
import typer

from neosctl import util
from neosctl.auth import ensure_login
from neosctl.util import process_response

app = typer.Typer()


def _kafka_topic_url(data_product: str, gateway_api_url: str) -> str:
    return "{}/kafka/{}/topic".format(gateway_api_url.rstrip("/"), data_product)


def _kafka_url(data_product: str, gateway_api_url: str) -> str:
    return "{}/kafka/{}".format(gateway_api_url.rstrip("/"), data_product)


@app.command()
def create_topic(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
    num_partitions: int = typer.Option(
        1,
        "--partitions",
        help="Number of partitions to create.",
    ),
    replication_factor: typing.Optional[int] = typer.Option(
        None,
        "--replication-factor",
        help="Replication factor of partitions, or -1 if replica_assignment is used.",
    ),
    replica_assignment: typing.Optional[str] = typer.Option(
        None,
        "--replica-assignment",
        help="""<bid_p1_r1:bid_p1_r2,bid_p2_r1:bid_p2_r2> A string representing list of manual partition to broker
        assignments for topic being created.
        Replication assignment (list of lists). The outer list index represents the partition index,
        the inner list is the replica assignment (broker ids) for that partition.
        replication_factor and replica_assignment are mutually exclusive.""",
        callback=util.sanitize,
    ),
    config: typing.Optional[typing.List[str]] = typer.Option(
        None,
        "--config",
        help="""<name=value> An override of the topic configuration being created.
        See http://kafka.apache.org/documentation.html#topicconfigs.""",
        callback=util.sanitize,
    ),
) -> None:
    """Create kafka topic for data product."""

    @ensure_login
    def _request(ctx: typer.Context, topic_settings: typing.Dict) -> httpx.Response:
        return util.post(
            ctx,
            _kafka_topic_url(product_identifier, ctx.obj.gateway_api_url),
            json=topic_settings,
        )

    topic_settings: typing.Dict[str, typing.Any] = {
        "num_partitions": num_partitions,
    }
    if replication_factor:
        topic_settings["replication_factor"] = replication_factor

    if replica_assignment:
        replica_assignments = []
        for assignment in replica_assignment.split(","):
            broker_ids = [int(a) for a in assignment.split(":")]
            replica_assignments.append(broker_ids)
        topic_settings["replica_assignment"] = replica_assignments

    if config:
        overrides = {}
        for override in config:
            name, value = override.split("=")
            overrides[name] = value
        topic_settings["config"] = overrides

    r = _request(ctx, topic_settings)

    process_response(r)


@app.command()
def list_topic(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """List kafka topic from data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            _kafka_topic_url(product_identifier, ctx.obj.gateway_api_url),
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def delete_topic(
    ctx: typer.Context,
    product_identifier: str = typer.Argument(
        ...,
        help="Data Product identifier",
        callback=util.sanitize,
    ),
) -> None:
    """Delete kafka topic from data product."""

    @ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.delete(
            ctx,
            _kafka_topic_url(product_identifier, ctx.obj.gateway_api_url),
        )

    r = _request(ctx)

    process_response(r)


@app.command()
def produce(
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
        help="Filepath of the records json payload",
        callback=util.sanitize,
    ),
) -> None:
    """Send one or more records to a given topic, optionally specifying a partition, key, or both.

    JSON example

    \b
    {
      "records": [
        {
          "key": "string",
          "value": "string",
          "partition": 0
        }
      ]
    }
    """  # noqa: D301

    @ensure_login
    def _request(ctx: typer.Context, data: typing.Dict) -> httpx.Response:
        return util.post(
            ctx,
            _kafka_url(product_identifier, ctx.obj.gateway_api_url),
            json=data,
        )

    fp = util.get_file_location(filepath)
    data = util.load_object_file(fp, "records")

    r = _request(ctx, data)

    process_response(r)
