# primazactl
primazactl is a simple Command Line Application for Primaza Administrators.

The first implemenation include primaza main install only and more functions will be added over time.

Initially you can run the tool:
- download this repository
- run the script using:
    - ```python3 scripts/src/primazactl/primazactl.py```
- this will return:
```
usage: primaza [-h] [-f PRIMAZA_CONFIG] [-c CLUSTER_NAME] [-k KUBECONFIG] [-v PRIMAZA_VERSION]
               {install,info,uninstall,join} {main,worker}
primaza: error: the following arguments are required: action, install_type
```
- if you also use the -h flag:
```
usage: primaza [-h] [-f PRIMAZA_CONFIG] [-c CLUSTER_NAME] [-k KUBECONFIG] [-v PRIMAZA_VERSION]
               {install,info,uninstall,join} {main,worker}

Configure and install primaza and primaza worker on clusters

positional arguments:
  {install,info,uninstall,join}
                        type of action to perform.
  {main,worker}         specify primaza or worker.

options:
  -h, --help            show this help message and exit
  -f PRIMAZA_CONFIG, --config PRIMAZA_CONFIG
                        primaza config file. Takes precedence over --version
  -c CLUSTER_NAME, --clustername CLUSTER_NAME
                        name of cluster, as it appears in kubeconfig, on which to install primaza or worker, default:
                        current kubeconfig context
  -k KUBECONFIG, --kubeconfig KUBECONFIG
                        path to kubeconfig file, default: KUBECONFIG environment variable if set, otherwise
                        /Users/martinmulholland/.kube/config
  -v PRIMAZA_VERSION, --version PRIMAZA_VERSION
                        Version of primaza to use, default: newest release available. Ignored if --config is set.

Brought to you by the RedHat app-services team.
```
- Note all flags are optional if the default are acceptable.
- Before running the script:
  - Ensure a properly configured cluster is available.
  - Ensure the required primaza image is uploaded to docker.






