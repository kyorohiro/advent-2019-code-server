これは、2019年 code-server に Advent Calender の 第3日目の記事です。
2日目 の続きです。
今回も、code-server って何だろう?と言う事を解説していきます。


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



# code-server は vscode の plugin が利用できます。

vscode の plugin を利用できます。オートコンプリート などの 補助機能やリファクタリング機能を利用して、お手軽にプログラムを書けるようになります。


python で、作成してみます。


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

ubuntu に python を　インストールしても良かったのですが、公式の python image を、利用しています。

RUN /works/code-server --install-extension として、 python 向けの plugin を インストールしています。

PYTHONPATH を指定して、ルートフォルダーをしてしています。



# 試してみる

```bash
docker build -t cs03 .
docker run -v "$PWD:/works/app" -p "8443:8443" -it cs03  
```

ブラウザーを開いて、何か書く

<img width="1246" alt="Screen Shot 2019-12-03 at 5.39.02.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/811dc6cb-591b-4a71-e550-4c0e131504a1.png">


お、補完が効いていますね!!


# 次回

作成したImageを配布してみましょう。 一度、作成したImageは、ほぼほぼ、同じ状態で動かす事ができます。


# PS

## ソース
https://github.com/kyorohiro/advent-2019-code-server


