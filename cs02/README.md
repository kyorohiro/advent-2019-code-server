これは、2019年 code-server に Advent Calender の 第2日目の記事です。
[一日目](https://qiita.com/kyorohiro/items/35bab591cd4a6b975c80) の続きです。
今回も、code-server って何だろう?と言う事を解説していきます。


(1) [code-server って何?](https://qiita.com/kyorohiro/items/35bab591cd4a6b975c80)
(2) [Dockerで独自のcode-server 環境を作って見る](https://qiita.com/kyorohiro/items/d991f6fbf77a425525c5)
(3) [VSCode の Plugin を 利用してみる](https://qiita.com/kyorohiro/items/11a13d32c8748f3d7002)
(..) ローカルで、DBなどの環境も含めて構築するには
(..) オンライン上に置くには?
(..) K8Sなどの最近の流行りの環境と連携するには?
(..) Code-Serverを改造して、より良くしたい


# あらすじ

前回は、Hello World!! を動かしてみました。ブラウザー上で動作するVSCodeを確認できたと思います。

実際に触ってみた方は、"/home/coder/project" と dockerを起動したディレトリーブ作成したコードが格納されたと思います


# Docker で独自の環境を作ってみる。

今回は、皆さんがよく使う Linux環境上でCode-Serverを動かしてみましょう。私はUbuntuをよく使うので、Ubuntu上に構築してみたいと思います!!


## まずは、ubuntuを動かしてみましょう

Dockerfile を作成します。

```Dockerfile
FROM ubuntu:20.04
```

ビルドして、Docker上でBashを起動してみましょう

```bash
# cs02 という名前でイメージを作成
$ docker build -t cs02 .

# cs02 上で bash を 起動してみる
$ docker run -it cs02 bash
root@9e2f79078fcd:/#
```

はい、ubuntu を Docker 上で動かせました!!


## code-server を　インストールしてみましょう

https://github.com/cdr/code-server に 記載されている、https://github.com/cdr/code-server/releases のページから最新のものを拾ってきます。

<img width="1044" alt="Screen Shot 2019-12-02 at 0.36.07.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/37cec251-d806-35d2-0023-f30574c91a63.png">

今回は、code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz を利用することにします。

```Dockerfile
FROM ubuntu:20.04
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

# デフォルトは、/works/app で起動するようにする。
CMD [ "/works/code-server", "--allow-http", "--auth", "none", "--port", "8443", "/works/app"]


```

※ dockerの中の ubuntu 上の bash で動作確認しながら、Dockerfileを作成していますが省略しています。


```bash
docker build -t cs02 .
```

## 作成したイメージを起動してみましょう

```bash
# bash などは指定しない
# カレントディレクトリ(絶対パス) と /works/app を mount する
# PCの8443 Portへの接続を Dockerの8443 Port への接続とする
docker run -v "$PWD:/works/app" -p "8443:8443" -it cs02 
```



とした後で、ブラウザーで、http://127.0.0.1:8443/ にアクセスすると、

<img width="1045" alt="Screen Shot 2019-12-02 at 0.57.02.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/4ba70546-1302-d475-ca45-1a11935a8735.png">

VSCode が　立ち上がりました!!


# 次回

作成したImageを配布してみましょう。 一度、作成したImageは、ほぼほぼ、同じ状態で動かす事ができます。

