import subprocess
from flask import (
    Flask,
    request,
    jsonify
)
from tools import token_required, abort

config = {
    "DEBUG": False
}

app = Flask(__name__)
app.config.from_mapping(config)

@app.route("/test", methods=["GET"])
def revoke():
    return "Ok"

if __name__ == '__main__':
    app.run()