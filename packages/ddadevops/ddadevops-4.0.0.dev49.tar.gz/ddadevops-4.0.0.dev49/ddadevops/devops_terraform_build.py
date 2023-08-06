from .devops_build import DevopsBuild, create_devops_build_config


def create_devops_terraform_build_config(
    stage,
    project_root_path,
    module,
    additional_vars,
    build_dir_name="target",
    output_json_name=None,
    use_workspace=True,
    use_package_common_files=True,
    build_commons_path=None,
    terraform_build_commons_dir_name="terraform",
    debug_print_terraform_command=False,
    additional_tfvar_files=None,
    terraform_semantic_version="1.0.8",
):
    if not output_json_name:
        output_json_name = "out_" + module + ".json"
    if not additional_tfvar_files:
        additional_tfvar_files = []
    ret = create_devops_build_config(stage, project_root_path, module, build_dir_name)
    ret.update(
        {
            "additional_vars": additional_vars,
            "output_json_name": output_json_name,
            "use_workspace": use_workspace,
            "use_package_common_files": use_package_common_files,
            "build_commons_path": build_commons_path,
            "terraform_build_commons_dir_name": terraform_build_commons_dir_name,
            "debug_print_terraform_command": debug_print_terraform_command,
            "additional_tfvar_files": additional_tfvar_files,
            "terraform_semantic_version": terraform_semantic_version,
        }
    )
    return ret


class DevopsTerraformBuild(DevopsBuild):
    def __init__(self, project, config):
        inp = config.copy()
        inp["name"] = project.name
        inp["module"] = config.get("module")
        inp["stage"] = config.get("stage")
        inp["project_root_path"] = config.get("project_root_path")
        inp["build_types"] = config.get("build_types", [])
        inp["mixin_types"] = config.get("mixin_types", [])
        super().__init__(project, inp)
        project.build_depends_on("dda-python-terraform")
        self.teraform_service = Terraform.prod()

    def initialize_build_dir(self):
        super().initialize_build_dir()
        devops = self.devops_repo.get_devops(self.project)
        self.teraform_service.initialize_build_dir(devops)

    def post_build(self):
        devops = self.devops_repo.get_devops(self.project)
        self.teraform_service.rescue_local_state(devops)

    def read_output_json(self) -> map:
        devops = self.devops_repo.get_devops(self.project)
        return self.teraform_service.read_output(devops)

    def plan(self):
        devops = self.devops_repo.get_devops(self.project)
        self.teraform_service.plan(devops)
        self.post_build()

    def plan_fail_on_diff(self):
        devops = self.devops_repo.get_devops(self.project)
        self.teraform_service.plan(devops, fail_on_diff=True)
        self.post_build()

    def apply(self, auto_approve=False):
        devops = self.devops_repo.get_devops(self.project)
        self.teraform_service.apply(devops, auto_approve=auto_approve)
        self.post_build()

    def refresh(self):
        devops = self.devops_repo.get_devops(self.project)
        self.teraform_service.refresh(devops)
        self.post_build()

    def destroy(self, auto_approve=False):
        devops = self.devops_repo.get_devops(self.project)
        self.teraform_service.refresh(devops)
        self.post_build()

    def tf_import(
        self,
        tf_import_name,
        tf_import_resource,
    ):
        devops = self.devops_repo.get_devops(self.project)
        self.teraform_service.tf_import(devops, tf_import_name, tf_import_resource)
        self.post_build()
