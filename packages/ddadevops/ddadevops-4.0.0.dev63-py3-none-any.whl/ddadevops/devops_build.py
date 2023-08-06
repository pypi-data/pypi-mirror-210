import deprecation
from .domain import InitService
from .infrastructure import DevopsRepository, FileApi


@deprecation.deprecated(deprecated_in="3.2", details="create objects direct instead")
def create_devops_build_config(
    stage, project_root_path, module, build_dir_name="target"
):
    return {
        "stage": stage,
        "project_root_path": project_root_path,
        "module": module,
        "build_dir_name": build_dir_name,
    }


def get_devops_build(project):
    return project.get_property("build")


class DevopsBuild:
    def __init__(self, project, inp: dict):
        self.project = project
        self.file_api = FileApi()
        self.init_service = InitService.prod(project.basedir)
        self.devops_repo = DevopsRepository()
        devops = self.init_service.initialize(inp)
        self.devops_repo.set_devops(self.project, devops)
        self.project.set_property("build", self)

    def name(self):
        devops = self.devops_repo.get_devops(self.project)
        return devops.name

    def build_path(self):
        devops = self.devops_repo.get_devops(self.project)
        return devops.build_path()

    def initialize_build_dir(self):
        devops = self.devops_repo.get_devops(self.project)
        self.file_api.clean_dir(devops.build_path())
