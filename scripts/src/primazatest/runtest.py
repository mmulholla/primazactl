import argparse
import subprocess
import sys
import time


def run_cmd(cmd):

    curr_time = time.strftime("%I:%M:%S %p", time.localtime())
    print(f"\n,---------,-\n| COMMAND: {curr_time} : {cmd}\n'---------'-")

    ctl_out = subprocess.run(cmd, capture_output=True)

    out = ""
    if ctl_out.stdout:
        out = ctl_out.stdout.decode("utf-8")

    err = ""
    if ctl_out.stderr:
        err = ctl_out.stderr.decode("utf-8").strip()

    return out, err


def run_and_check(venv_dir, args, expect_msg, expect_error_msg, fail_msg):

    command = [f"{venv_dir}/bin/primazactl"]
    if args:
        command += args
    ctl_out, ctl_err = run_cmd(command)

    outcome = True

    if expect_msg:
        if ctl_out:
            print(f"Response was:\n{ctl_out}")
            if expect_msg in ctl_out:
                print(f"[PASS] args: {args}")
            else:
                print(f"[FAIL] args: {args} : {fail_msg}")
                outcome = False
        else:
            print(f"[FAIL] args: {args} : {fail_msg}")
            outcome = False

    if expect_error_msg:
        if ctl_err:
            print(f"Error response was:\n{ctl_err}")
            if expect_error_msg in ctl_err:
                print(f"[PASS] args: {args}")
            else:
                print(f"[FAIL] args: {args} : {fail_msg}")
                outcome = False
        else:
            print(f"[FAIL] args: {args} : {fail_msg}")
            outcome = False

    return outcome


def test_args(venv_dir):

    outcome = True
    expect_error_msg = "arguments are required: action, install_type"
    fail_msg = "unexpected response to no arguments"
    outcome = outcome & run_and_check(venv_dir, None, None,
                                      expect_error_msg, fail_msg)

    args = ["install"]
    expect_error_msg = "arguments are required: install_type"
    fail_msg = "unexpected response to single argument"
    outcome = outcome & run_and_check(venv_dir, args, None,
                                      expect_error_msg, fail_msg)

    args = ["drink"]
    expect_error_msg = " argument action: invalid choice: 'drink'"
    fail_msg = "unexpected response invalid action"
    outcome = outcome & run_and_check(venv_dir, args, None,
                                      expect_error_msg, fail_msg)

    args = ["install", "marker"]
    expect_error_msg = "argument install_type: invalid choice: 'marker'"
    fail_msg = "unexpected response to nad install type"
    outcome = outcome & run_and_check(venv_dir, args, None,
                                      expect_error_msg, fail_msg)

    return outcome


def test_main_install(venv_dir, config, cluster):

    command = [f"{venv_dir}/bin/primazactl",
               "install", "main",
               "-f", config,
               "-v", venv_dir,
               "-c", cluster]
    out, err = run_cmd(command)

    if err:
        print(f"[FAIL] Unexpected error response: {err}")
        return False

    outcome = True
    for i in range(1, 50):
        pods, err = run_cmd(["kubectl", "get", "pods", "-n",
                            "primaza-system"])

        if pods:
            print(pods)
            if "ContainerCreating" not in pods:
                if "ImagePullBackOff" in pods or "ErrImagePull" in pods:
                    print("[FAIL] primaza main failed to install")
                    outcome = False
                break
        if err:
            print(f"[FAIL]: {err}")
            outcome = False
            break
        time.sleep(1)

    if not outcome:
        time.sleep(5)
        pods, err = run_cmd(["kubectl", "describe",
                            "pods", "-n", "primaza-system"])
        if pods:
            print(pods)
        if err:
            print(err)

    return outcome


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

    outcome = test_args(args.venv_dir)
    outcome = outcome & test_main_install(args.venv_dir, args.primaza_config,
                                          args.cluster_name)

    if outcome:
        print("[SUCCESS] All tests passed")
    else:
        print("[FAILED] One or more tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
