Dart Advent Calendar 2019 の 記事です。

Dart の Native Interface に ついての記事です。
Go や C言語の機能をDartで利用する方法について解説します。また、すぐに Native  Interface を試せるように、 Docker Image を 用意しました。


# Native Interface とは : C言語 の ライブラリーを使用することができる機能です
https://dart.dev/guides/libraries/c-interop

C言語 の ライブラリーを使用することができる機能です。ただし、C言語と言ってもC言語でのライブラリーに閉じたものではないです。

Linux や Mac や Windows や Andoid や iOS は、様々なライブラリの組み合わせでできています。

オブジェクトファイル化されたコードをお互いに利用しあって、アプリやサービスが作られています。 通信機能から、描画機能まで、すべて、オブジェクトファイルの書かれたコードを元に動作しています。

このオブジェクトファイルにアクセスするのが、Native Interface です。特に、Shared Libraryにアクセスすることができます。


# とても便利 : OSの機能をフルに使える

Dartは、まだまだライブラリーが不足している状態です。ですので、C言語で開発されたライブラリーや、Goで開発されたライブラリーを利用する必要があります。
Native Interface によち、 Dart がより便利になります。



# 開発環境 : Docker 環境を用意しました。

Code-Server という VSCode が　オンライン上で動作する エディターを含めました。
このため、 Dockerを起動すれば、即、開発ができます。

https://github.com/kyorohiro/my-code-server/tree/master/w/dart_and_go_and_c/

https://github.com/kyorohiro/advent-2019-code-server/tree/master/extra/dart_fmi_and_go_and_c



```Dockerfile
FROM ubuntu:20.04

WORKDIR /works
# install dart
RUN apt-get update
RUN apt-get install -y wget gnupg1
RUN apt-get install apt-transport-https
RUN sh -c 'wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -'
RUN sh -c 'wget -qO- https://storage.googleapis.com/download.dartlang.org/linux/debian/dart_stable.list > /etc/apt/sources.list.d/dart_stable.list'
RUN apt-get update
RUN apt-get -y install dart

# install go
RUN apt-get install software-properties-common -y
#RUN add-apt-repository ppa:longsleep/golang-backports
RUN apt-get update
RUN apt-get install golang-go -y
RUN apt-get install git -y
RUN go get github.com/ramya-rao-a/go-outline
RUN go get github.com/mdempsky/gocode
RUN go get github.com/uudashr/gopkgs/cmd/gopkgs
RUN go get github.com/sqs/goreturns
RUN go get github.com/rogpeppe/godef

# install c
RUN apt-get install musl-dev -y

# code-server
RUN wget https://github.com/cdr/code-server/releases/download/2.1692-vsc1.39.2/code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz
RUN tar -xzf code-server2.1692-vsc1.39.2-linux-x86_64.tar.gz -C ./ --strip-components 1


RUN /works/code-server --install-extension Dart-Code.dart-code
RUN /works/code-server --install-extension ms-vscode.go
RUN /works/code-server --install-extension ms-vscode.cpptools

WORKDIR /app
ENV PATH=${PATH}:/lib/dart/bin
ENV PATH="${PATH}:/root/.pub-cache/bin"
RUN pub global activate webdev
RUN pub global activate stagehand

CMD ["/works/code-server", "--auth","none", "--host","0.0.0.0","--port","8443", "/app"]

```

```docker-compose.yml
version: '3'
services: 
  app:
    build: ./app
    ports:
     - "8080:8080"
     - "8443:8443"
    volumes: 
      - ./app:/app
    # - /var/run/docker.sock:/var/run/docker.sock
    command: /works/code-server --auth none --host 0.0.0.0 --port 8443 /app 
```


具体的には、github を参照してください。


# 開発環境を起動する。

```
$ git clone https://github.com/kyorohiro/advent-2019-code-server.git
$ cd advent-2019-code-server/extra/dart_fmi_and_go_and_c
$ docker-compose build
$ docker-compose up -d
```

ブラウザーで、`http://127.0.0.1:8443/` を開く

<img width="1191" alt="Screen Shot 2019-12-22 at 20.31.13.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/cca1b1e0-a1c3-cb52-d639-804335854c9c.png">


# Go で Shared Library を 作成する。

`VSCode->File(Menu)->/app/wgo` に移動する。

```go:hello.go
package main

import "C"
import "fmt"

//export PrintHello
func PrintHello() {
	fmt.Print("Hello,World")
}

func main() {}

```

Goの PrintHello 関数を、Dart から呼ばれる予定です。

```
$ go build -o libhello.so  -buildmode=c-shared  hello.go
```
とすると、`libhello.h` と `libhello.so` というファイルができます。
Dart で読み込む前に、C言語から読み込んでみましょう。

```c:main_hello.c
#include <stdio.h>
#include "libhello.h"


int main(int argc, char const *argv[])
{
  PrintHello();
  return 0;
}

```

```bash:Terminal

$ gcc -Wall -o main_hello.exe main_hello.c -L. -lhello
$ LD_LIBRARY_PATH=. ./main_hello.exe -L. -lhello
Hello,World
```

おっ!!  上手く動作しました。

# Dart から読み込んでみる。

`VSCode->File(Menu)->/app/wdart` に移動する。


```dart:bin/main.dart
import 'dart:ffi' as ffi;

typedef PrintHello_func = ffi.Void Function();
typedef PrintHello = void Function();

void main(List<String> arguments) {
  var path = "/app/wgo/libhello.so";
  ffi.DynamicLibrary dylib = ffi.DynamicLibrary.open(path);
  final PrintHello hello = dylib
      .lookup<ffi.NativeFunction<PrintHello_func>>('PrintHello')
      .asFunction();
  hello();
}


```

```bash:Terminal
$ dart ./bin/main.dart
Hello,World
```


# PS

C言語の環境も用意しました。
先ほどの、github レポジトリーから見れます。

---

Go言語で開発された機能をDartでフルに利用できます。ので、Dart から　ほぼなんでも出来る状態になりました。
FMIがサポートされたことで、気軽に Native Interface を書けるようになったと思います。

---

サーバーサイド向けでしたら、今回用意した Docker Image などが便利です。 
今回、使用した Code-Server を使いましたので、
Auto Complete が 使えたりして便利です。

今回 20回以上に分けて解説していますので、興味ある方は、ご参照ください。

https://qiita.com/advent-calendar/2019/code-server

※ Docker Image として固めてHub に 配置するなどすれば、必ず動作するようになりますが、Image には固めていません。個人利用する際は、 Image に固めて保管しておくことをお勧めします。


# Code

https://github.com/kyorohiro/my-code-server/tree/master/w/dart_and_go_and_c/

https://github.com/kyorohiro/advent-2019-code-server/tree/master/extra/dart_fmi_and_go_and_c



