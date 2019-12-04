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

