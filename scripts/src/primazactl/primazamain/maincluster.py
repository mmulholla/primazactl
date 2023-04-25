
from primazactl.utils import logger
from primazactl.utils.kubeconfigwrapper import KubeConfigWrapper
from primazactl.primazamain.constants import PRIMAZA_NAMESPACE
from primazactl.primaza.primazacluster import PrimazaCluster
from primazactl.cmd.worker.create.constants import APPLICATION, SERVICE
from primazactl.identity.kubeidentity import KubeIdentity
from .clusterenvironment import ClusterEnvironment


class MainCluster(PrimazaCluster):
    kubeconfig: KubeConfigWrapper = None
    kube_config_file: str
    primaza_version: str | None = None

    def __init__(
            self,
            cluster_name: str | None,
            kubeconfig_path: str | None,
            config_file: str | None,
            version: str | None):

        super().__init__(PRIMAZA_NAMESPACE,
                         cluster_name,
                         None,
                         kubeconfig_path,
                         config_file)

        self.cluster_name = cluster_name \
            if cluster_name is not None \
            else KubeConfigWrapper(None, self.kube_config_file).get_context()

        self.primaza_version = version

        kcw = KubeConfigWrapper(cluster_name, self.kube_config_file)
        self.kubeconfig = kcw.get_kube_config_for_cluster()

        logger.log_info("Primaza main created for cluster "
                        f"{self.cluster_name}")

    def install_primaza(self):
        try:
            self.install_config()
        except Exception as exc:
            raise RuntimeError(
                "error deploying Primaza's controller into "
                f"cluster {self.cluster_name} : {exc}")

    def create_primaza_identity(self, cluster_environment: str,
                                type: str = None) -> KubeIdentity:
        logger.log_entry(f"type: {type} environment: {cluster_environment}")
        if type == APPLICATION or type == SERVICE:
            sa_name = f"primaza-{type}-{cluster_environment}-sa"
        else:
            sa_name = f"primaza-{cluster_environment}-{self.namespace}-sa"

        return self.create_identity(sa_name)

    def create_cluster_environment(self,
                                   cluster_environment_name,
                                   environment_name,
                                   secret_name) -> ClusterEnvironment:

        logger.log_entry("kind: ClusterEnvironment, "
                         f"name: {cluster_environment_name}, "
                         f"environment_name: {environment_name} "
                         f"secret_name: {secret_name}")

        ce = ClusterEnvironment(self.kubeconfig.get_api_client(),
                                self.namespace,
                                cluster_environment_name,
                                environment_name,
                                secret_name)
        ce.create()
        return ce

    def get_cluster_environment(self) -> ClusterEnvironment:
        ce = ClusterEnvironment(self.kubeconfig.get_api_client(),
                                self.namespace)
        ce.find()
        return ce

    def uninstall_primaza(self):
        self.uninstall_config()
