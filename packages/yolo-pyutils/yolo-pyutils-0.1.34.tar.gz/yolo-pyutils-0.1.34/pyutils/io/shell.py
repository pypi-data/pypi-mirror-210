from subprocess import Popen, PIPE
import codecs


# return stdout, stderr
# raise exception if failed to execute
def run(cmd, timeout_sec=None, execute_dir=None, env=None):
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, cwd=execute_dir, env=env)
    stdout_b, stderr_b = proc.communicate(timeout=timeout_sec)
    return proc.returncode, codecs.decode(stdout_b).strip(), codecs.decode(stderr_b).strip()
