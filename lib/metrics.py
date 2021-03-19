from typing import Dict, List
import logging

import boto3

from lib.config import config, STAGE, REGION

client = boto3.client("cloudwatch", REGION)
SERVICE = config.get("SERVICE")


class Unit:
    SECONDS = "Seconds"
    MICROSECONDS = "Microseconds"
    MILLISECONDS = "Milliseconds"
    BYTES = "Bytes"
    KILOBYTES = "Kilobytes"
    MEGABYTES = "Megabytes"
    GIGABYTES = "Gigabytes"
    TERABYTES = "Terabytes"
    BITS = "Bits"
    KILOBITS = "Kilobits"
    MEGABITS = "Megabits"
    GIGABITS = "Gigabits"
    TERABITS = "Terabits"
    PERCENT = "Percent"
    COUNT = "Count"
    BYTES_PER_SECOND = "Bytes/Second"
    KILOBYTES_PER_SECOND = "Kilobytes/Second"
    MEGABYTES_PER_SECOND = "Megabytes/Second"
    GIGABYTES_PER_SECOND = "Gigabytes/Second"
    TERABYTES_PER_SECOND = "Terabytes/Second"
    BITS_PER_SECOND = "Bits/Second"
    KILOBITS_PER_SECOND = "Kilobits/Second"
    MEGABITS_PER_SECOND = "Megabits/Second"
    GIGABITS_PER_SECOND = "Gigabits/Second"
    TERABITS_PER_SECOND = "Terabits/Second"
    COUNT_PER_SECOND = "Count/Second"


def write_metric(
    name: str,
    value: float,
    unit: str = Unit.COUNT,
    tags: Dict[str, str] = None,
) -> None:
    if STAGE == "local":
        logging.info(
            f"Skipping metric write for name:{name} | value:{value} | tags:{tags}"
        )
        return
    default_tags = {"stage": STAGE}
    if tags:
        default_tags.update(tags)
    formatted_tags = [{"Name": k, "Value": v} for k, v in default_tags.items()]

    client.put_metric_data(
        Namespace=SERVICE,
        MetricData=[
            {
                "MetricName": name,
                "Dimensions": formatted_tags,
                "Value": value,
                "Unit": unit,
            },
        ],
    )


def write_aggregate_metrics(
    name: str, unit: str = Unit.COUNT, values=List[float]
) -> None:
    if STAGE == "local":
        logging.info(
            f"Skipping aggregate metric write for name:{name} | values:{values}"
        )
        return

    client.put_metric_data(
        Namespace=SERVICE,
        MetricData=[
            {
                "MetricName": name,
                "StatisticValues": {
                    "SampleCount": len(values),
                    "Sum": sum(values),
                    "Minimum": min(values),
                    "Maximum": max(values),
                },
                "Unit": unit,
            },
        ],
    )
