import hashlib
from dataclasses import dataclass
from typing import Optional

from practicuscore.util import CryptoUtil


class K8sAuthToken:
    def __init__(self, refresh_token: str, access_token: str) -> None:
        self.refresh_token = refresh_token
        self.access_token = access_token


@dataclass
class K8sClusterDefinition:
    name: str = ""
    region_name: str = ""


class K8sConfig:
    def __init__(self, host_url: str, email: str, refresh_token: Optional[str] = None):
        super().__init__()
        self.host_url = host_url
        self.email = email
        self.refresh_token = refresh_token
        self.password: Optional[str] = None
        self.cluster_name: Optional[str] = None
        self.region_name: Optional[str] = None

    def to_dict(self) -> dict:
        conf_dict = {'host_url': self.host_url, 'email': self.email}

        if self.password is not None:
            conf_dict['password'] = self.password

        if self.refresh_token is not None:
            conf_dict['refresh_token'] = self.refresh_token

        if self.cluster_name is not None:
            conf_dict['cluster_name'] = self.cluster_name

        if self.region_name is not None:
            conf_dict['region_name'] = self.region_name

        return conf_dict

    @staticmethod
    def from_dict(dict_item: dict) -> 'K8sConfig':
        k8s_config = K8sConfig(
            host_url=dict_item['host_url'], email=dict_item['email'], refresh_token=dict_item['refresh_token'])
        k8s_config.password = dict_item['password']
        k8s_config.cluster_name = dict_item['cluster_name']
        k8s_config.region_name = dict_item['region_name']
        return k8s_config

    def set_password(self, password_plain_text: str):
        self.password = CryptoUtil.encrypt(password_plain_text)

    @property
    def password_in_plain_text(self) -> Optional[str]:
        if self.password:
            return CryptoUtil.decrypt(self.password)
        else:
            return None

    @property
    def ssl(self) -> bool:
        return self.host_url.startswith("https")

    @property
    def host_dns(self) -> str:
        return self.host_url.replace("https://", "").replace("http://", "")

    @property
    def hash_key(self) -> str:
        text_to_hash = f"{self.host_url}-{self.email}"
        m = hashlib.md5()
        m.update(bytes(text_to_hash, "utf-8"))
        return str(m.hexdigest())
