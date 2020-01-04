
This Script create ec2 instance and run docker image on Github repogitory



```
$ git clone https://github.com/kyorohiro/advent-2019-code-server.git
$ cd advent-2019-code-server/app/docker_image_uploader_for_ec2
$ docker-compose build
$ docker-compose up -d
```

open `http://127.0.0.1:8443/` at browser


on vscode 's terminal

```bash:Terminal
$ pip install -r requirements.txt
$ aws configure 
..
..
```

create ec2 instance

```
$ python main.py --create
```

get ec2 infomation

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


## delete

```
$ python main.py --delete
```

## stop

```
$ python main.py --stop
```

## start 

```
$ python main.py --start
```

## ssh command

```
$ ssh -i advent-instance.pem ubuntu@3.112.18.33
```
