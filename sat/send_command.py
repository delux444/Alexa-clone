import paramiko
import requests

from paramiko.ssh_exception import SSHException
from read_config import get_from_config as config

def main():
    filename           = config(parameter="COMMAND_FILE")
    host_path          = config(parameter="PATH_ON_HOST_TO_SEND_AUDIO_FILE")
    host_ip            = config(parameter="HOST_IP")
    host_username      = config(parameter="HOST_USERNAME")
    host_password      = config(parameter="HOST_PASSWORD")
    whisper_audio_path = config(parameter="PATH_ON_WHISPER_TO_AUDIO=")
    whisper_port       = 8080

    #print(filename)
    #print(host_path)
    #print(host_ip)
    #print(host_username)
    #print(host_password)
    #print(whisper_port)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host_ip, username=host_username, password=host_password)
        sftp = ssh.open_sftp()
        sftp.put(filename, host_path)
        sftp.close()
        ssh.close()
        print("[*] file send to host with sucess via SFTP")
        
    except (SSHException, IOError) as e:
        return f"[!] Error SSH/SFTP: Sending not done: {e}"
    

    files = {
        "file": whisper_audio_path,
        "temperature": "0.0",
        "temperature_inc": "0.2",
        "response_format": "json",
        "language": "pl",
    }
    response = requests.post(f"http://{host_ip}:{whisper_port}/inference", files=files)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('text', 'no text in answer')
    else:
        return f"[!] Server error: {response.status_code}"
        
if __name__ == "__main__":
    print(main())
