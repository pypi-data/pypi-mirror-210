from lambda_executor import LambdaExecutor


def handler(event, context):
    handler = LambdaExecutor()
    handler.execute(event, context)

