これは、2019年 code-server に Advent Calender の 第4日目の記事です。今回も、code-server って何だろう?と言う事を解説していきます。


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



今回から2-3回に渡って、ローカルで動作する web framework の開発環境を作成していきます。

docker-compose を利用して、db、phpmyadmin、flask を利用した開発環境を構築してみましょう!!


# 今回の何?
### チームでの開発環境を構築するコストを無くす事ができる
code-server の 開発元である Coder でも解説されていますが、
https://coder.com/docs/introduction

チームでの開発環境を構築するコストを無くす事が、code-server で 実現できます。
一度、環境を構築して、イメージを固めることで、2度と開発環境を構築する必要がなくなります。


# Docker-Composeで利用してみよう

前回作成したPythonの環境を、docker-compose から呼び出すようにして呼び出してみます。

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
    command: /works/code-server --allow-http --auth none --port 8443 /works/app
```

以下のように配置しています。

```bash
$ find . -type f
.
./app
./app/Dockerfile
./app/main.py
./docker-compose.yml

```

docker-compose.yml は、前回の呼び出しコマンドとほとんど同じですね!!

https://docs.docker.com/compose/compose-file/

などを、参考にすると良いでしょう。

# 実行してみよう

```bash
$ docker-compose build
$ docker-compose up -d

```
とする事で、code-server を 起動 できます。

そして、
ブラウザーで　http://127.0.0.1:8443/ にアクセスすると、
<img width="1246" alt="Screen Shot 2019-12-03 at 5.39.02.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/811dc6cb-591b-4a71-e550-4c0e131504a1.png">


VSCodeを開く事ができます

# 次回

flask という python の web framework の 環境を作成してみます

# PS

## ソース
https://github.com/kyorohiro/advent-2019-code-server
