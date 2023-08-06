import boto3

from .. import docker

SESSION_OPTS = {
    "aws_access_key_id": None,
    "aws_secret_access_key": None,
    "aws_session_token": None,
    "region_name": None,
    "botocore_session": None,
    "profile_name": None,
}

################################################################
# Helpers
################################################################
# create client for SecretsManager
def session_maker(
    profile_name=None,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    region_name="ap-northeast-2",
    load_docker_secret=True,
    session_opts=None,
):
    """Create boto3 secretsmanager client.

    Priority:
        1. profile_name
        2. aws_access_key_id & secret_access_key
        3. docker secret (/run/secret)
    """

    # session configuration
    session_opts = session_opts or dict()
    if load_docker_secret:
        docker.load_secrets()
    if region_name is not None:
        session_opts.update({"region_name": region_name})
    if aws_access_key_id is not None:
        if aws_secret_access_key is not None:
            session_opts.update(
                {
                    "aws_access_key_id": aws_access_key_id,
                    "aws_secret_access_key": aws_secret_access_key,
                }
            )
    if profile_name is not None:
        session_opts = {"profile_name": profile_name}

    # return clinet
    return boto3.session.Session(**session_opts)


def validate_response(response, success_codes=[200]):
    meta = response["ResponseMetadata"]
    if meta["HTTPStatusCode"] not in success_codes:
        raise ReferenceError(f"status code {meta['HTTPStatusCode']}, {str(meta)}")
