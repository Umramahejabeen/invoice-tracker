import os

import boto3

REGION = os.getenv("AWS_REGION", "ap-south-1")

cloudwatch = boto3.client("cloudwatch", region_name=REGION)

cloudwatch.put_metric_data(
    Namespace="InvoiceTracker",
    MetricData=[
        {
            "MetricName": "DeploymentHealth",
            "Value": 1,
            "Unit": "Count",
        }
    ],
)

print("Pushed DeploymentHealth metric")