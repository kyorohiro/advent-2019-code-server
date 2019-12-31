import paramiko


def run_command(client: paramiko.SSHClient, command: str):
    print(f"run>{command}\n")
    stdin, stdout, stderr = client.exec_command(command)
    d = stdout.read().decode('utf-8')
    print(f"stdout>\n{d}")
    d = stderr.read().decode('utf-8')
    print(f"stderr>\n{d}")
    return stdin

def run_script(ip:str, rsa_key_path:str):
    rsa_key: paramiko.rsakey.RSAKey = paramiko.rsakey.RSAKey.from_private_key_file(rsa_key_path)
    client: paramiko.SSHClient = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username="ubuntu", pkey=rsa_key)

    run_command(client, "sudo apt-get update")
    run_command(client, "sudo apt-get install -y docker.io")
    run_command(client, "sudo docker run -p 0.0.0.0:8080:8080 -p0.0.0.0:8443:8443 codercom/code-server:v2 --cert")
    
    client.close()

run_script("18.177.154.240", "/works/app/advent-code-server.pem")
