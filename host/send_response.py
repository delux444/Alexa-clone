import paramiko
import requests

from paramiko.ssh_exception import SSHException
from read_config import get_from_config as config

def main():
    filename = config(parameter="RESP_FILE")
    sat_path = config(parameter="SAT_PATH")
    sat_ip = config(parameter="SAT_IP")
    sat_usr = config(parameter="SAT_USR")
    sat_pass = config(parameter="SAT_PASS")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(sat_ip, username=sat_usr, password=sat_pass)
        sftp = ssh.open_sftp()
        sftp.put(filename, sat_path)
        sftp.close()
        ssh.close()
        print("[*] file send to sat. with sucess via SFTP")
        
    except (SSHException, IOError) as e:
        return f"[!] Error SSH/SFTP: Sending not done: {e}"
        
if __name__ == "__main__":
    print(main())

