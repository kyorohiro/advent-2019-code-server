import paramiko

with paramiko.SSHClient() as ssh:
    ssh.connect
if __name__ == "__main__":
    print("Hello, World!!")