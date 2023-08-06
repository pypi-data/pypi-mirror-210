import os
from lambda_executor import LambdaExecutor


def handler(event, context):
    environment=os.environ['ENV'],  # DEV or TEST
    prefix=os.environ['PREFIX'],    # unique to each cloudformation deployment
    ship_name=os.environ['SHIP'],
    cruise_name=os.environ['CRUISE'],
    sensor_name=os.environ['SENSOR']
    handler = LambdaExecutor(environment, prefix, ship_name, cruise_name, sensor_name)
    handler.execute()

