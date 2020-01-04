from server.server_main import app, setup

if __name__ == "__main__":
    setup()
    app.run(host="0.0.0.0",port=8080,threaded=True)
