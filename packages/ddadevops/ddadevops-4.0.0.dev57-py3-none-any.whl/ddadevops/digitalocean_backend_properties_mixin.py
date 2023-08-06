from dda_python_terraform import Terraform
from .digitalocean_terraform_build import DigitaloceanTerraformBuild


def add_digitalocean_backend_properties_mixin_config(
    config, account_name, endpoint, bucket, key, region="eu-central-1"
):
    config.update(
        {
            "DigitaloceanBackendPropertiesMixin": {
                "account_name": account_name,
                "endpoint": endpoint,
                "bucket": bucket,
                "key": key,
                "region": region,
            }
        }
    )
    return config


class DigitaloceanBackendPropertiesMixin(DigitaloceanTerraformBuild):
    def __init__(self, project, config):
        super().__init__(project, config)
        do_mixin_config = config["DigitaloceanBackendPropertiesMixin"]
        self.account_name = do_mixin_config["account_name"]
        self.endpoint = do_mixin_config["endpoint"]
        self.bucket = do_mixin_config["bucket"]
        self.key = do_mixin_config["account_name"] + "/" + do_mixin_config["key"]
        self.region = do_mixin_config["region"]
        self.backend_config = {
            "access_key": self.do_spaces_access_id,
            "secret_key": self.do_spaces_secret_key,
            "endpoint": self.endpoint,
            "bucket": self.bucket,
            "key": self.key,
            "region": self.region,
        }

    def project_vars(self):
        ret = super().project_vars()
        ret.update({"account_name": self.account_name})
        ret.update({"endpoint": self.endpoint})
        ret.update({"bucket": self.bucket})
        ret.update({"key": self.key})
        ret.update({"region": self.region})
        return ret

    def copy_build_resources_from_package(self):
        super().copy_build_resources_from_package()
        self.copy_build_resource_file_from_package("do_backend_properties_vars.tf")
        self.copy_build_resource_file_from_package("do_backend_with_properties.tf")

    def copy_local_state(self):
        pass

    def rescue_local_state(self):
        pass

    def init_client(self):
        terraform = Terraform(
            working_dir=self.build_path(),
            terraform_semantic_version=self.terraform_semantic_version,
        )
        terraform.init(backend_config=self.backend_config)
        self.print_terraform_command(terraform)
        if self.use_workspace:
            try:
                terraform.workspace("select", self.stage)
                self.print_terraform_command(terraform)
            except:
                terraform.workspace("new", self.stage)
                self.print_terraform_command(terraform)
        return terraform
