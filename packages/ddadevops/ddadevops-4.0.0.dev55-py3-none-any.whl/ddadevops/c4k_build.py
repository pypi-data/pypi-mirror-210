import deprecation
from .domain import BuildType, DnsRecord
from .devops_build import DevopsBuild
from .credential import gopass_field_from_path, gopass_password_from_path
from .infrastructure import ExecutionApi


@deprecation.deprecated(deprecated_in="3.2", details="use direct dict instead")
def add_c4k_mixin_config(
    config,
    c4k_config_dict,
    c4k_auth_dict,
    executable_name=None,
    grafana_cloud_user=None,
    grafana_cloud_password=None,
    grafana_cloud_url="https://prometheus-prod-01-eu-west-0.grafana.net/api/prom/push",
):
    if not grafana_cloud_user:
        grafana_cloud_user = gopass_field_from_path(
            "server/meissa/grafana-cloud", "grafana-cloud-user"
        )
    if not grafana_cloud_password:
        grafana_cloud_password = gopass_password_from_path(
            "server/meissa/grafana-cloud"
        )
    c4k_auth_dict.update(
        {
            "mon-auth": {
                "grafana-cloud-user": grafana_cloud_user,
                "grafana-cloud-password": grafana_cloud_password,
            }
        }
    )
    c4k_config_dict.update({"mon-cfg": {"grafana-cloud-url": grafana_cloud_url}})
    config.update(
        {
            "C4kMixin": {
                "executable_name": executable_name,
                "config": c4k_config_dict,
                "auth": c4k_auth_dict,
            }
        }
    )
    return config


class C4kBuild(DevopsBuild):
    def __init__(self, project, config):
        super().__init__(project, config)
        self.execution_api = ExecutionApi()
        devops = self.devops_repo.get_devops(self.project)
        if BuildType.C4K not in devops.specialized_builds:
            raise ValueError("C4kBuild requires BuildType.C4K")

    def update_runtime_config(self, dns_record: DnsRecord):
        devops = self.devops_repo.get_devops(self.project)
        devops.specialized_builds[BuildType.C4K].update_runtime_config(dns_record)
        self.devops_repo.set_devops(self.project, devops)

    def write_c4k_config(self):
        devops = self.devops_repo.get_devops(self.project)
        path = devops.build_path() + "/out_c4k_config.yaml"
        self.file_api.write_yaml_to_file(
            path, devops.specialized_builds[BuildType.C4K].config()
        )

    def write_c4k_auth(self):
        devops = self.devops_repo.get_devops(self.project)
        path = devops.build_path() + "/out_c4k_auth.yaml"
        self.file_api.write_yaml_to_file(
            path, devops.specialized_builds[BuildType.C4K].auth()
        )

    def c4k_apply(self, dry_run=False):
        devops = self.devops_repo.get_devops(self.project)
        return self.execution_api.execute(
            devops.specialized_builds[BuildType.C4K].command(devops), dry_run
        )
