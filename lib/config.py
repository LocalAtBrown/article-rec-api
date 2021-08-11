import os
import json
from pathlib import Path

import boto3

STAGE = os.environ["STAGE"]
REGION = os.getenv("REGION", "us-east-1")
CWD = str(Path(__file__).parent.resolve())
INPUT_FILEPATH = f"{CWD}/../env.json"
CLIENT = boto3.client("ssm", REGION)


class Config:
    def __init__(self):
        self._config = self.load_env()

    def get_secret(self, secret_key):
        res = CLIENT.get_parameter(Name=secret_key, WithDecryption=True)
        val = res["Parameter"]["Value"]
        try:
            val = json.loads(val)
        except json.decoder.JSONDecodeError:
            # expect this error for strings
            pass
        return val

    def is_secret(self, val):
        if not isinstance(val, str):
            return False

        if val.startswith("/prod") or val.startswith("/dev"):
            return True

    def get(self, var_name):
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
            # if self.is_secret(val):
            #     val = self.get_secret(val)

            config[var_name] = val

        return config


config = Config()
