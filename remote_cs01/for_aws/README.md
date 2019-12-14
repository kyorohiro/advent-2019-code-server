# create network & create instances

```
python create.py
```

# remove network & remove instances

```
python rm.py
```


# get instance info

```
python get_inst.py
>>>> i-0df78917731498ed1
>>>> ec2-13-230-8-80.ap-northeast-1.compute.amazonaws.com
>>>> 13.230.8.80
>>>> ip-172-31-42-142.ap-northeast-1.compute.internal
>>>> 172.31.42.142
>>>> {'Code': 16, 'Name': 'running'}
```

```
chmod 600 advent-code-server.pem
ssh -i advent-code-server.pem ubuntu@ec2-13-230-8-80.ap-northeast-1.compute.amazonaws.com
```
