# Code-Server x Dart fmi x Go x Clang

This Article is about Dart ‘s Native Interface. And For This Article, I create a Dockerfile for develop environment which is used code-server.
You can develop a service and a application at Go and C and Dart with fmi at VSCode with auto-complete.


## What is Native Interface

https://dart.dev/guides/libraries/c-interop

Dart’s Native Interface is so useful. By this interface We can use native interface for C ‘s Shared Library At Dart!!

For example. you can use golang library and you can use clang library, to create shared library by those language

## Code-Server ‘s Develop Environment

For this article, I create docker image.

You can use VSCode with auto-complete for clang and golang and dartlang


```
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


*?? if you want to know more info? please check followiing repogitory*

- https://github.com/kyorohiro/my-code-server/tree/master/w/dart_and_go_and_c/
- https://github.com/kyorohiro/advent-2019-code-server/tree/master/extra/dart_fmi_and_go_and_c


## To Start Development env

```
$ git clone https://github.com/kyorohiro/advent-2019-code-server.git
$ cd advent-2019-code-server/extra/dart_fmi_and_go_and_c
$ docker-compose build
$ docker-compose up -d
```

and open *http://127.0.0.1:8443/* at browser

<img width="1191" alt="Screen Shot 2019-12-22 at 20.31.13.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/54192/cca1b1e0-a1c3-cb52-d639-804335854c9c.png">


## To Create Share Library At Go

move to *VSCode->File(Menu)->/app/wgo*


```
package main

import "C"
import "fmt"

//export PrintHello
func PrintHello() {
    fmt.Print("Hello,World")
}

func main() {}
```

in this Article ‘s last, PrintHello function is called by Dart!!

```
$ go build -o libhello.so  -buildmode=c-shared  hello.go
```

then. create *libhello.h* and *libhello.so*

Let’s test this so file at clang

```
#include <stdio.h>
#include "libhello.h"


int main(int argc, char const *argv[])
{
  PrintHello();
  return 0;
}$ gcc -Wall -o main_hello.exe main_hello.c -L. -lhello
$ LD_LIBRARY_PATH=. ./main_hello.exe -L. -lhello
Hello,World
```


Good!!


## To Call This From Dart

move to *VSCode->File(Menu)->/app/wdart*

```
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

```
$ dart ./bin/main.dart
Hello,World
```



# PS

I created Clang environment in my introduced a git hub repository.
Code

https://github.com/kyorohiro/my-code-server/tree/master/w/dart_and_go_and_c/

https://github.com/kyorohiro/advent-2019-code-server/tree/master/extra/dart_fmi_and_go_and_c

