from kubernetes import client
from kubernetes.client.rest import ApiException
from primazactl.utils import logger
from primazactl.utils import settings
import yaml


class ServiceAccount(object):

    identity: str = None
    namespace: str = None
    corev1: client.CoreV1Api = None
    authv1: client.AuthorizationV1Api = None
    sa: client.V1ServiceAccount = None

    def __init__(self,  api_client: client,
                 idendtity: str,
                 namespace: str):
        self.identity = idendtity
        self.namespace = namespace
        self.corev1 = client.CoreV1Api(api_client)
        self.authv1 = client.AuthorizationV1Api(api_client)

    def create(self):
        logger.log_entry(f"Identity: {self.identity}, "
                         f"namespace: {self.namespace}")

        new_sa = client.V1ServiceAccount(
            api_version="v1",
            kind="ServiceAccount",
            metadata=client.V1ObjectMeta(
                name=self.identity,
                namespace=self.namespace,
                labels={
                    "app.kubernetes.io/component": "rbac",
                    "app.kubernetes.io/created-by": "primaza",
                    "app.kubernetes.io/instance": self.identity,
                    "app.kubernetes.io/managed-by": "primazactl",
                    "app.kubernetes.io/name": "serviceaccount",
                    "app.kubernetes.io/part-of": "primaza"})
        )
        settings.output(new_sa.to_dict())
        if not self.read():
            self.sa = new_sa
            try:
                if settings.dry_run:
                    self.corev1.create_namespaced_service_account(
                        self.namespace, self.sa, dry_run="All")
                else:
                    self.corev1.create_namespaced_service_account(
                        self.namespace, self.sa)
                logger.log_info('SUCCESS: create of ServiceAccount '
                                f'{self.sa.metadata.name}',
                                settings.dry_run)
            except ApiException as e:
                body = yaml.safe_load(e.body)
                logger.log_error('FAILED: create of ServiceAccount '
                                 f'{self.sa.metadata.name} '
                                 f'Exception: {body["message"]}')
                if not settings.dry_run:
                    raise e
        else:
            logger.log_info('UNCHANGED: ServiceAccount '
                            f'{new_sa.metadata.name} already exists',
                            settings.dry_run)

    def read(self) -> client.V1ServiceAccount | None:
        logger.log_entry(f"Identity: {self.identity}, "
                         f"namespace: {self.namespace}")

        if settings.dry_run:
            return self.sa
        try:
            return self.corev1.read_namespaced_service_account(
                name=self.identity,
                namespace=self.namespace)

        except ApiException as e:
            if e.reason != "Not Found":
                logger.log_error("Exception when calling "
                                 "read_namespaced_secret: %s\n" % e)
                raise e

        return None

    def delete(self):
        logger.log_entry(f"Identity: {self.identity}, "
                         f"namespace: {self.namespace}")

        try:
            self.corev1.delete_namespaced_service_account(
                name=self.identity,
                namespace=self.namespace)
        except ApiException as e:
            if e.reason != "Not Found":
                logger.log_error("Exception when calling "
                                 "delete_namespaced_service_account: "
                                 "%s\n" % e)
                raise e
