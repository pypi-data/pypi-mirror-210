import deprecation
from .domain import BuildType
from .application import ImageBuildService
from .devops_build import DevopsBuild, create_devops_build_config


@deprecation.deprecated(deprecated_in="3.2", details="use direct dict instead")
def create_devops_docker_build_config(
    stage,
    project_root_path,
    module,
    dockerhub_user,
    dockerhub_password,
    build_dir_name="target",
    use_package_common_files=True,
    build_commons_path=None,
    docker_build_commons_dir_name="docker",
    docker_publish_tag=None,
):
    ret = create_devops_build_config(stage, project_root_path, module, build_dir_name)
    ret.update(
        {
            "dockerhub_user": dockerhub_user,
            "dockerhub_password": dockerhub_password,
            "use_package_common_files": use_package_common_files,
            "docker_build_commons_dir_name": docker_build_commons_dir_name,
            "build_commons_path": build_commons_path,
            "docker_publish_tag": docker_publish_tag,
        }
    )
    return ret


class DevopsImageBuild(DevopsBuild):
    def __init__(self, project, inp: dict):
        super().__init__(project, inp)
        self.image_build_service = ImageBuildService.prod()
        devops = self.devops_repo.get_devops(self.project)
        if BuildType.IMAGE not in devops.specialized_builds:
            raise ValueError("ImageBuild requires BuildType.IMAGE")

    def initialize_build_dir(self):
        super().initialize_build_dir()
        devops = self.devops_repo.get_devops(self.project)
        self.image_build_service.initialize_build_dir(devops)

    def image(self):
        devops = self.devops_repo.get_devops(self.project)
        self.image_build_service.image(devops)

    def drun(self):
        devops = self.devops_repo.get_devops(self.project)
        self.image_build_service.drun(devops)

    def dockerhub_login(self):
        devops = self.devops_repo.get_devops(self.project)
        self.image_build_service.dockerhub_login(devops)

    def dockerhub_publish(self):
        devops = self.devops_repo.get_devops(self.project)
        self.image_build_service.dockerhub_publish(devops)

    def test(self):
        devops = self.devops_repo.get_devops(self.project)
        self.image_build_service.test(devops)
