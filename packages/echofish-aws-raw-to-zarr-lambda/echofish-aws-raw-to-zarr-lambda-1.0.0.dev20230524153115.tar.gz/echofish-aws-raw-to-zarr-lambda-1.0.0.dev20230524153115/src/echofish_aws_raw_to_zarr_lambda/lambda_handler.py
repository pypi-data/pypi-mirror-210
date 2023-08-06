import os
from lambda_executor import LambdaExecutor


def handler(event, context):
    environment=os.environ['ENV'],  # DEV or TEST
    prefix=os.environ['PREFIX'],  # unique to each cloudformation deployment
    ship_name=os.environ['SHIP'],
    cruise_name=os.environ['CRUISE'],
    sensor_name=os.environ['SENSOR']
    input_bucket=os.environ['INPUT_BUCKET']
    output_bucket=os.environ['OUTPUT_BUCKET']

    print(f"total cpus: {os.cpu_count()}")
    handler = LambdaExecutor(environment, prefix, ship_name, cruise_name, sensor_name, input_bucket, output_bucket, overwrite=True)
    handler.execute()
    print('done')

