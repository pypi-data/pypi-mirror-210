from .devops_terraform_build import DevopsTerraformBuild, create_devops_terraform_build_config


def create_digitalocean_terraform_build_config(stage,
                                               project_root_path,
                                               module,
                                               additional_vars,
                                               do_api_key,
                                               do_spaces_access_id,
                                               do_spaces_secret_key,
                                               build_dir_name='target',
                                               output_json_name=None,
                                               use_workspace=True,
                                               use_package_common_files=True,
                                               build_commons_path=None,
                                               terraform_build_commons_dir_name='terraform',
                                               debug_print_terraform_command=False,
                                               additional_tfvar_files=None,
                                               terraform_semantic_version="1.0.8",
                                               ):
    if not additional_tfvar_files:
        additional_tfvar_files = []
    config = create_devops_terraform_build_config(stage,
                                                  project_root_path,
                                                  module,
                                                  additional_vars,
                                                  build_dir_name,
                                                  output_json_name,
                                                  use_workspace,
                                                  use_package_common_files,
                                                  build_commons_path,
                                                  terraform_build_commons_dir_name,
                                                  debug_print_terraform_command,
                                                  additional_tfvar_files,
                                                  terraform_semantic_version)
    config.update({'DigitaloceanTerraformBuild':
                   {'do_api_key': do_api_key,
                    'do_spaces_access_id': do_spaces_access_id,
                    'do_spaces_secret_key': do_spaces_secret_key}})
    return config


class DigitaloceanTerraformBuild(DevopsTerraformBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        do_mixin_config = config['DigitaloceanTerraformBuild']
        self.do_api_key = do_mixin_config['do_api_key']
        self.do_spaces_access_id = do_mixin_config['do_spaces_access_id']
        self.do_spaces_secret_key = do_mixin_config['do_spaces_secret_key']

    def project_vars(self):
        ret = super().project_vars()
        ret['do_api_key'] = self.do_api_key
        ret['do_spaces_access_id'] = self.do_spaces_access_id
        ret['do_spaces_secret_key'] = self.do_spaces_secret_key
        return ret

    def copy_build_resources_from_package(self):
        super().copy_build_resources_from_package()
        self.copy_build_resource_file_from_package('provider_registry.tf')
        self.copy_build_resource_file_from_package('do_provider.tf')
        self.copy_build_resource_file_from_package('do_mixin_vars.tf')
