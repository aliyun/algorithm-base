import subprocess


def test_kerberos(client):
    """
    -s  Causes klist to run silently (produce no output).
        klist will exit with status 1 if the credentials cache cannot be read or is expired,
        and with status 0 otherwise.
    """
    assert subprocess.run(['klist', '-s']).returncode == 0
