import configparser
import json
import pathlib
import typing

import click
import httpx
import pydantic
import typer
from pygments import formatters, highlight, lexers

from neosctl import constant, schema


def dumps_formatted_json(payload: typing.Union[typing.Dict, typing.List]) -> str:
    """Dump formatted json.

    json.dump provided payload with indent 2 and sorted keys.
    """
    return json.dumps(payload, indent=2, sort_keys=True)


def prettify_json(payload: typing.Union[typing.Dict, typing.List]) -> str:
    """Dump formatted json with colour highlighting."""
    return highlight(dumps_formatted_json(payload), lexers.JsonLexer(), formatters.TerminalFormatter())


def is_success_response(response: httpx.Response) -> bool:
    """Check if a response is `successful`."""
    if constant.SUCCESS_CODE <= response.status_code < constant.REDIRECT_CODE:
        return True
    return False


def exit_with_output(msg: str, exit_code: int = 0) -> typer.Exit:
    """Render output to terminal and exit."""
    typer.echo(msg)

    return typer.Exit(exit_code)


def process_response(
    response: httpx.Response,
    render_callable: typing.Callable[[typing.Union[typing.Dict, typing.List]], str] = prettify_json,
) -> None:
    """Process a server response, render the output and exit."""
    exit_code = 0
    data = response.json()
    if response.status_code >= constant.BAD_REQUEST_CODE:
        exit_code = 1
        message = prettify_json(data)
    else:
        message = render_callable(data)

    raise exit_with_output(
        msg=message,
        exit_code=exit_code,
    )


def read_config_dotfile() -> configparser.ConfigParser:
    """Read in `.neosctl` configuration file and parse."""
    c = configparser.ConfigParser()
    c.read(constant.PROFILE_FILEPATH)
    return c


def get_optional_user_profile_section(
    c: configparser.ConfigParser,
    profile_name: str,
) -> typing.Optional[configparser.SectionProxy]:
    """Get profile from neosctl configuration.

    Returns:
    -------
    Return configparser.SectionProxy if found, or None.
    """
    try:
        return c[profile_name]
    except KeyError:
        return None


def get_user_profile_section(c: configparser.ConfigParser, profile_name: str) -> configparser.SectionProxy:
    """Get profile from neosctl configuration.

    If profile is not found exit cli.

    Returns:
    -------
    configparser.SectionProxy for the requested profile.
    """
    try:
        return c[profile_name]
    except KeyError:
        pass

    raise exit_with_output(
        msg=f"Profile {profile_name} not found.",
        exit_code=1,
    )


def get_user_profile(
    c: configparser.ConfigParser,
    profile_name: str,
    *,
    allow_missing: bool = False,
) -> typing.Optional[typing.Union[schema.Profile, schema.OptionalProfile]]:
    """Get user profile.

    If allow_missing if False and the profile is not found, the cli will exit with an error output.
    """
    if allow_missing:
        profile_config = get_optional_user_profile_section(c, profile_name)
    else:
        profile_config = get_user_profile_section(c, profile_name)

    if profile_config:
        try:
            return schema.Profile(**profile_config)
        except pydantic.ValidationError as e:
            required_fields = [str(err["loc"][0]) for err in e.errors() if err["msg"] == "field required"]
            raise exit_with_output(  # noqa: TRY200, B904
                msg=("Profile dotfile doesn't include fields:\n  {}\nUse neosctl -p {} profile init").format(
                    "\n  ".join(required_fields),
                    profile_name,
                ),
                exit_code=1,
            )
    return None


def bearer(ctx: click.Context) -> typing.Optional[typing.Dict]:
    """Generate bearer authorization header."""
    if not (ctx.obj.profile and ctx.obj.profile.access_token != ""):  # nosec: B105
        return None

    return {"Authorization": f"Bearer {ctx.obj.profile.access_token}"}


def check_profile_exists(ctx: click.Context) -> bool:
    """Check if a profile exists in neosctl configuration or exit."""
    if not ctx.obj.profile:
        raise exit_with_output(
            msg=f"Profile not found! Run neosctl -p {ctx.obj.profile_name} profile init",
            exit_code=1,
        )

    return True


def upsert_config(
    ctx: click.Context,
    profile: schema.Profile,
) -> configparser.ConfigParser:
    """Update neosctl configuration profile in place."""
    ctx.obj.config[ctx.obj.profile_name] = profile.dict()

    with constant.PROFILE_FILEPATH.open("w") as profile_file:
        ctx.obj.config.write(profile_file)

    return ctx.obj.config


def remove_config(
    ctx: click.Context,
) -> configparser.ConfigParser:
    """Remove a profile from neosctl configuration."""
    if not ctx.obj.config.remove_section(ctx.obj.profile_name):
        raise exit_with_output(
            msg=f"Can not remove {ctx.obj.profile_name} profile, profile not found.",
            exit_code=1,
        )

    with constant.PROFILE_FILEPATH.open("w") as profile_file:
        ctx.obj.config.write(profile_file)

    return ctx.obj.config


def get_file_location(filepath: str) -> pathlib.Path:
    """Get a Path for the provided filepath, exit if not found."""
    fp = pathlib.Path(filepath)
    if not fp.exists():
        raise exit_with_output(
            msg=f"Can not find file: {fp}",
            exit_code=1,
        )
    return fp


def load_json_file(fp: pathlib.Path, content_type: str) -> typing.Union[typing.Dict, typing.List]:
    """Load contents of json file, exit if not found."""
    with fp.open() as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            raise exit_with_output(  # noqa: TRY200, B904
                msg=f"Invalid {content_type} file, must be json format.",
                exit_code=1,
            )
            return []  # never reached as raise exit_with_output, but it makes type checker happy

    return data


def load_object_file(fp: pathlib.Path, content_type: str) -> typing.Dict:
    """Load contents of json file containing an object."""
    r = load_json_file(fp, content_type)
    return dict(r)


def _request(ctx: click.Context, method: str, url: str, **kwargs: ...) -> httpx.Response:
    return httpx.request(method=method, url=url, headers=bearer(ctx), verify=not ctx.obj.profile.ignore_tls, **kwargs)


def get(ctx: click.Context, url: str, **kwargs: ...) -> httpx.Response:
    """Execute a GET request."""
    return _request(ctx, "GET", url, **kwargs)


def post(ctx: click.Context, url: str, **kwargs: ...) -> httpx.Response:
    """Execute a POST request."""
    return _request(ctx, "POST", url, **kwargs)


def put(ctx: click.Context, url: str, **kwargs: ...) -> httpx.Response:
    """Execute a PUT request."""
    return _request(ctx, "PUT", url, **kwargs)


def patch(ctx: click.Context, url: str, **kwargs: ...) -> httpx.Response:
    """Execute a PATCH request."""
    return _request(ctx, "PATCH", url, **kwargs)


def delete(ctx: click.Context, url: str, **kwargs: ...) -> httpx.Response:
    """Execute a DELETE request."""
    return _request(ctx, "DELETE", url, **kwargs)


def sanitize(
    ctx: click.Context,  # noqa: ARG001
    param: click.Parameter,  # noqa: ARG001
    value: typing.Optional[str],
) -> typing.Optional[str]:
    """Parameter's sanitize callback."""
    if value and isinstance(value, str):
        return value.rstrip("\r\n")

    return value


def validate_string_not_empty(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
) -> str:
    """String validation callback."""
    value = value.strip()

    if not value:
        message = "Value must be a non-empty string."
        raise typer.BadParameter(message, ctx=ctx, param=param)

    return value


def validate_strings_are_not_empty(
    ctx: click.Context,
    param: click.Parameter,
    values: typing.List[str],
) -> typing.List[str]:
    """List of strings validation callback."""
    return [validate_string_not_empty(ctx, param, value) for value in values]
