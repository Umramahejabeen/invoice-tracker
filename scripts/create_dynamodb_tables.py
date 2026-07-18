import boto3

REGION = "ap-south-1"

dynamodb = boto3.client("dynamodb", region_name=REGION)

tables = [
    {
        "TableName": "InvoiceTracker_Clients",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "InvoiceTracker_Invoices",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
]

existing_tables = dynamodb.list_tables()["TableNames"]

for table in tables:
    table_name = table["TableName"]

    if table_name in existing_tables:
        print(f"{table_name} already exists")
        continue

    dynamodb.create_table(**table)
    waiter = dynamodb.get_waiter("table_exists")
    waiter.wait(TableName=table_name)
    print(f"Created {table_name}")