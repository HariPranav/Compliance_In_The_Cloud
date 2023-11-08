from aws_cdk import (
aws_ec2 as ec2, aws_ecs as ecs,
                     aws_ecs_patterns as ecs_patterns,
                     aws_iam as iam,
                     aws_ecr as ecr,
                     Stack
)



from constructs import Construct

class MyEcsConstructStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecr_repository = ecr.Repository.from_repository_attributes(
            self,
            "ECRRepository",
            repository_name="prowler",
            # Run a command to get the arn of  https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecr/describe-repositories.html
            repository_arn="arn:aws:ecr:us-east-1:170668165872:repository/prowler"
            
            
            # repository_uri="AccountId.dkr.ecr.us-east-1.amazonaws.com/prowler:latest",
        )
        # The code that defines your stack goes here
        # example resource
        # queue = sqs.Queue(
        #     self, "MyEcsConstructQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        vpc = ec2.Vpc(self, "MyVpc", max_azs=2)     # default is all AZs in region
        existing_task_role_arn = "arn:aws:iam::170668165872:role/ecsTaskExecutionRole"
        existing_execution_role_arn = "arn:aws:iam::170668165872:role/ecsTaskExecutionRole"
        # Define a task role using the provided ARN
        task_role = iam.Role.from_role_arn(
            self,
            "ExistingTaskRole",
            role_arn=existing_task_role_arn,
        )
        # ecr_repository.grant_pull(task_role) 
        # Define a task execution role using the provided ARN
        execution_role = iam.Role.from_role_arn(
            self,
            "ExistingExecutionRole",
            role_arn=existing_execution_role_arn,
        )
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)
        ecs_patterns.ApplicationLoadBalancedFargateService(self, "MyFargateService",
            cluster=cluster,            # Required
            cpu=512,                    # Default is 256
            desired_count=1,            # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
            image=ecs.ContainerImage.from_ecr_repository(repository= ecr_repository, tag="latest"),
            task_role=task_role,  # Assign the existing task role
            execution_role=execution_role,  # Assign the existing execution role
            container_name="prowler"
            ),
            memory_limit_mib=2048,      # Default is 512
            public_load_balancer=True)  # Default is True         
