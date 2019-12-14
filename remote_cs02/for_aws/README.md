# create network & create instances

```
$ python create.py
```

# remove network & remove instances

```
$ python rm.py
```


# get instance info

```
$ python get_inst.py
>>>> i-0df78917731498ed1
>>>> ec2-13-230-8-80.ap-northeast-1.compute.amazonaws.com
>>>> 13.230.8.80
>>>> ip-172-31-42-142.ap-northeast-1.compute.internal
>>>> 172.31.42.142
>>>> {'Code': 16, 'Name': 'running'}
```

```
$ chmod 600 advent-code-server.pem
$ ssh -i advent-code-server.pem ubuntu@ec2-13-230-8-80.ap-northeast-1.compute.amazonaws.com
```


# install code-server

```
$ wget https://github.com/cdr/code-server/releases/download/2.1692-vsc1.39.2/code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz
$ tar -xzf code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz -C ./ --strip-components 1
$ mkdir app
$ ./code-server --cert --port 8443 --host 0.0.0.0 ./app &
info  Server listening on https://0.0.0.0:8443
info    - Password is ceb561553cbc44bde07b225d
info      - To use your own password, set the PASSWORD environment variable
info      - To disable use `--auth none`
info    - Using generated certificate and key for HTTPS
```

https://ec2-13-113-205-131.ap-northeast-1.compute.amazonaws.com:8443/

