import json
from typing import Optional

from botocore.client import BaseClient

from dstack.backend.aws import runners
from dstack.backend.aws.utils import retry_operation_on_service_errors
from dstack.backend.base.secrets import SecretsManager
from dstack.core.secret import Secret


class AWSSecretsManager(SecretsManager):
    def __init__(
        self,
        secretsmanager_client: BaseClient,
        iam_client: BaseClient,
        sts_client: BaseClient,
        bucket_name: str,
    ):
        self.secretsmanager_client = secretsmanager_client
        self.iam_client = iam_client
        self.sts_client = sts_client
        self.bucket_name = bucket_name

    def get_secret(self, repo_id: str, secret_name: str) -> Optional[Secret]:
        value = _get_secret_value(
            secretsmanager_client=self.secretsmanager_client,
            secret_key=_get_secret_key(self.bucket_name, repo_id, secret_name),
        )
        if value is None:
            return None
        return Secret(secret_name=secret_name, secret_value=value)

    def add_secret(self, repo_id: str, secret: Secret):
        _add_secret(
            secretsmanager_client=self.secretsmanager_client,
            sts_client=self.sts_client,
            iam_client=self.iam_client,
            bucket_name=self.bucket_name,
            secret_key=_get_secret_key(self.bucket_name, repo_id, secret.secret_name),
            secret_value=secret.secret_value,
        )

    def update_secret(self, repo_id: str, secret: Secret):
        _update_secret(
            secretsmanager_client=self.secretsmanager_client,
            secret_key=_get_secret_key(self.bucket_name, repo_id, secret.secret_name),
            secret_value=secret.secret_value,
        )

    def delete_secret(self, repo_id: str, secret_name: str):
        _delete_secret(
            secretsmanager_client=self.secretsmanager_client,
            secret_key=_get_secret_key(self.bucket_name, repo_id, secret_name),
        )

    def get_credentials(self, repo_id: str) -> Optional[str]:
        return _get_secret_value(
            secretsmanager_client=self.secretsmanager_client,
            secret_key=_get_credentials_key(self.bucket_name, repo_id),
        )

    def add_credentials(self, repo_id: str, data: str):
        _add_secret(
            secretsmanager_client=self.secretsmanager_client,
            sts_client=self.sts_client,
            iam_client=self.iam_client,
            bucket_name=self.bucket_name,
            secret_key=_get_credentials_key(self.bucket_name, repo_id),
            secret_value=data,
        )

    def update_credentials(self, repo_id: str, data: str):
        _update_secret(
            secretsmanager_client=self.secretsmanager_client,
            secret_key=_get_credentials_key(self.bucket_name, repo_id),
            secret_value=data,
        )


def _get_secret_value(
    secretsmanager_client: BaseClient,
    secret_key: str,
) -> Optional[Secret]:
    try:
        return secretsmanager_client.get_secret_value(SecretId=secret_key)["SecretString"]
    except Exception as e:
        if (
            hasattr(e, "response")
            and e.response.get("Error")
            and e.response["Error"].get("Code")
            in ["ResourceNotFoundException", "InvalidRequestException"]
        ):
            return None
        else:
            raise e


def _add_secret(
    sts_client: BaseClient,
    iam_client: BaseClient,
    secretsmanager_client: BaseClient,
    bucket_name: str,
    secret_key: str,
    secret_value: str,
):
    secretsmanager_client.create_secret(
        Name=secret_key,
        SecretString=secret_value,
        Description="Generated by dstack",
        Tags=[
            {"Key": "owner", "Value": "dstack"},
            {"Key": "dstack_bucket", "Value": bucket_name},
        ],
    )
    role_name = runners.role_name(iam_client, bucket_name)
    account_id = sts_client.get_caller_identity()["Account"]
    resource_policy = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{account_id}:role/{role_name}"},
                    "Action": [
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:ListSecrets",
                    ],
                    "Resource": "*",
                }
            ],
        }
    )
    # The policy may not exist yet if we just created it because of AWS eventual consistency
    retry_operation_on_service_errors(
        secretsmanager_client.put_resource_policy,
        ["MalformedPolicyDocumentException"],
        delay=5,
        SecretId=secret_key,
        ResourcePolicy=resource_policy,
    )


def _update_secret(
    secretsmanager_client: BaseClient,
    secret_key: str,
    secret_value: str,
):
    secretsmanager_client.put_secret_value(
        SecretId=secret_key,
        SecretString=secret_value,
    )


def _delete_secret(
    secretsmanager_client: BaseClient,
    secret_key: str,
):
    secretsmanager_client.delete_secret(
        SecretId=secret_key,
        ForceDeleteWithoutRecovery=True,
    )


def _get_secret_key(bucket_name: str, repo_id: str, secret_name: str) -> str:
    return f"/dstack/{bucket_name}/secrets/{repo_id}/{secret_name}"


def _get_credentials_key(bucket_name: str, repo_id: str) -> str:
    return f"/dstack/{bucket_name}/credentials/{repo_id}"
