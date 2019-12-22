これは、2019年 code-server に Advent Calender の 第6日目の記事です。今回も、code-server って何だろう?と言う事を解説していきます。

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


前回の続きで、db を動作させてみます。

# 今回の何?
## Compose File なら、Docker同士の連携が楽!!



# MySQL DB を追加してみましょう。


```yml:docker-compose.yml
version: '3'
services: 
  app:
    build: ./app
    ports: 
      - 8443:8443
      - 8080:8080
    volumes:
      - ./app:/works/app
    links:
      - mysqld
    command: /works/code-server --allow-http --auth none --port 8443 /works/app
  mysqld:
    image: mysql:5.7
    ports: 
      - "3306:3306"
    environment: 
      MYSQL_ROOT_PASSWORD: passwd
      MYSQL_DATABASE: hello
      #MYSQL_USER: user
      #MYSQL_PASSWORD: password
```

mysql用のサービスを追加しました。
- Docker Image を mysql:5.7 に
- Ports を 3306 同士で
- パスワードをpasswd に
- linksタグで、前回作成した、python から アクセス

という構成にしました。



# 動かしてみましょう!!

いつもの、コマンドを入力して、

```bash
$ docker-compose build
$ docker-compose up -d
```

ブラウザーでアクセスしてみます。

```
http://127.0.0.1:8443/
```

VSCode が表示されます!!

<img width="1448" alt="Screen Shot 2019-12-07 at 3.03.46.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/98eb6ad9-5d7d-8b32-f1ed-bb1107e41499.png">

Terminal を開いて、mysql client を インストール

```
$ apt-get install -y mariadb-server
```

# mysql サーバーに接続してみましょう

```
root@f80f67f3bcb4:/works/app# mysql -uroot -hmysqld -ppasswd
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 5
Server version: 5.7.28 MySQL Community Server (GPL)

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [(none)]> show database;
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'database' at line 1
MySQL [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| hello              |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
5 rows in set (0.001 sec)

MySQL [(none)]> 
```

おー、繋がりました!!

# おまけ

せっかくなので、Dockerfile に追加しておきましょう

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

# mysql を Install
RUN apt-get install -y mariadb-server

# デフォルトは、/works/app で起動するようにする。
CMD [ "/works/code-server", "--allow-http", "--auth", "none", "--port", "8443", "/works/app"]

```


# 次回

PHPMyAdmin を導入したり、 SQLサーバーを初期化したり
してみます。




# PS

## ソース
https://github.com/kyorohiro/advent-2019-code-server

