"""
ddadevops provide tools to support builds combining gopass,
terraform, dda-pallet, aws & hetzner-cloud.

"""

from .python_util import execute
from .provs_k3s_build import ProvsK3sBuild
from .aws_mfa_mixin import AwsMfaMixin, add_aws_mfa_mixin_config
from .aws_backend_properties_mixin import AwsBackendPropertiesMixin, add_aws_backend_properties_mixin_config
from .c4k_build import C4kBuild
from .digitalocean_backend_properties_mixin import DigitaloceanBackendPropertiesMixin, add_digitalocean_backend_properties_mixin_config
from .digitalocean_terraform_build import DigitaloceanTerraformBuild, create_digitalocean_terraform_build_config
from .hetzner_mixin import HetznerMixin, add_hetzner_mixin_config
from .devops_image_build import DevopsImageBuild
from .devops_terraform_build import DevopsTerraformBuild, create_devops_terraform_build_config
from .devops_build import DevopsBuild, create_devops_build_config, get_devops_build
from .credential import gopass_password_from_path, gopass_field_from_path
from .release_mixin import ReleaseMixin

__version__ = "${version}"
