import os

class LambdaExecutor:

    def __init__(self):
        pass

    def __print_diagnostics(self, context):
        # print(f"TEMPDIR: {TEMPDIR}")
        print(f"Lambda function ARN: {context.invoked_function_arn}")
        print(f"CloudWatch log stream name: {context.log_stream_name}")
        print(f"CloudWatch log group name: {context.log_group_name}")
        print(f"Lambda Request ID: {context.aws_request_id}")
        print(f"Lambda function memory limits in MB: {context.memory_limit_in_mb}")
        print(f"Lambda time remaining in MS: {context.get_remaining_time_in_millis()}")
        print(f"_HANDLER: {os.environ['_HANDLER']}")
        print(f"AWS_EXECUTION_ENV: {os.environ['AWS_EXECUTION_ENV']}")
        # print(f"AWS_LAMBDA_FUNCTION_MEMORY_SIZE: {os.environ['AWS_LAMBDA_FUNCTION_MEMORY_SIZE']}")

    def execute(self, event, context):
        self.__print_diagnostics(context)

