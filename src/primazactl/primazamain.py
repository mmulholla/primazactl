
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from kubernetes import client
from kubernetes.client.rest import ApiException
from primazactl.command import Command
from primazactl.kubeconfigcontent import KubeConfigContent
import tempfile
import os
import sys
from urllib.parse import urlparse



class PrimazaMain(object):
    """
    Base class for instances of Primaza clusters.
    Implements functionalities for configuration of kubernetes clusters that will host Primaza,
    like CertificateSigningRequest or ClusterContext creation.

    Concrete implementations built on this class will have to implement the `install_primaza` method,
    as the installation procedure usually varies with respect to the Cluster Provisioner
    (i.e., kind, minikube, openshift)
    """
    certificate_private_key: bytes = None
    certificate: RSAPrivateKey = None
    primaza_namespace: str = None
    kube_config_file: str = None
    primaza_cluster_name: str = None
    kustomize = "./bin/kustomize"
    config = "config/default"


    def __init__(self, cluster_name: str, kubeconfigfile: str, namespace: str = "primaza-system-main"):
        print("Init called")
        self.primaza_cluster_name = cluster_name
        self.kube_config_file = kubeconfigfile
        self.certificate = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.certificate_private_key = self.certificate.private_bytes(
            format=serialization.PrivateFormat.PKCS8,
            encoding=serialization.Encoding.PEM,
            encryption_algorithm=serialization.NoEncryption()).decode("utf-8")
        self.primaza_namespace = namespace

    def start(self):
        self.install_primaza()

    def install_primaza(self):

        img = "primaza-controller:latest"

        ## need an agnostic way to get the kubeconfig - get as a parameter
        kubeconfigcontent = KubeConfigContent(self.primaza_cluster_name,self.kube_config_file)
        kubeconfig = kubeconfigcontent.get_kube_config_content()
        with tempfile.NamedTemporaryFile(prefix=f"kubeconfig-primaza-{self.primaza_cluster_name}-") as t:
            t.write(kubeconfig.encode("utf-8"))
            self.__load_and_deploy_primaza(t.name, img)

    def __load_and_deploy_primaza(self, kubeconfig_path: str, img: str):
        self.__load_image(img)
        self.__deploy_primaza(kubeconfig_path, img)

    #kind command here, need agnostic or one for each flavor.
    def __load_image(self, img: str):
        out, err = Command().run(f"kind load docker-image {img} --name {self.primaza_cluster_name}")
        print(out)
        assert err == 0, f"error loading Primaza's controller into kind cluster {self.primaza_cluster_name}"

    def __deploy_primaza(self, kubeconfig_path: str, img: str):

        kubeconfigcontent = KubeConfigContent(self.primaza_cluster_name,kubeconfig_path)
        kubeconfigcontent.use_context()

        out, err = Command().setenv("KUBECONFIG",kubeconfig_path).run(f"{self.kustomize} build {self.config} | kubectl apply -f -")
        #out, err = self.__build_install_primaza_base_cmd(kubeconfig_path, img).run("make deploy")
        print(out)
        if err != 0:
            print(f"\n[ERROR] error deploying Primaza's controller into cluster {self.primaza_cluster_name}\n")
            sys.exit(1)

    def get_kube_config_content(self):
        with open(str(self.kube_config_file), "r") as kc_file:
            kc_content = kc_file.read()
            return kc_content

