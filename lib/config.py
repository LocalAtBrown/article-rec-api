import json
import logging
import os
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import NoCredentialsError

STAGE = os.environ["STAGE"]
REGION = os.getenv("REGION", "us-east-1")
CWD = str(Path(__file__).parent.resolve())
INPUT_FILEPATH = f"{CWD}/../env.json"
CLIENT = boto3.client("ssm", REGION)


class Config:
    def __init__(self):
        self._config = self.load_env()

    def get_secret(self, secret_key: str) -> Any:
        res = CLIENT.get_parameter(Name=secret_key, WithDecryption=True)
        val = res["Parameter"]["Value"]
        try:
            val = json.loads(val)
        except json.decoder.JSONDecodeError:
            # expect this error for strings
            pass
        return val

    def is_secret(self, val: str) -> bool:
        try:
            return val.startswith("/prod") or val.startswith("/dev")
        except AttributeError:
            return False

    def get(self, var_name: str) -> Any:
        try:
            val = self._config[var_name]
        except KeyError:
            raise TypeError(f"Variable {var_name} not found in config")

        return val

    def load_env(self):
        with open(INPUT_FILEPATH) as json_file:
            env_vars = json.load(json_file)

        config = {}
        stage_env = env_vars.get("default", {})
        stage_env.update(env_vars[STAGE])

        for var_name, val in stage_env.items():
            if self.is_secret(val):
                try:
                    val = self.get_secret(val)
                except NoCredentialsError:
                    # alright if github action test workflow does not have aws credentials
                    logging.warning(f"AWS credentials missing. Can't fetch secret: '{val}'")

            config[var_name] = val

        return config


config = Config()
