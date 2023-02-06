

import tempfile
import os
import sys
from utils import command
from utils import kubeconfigwrapper


class PrimazaMain(object):
    """
    Base class for instances of Primaza clusters.
    Implements functionalities for configuration of kubernetes clusters that will host Primaza,
    like CertificateSigningRequest or ClusterContext creation.

    Concrete implementations built on this class will have to implement the `install_primaza` method,
    as the installation procedure usually varies with respect to the Cluster Provisioner
    (i.e., kind, minikube, openshift)
    """
    primaza_namespace: str = None
    kube_config_file: str = None
    primaza_cluster_name: str = None
    kustomize: str = None
    primaza_config: str = None


    def __init__(self, cluster_name: str, kubeconfigfile: str, config: str):
        self.primaza_cluster_name = cluster_name
        self.kube_config_file = kubeconfigfile
        self.primaza_config = config
        self.set_kustomize()

    def start(self):
        self.install_primaza()

    def install_primaza(self):

        img = "primaza-controller:latest"

        ## need an agnostic way to get the kubeconfig - get as a parameter
        kcw = kubeconfigwrapper.KubeConfigWrapper(self.primaza_cluster_name,self.kube_config_file)
        kcc = kcw.get_kube_config_content()
        with tempfile.NamedTemporaryFile(prefix=f"kubeconfig-primaza-{self.primaza_cluster_name}-") as t:
            t.write(kcc.encode("utf-8"))
            self.__deploy_primaza(t.name, img)

    def __deploy_primaza(self, kubeconfig_path: str, img: str):

        # make sure we deploy to the required cluster
        kc = kubeconfigwrapper.KubeConfigWrapper(self.primaza_cluster_name,kubeconfig_path)
        kc.use_context()

        print(f"self.primaza_config = {self.primaza_config}")
        if os.path.isdir(self.primaza_config):
           out, err = command.Command().setenv("KUBECONFIG",kubeconfig_path).run(f"{self.kustomize} build {self.primaza_config} | kubectl apply -f -")
        else:
            out, err = command.Command().setenv("KUBECONFIG",kubeconfig_path).run(f"kubectl apply -f {self.primaza_config}")
        print(out)
        if err != 0:
            print(f"\n[ERROR] error deploying Primaza's controller into cluster {self.primaza_cluster_name} : {err}\n")
            sys.exit(1)

    def set_kustomize(self):
        file_path = os.path.dirname(os.path.realpath(__file__))
        self.kustomize = os.path.abspath(f"{file_path}/../../../bin/kustomize")

