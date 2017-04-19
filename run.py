#-*-coding: utf-8-*-
from settings import app

if __name__ == "__main__":
    app.debug = True
    app.secret_key = 's3cr3t'
    app.run()

