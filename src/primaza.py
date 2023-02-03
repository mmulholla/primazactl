import argparse
import os
import sys
from pathlib import Path
from kubeconfig import KubeConfig
from primazactl import primazamain

def main():
    parser = argparse.ArgumentParser(
        prog = 'primaza',
        description = 'Configure and install primaza and primaza worker on clusters',
        epilog = "Brought to you by the RedHat app-services team.")
    parser.add_argument("action", type=str, choices=["install","info","uninstall","join"], help='type of action to perform.')
    parser.add_argument('install_type', type=str, choices=["main", "worker"], help='specify primaza or worker.')
    parser.add_argument("-s", "--namespace", dest="namespace", type=str, required=False,
                    help="namespace to use for primaza or worker, defaults: primaza_system_main, primaza_system_worker")
    parser.add_argument("-c", "--clustername", dest="cluster_name", type=str, required=False,
                        help="cluster on which to install primaza or worker, defaults: primaza_main, primaza_worker")
    parser.add_argument("-k", "--kubeconfig", dest="kubeconfig", type=str, required=False, help=f"path to kubeconfig file, default: KUBECONFIG environment variable if set, otherwise {(os.path.join(Path.home(),'.kube','config'))}")

    args = parser.parse_args()

    cluster_name = args.cluster_name
    if not args.cluster_name:
        cluster_name = f"primaza_{args.install_type}"

    namespace = args.namespace
    if not args.namespace:
        namespace = f"primaza_system_{args.install_type}"

    kube_config = args.kubeconfig
    if not kube_config:
        kube_config = os.environ.get("KUBECONFIG")
        if not kube_config:
            kube_config = str(os.path.join(Path.home(),".kube","config"))
            os.environ["KUBECONFIG"]=str(kube_config)
    else:
        os.environ["KUBECONFIG"]=str(kube_config)

    if not os.path.isfile(kube_config):
        print("\n[ERROR] kubeconfig file not found: {kube_config}\n")
        parser.print_help()
        sys.exit(1)

    print(f'install_type: {args.install_type}')
    print(f'namespace: {namespace}')
    print(f'cluster name: {cluster_name}')
    print(f'kube config: {kube_config}')

    if args.install_type == "worker":
        print("Install and configure primaza worker is not yet implemented")
    else:
        print("Install and configure primaza main is in progress")
        pmain = primazamain.PrimazaMain(cluster_name,kube_config,namespace)
        pmain.install_primaza()
        #conf = KubeConfig(kube_config)
        #conf.use_context(name=cluster_name)
        #print(conf.view())
        #print(conf.current_context())



if __name__ == "__main__":
    main()