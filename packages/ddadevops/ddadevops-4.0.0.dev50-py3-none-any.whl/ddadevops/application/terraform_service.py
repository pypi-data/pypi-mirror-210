from pathlib import Path
from dda_python_terraform import Terraform, IsFlagged
from packaging import version

from ..domain import Devops, BuildType, TerraformDomain
from ..infrastructure import FileApi, ResourceApi, TerraformApi


# TODO: mv more fkt to Terraform_api ?
class TerraformService:
    def __init__(
        self, file_api: FileApi, resource_api: ResourceApi, terraform_api: TerraformApi
    ):
        self.file_api = file_api
        self.resource_api = resource_api
        self.terraform_api = terraform_api

    @classmethod
    def prod(cls):
        return cls(
            FileApi(),
            ResourceApi(),
            TerraformApi(),
        )

    def __copy_build_resource_file_from_package__(self, resource_name, devops: Devops):
        data = self.resource_api.read_resource(
            f"src/main/resources/terraform/{resource_name}"
        )
        self.file_api.write_data_to_file(
            Path(f"{devops.build_path()}/{resource_name}"), data
        )

    def __copy_build_resources_from_package__(self, devops: Devops):
        self.__copy_build_resource_file_from_package__("versions.tf", devops)
        self.__copy_build_resource_file_from_package__(
            "terraform_build_vars.tf", devops
        )

    def __copy_build_resources_from_dir__(self, devops: Devops):
        terraform = devops.specialized_builds[BuildType.TERRAFORM]
        self.file_api.cp_force(
            f"{terraform.build_commons_path()}/*", devops.build_path()
        )

    def __print_terraform_command__(self, terraform: Terraform, devops: Devops):
        terraform_domain = devops.specialized_builds[BuildType.TERRAFORM]
        if terraform_domain.tf_debug_print_terraform_command:
            output = f"cd {devops.build_path()} && {terraform.latest_cmd()}"
            print(output)

    def copy_local_state(self, devops: Devops):
        # TODO: orignal was unchecked ...
        self.file_api.cp("terraform.tfstate", devops.build_path())

    def rescue_local_state(self, devops: Devops):
        # TODO: orignal was unchecked ...
        self.file_api.cp(f"{devops.build_path()}/terraform.tfstate", ".")

    def initialize_build_dir(self, devops: Devops):
        terraform = devops.specialized_builds[BuildType.TERRAFORM]
        if terraform.tf_use_package_common_files:
            self.__copy_build_resources_from_package__(devops)
        else:
            self.__copy_build_resources_from_dir__(devops)
        # TODO: orignal was unchecked ...
        self.copy_local_state(devops)
        self.file_api.cp("*.tf", devops.build_path())
        self.file_api.cp("*.properties", devops.build_path())
        self.file_api.cp("*.tfvars", devops.build_path())
        self.file_api.cp_recursive("scripts", devops.build_path())

    def init_client(self, devops: Devops):
        terraform_domain = devops.specialized_builds[BuildType.TERRAFORM]
        terraform = Terraform(
            working_dir=devops.build_path(),
            terraform_semantic_version=terraform_domain.tf_terraform_semantic_version,
        )
        terraform.init()
        self.__print_terraform_command__(terraform, devops)
        if terraform_domain.tf_use_workspace:
            try:
                terraform.workspace("select", self.stage)
                self.__print_terraform_command__(terraform, devops)
            except:
                terraform.workspace("new", self.stage)
                self.__print_terraform_command__(terraform, devops)
        return terraform

    def write_output(self, terraform, devops: Devops):
        terraform_domain = devops.specialized_builds[BuildType.TERRAFORM]
        result = terraform.output(json=IsFlagged)
        self.__print_terraform_command__(terraform, devops)
        self.file_api.write_json_to_file(
            Path(f"{devops.build_path()}{terraform_domain.tf_output_json_name}"), result
        )

    def read_output(self, devops: Devops):
        terraform_domain = devops.specialized_builds[BuildType.TERRAFORM]
        return self.file_api.read_json_fro_file(
            Path(f"{devops.build_path()}{terraform_domain.tf_output_json_name}")
        )

    def plan(self, devops: Devops, fail_on_diff=False):
        terraform_domain = devops.specialized_builds[BuildType.TERRAFORM]
        if fail_on_diff:
            detailed_exitcode = IsFlagged
        else:
            detailed_exitcode = None
        terraform = self.init_client(devops)
        return_code, _, stderr = terraform.plan(
            detailed_exitcode=detailed_exitcode,
            capture_output=False,
            raise_on_error=False,
            var=terraform_domain.project_vars(),
            var_file=terraform_domain.tf_additional_tfvar_files,
        )
        self.__print_terraform_command__(terraform)
        if return_code not in (0, 2):
            raise RuntimeError(return_code, "terraform error:", stderr)
        if return_code == 2:
            raise RuntimeError(return_code, "diff in config found:", stderr)

    def apply(self, devops: Devops, auto_approve=False):
        terraform_domain = devops.specialized_builds[BuildType.TERRAFORM]
        if auto_approve:
            auto_approve_flag = IsFlagged
        else:
            auto_approve_flag = None
        terraform = self.init_client(devops)
        if version.parse(
            terraform_domain.tf_terraform_semantic_version
        ) >= version.parse("1.0.0"):
            return_code, _, stderr = terraform.apply(
                capture_output=False,
                raise_on_error=True,
                auto_approve=auto_approve_flag,
                var=terraform_domain.project_vars(),
                var_file=terraform_domain.tf_additional_tfvar_files,
            )
        else:
            return_code, _, stderr = terraform.apply(
                capture_output=False,
                raise_on_error=True,
                skip_plan=auto_approve,
                var=terraform_domain.project_vars(),
                var_file=terraform_domain.tf_additional_tfvar_files,
            )
        self.__print_terraform_command__(terraform, devops)
        if return_code > 0:
            raise RuntimeError(return_code, "terraform error:", stderr)
        self.write_output(terraform, devops)

    def refresh(self, devops: Devops):
        terraform_domain = devops.specialized_builds[BuildType.TERRAFORM]
        terraform = self.init_client(devops)
        return_code, _, stderr = terraform.refresh(
            var=terraform_domain.project_vars(),
            var_file=terraform_domain.tf_additional_tfvar_files,
        )
        self.__print_terraform_command__(terraform, devops)
        if return_code > 0:
            raise RuntimeError(return_code, "terraform error:", stderr)
        self.write_output(terraform, devops)

    def destroy(self, devops: Devops, auto_approve=False):
        terraform_domain = devops.specialized_builds[BuildType.TERRAFORM]
        if auto_approve:
            auto_approve_flag = IsFlagged
        else:
            auto_approve_flag = None
        terraform = self.init_client(devops)
        if version.parse(
            terraform_domain.tf_terraform_semantic_version
        ) >= version.parse("1.0.0"):
            return_code, _, stderr = terraform.destroy(
                capture_output=False,
                raise_on_error=True,
                auto_approve=auto_approve_flag,
                var=terraform_domain.project_vars(),
                var_file=terraform_domain.tf_additional_tfvar_files,
            )
        else:
            return_code, _, stderr = terraform.destroy(
                capture_output=False,
                raise_on_error=True,
                force=auto_approve_flag,
                var=terraform_domain.project_vars(),
                var_file=terraform_domain.tf_additional_tfvar_files,
            )
        self.__print_terraform_command__(terraform, devops)
        if return_code > 0:
            raise RuntimeError(return_code, "terraform error:", stderr)

    def tf_import(
        self,
        devops: Devops,
        tf_import_name,
        tf_import_resource,
    ):
        terraform_domain = devops.specialized_builds[BuildType.TERRAFORM]
        return_code, _, stderr = terraform.import_cmd(
            tf_import_name,
            tf_import_resource,
            capture_output=False,
            raise_on_error=True,
            var=terraform_domain.project_vars(),
            var_file=terraform_domain.tf_additional_tfvar_files,
        )
        self.print_terraform_command(terraform, devops)
        if return_code > 0:
            raise RuntimeError(return_code, "terraform error:", stderr)
