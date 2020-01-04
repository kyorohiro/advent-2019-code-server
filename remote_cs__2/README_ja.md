これは、2019年 code-server に Advent Calender の 第16日目の記事です。


目次
[ローカル環境篇 1日目](https://qiita.com/kyorohiro/items/35bab591cd4a6b975c80) 
[オンライン環境篇 1日目 作業環境を整備する](https://qiita.com/kyorohiro/items/603d6ee693fc2300079e)

[オンライン環境篇 2日目 仮想ネットワークを作成する](https://qiita.com/kyorohiro/items/6f2452ec2a2fe3640979)

[オンライン環境篇 3日目 Boto3 で EC2 インスタンスを立ち上げる](https://qiita.com/kyorohiro/items/32c9b7f9ebfccbeb6ac5)

[オンライン環境篇 4日目 Code-Serverをクラウドで動かしてみる](https://qiita.com/kyorohiro/items/3701fc97f61e94c5ba95)

[オンライン環境篇 5日目 Docker 上で、code-server を立ち上げる](https://qiita.com/kyorohiro/items/ad9d5ac702bdebf93ad0)

オンライン篇 6日目 自動化してみよう

オンライン篇 ７日目 簡単な起動アプリを作成してみよう(オンライン上に)

...
オンライン篇 .. Coomposeファイルで構築

オンライン篇 .. K8Sを試してみる

...

魔改造篇 


# はじめに

前回までで、Docker を利用して、EC Instance 上に Code-Serverを立ち上げてみました。
今回は、この作業を自動化してみます。


# EC2 Instance を作る

前回のつづきから

```
$ git clone https://github.com/kyorohiro/advent-2019-code-server.git
$ cd advent-2019-code-server/remote_cs04/
$ docker-compose build
$ docker-compose up -d
```

ブラウザで、`http://127.0.0.1:8443/` を開く。

<img width="1211" alt="Screen Shot 2019-12-24 at 0.39.23.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/dc06b338-2af1-a5cd-f594-4d9ca26a8a7e.png">


Terminal 上で

```bash:Terminal
$ pip install -r requirements.txt
$ aws configure 
..
..
```

EC2Instance を 作成

```
$ python main.py --create
```

EC2 情報を取得

```
$ python main.py --get
>>>> i-0d1e7775a07bbb326
>>>> 
>>>> 3.112.18.33
>>>> ip-10-1-0-228.ap-northeast-1.compute.internal
>>>> 10.1.0.228
>>>> {'Code': 16, 'Name': 'running'}
```


# SSHで中に入る

```python:initialize.py
import paramiko


def run_script(ip:str, rsa_key_path:str):
    rsa_key: paramiko.rsakey.RSAKey = paramiko.rsakey.RSAKey.from_private_key_file(rsa_key_path)
    client: paramiko.SSHClient = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username="ubuntu", pkey=rsa_key)


    stdin, stdout, stderr = client.exec_command("ls /")
    d = stdout.read().decode('utf-8')
    print(f"{d}")
    client.close()

run_script("18.177.154.240", "/works/app/advent-code-server.pem")
```


# Docker を install 

Docker 環境を作成していきます

EC2上で

```python:initialize.py
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

    client.close()

run_script("18.177.154.240", "/works/app/advent-code-server.pem")

```

# Docker の Hello World

```
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
    run_command(client, "sudo docker run hello-world")

    client.close()

run_script("18.177.154.240", "/works/app/advent-code-server.pem")
```

```
atest: Pulling from library/hello-world
1b930d010525: Pull complete 
Digest: sha256:4fe721ccc2e8dc7362278a29dc660d833570ec2682f4e4194f4ee23e415e1064
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
```


# Code-Server を 起動してみよう

```python:initialize.py
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
#    run_command(client, "mkdir -p  ${HOME}/.local/share/code-server/extensions")
    run_command(client, "sudo docker run -p 0.0.0.0:8080:8080 -p0.0.0.0:8443:8443 codercom/code-server:v2 --cert")
    

    client.close()

run_script("18.177.154.240", "/works/app/advent-code-server.pem")
```

```
..
..
info  Server listening on https://0.0.0.0:8080
info    - Password is 86821ed9f02ef11d83e980da
info      - To use your own password, set the PASSWORD environment variable
info      - To disable use `--auth none`
info    - Using generated certificate and key for HTTPS
```


<img width="1216" alt="Screen Shot 2019-12-24 at 1.11.08.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/58a9b12e-929f-ec4f-de5b-33c2deded7a7.png">


<img width="1214" alt="Screen Shot 2019-12-24 at 1.06.50.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/420b0110-94a3-974f-96e9-929c9cfbe68c.png">


<img width="1209" alt="Screen Shot 2019-12-24 at 1.12.23.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/4262bbd4-7120-b96c-970f-705edf86808b.png">

できました!!



# 削除しよう

```
# ec2 instance から logout
$ exit

# local の code-server 上で
$ python main.py --delete

```

なんども使い回したいならば、 ec2 instance を停止するようにしてください

※ 次回か次次回


# 次回

Webアプリ化して、指定した Docker Image を、立ち上げる機能を作成してみましょう!!
そろそろ、EC2 Instance 編、これで、終わりです。

自作してみましたが、AWS や GCP では、ありものが使えますので、
それを利用して行きます。



# コード

https://github.com/kyorohiro/advent-2019-code-server/tree/master/remote_cs06