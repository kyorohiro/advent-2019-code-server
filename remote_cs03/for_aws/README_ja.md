これは、2019年 code-server に Advent Calender の 第15日目の記事です。

前回に続き、EC2 Instance を 立ち上げたいと思います。

目次
[ローカル環境篇 1日目](https://qiita.com/kyorohiro/items/35bab591cd4a6b975c80) 
[オンライン環境篇 1日目 作業環境を整備する](https://qiita.com/kyorohiro/items/603d6ee693fc2300079e)
[オンライン環境篇 2日目 仮想ネットワークを作成する](https://qiita.com/kyorohiro/items/6f2452ec2a2fe3640979)
[オンライン環境篇 3日目 Boto3 で EC2 インスタンスを立ち上げる](https://qiita.com/kyorohiro/items/32c9b7f9ebfccbeb6ac5)
[オンライン環境篇 4日目 Code-Serverをクラウドで動かしてみる](https://qiita.com/kyorohiro/items/3701fc97f61e94c5ba95)
オンライン篇 5日目 Docker環境を構築してアレコレ
オンライン篇 6日目 簡単な起動アプリを作成してみよう
...
オンライン篇 .. Coomposeファイルで構築
オンライン篇 .. K8Sを試してみる
...
魔改造篇 


# はじめに

前回までで、boto3 x python で EC2 Instance を　立ち上げました。
今回は、この立ち上げたInstance に Code-Server を インストールしてみましょう。


# SSH で接続してみる

作成した EC Instance を cli から　操作してみましょう

## Instance 情報を取得する

ssh 接続する際に、Public IP の情報が必要です。
以下のようなコードで取得できます。

```python
def get_inst(ec2_client:ec2.Client, project_name="advent-code-server"):
    try:
        print(">>>> ec2client.describe_instances")
        res = ec2_client.describe_instances(Filters=[{"Name":"tag:Name","Values":[project_name]}])
        print("{}".format(res))

        for reserve_info in res['Reservations']:
            print("-")
            for instance_info in reserve_info['Instances']:
                print(">>>> {}".format(instance_info.get('InstanceId',"")))
                print(">>>> {}".format(instance_info.get('PublicDnsName',"")))
                print(">>>> {}".format(instance_info.get('PublicIpAddress',"")))
                print(">>>> {}".format(instance_info.get('PrivateDnsName',"")))
                print(">>>> {}".format(instance_info.get('PrivateIpAddress',"")))
                print(">>>> {}".format(instance_info.get('State',"")))
 
    except ClientError as e:
        print("-- {}".format(e.response))
```

## ssh 接続する

pemファイルのセキュリテイを変える

```bash
$ chmod 600 advent-code-server.pem 
```

ssh で ec instance に接続する

```
$ ssh -i advent-code-server.pem ubuntu@18.182.61.231
root@dabe0caa28a0:/works/app# ssh -i advent-code-server.pem ubuntu@18.182.61.231
Welcome to Ubuntu 18.04.3 LTS (GNU/Linux 4.15.0-1051-aws x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sat Dec 21 15:32:31 UTC 2019

  System load:  0.01              Processes:           88
  Usage of /:   13.6% of 7.69GB   Users logged in:     0
  Memory usage: 14%               IP address for eth0: 10.1.0.227
  Swap usage:   0%

0 packages can be updated.
0 updates are security updates.



The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

ubuntu@ip-10-1-0-227:~$ 
```

接続できました!!


# PORTが開いているか確認！!

static サーバーを起動

```
ubuntu@ip-10-1-0-227:~$ sudo apt-get install python3
ubuntu@ip-10-1-0-227:~$ python3 -m http.server 8080
```

ブラウザーで、`http://18.182.61.231:8080/` でアクセスしてみましょう!!

<img width="978" alt="Screen Shot 2019-12-22 at 0.36.17.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/07afd68a-f2c6-5d98-e470-2dcca3e4f726.png">

上手く動作しているようです

# Code-Server を install してみよう!!


```bash
ubuntu@ip-10-1-0-227:~$ wget https://github.com/cdr/code-server/releases/download/2.1692-vsc1.39.2/code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz

ubuntu@ip-10-1-0-227:~$ tar -xzf code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz -C ./ --strip-components 1　

```

# Code-Server を 実行 してみよう!!

```bash
ubuntu@ip-10-1-0-227:~$ ./code-server --cert --port 8443 ./
on https://localhost:8443
info    - Password is 50cdee5af7ee7824126382ff
info      - To use your own password, set the PASSWORD environment variable
info      - To disable use `--auth none`
info    - Using generated certificate and key for HTTPS


```

`https://18.182.61.231:8443/` に接続してみましょう

<img width="980" alt="Screen Shot 2019-12-22 at 0.45.22.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/b73cdd2a-f7c1-7b22-6903-769954af5800.png">

<img width="980" alt="Screen Shot 2019-12-22 at 0.46.07.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/d97ecdf6-ed9f-4b92-7197-32a6a0970d9b.png">

<img width="982" alt="Screen Shot 2019-12-22 at 0.46.39.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/818a8acc-c657-a593-7d00-198a51232e50.png">


無事起動できました!!

# 補足

この状態だと、SSH接続が切れると、アプリが終了してしまうので、

```bash
ubuntu@ip-10-1-0-227:~$ ./code-server --cert --port 8443 ./&
```
みたいな感じで起動してあげましょう

確認

```bash
buntu@ip-10-1-0-227:~$ jobs
[1]+  Running                 ./code-server --cert --port 8443 ./ &
```


終了したい時

```
ubuntu@ip-10-1-0-227:~$ ps -aux | grep code-server
ubuntu    1786  0.2  5.2 840588 52580 ?        Sl   15:48   0:00 /home/ubuntu/code-server --cert --port 8443 ./
ubuntu    1918  0.0  0.0  14856  1004 pts/1    S+   15:51   0:00 grep --color=auto code-server

ubuntu@ip-10-1-0-227:~$ kill -9 1786
```


# 次回

Docker を導入して、ローカル篇で作成したイメージをオンライン上で起動してみましょう


# コード

https://github.com/kyorohiro/advent-2019-code-server/tree/master/remote_cs03

