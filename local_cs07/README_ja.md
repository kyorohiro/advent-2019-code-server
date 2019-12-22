これは、2019年 code-server に Advent Calender の 第7日目の記事です。今回も、code-server って何だろう?と言う事を解説していきます。


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


前回の続きで、db の初期化などを、していきます。

# 今回の何?
### コンテナー単位でツールを追加すると便利!!


# PHPMyAdminを追加してみよう!!

データを直接、CLIで操作しても良いでもすが、GUIで操作するのも一つの手です。
PHPMyAdmin を 利用して GUIからDBを操作できるようにしてみましょう。



docker-compose.yml に phpmyadmin を 追加します。

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
  phpmyadmin:
    #https://hub.docker.com/r/phpmyadmin/phpmyadmin
    image: phpmyadmin/phpmyadmin:4.8.5
    environment:
      PMA_HOST: mysqld
      PMA_USER: root
      PMA_PASSWORD: passwd
    links:
      - mysqld
    ports:
      - '18080:80'

```

# 動作確認をしてみよう

ブラウザ-で 'http://127.0.0.1:18080/' にアクセスする。


<img width="1393" alt="Screen Shot 2019-12-07 at 16.36.22.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/5c0a0bc6-2276-5f42-c595-cbc4f3c447ed.png">


phpMyAdmin を起動できました。

これで、DBもGUIで操作できます。

 

# 次回

SQLサーバーを初期化してみます。

# PS

## ソース
https://github.com/kyorohiro/advent-2019-code-server



