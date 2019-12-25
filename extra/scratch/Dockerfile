FROM ubuntu:20.04

WORKDIR /works
RUN apt-get update
RUN apt-get install -y wget gnupg1
RUN apt-get install git -y
RUN apt-get install npm -y
# code-server
RUN wget https://github.com/cdr/code-server/releases/download/2.1692-vsc1.39.2/code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz
RUN tar -xzf code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz -C ./ --strip-components 1

WORKDIR /app

CMD ["/works/code-server", "--auth","none", "--host","0.0.0.0","--port","8443", "/app"]

# https://marketplace.visualstudio.com/items?itemName=nodesource.vscode-for-node-js-development-pack
