import logging
import json

import boto3
from botocore.exceptions import ClientError

from lib.config import REGION


session = boto3.session.Session()
client = session.client(service_name="secretsmanager", region_name=REGION)


def get_secret(secret_id):
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_id)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logging.error(f"The requested secret {secret_id} was not found")
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            logging.error("The request was invalid")
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            logging.error("The request had invalid params")
        raise (e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary,
        # only one of these fields will be populated
        if "SecretString" in get_secret_value_response:
            secret_data = get_secret_value_response["SecretString"]
        else:
            secret_data = get_secret_value_response["SecretBinary"]

    return json.loads(secret_data)
