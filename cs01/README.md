これは、2019年 code-server に Advent Calender の 第1日目の記事です。
第一日目の記事という事で、code-server って何という事を書こうかと考えています。

ただ、この Advent Calender の 書く側の登録者も少ないので、code-server とは　何かということを、この Advent Calendar を通して、紹介していければと思います。

来年の3月に時間が取れるので、最悪、そのくらいまでに、のんびりと書こうと思います。


(1) [code-server って何?](https://qiita.com/kyorohiro/items/35bab591cd4a6b975c80)
(2) [Dockerで独自のcode-server 環境を作って見る](https://qiita.com/kyorohiro/items/d991f6fbf77a425525c5)
(3) [VSCode の Plugin を 利用してみる](https://qiita.com/kyorohiro/items/11a13d32c8748f3d7002)
(..) ローカルで、DBなどの環境も含めて構築するには
(..) オンライン上に置くには?
(..) K8Sなどの最近の流行りの環境と連携するには?
(..) Code-Serverを改造して、より良くしたい



# 何とか何か?
 Advent Calender の 10日分くらいを費やして紹介していくわけです。が、もちろん書く事はたくさんあります。
　まずは、「何?」という問いは難しいもので、これだけだと、多くのQuestionを内包しています。例えば、「何をするものなのか」、「何ができるのか」、「どのように使えるのか」など、答えたい事はいくつもあります。

- ローカルで、開発環境を構築するには
- 開発環境を共有するには?
- ローカルで、DBなどの環境も含めて構築するには
- オンライン上に置くには?
- K8Sなどの最近の流行りの環境と連携するには?
- Code-Serverを改造して、より良くしたい
- Pluginとかも追加したい

などなど、そういった事を手軽出来るようになってもらいます。

※ 基本的には、Coder の Introduction を 10回以上に分けて、ゆっくりと紹介していくイメージで進めます。https://coder.com/docs/introduction




# 第一日目は、[Hello World](https://ja.wikipedia.org/wiki/Hello_world)!!


## リモートサーバーで動作するVSCodeエディター
Code-Server とは何かを機能面で言うならば、リモートサーバー上で動作するVSCodeエディターです。Codeder (https://github.com/cdr/) によって開発されています。

サーバー側でcode-serverを起動して、ブラウザーからVSCodeを利用することができるようになります。

VSCodeは、program の 開発をサポートする Plugin  が沢山用意されており
https://marketplace.visualstudio.com/VSCode

- Autocomplete 機能 
- リファクタリング機能

などなど、各言語で利用可能です。また、ブラウザー上でVSCodeが動作するので、
使い慣れた Linux 構築した開発環境をあらゆるPFで利用できます

- Windows
- Mac
- iPad
- Android

また、本番環境がLinuxの場合、本番環境と開発環境とで差異がなくなるわけですから、PFの違いによる問題などが出にくくなります。


## Hello、World!!
※ Docker 環境が必要です!!

では、とりあえず、動かしてみましょう。
https://github.com/cdr/code-server 
の README.md を参考に 

```bash
docker run -it -p 127.0.0.1:8080:8080 -v "${HOME}/.local/share/code-server:/home/coder/.local/share/code-server" -v "$PWD:/home/coder/project" codercom/code-server:v2
```

<img width="1190" alt="Screen Shot 2019-12-01 at 2.00.32.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/e304f0cd-d730-4844-e265-c0e5531b1763.png">


<img width="1129" alt="Screen Shot 2019-12-01 at 2.01.30.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/178f5265-5c06-b62d-369c-06053d3bdab6.png">

<img width="1130" alt="Screen Shot 2019-12-01 at 2.02.08.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/5e1a6cc1-0588-5f1f-a5ac-e07833ad1c52.png">


## 次回

Dockerで独自の環境を作ってみましょう。


