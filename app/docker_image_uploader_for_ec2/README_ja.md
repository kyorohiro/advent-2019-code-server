EC2 Instance を起動して、そこに Github 上の Docker Image を配置するスクリプト

```
$ git clone https://github.com/kyorohiro/advent-2019-code-server.git
$ cd advent-2019-code-server/app/docker_image_uploader_for_ec2
$ docker-compose build
$ docker-compose up -d
```

ブラウザで、`http://127.0.0.1:8443/` を開く。


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

http://3.112.18.33:8443/


## 削除

```
$ python main.py --delete
```

## 一時停止

```
$ python main.py --stop
```

## 再開

```
$ python main.py --start
```

## SSHで中に入る

```
$ ssh -i advent-instance.pem ubuntu@3.112.18.33
```
