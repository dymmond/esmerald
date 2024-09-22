import os
import subprocess


def run_cmd(app, cmd, is_app=True):
    if is_app:
        os.environ["ESMERALD_DEFAULT_APP"] = app
    cmd = f"hatch --env test run {cmd}"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = process.communicate()
    print("\n$ " + cmd)
    print(stdout.decode("utf-8"))
    print(stderr.decode("utf-8"))
    return stdout, stderr, process.wait()
