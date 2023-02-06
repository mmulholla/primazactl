import argparse
import os
import sys
from pathlib import Path
from primazamain import primazamain

def main():
    parser = argparse.ArgumentParser(
        prog = 'primaza',
        description = 'Configure and install primaza and primaza worker on clusters',
        epilog = "Brought to you by the RedHat app-services team.")
    parser.add_argument("action", type=str, choices=["install","info","uninstall","join"], help='type of action to perform.')
    parser.add_argument('install_type', type=str, choices=["main", "worker"], help='specify primaza or worker.')
    parser.add_argument("-f", "--config", dest="primazaconfig", type=str, required=False,
                    help="primaza config file or directory (required for: install main)")
    parser.add_argument("-c", "--clustername", dest="cluster_name", type=str, required=False,
                        help="name of cluster, as it appears in kubeconfig, on which to install primaza or worker, defaults: current kubeconfig context")
    parser.add_argument("-k", "--kubeconfig", dest="kubeconfig", type=str, required=False, help=f"path to kubeconfig file, default: KUBECONFIG environment variable if set, otherwise {(os.path.join(Path.home(),'.kube','config'))}")

    args = parser.parse_args()

    cluster_name = args.cluster_name

    kube_config = args.kubeconfig
    if not kube_config:
        kube_config = os.environ.get("KUBECONFIG")
        if not kube_config:
            kube_config = str(os.path.join(Path.home(),".kube","config"))

    if not os.path.isfile(kube_config):
        print("\n[ERROR] kubeconfig file not found: {kube_config}\n")
        parser.print_help()
        sys.exit(1)

    primaza_config = args.primazaconfig
    if args.action == "install" and args.install_type == "main":
        if not primaza_config:
            print("\n[ERROR] --config is required for: install main\n")
            parser.print_help()
            sys.exit(1)
        elif not os.path.exists(primaza_config):
            print("\n[ERROR] --config does not specify a valid file or directory\n")
            parser.print_help()
            sys.exit(1)

    print(f'install_type: {args.install_type}')
    print(f'primaza_config: {primaza_config}')
    print(f'cluster name: {cluster_name}')
    print(f'kube config: {kube_config}')

    if args.action == "install":

        if args.install_type == "worker":
            print("Install and configure primaza worker is not yet implemented")
        else:
            print("Install and configure primaza main is in progress")
            pmain = primazamain.PrimazaMain(cluster_name,kube_config,primaza_config)
            pmain.install_primaza()
    else:
        print("info, uninstall and join are not yet implemented.")



if __name__ == "__main__":
    main()