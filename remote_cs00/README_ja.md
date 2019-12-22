　これは、2019年 code-server に Advent Calender の 第12日目の記事です。
　第一日目の [code-server って何?](https://qiita.com/kyorohiro/items/35bab591cd4a6b975c80) にて、ローカル環境にて、Docker や Docker-Compose を利用してVSCodeを内蔵する開発環境作成していきました。
　本日より、オンライン篇に入ります。オンライン篇では、クラウド上にInstanceを立ち上げて、そこに、Code-Server を配置していきます。
　これにより、どこからでも開発リソースにアクセスできるようになりますし。とても高価なマシーン短期間だけ利用してアレコレしたり、
 iPad などを利用して外出時もプログラムが書けるようになります。


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


# EC2 Instance を 立ち上げてみよう

 どの環境を利用しようか迷ったのですが、オーソドックスに AWS を利用する事にしました。
 AWSには、Dockerを利用したサービスがあります。ローカル篇で学習したComposeファイルをそのままリリースに使用できたり。K8Sを利用した今時な方法を利用したりできます。
 が、今回は、EC2 Instaceを立ち上げるところから始めてみたいと思います。



# Boto3 を使います
AWS 上に Instanceを立ち上げる方法は、いくつかあります。
- 主導でGUI コンソールを操作しておこなう
- CloudFormation や Terraform などの構成管理ツールを利用して行う
- AWS CLI を利用してコマンドラインから行う
- AWS SDK を利用してプログラムから行う

構成管理ツールを使うのがスタンダードだと思います。がBoto3でゴリゴリ書いていきたいと思います。

※ ただの私の好みです。


# ACCESS KEYを取得しよう。
SDKから利用するためには、ACCESS KEY ID と SECRET KEY を取得する必要があります。

https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-chap-configure.html

に記載の通り

```
1. AWS マネジメントコンソール にサインインし、IAM コンソール（https://console.aws.amazon.com/iam/）を開きます。

2. ナビゲーションペインで [Users] を選択します。

3. アクセスキーを作成するユーザー名を選択し、[Security credentials] タブを選択します。

4. [Access keys (アクセスキー)] セクションで、[Create access key (アクセスキーの作成)] を選択します。

5. 新しいアクセスキーペアを表示するには、[Show] を選択します。このダイアログボックスを閉じた後、シークレットアクセスキーに再度アクセスすることはできません。認証情報は以下のようになります。

アクセスキー ID: AKIAIOSFODNN7EXAMPLE

シークレットアクセスキー: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```


# AWSの操作する開発環境を用意する。

今までに作成したDockerがそのまま利用できます。

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
RUN apt-get install groff -y

# デフォルトは、/works/app で起動するようにする。
CMD [ "/works/code-server", "--allow-http", "--auth", "none", "--port", "8443", "/works/app"]

```

同じですね!! docker-composeも含めた環境を以下におきました。

https://github.com/kyorohiro/advent-2019-code-server/tree/master/remote_cs01/for_aws 

requirements.txt が変わります

```
awscli==1.16.300
boto3==1.10.36
botocore==1.13.36
boto3-type-annotations==0.3.1
rope==0.14.0
```

# 立ち上げてみましょう

```bash
$ docker-compose build
$ docker-compose up -d
```

# VSCode を開いてみましょう

`http://127.0.0.1:8443/` をブラウザーで開いてみます。

<img width="1159" alt="Screen Shot 2019-12-17 at 0.28.58.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/07f27313-b397-cd8b-a5e7-f0b0ee125e64.png">


# ACCESS KEY ID と SECRET KEY を設定しよう

VSCodeのターミナルを開いて、aws cli を install

```
$ pip install -r requirements.txt 
```

AWS コマンドの設定をします。ACCESS KEY ID と SECRET KEY を追加してください。
regionは TOKYOを利用したい場合は、`ap-northeast-1` を指定してください

```
$ aws configure
AWS Access Key ID [None]: xxxx
AWS Secret Access Key [None]: xxxxx
Default region name [None]: ap-northeast-1
Default output format [None]: json
```


# AWS CLI コマンドを叩いてみる

```
$ aws ec2 describe-instances
```

※ もしかしたら、`apt-get install groff -y` が必要かも


# 次回

Boto3 を利用してInstance を生成/削除をしてみます。


# コード

https://github.com/kyorohiro/advent-2019-code-server/tree/master/remote_cs01



