from bson.objectid import ObjectId
from flask import Flask, render_template, request
from flask import redirect, url_for
from pymongo import MongoClient
from datetime import datetime
import time

client = MongoClient("localhost", 27017)
db = client.dbapp2

from flask import Flask

app = Flask(__name__)


@app.route("/list")
def board_lists():
    datas = db.board.find({})
    return render_template("list2.html", datas=datas)


@app.template_filter("formatdatetime")
def format_datetime(value):
    if value is None:
        return ""
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
        now_timestamp
    )
    value = datetime.fromtimestamp((int(value) / 1000)) + offset
    return value.strftime("%Y-%m-%d %H:%M:%S")


@app.route("/view/<idx>", methods=["GET", "POST"])
def board_view(idx):
    data = db.board.find_one({"_id": ObjectId(idx)})
    return render_template("view2.html", data=data)


@app.route("/write", methods=["GET", "POST"])
def board_write():
    if request.method == "GET":
        return render_template("write2.html")
    else:
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        name = request.form["name"]
        title = request.form["title"]
        contents = request.form["contents"]
        post = {
            "name": name,
            "title": title,
            "contents": contents,
            "pubdate": current_utc_time,
            "view": 0,
        }
        x = db.board.insert_one(post)
        return redirect(url_for("board_view", idx=x.inserted_id))


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
