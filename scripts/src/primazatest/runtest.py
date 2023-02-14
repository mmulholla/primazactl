import argparse
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(
        prog='runtest',
        description='Run primazactl tests',
        epilog="Brought to you by the RedHat app-services team.")
    parser.add_argument("-v", "--venvdir",
                        dest="venv_dir", type=str, required=True,
                        help="location of python venv dir")
    parser.add_argument("-f", "--config",
                        dest="primaza_config", type=str, required=True,
                        help="primaza config file.")
    parser.add_argument("-c", "--clustername",
                        dest="cluster_name", type=str, required=True,
                        help="name of cluster, as it appears in kubeconfig, \
                        on which to install primaza or worker")

    args = parser.parse_args()

    ctl_out = subprocess.run([f"{args.venv_dir}/bin/primazactl",
                              "install", "main",
                              "-f", args.primaza_config,
                              "-v", args.venv_dir,
                              "-c", args.cluster_name])

    if ctl_out.stdout:
        out = ctl_out.stdout.decode("utf-8")
        print(out)
    if ctl_out.stderr:
        err = ctl_out.stderr.decode("utf-8").strip()
        if err:
            print("[FAIL]: {err}")
            sys.exit(1)

    for i in range(1, 50):
        pods = subprocess.run(["kubectl", "get", "pods", "-n",
                               "primaza-system"], capture_output=True)
        print(f'{i} {time.strftime("%I:%M:%S %p", time.localtime())}. '
              f'kubectl get pods -n primaza-system:')
        pods_out = pods.stdout.decode("utf-8")
        print(pods_out)
        err = pods.stderr.decode("utf-8").strip()
        if err:
            print("[FAIL]: {err}")
            sys.exit(1)
        sleep(1)

    sleep(5)
    pods = subprocess.run(["kubectl", "describe",
                           "pods", "-n", "primaza-system"],
                          capture_output=True)

    print("kubectl describe pods -n primaza-system:")
    print(pods.stdout.decode("utf-8"))
    err = pods.stderr.decode("utf-8").strip()
    if err:
        print("[FAIL]: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
