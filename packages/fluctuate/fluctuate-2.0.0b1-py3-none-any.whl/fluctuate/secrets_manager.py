import json
import logging

from fauna.encoding import FaunaDecoder
from faunadb._json import parse_json


class DummyModule:
    """A dummy stand in for the boto3 import that will raise a useful error message
    if any attribute is accessed.
    """

    def __getattr__(self, name):
        raise ImportError(
            "To use AWS Secrets Manager, the `aws_secrets_manager` extra dependency"
            " must be installed."
        )


try:
    import boto3
except ImportError:
    boto3 = DummyModule()

logger = logging.getLogger(__name__)


def get_fauna_secret(arn):
    """Returns the current FaunaDB Key object stored in the AWS SecretsManaqer secret
    pointed to by the provided ARN.

    This first attempts to decode the secret as FQLv10. If that fails, it falls back to
    using the non-public FQLv4 `parse_json` funtion.
    """
    logger.debug("Attempting to instantiate the Secrets Manager client.")
    secrets_manager_client = boto3.client("secretsmanager")
    logger.debug("Successfully instantiated the Secrets Manager client.")

    logger.debug("Attempting to retrieve the secret value with ARN %s.", arn)
    secret = secrets_manager_client.get_secret_value(SecretId=arn)
    logger.debug("Successfully retrieved the secret value with ARN %s.", arn)

    try:
        logger.debug("Attempting to decode the secret with FQLv10 decoders.")
        result = FaunaDecoder.decode(json.loads(secret["SecretString"]))
        logger.debug("Successfully decoded the secret with FQLv10 decoders.")
    except Exception:
        logger.debug(
            "Failed to decode the secret with FQLv10 decoders. Attempting to decode the"
            " secret using FQLv4 decoders."
        )
        result = parse_json(secret["SecretString"])
        logger.debug("Successfully decoded the secret with FQLv4 decoders.")

    return result
