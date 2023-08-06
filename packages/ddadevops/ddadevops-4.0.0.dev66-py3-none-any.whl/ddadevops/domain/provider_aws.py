from typing import List, Dict, Set, Any
from .common import Validateable, CredentialMappingDefault


class Aws(Validateable, CredentialMappingDefault):
    def __init__(
        self,
        inp: dict,
    ):
        self.stage = inp.get("stage")
        self.module = inp.get("module")
        self.aws_bucket = inp.get("aws_bucket")
        self.aws_bucket_kms_key_id = inp.get("aws_bucket_kms_key_id")
        self.aws_account_name = inp.get("aws_account_name", self.stage)
        self.aws_bucket_key = inp.get("aws_bucket_key", self.module)
        self.aws_as_backend = inp.get("aws_as_backend", False)
        self.aws_region = inp.get("aws_region", "eu-central-1")

    def validate(self) -> List[str]:
        result = []
        result += self.__validate_is_not_empty__("stage")
        result += self.__validate_is_not_empty__("module")
        result += self.__validate_is_not_empty__("aws_account_name")
        result += self.__validate_is_not_empty__("aws_as_backend")
        if self.aws_as_backend:
            result += self.__validate_is_not_empty__("aws_bucket")
            result += self.__validate_is_not_empty__("aws_bucket_key")
            result += self.__validate_is_not_empty__("aws_bucket_kms_key_id")
            result += self.__validate_is_not_empty__("aws_region")
        return result

    def backend_config(self) -> Dict[str, Any]:
        result = {}
        if self.aws_as_backend:
            result = {
                "bucket": self.aws_bucket,
                "key": self.__bucket_key__(),
                "region": self.aws_region,
            }
            if self.aws_bucket_kms_key_id:
                result["kms_key_id"] = self.aws_bucket_kms_key_id
        return result

    def resources_from_package(self) -> Set[str]:
        result = {"provider_registry.tf", "aws_provider.tf"}
        if self.aws_as_backend:
            result.update(
                {"aws_backend_properties_vars.tf", "aws_backend_with_properties.tf"}
            )
        return result

    def project_vars(self):
        result = {}
        if self.aws_as_backend:
            result.update(
                {
                    "account_name": self.aws_account_name,
                    "bucket": self.aws_bucket,
                    "key": self.__bucket_key__(),
                    "kms_key_id": self.aws_bucket_kms_key_id,
                    "region": self.aws_region,
                }
            )
        return result

    def is_local_state(self):
        return not self.aws_as_backend

    def __bucket_key__(self):
        result = ""
        if self.aws_as_backend:
            if self.aws_account_name and self.aws_bucket_key:
                result = f"{self.aws_account_name}/{self.aws_bucket_key}"
            else:
                result = f"{self.stage}/{self.module}"
        return result

    @classmethod
    def get_mapping_default(cls) -> List[Dict[str, str]]:
        return []
