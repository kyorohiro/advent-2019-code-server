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


前回の続きで、flaskを動作させてみます。

# 今回の何?
### Terminalが便利。Bashがオススメ

VSCodeなので、Terminalを利用できます。
Linuxをcliで操作できます。なので、別途sshを立ち上げたり

```
dockeer-compose exec -it app bash
```

などして、別途　Terminalを立ち上げる必要もなくなります。
私は、bashが使いバレているので、最初に

```
bash
```

と入力するようにしています。


# Flaskとは
軽量のWebFrameworkです。超簡単にWebページを作成する事ができます。

https://github.com/pallets/flask


# Flask環境を作成してみよう!!

<img width="1250" alt="Screen Shot 2019-12-05 at 0.55.13.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/893618d8-85f6-7a5f-8653-c8f75098c7f6.png">

前回の続きから初めてみます。


requirements.txt を作成します。

```:requirements.txt
flask
```

コマンドライン上で、

```
pip install -r requirements.txt 
```

コードを書いてみます。

```python:main.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

app.run("0.0.0.0",port=8080)

```

実行してみましょう!!

```bash

$ python main.py 
 * Serving Flask app "main" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```

http://127.0.0.1:8080/ をブラウザーで開くと、Hello,World! と表示されます

<img width="1251" alt="Screen Shot 2019-12-05 at 1.11.23.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/5fd15ad1-8d58-80c8-09b2-6435f6d3888e.png">



# 次回

db の 環境を作成してみます

# PS

## ソース
https://github.com/kyorohiro/advent-2019-code-server

