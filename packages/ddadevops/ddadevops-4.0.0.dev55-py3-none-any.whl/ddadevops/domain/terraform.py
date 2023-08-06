from typing import List, Optional
from pathlib import Path
from .common import (
    Validateable,
    ProviderType,
    DnsRecord,
    Devops,
    filter_none,
)
from .provider_digitalocean import Digitalocean


class TerraformDomain(Validateable):
    def __init__(self, inp: dict):
        self.module = inp.get("module")
        self.stage = inp.get("stage")
        self.tf_additional_vars = inp.get("tf_additional_vars")
        self.tf_output_json_name = inp.get("tf_output_json_name")
        self.tf_build_commons_path = inp.get("tf_build_commons_path")
        self.tf_provider_types = inp.get("tf_provider_types", [])
        self.tf_additional_resources_from_package = inp.get(
            "tf_additional_resources_from_package", []
        )
        self.tf_additional_tfvar_files = inp.get("tf_additional_tfvar_files", [])
        self.tf_use_workspace = inp.get("tf_use_workspace", True)
        self.tf_debug_print_terraform_command = inp.get(
            "tf_debug_print_terraform_command", False
        )
        self.tf_build_commons_dir_name = inp.get(
            "tf_build_commons_dir_name", "terraform"
        )
        self.tf_terraform_semantic_version = inp.get(
            "tf_terraform_semantic_version", "1.0.8"
        )
        self.tf_use_package_common_files = inp.get("tf_use_package_common_files", True)

        provider_types = TerraformDomain.parse_provider_types(self.tf_provider_types)
        self.providers = {}
        if ProviderType.DIGITALOCEAN in provider_types:
            self.providers[ProviderType.DIGITALOCEAN] = Digitalocean(inp)

    def validate(self) -> List[str]:
        result = []
        result += self.__validate_is_not_empty__("module")
        result += self.__validate_is_not_empty__("stage")
        result += self.__validate_is_not_empty__("tf_build_commons_dir_name")
        result += self.__validate_is_not_none__("tf_additional_resources_from_package")
        result += self.__validate_is_not_none__("tf_additional_tfvar_files")
        result += self.__validate_is_not_none__("tf_provider_types")
        for provider in self.providers.values():
            result += provider.validate()
        return result

    def output_json_name(self) -> str:
        if self.tf_output_json_name:
            return self.tf_output_json_name
        else:
            return f"out_{self.module}.json"

    def terraform_build_commons_path(self) -> Path:
        mylist = [self.tf_build_commons_path, self.tf_build_commons_dir_name]
        return Path("/".join(filter_none(mylist)) + "/")

    def project_vars(self):
        result = {"stage": self.stage, "module": self.module}
        for provider in self.providers.values():
            result.update(provider.project_vars())
        if self.tf_additional_vars:
            result.update(self.tf_additional_vars)
        return result

    def resources_from_package(self) -> List[str]:
        result = ["versions.tf", "terraform_build_vars.tf"]
        for provider in self.providers.values():
            result += provider.resources_from_package()
        result += self.tf_additional_resources_from_package
        return result

    @classmethod
    def parse_provider_types(
        cls, tf_provider_types: List[str]
    ) -> List[ProviderType]:
        result = []
        for provider_type in tf_provider_types:
            result.append(ProviderType[provider_type])
        return result
