from typing import List, Optional
from string import Template
from .common import (
    Validateable,
    DnsRecord,
    Devops,
)

CONFIG_BASE = """
fqdn: $fqdn
"""
CONFIG_IPV4 = """node:
  ipv4: $ipv4
"""
CONFIG_IPV6 = """  ipv6: $ipv6
"""
CONFIG_CERTMANAGER = """certmanager:
  email: $letsencrypt_email
  letsencryptEndpoint: $letsencrypt_endpoint
"""
CONFIG_ECHO = """echo: $echo
"""


class K3s(Validateable):
    def __init__(self, inp: dict):
        self.k3s_provision_user = inp.get("k3s_provision_user")
        self.k3s_letsencrypt_email = inp.get("k3s_letsencrypt_email")
        self.k3s_letsencrypt_endpoint = inp.get("k3s_letsencrypt_endpoint")
        self.k3s_app_filename_to_provision = inp.get("k3s_app_filename_to_provision")
        self.k3s_enable_echo = inp.get("k3s_enable_echo", "false")
        self.k3s_provs_template = inp.get("k3s_provs_template", None)
        self.provision_dns: Optional[DnsRecord] = None

    def validate(self) -> List[str]:
        result = []
        result += self.__validate_is_not_empty__("k3s_letsencrypt_email")
        result += self.__validate_is_not_empty__("k3s_letsencrypt_endpoint")
        result += self.__validate_is_not_empty__("k3s_app_filename_to_provision")
        if self.provision_dns:
            result += self.provision_dns.validate()
        return result

    def update_runtime_config(self, dns_record: DnsRecord):
        self.provision_dns = dns_record
        self.throw_if_invalid()

    def provs_config(self) -> str:
        if not self.provision_dns:
            raise ValueError("provision_dns was not set.")
        substitutes = {
            "fqdn": self.provision_dns.fqdn,
        }
        if self.provision_dns.ipv4 is not None:
            substitutes["ipv4"] = self.provision_dns.ipv4
        if self.provision_dns.ipv6 is not None:
            substitutes["ipv6"] = self.provision_dns.ipv6
        if self.k3s_letsencrypt_email is not None:
            substitutes["letsencrypt_email"] = self.k3s_letsencrypt_email
        if self.k3s_letsencrypt_endpoint is not None:
            substitutes["letsencrypt_endpoint"] = self.k3s_letsencrypt_endpoint
        if self.k3s_enable_echo is not None:
            substitutes["echo"] = self.k3s_enable_echo
        return self.__config_template__().substitute(substitutes)

    def command(self, devops: Devops):
        if not self.provision_dns:
            raise ValueError("provision_dns was not set.")
        cmd = [
            "provs-server.jar",
            "k3s",
            f"{self.k3s_provision_user}@{self.provision_dns.fqdn}",
            "-c",
            f"{devops.build_path()}/out_k3sServerConfig.yaml",
            "-a",
            f"{devops.build_path()}/{self.k3s_app_filename_to_provision}",
        ]
        return " ".join(cmd)

    def __config_template__(self) -> Template:
        template_text = self.k3s_provs_template
        if template_text is None:
            template_text = CONFIG_BASE
            if self.k3s_letsencrypt_endpoint is not None:
                template_text += CONFIG_CERTMANAGER
            if self.k3s_enable_echo is not None:
                template_text += CONFIG_ECHO
            if self.provision_dns.ipv4 is not None:
                template_text += CONFIG_IPV4
            if self.provision_dns.ipv6 is not None:
                template_text += CONFIG_IPV6
        return Template(template_text)
