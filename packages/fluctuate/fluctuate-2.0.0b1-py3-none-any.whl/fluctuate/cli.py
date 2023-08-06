import logging
from importlib.metadata import version as version_check

import cloup
from click import ClickException
from click_log import basic_config, simple_verbosity_option
from cloup.constraints import require_one

from fluctuate.migrations import migrate as migrate_function
from fluctuate.migrations import unmigrate as unmigrate_function
from fluctuate.secrets_manager import get_fauna_secret

# Get the root logger on purpose so all other loggers propagate to the CLI configured
# one.
logger = logging.getLogger()
basic_config(logger)

# Credentials will be required by most subcommands. We use this method to re-use the
# decorator declaration for multiple subcommands. We don't place these on the top level
# group because of this issue: https://github.com/janluke/cloup/issues/129
common_options = cloup.option_group(
    "credentials",
    cloup.option(
        "-k",
        "--key",
        # Manually set the envvar so that we can use a consistent environment variable
        # for each subcommand that needs credentials, rather than relying on
        # `auto_envar_prefix` which will require setting a different envvar for each
        # command.
        envvar="FLUCTUATE_KEY",
        help="""
        The FaunaDB admin key.

        This can also be set using the `FLUCTUATE_KEY` environment variable.
        """,
    ),
    cloup.option(
        "-s",
        "--secret-arn",
        # Manually set the envvar so that we can use a consistent environment variable
        # for each subcommand that needs credentials, rather than relying on
        # `auto_envar_prefix` which will require setting a different envvar for each
        # command.
        envvar="FLUCTUATE_SECRET_ARN",
        help="""
        The ARN of the existing Secrets Manager secret that contains a FaunaDB admin
        key.

        Usage of this option requires that the credentials be configured for boto3 via
        one of the following documented methods that does not involve setting the
        credentials on the client or session objects:
        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

        These credentials must have permission to read the secret value.

        This can also be set using the `FLUCTUATE_SECRET_ARN` environment variable.
        """,
    ),
    constraint=require_one,
)


def _process_common_options(key, secret_arn):
    """A common helper method to help process the common options."""
    if secret_arn:
        key = get_fauna_secret(arn=secret_arn)["secret"]

    return key


@cloup.group(invoke_without_command=True)
@cloup.option(
    "--version", is_flag=True, help="""Print the version of Fluctuate and exit."""
)
@simple_verbosity_option(logger)
def cli(version):
    """A simple migration framework for FaunaDB written in Python."""
    if version:
        logger.info("Fluctuate version %s.", version_check("fluctuate"))


@cli.command()
@common_options
def migrate(key, secret_arn):
    """This applies all migrations that need to be applied in a single transaction."""
    logger.info("Applying migrations...")
    migrate_function(key=_process_common_options(key=key, secret_arn=secret_arn))
    logger.info("Done.")


@cli.command()
@common_options
@cloup.option(
    "-t",
    "--target",
    help="""
    The full name of the migration that is targeting to be unapplied. All migrations
    prior to this one will be removed in reverse order.

    The full name of the migration should be of the form "<namespace>.<name>".

    This can also be set using the `FLUCTUATE_UNMIGRATE_TARGET` environment variable.
    """,
)
def unmigrate(key, secret_arn, target):
    """This unapplies all migrations, in reverse order, up to the provided target in a
    single transaction.

    If a target migration is not provided, all migrations are unapplied.
    """
    logger.info("Unapplying migrations...")
    try:
        unmigrate_function(
            key=_process_common_options(key=key, secret_arn=secret_arn), target=target
        )
    except ValueError as exception:
        raise ClickException(exception) from exception

    logger.info("Done.")


def entrypoint():
    """This is the script entrypoint. This has to be done this way to set the
    `auto_envvar_prefix`, as there seems to be no other method to do so.
    """
    # pylint: disable=no-value-for-parameter
    cli(auto_envvar_prefix="FLUCTUATE")
