from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    Duration,
    aws_iam as iam
    # aws_sqs as sqs,
)
import aws_cdk.aws_s3 as s3
from constructs import Construct

class OptimisationCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # Here define a Lambda Layer 
        ortools_lambda_layer = _lambda.LayerVersion(
            self, 'OrtoolsLambdaLayer',
            code=_lambda.Code.from_asset('ortoolsfolder'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
            description='ortools Library',
            layer_version_name='ortoolsv1'
        )

        optimise_lambda = _lambda.Function(
            self, 'OptimisationHandler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda'),
            handler='optimisation.handler',
            timeout=Duration.seconds(300),
            layers=[ortools_lambda_layer],
        )
        optimise_lambda.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
        # bucket = s3.Bucket(self, "optimisation", versioned=True)
        # example resource
        # queue = sqs.Queue(
        #     self, "OptimisationCdkQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
