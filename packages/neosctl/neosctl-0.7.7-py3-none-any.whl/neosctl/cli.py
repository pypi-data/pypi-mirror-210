import configparser
import os
import typing

import typer

import neosctl
from neosctl import (
    auth,
    constant,
    profile,
    schema,
    services,
    util,
)
from neosctl.util import get_user_profile, read_config_dotfile


def _generate_common_schema(
    gateway_api_url: str,
    registry_api_url: str,
    iam_api_url: str,
    storage_api_url: str,
    profile_name: str,
    config: configparser.ConfigParser,
    profile: typing.Union[schema.Profile, schema.OptionalProfile, None] = None,
) -> schema.Common:
    """Generate a common schema object.

    Set the default api values using user_profile and cli provided defaults.
    """
    common_schema = schema.Common(
        gateway_api_url=gateway_api_url,
        registry_api_url=registry_api_url,
        iam_api_url=iam_api_url,
        storage_api_url=storage_api_url,
        profile_name=profile_name,
        config=config,
        profile=profile,
    )
    common_schema.gateway_api_url = common_schema.get_gateway_api_url()
    common_schema.registry_api_url = common_schema.get_registry_api_url()
    common_schema.iam_api_url = common_schema.get_iam_api_url()
    common_schema.storage_api_url = common_schema.get_storage_api_url()

    return common_schema


def _version_callback(*, value: bool) -> None:
    """Get current cli version."""
    if value:
        typer.echo(f"neosctl {neosctl.__version__}")
        raise typer.Exit


def _callback(
    ctx: typer.Context,
    version: typing.Optional[bool] = typer.Option(  # noqa: ARG001
        None,
        "--version",
        callback=_version_callback,
        help="Print version and exit.",
    ),
    gateway_api_url: str = typer.Option(
        "",
        "--gateway-api-url",
        "--gurl",
        help="Gateway API URL",
        callback=util.sanitize,
    ),
    registry_api_url: str = typer.Option(
        "",
        "--registry-api-url",
        "--rurl",
        help="Registry API URL",
        callback=util.sanitize,
    ),
    iam_api_url: str = typer.Option("", "--iam-api-url", "--iurl", help="IAM API URL", callback=util.sanitize),
    storage_api_url: str = typer.Option(
        "",
        "--storage-api-url",
        "--surl",
        help="Storage API URL",
        callback=util.sanitize,
    ),
    profile: str = typer.Option(
        os.getenv("NEOSCTL_PROFILE", constant.DEFAULT_PROFILE),
        "--profile",
        "-p",
        help="Profile name",
        callback=util.sanitize,
    ),
) -> None:
    """Inject common configuration defaults into context.

    Allow missing user_profile to support profile generation etc.
    """
    config = read_config_dotfile()
    user_profile = get_user_profile(config, profile, allow_missing=True)

    common_schema = _generate_common_schema(
        gateway_api_url=gateway_api_url,
        registry_api_url=registry_api_url,
        iam_api_url=iam_api_url,
        storage_api_url=storage_api_url,
        profile_name=profile,
        config=config,
        profile=user_profile,
    )

    ctx.obj = common_schema


def _common(
    ctx: typer.Context,
) -> None:
    """Inject required user_profile into context."""
    user_profile = get_user_profile(ctx.obj.config, ctx.obj.profile_name)
    ctx.obj.profile = user_profile


app = typer.Typer(name="neosctl", callback=_callback)
app.add_typer(profile.app, name="profile", help="Manage profiles.")
app.add_typer(auth.app, name="auth", callback=_common, help="Manage authentication status.")
app.add_typer(
    services.gateway.consume.app,
    name="consume",
    callback=_common,
    help="Consume published data products.",
)
app.add_typer(services.iam.app, name="iam", callback=_common, help="Manage access policies.")
app.add_typer(services.storage.app, name="storage", callback=_common, help="Interact with Storage (as a service).")
app.add_typer(services.gateway.metadata.app, name="metadata", callback=_common, help="Manage and browse metadata.")
app.add_typer(services.gateway.product.app, name="product", callback=_common, help="Manage data products.")
app.add_typer(services.gateway.source.app, name="source", help="Manage sources.")
app.add_typer(services.registry.app, name="registry", callback=_common, help="Manage cores and search data products.")
app.add_typer(services.gateway.spark.app, name="spark", callback=_common, help="Manage data product spark jobs.")
app.add_typer(services.gateway.secret.app, name="secret", callback=_common, help="Manage secrets.")
app.add_typer(services.gateway.kafka.app, name="kafka", callback=_common, help="Manage data product kafka streaming.")
app.add_typer(services.gateway.link.app, name="link", callback=_common, help="Manage links.")
