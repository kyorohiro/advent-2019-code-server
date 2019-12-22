これは、2019年 code-server に Advent Calender の 第9日目の記事です。今回も、code-server って何だろう?と言う事を解説していきます。

(1) [code-server って何?](https://qiita.com/kyorohiro/items/35bab591cd4a6b975c80)
(2) [Dockerで独自のcode-server 環境を作って見る](https://qiita.com/kyorohiro/items/d991f6fbf77a425525c5)
(3) [VSCode の Plugin を 利用してみる](https://qiita.com/kyorohiro/items/11a13d32c8748f3d7002)
(4) [DBなども含めたMVC環境を用意してみよう (1)](https://qiita.com/kyorohiro/items/4ed279dd91e39321ed20)
(5) [DBなども含めたMVC環境を用意してみよう (2)](https://qiita.com/kyorohiro/items/94c75a13ddccc5f39d85)
(6) [DBなども含めたMVC環境を用意してみよう (3)](https://qiita.com/kyorohiro/items/71a8b6ce3cbb9b36019a)
(7) [DBなども含めたMVC環境を用意してみよう (4)](https://qiita.com/kyorohiro/items/106ebb7003072a8dc989)
(8) [DBなども含めたMVC環境を用意してみよう (5)](https://qiita.com/kyorohiro/items/a019e4ab6dcda55896e0)
(9) [DBなども含めたMVC環境を用意してみよう (6)](https://qiita.com/kyorohiro/items/287364f03ed7a88f714e)
(10) [おまけ](https://qiita.com/kyorohiro/items/f96d27bba9fb23c0a097)

(NEXT->) [オンライン環境篇 1日目 作業環境を整備する](https://qiita.com/kyorohiro/items/603d6ee693fc2300079e)

(..) ローカルで、DBなどの環境も含めて構築するには
(..) オンライン上に置くには?
(..) K8Sなどの最近の流行りの環境と連携するには?
(..) Code-Serverを改造して、より良くしたい


ローカル環境篇 を通して、DB と アプリ と VSCode を含む開発環境を、Docker-Composeで固めて提供できるようになりました。

WebFrameWork を用いた開発環境などは、組めるようになったのではないでしょうか。
オンライン篇と魔改造篇に進むわけですが、Docker について、補足していきたいと思います。

# 今回の何?
### Image として 固めて再利用できる


# 開発環境を固めたい!!

Dockerfile を書いたとはいえ、次に必ず Docker Image の Build が成功するとは限りません。

一度、ビルドに成功したイメージは、使いまわしましょう。


Python の開発環境があるとします。

```Dockerfile
FROM python:3.8.0-buster

RUN apt-get update
# code-server を取得するのに wget を install しておく
RUN apt-get install -y wget

# 作業ディレクトリを /works にする。どこでも良いです
WORKDIR /works

# code-server のバイナリーを取得
RUN wget https://github.com/cdr/code-server/releases/download/2.1692-vsc1.39.2/code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz

# code-server を /works 配下に解凍する
RUN tar -xzf code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz -C ./ --strip-components 1　

WORKDIR /works/app
ENV PYTHONPATH=/works/app

# python の plugin をインストール 
RUN /works/code-server --install-extension ms-python.python
RUN /usr/local/bin/python -m pip install -U pylint --user

# デフォルトは、/works/app で起動するようにする。
CMD [ "/works/code-server", "--allow-http", "--auth", "none", "--port", "8443", "/works/app"]

```

`$ docker  build -t for_python .` としてビルドしてあげれば、以降は、`$ docker run -it for_python bash` といった感じで使えます。


この、Image を、他の人と共有するには、Docker Hub が便利です。
https://hub.docker.com/


会員登録後、作成したImage を公開することができます。公開してみましょう。


# リポジトリーに配置しよう

まずは、Loginします。

```
$ docker login -u kyorohiro
Password: 
Login Succeeded
```

ビルドして、Pushしてみましょう

```bash
# rename
$ docker tag for_python kyorohiro/for_python:latest
# push
$ docker push kyorohiro/for_python:latest
$ docker push kyorohiro/for_python:latest
The push refers to repository [docker.io/kyorohiro/for_python]
64a79ea89615: Pushing [============>         ]  9.104MB/11.06MB
72d671b5ce06: Pushing [=>                                               ]  6.086MB/195MB
36788bc3e719: Pushed 
1ca79cb1c3f8: Pushing [==>                                                ]  8.901MB/182.6MB
9a5303639ce9: Pushing [==>                                                ]   2.46MB/47.3MB
14f67da8f102: Pushing  1.536kB
4f67a1129031: Waiting 
a4371f75e248: Waiting 
00947a3aa859: Waiting 
7290ddeeb6e8: Waiting 
d3bfe2faf397: Waiting 
cecea5b3282e: Waiting 

```

以降は、`docker pull kyorohiro/for_python` として Build 済みの Image を取得できるようになります。


# Dockerfileに書かれていない内容も、Image化できる。

独自の Docker Image を Dockerfile を Build するだけではありません。
実際に手作業で行った作業の結果も Docker Image 化 できます。

試してみましょう

```bash
$ docker run -it ubuntu bash
# 以降は Docker の中
$ curl www.google.com
bash: curl: command not found
$ apt-get update
$ apt-get install -y curl
$ curl www.google.com
<!doctype html><html itemscope="" ...
 lang="ja"><head>...
$ exit
```

では、この終了したContainerを再起動してみましょう

```
# container 一覧を取得
$ docker ps -a | grep ubuntu
8269ec081004        ubuntu                        "bash"                   4 minutes ago       Exited (0) 46 seconds ago                                                    agitated_goldberg

# 再開
$ docker start 8269ec081004 
# Bashを起動
$ docker exec -it  8269ec081004 bash 
# Curl も動きます
$ curl www.google.com
```

次は、Image化してみましょう

```
# 起動しているか確認
$ docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
8269ec081004        ubuntu              "bash"              7 minutes ago       Up 3 seconds                            agitated_goldberg

# 起動しているなら停止
$ docker stop 8269ec081004 

# Image化する
$ docker commit 8269ec081004 manual_test
sha256:ec4c80afae824f4b3bf5c6b4997e30cdebb7264d80f0144dff9af07e38bbe73b

# 確認
$ docker image ls manual_test
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
manual_test         latest              ec4c80afae82        49 seconds ago      106MB

```

おっ、Image 化できましたね!! これで、再度ビルドする事なくアレコレできますね..


# 次回

オンライン篇に入ります。


# PS
ソース
https://github.com/kyorohiro/advent-2019-code-server

