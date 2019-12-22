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


前回の続きで、flaskを利用して APIを追加していきます。

# 今回の何?
### Terminal は 複数を同時に起動できる

# どんなAPIか決める

以前、作成したflaskを改造してみましょう

```python:main.py
from flask import Flask, request as fl_request, Request
from typing import Dict
import json
import logging

app = Flask(__name__)
logger = logging.getLogger("XXX")
logging.basicConfig(level=logging.DEBUG)

@app.route("/users")
def get_user_from_id():
    request:Request = fl_request
    input:Dict = request.args
    logger.debug("> input: {}".format(input))
    user:Dict = {
        "name":"one",
        "email":"kyorohiro+one@example.com",
        "id":1}
    return json.dumps(user)

app.run("0.0.0.0",port=8080)

```

`http://0.0.0.0/users?id=1` と、IDが渡されたら、そのIDに対応するユーザー情報を返すようにします。

# 動かしてみる

flaskを起動してみます。

```sh

$ python main.py 
 * Serving Flask app "main" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
INFO:werkzeug: * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```

新しく、terminalを開いて、curlコマンドを叩いてみる


```sh
$ curl 127.0.0.1:8080/users?id=1
{"name": "one", "email": "kyorohiro+one@example.com", "id": 1}
```

おっ、ユーザー情報がされました。


# DBからデータを読み込んで表示してみる

pythonから、dbを操作するのに、今回は、dataset package を利用しています。
https://github.com/pudo/dataset


```sh
$ pip install dataset
```

mysqlを利用するので、mysqlclient package を追加します。

```
$ pip install mysqlclient
```

```python:main.py
from flask import Flask, request as fl_request, Request
from typing import Dict
import json
import dataset
import logging

app = Flask(__name__)
logger = logging.getLogger("XXX")
logging.basicConfig(level=logging.DEBUG)

db:dataset.Database = dataset.connect('mysql://root:passwd@mysqld/app_db')

@app.route("/users")
def get_user_from_id():
    request:Request = fl_request
    input:Dict = request.args
    logger.debug("> input: {}".format(input))
    users_table:dataset.Table = db.get_table("users")
    user:Dict = users_table.find_one(id=int(input["id"]))
    return json.dumps(user)

app.run("0.0.0.0", port=8080)

```

`dataset.connect` で、データーベースと接続して、`users_table.find_one` でユーザー情報を取得しています。


# 動かしてみる

flaskを起動してみます。

```sh

$ python main.py 
 * Serving Flask app "main" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
INFO:werkzeug: * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```

新しく、terminalを開いて、curlコマンドを叩いてみる


```sh
$ curl 127.0.0.1:8080/users?id=1
{"name": "one", "email": "kyorohiro+one@example.com", "id": 1}
```

おっ、ユーザー情報がされました。

# PS

requirements.txt を作成しておきましょう!!

pythonのパッケージは、ファイルにまとめておく習慣があります。
https://pip.readthedocs.io/en/1.1/requirements.html

```
pip install -r requirements.txt
```
-r コマンドラインオプションを追加して実行します。

```requirements.txt
Flask==1.1.1
dataset==1.1.2
mysqlclient==1.4.6
```


また、`pip freeze > requirements_lock.txt `とすると、依存しているpackage の一覧をファイルに書き出せます。

# 次回

Flask で、userを追加してみます。
あと、2回くらいででローカル環境篇を終わらせて、オンライン環境篇、魔改造篇に入る予定です。

# PS
ソース
https://github.com/kyorohiro/advent-2019-code-server




