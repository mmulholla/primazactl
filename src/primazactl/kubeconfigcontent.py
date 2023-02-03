from kubeconfig import KubeConfig
import yaml


class KubeConfigContent(object):

    kube_config_file: str = None
    kube_config_content = None
    cluster_name: str = None

    def __init__(self, cluster_name: str,kube_config_file: str):
        self.kube_config_file = kube_config_file
        self.cluster_name = cluster_name

    def get_server_url(self):
        kube_config_content = self.__get_kube_config_content_as_yaml()

        for cluster in kube_config_content["clusters"]:
            if cluster["name"] == self.cluster_name:
                print(f'Found Cluster: {self.cluster_name}, server: {cluster["cluster"]["server"]}')
                return cluster["cluster"]["server"]
        return None

    def set_server_url(self,server_url):
        config = KubeConfig(self.kube_config_file)
        config.use_context(f"kind-{self.cluster_name}")
        config.set_cluster(server=server_url)

    def use_context(self):
        config = KubeConfig(self.kube_config_file)
        config.use_context(f"kind-{self.cluster_name}")

    def __get_kube_config_content_as_yaml(self):
        if not self.kube_config_content:
            with open(str(self.kube_config_file), "r") as kc_file:
                self.kube_config_content = yaml.safe_load(kc_file)
        return self.kube_config_content

    def get_kube_config_content(self):
        with open(str(self.kube_config_file), "r") as kc_file:
            return kc_file.read()
        return ""








