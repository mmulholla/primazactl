from kubernetes import client
from primazactl.utils import logger
from primazactl.cmd.worker.create.constants import APPLICATION
from primazactl.kube.customnamespaced import CustomNamespaced


class ClusterEnvironment(object):

    name: str = None
    namespace: str = None
    custom_namespaced: CustomNamespaced = None
    body: {} = None

    def __init__(self, api_client,
                 namespace, name=None,
                 environment=None, secret_name=None):
        self.name = name
        self.namespace = namespace
        group = "primaza.io"
        version = "v1alpha1"
        kind = "ClusterEnvironment"
        plural = "clusterenvironments"

        if name and environment and secret_name:
            self.body = {
                "apiVersion": f"{group}/{version}",
                "kind": kind,
                "metadata": {
                    "name": self.name,
                    "namespace": self.namespace,
                },
                "spec": {
                    "environmentName": environment,
                    "clusterContextSecret": secret_name,
                }
            }

        self.custom_namespaced = CustomNamespaced(api_client,
                                                  group,
                                                  version,
                                                  kind,
                                                  plural,
                                                  self.name,
                                                  self.namespace,
                                                  self.body)

    def create(self):
        logger.log_entry(f"name: {self.name}, namespace: {self.namespace}")
        self.custom_namespaced.create()

    def read(self) -> client.V1Namespace | None:
        logger.log_entry(f"name: {self.name}, namespace: {self.namespace}")
        self.body = self.custom_namespaced.read()
        return self.body

    def delete(self):
        logger.log_entry(f"namespace: {self.name}")
        self.custom_namespaced.delete()

    def find(self):
        logger.log_entry(f"namespace: {self.name}")
        self.body = self.custom_namespaced.find()

    def add_namespace(self, type, name):
        logger.log_entry(f"type: {type}, name: {name}")
        if not self.body:
            self.read()

        if type == APPLICATION:
            entry = "applicationNamespaces"
        else:
            entry = "serviceNamespaces"

        if entry in self.body["spec"]:
            values = self.body["spec"][entry]
            values.append(name)
            self.body["spec"][entry] = values
        else:
            self.body["spec"][entry] = [name]

        logger.log_info(f'patch new spec: {self.body["spec"]}')

        self.custom_namespaced.patch(self.body)

    def check(self, state, ctype, cstatus):
        self.check_state(state)
        self.check_status_condition(ctype, cstatus)
        self.check_status_condition("ApplicationNamespacePermissionsRequired",
                                    "False")
        self.check_status_condition("ServiceNamespacePermissionsRequired",
                                    "False")

    def check_state(self, state):
        logger.log_entry(f"check state, name: {self.name}, state:{state}")
        self.custom_namespaced.check_state(state)

    def check_status_condition(self, ctype: str, cstatus: str):
        logger.log_entry(f"check status condition, name: {self.name},"
                         f"type: {ctype}, status {cstatus}")
        self.custom_namespaced.check_status_condition(ctype, cstatus)
