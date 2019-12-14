code-server オンライン篇 (1) オンラインにCode-Serverを配置する

code-serverのオンライン篇に入ります。色々なケースを考えて、オンライン上に
docker-serverを配置してみましょう


第一回目は、ec2上に code-server を配置してみます。

# 準備

aws cli や boto3 を利用してec2インスタンスを立ち上げたいと思います。

まずは、AWS Access Key ID および AWS Secret Access Key を取得してください
https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-chap-configure.html




