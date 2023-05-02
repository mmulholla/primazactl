

USER = "<user>"
USER_TYPE = "<user-type>"
CLUSTER_ENVIRONMENT = "<cluster-environment>"
REF_NAMESPACE = "<reference-namespace>"
REF_KUBECONFIG = "<kubeconfig-reference>"
TENANT = "<tenant>"
PROVIDER = "<provider>"

USER_TYPE_SVC = "svc"
USER_TYPE_APP = "app"
USER_TYPE_MAIN = "primaza"
USER_TYPE_WORKER = "worker"

naming_convention = {
    "identity": {
        "service_account": {
            "name": f"{USER}-{TENANT}-{PROVIDER}",
        },
        "secret": {
            "name": f"primaza-token-{USER}-{TENANT}-{PROVIDER}",
        },
    },
    "kubeconfig_secret": {
        "name": f"kubeconfig-{REF_KUBECONFIG}-{USER_TYPE}"
    },
    "role": {
        "name": f"primaza:controlplane:{USER_TYPE}"
    },
    "rolebinding": {
        "name": f"primaza:controlplane:{USER_TYPE}"
    }
}


def get_kube_secret_name(reference, user_type):

    name = naming_convention["kubeconfig_secret"]["name"]
    name = name.replace(REF_KUBECONFIG, reference)
    return name.replace(USER_TYPE, user_type)


def get_identity_names(user_name, tenant, provider):

    sa = naming_convention["identity"]["service_account"]["name"]
    sa = sa.replace(USER, user_name)
    sa = sa.replace(TENANT, tenant)
    sa = sa.replace(PROVIDER, provider)
    tkn = naming_convention["identity"]["secret"]["name"]
    tkn = tkn.replace(USER, user_name)
    tkn = tkn.replace(TENANT, tenant)
    tkn = tkn.replace(PROVIDER, provider)

    return sa, tkn


def get_role_name(user_type):

    role = naming_convention["role"]["name"]
    return role.replace(USER_TYPE, user_type)


def get_rolebinding_name(user_type):

    roleb = naming_convention["rolebinding"]["name"]
    return roleb.replace(USER_TYPE, user_type)
