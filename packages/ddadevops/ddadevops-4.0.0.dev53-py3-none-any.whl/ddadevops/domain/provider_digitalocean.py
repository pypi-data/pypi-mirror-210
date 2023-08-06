from typing import List
from .common import Validateable, CredentialMappingDefault


class Digitalocean(Validateable, CredentialMappingDefault):
    def __init__(
        self,
        inp: dict,
    ):
        self.do_api_key = inp.get("do_api_key")
        self.do_spaces_access_id = inp.get("do_spaces_access_id")
        self.do_spaces_secret_key = inp.get("do_spaces_secret_key")

    def validate(self) -> List[str]:
        result = []
        result += self.__validate_is_not_empty__("do_api_key")
        result += self.__validate_is_not_empty__("do_spaces_access_id")
        result += self.__validate_is_not_empty__("do_spaces_secret_key")
        return result

    def resources_from_package(self) -> List[str]:
        return ["provider_registry.tf", "do_provider.tf", "do_mixin_vars.tf"]

    def project_vars(self):
        return {
            "do_api_key": self.do_api_key,
            "do_spaces_access_id": self.do_spaces_access_id,
            "do_spaces_secret_key": self.do_spaces_secret_key,
        }

    @classmethod
    def get_mapping_default(cls) -> List[map]:
        return [
            {
                "gopass_path": "server/devops/digitalocean/s3",
                "gopass_field": "id",
                "name": "do_spaces_access_id",
            },
            {
                "gopass_path": "server/devops/digitalocean/s3",
                "gopass_field": "secret",
                "name": "do_spaces_secret_key",
            },
        ]
