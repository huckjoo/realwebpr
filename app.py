from bson.objectid import ObjectId
from flask import Flask, render_template
from flask import request
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
from flask import abort, redirect, url_for
import time


app = Flask(__name__)
# flask-pymongo사용법
app.config["MONGO_URI"] = "mongodb://localhost:27017/dbapp2"
mongo = PyMongo(app)


@app.route("/list")
def lists():
    board = mongo.db.board
    datas = board.find({})
    return render_template("list.html", datas=datas)


# flask에서 제공되는 filter
@app.template_filter("formatdatetime")
def format_datetime(value):  # value를 시간값으로 받는다.
    if value is None:
        return ""
    now_timestamp = time.time()  # 게시물을 작성하는 사람 시간
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
        now_timestamp
    )
    value = datetime.fromtimestamp(int(value) / 1000) + offset  # milisecond로 다시변경
    return value.strftime("%Y-%m-%d %H:%M:%S")


@app.route("/view/<idx>")
def board_view(idx):
    # /view?idx=id값&a=10&b=20에서 값을 뽑아오는 방법
    if idx is not None:
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})
        if data is not None:
            result = {
                "id": data.get("_id"),
                "name": data.get("name"),
                "title": data.get("title"),
                "contents": data.get("contents"),
                "pubdate": data.get("pubdate"),
                "view": data.get("view"),
            }
            return render_template("view.html", result=result)
    return abort(404)


@app.route("/write", methods=["GET", "POST"])
def board_write():
    if request.method == "POST":
        name = request.form["name"]
        title = request.form["title"]
        contents = request.form["contents"]
        # 시간은 가공하기 쉬운 상태로 db에 저장해놔야함
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        board = mongo.db.board
        post = {
            "name": name,
            "title": title,
            "contents": contents,
            "pubdate": current_utc_time,
            "view": 0,
        }
        x = board.insert_one(post)  # x에 저장하고 나중에 inserted_id를 이용해 idx값 뽑아낸다.
        return redirect(
            url_for("board_view", idx=x.inserted_id)
        )  # board_view()함수가 있는 url로 redirect
    else:
        return render_template("write.html")


# entry point(진입점)
if __name__ == "__main__":  # app.py가 직접 실행되면 아래가 실행됨
    # 만약 app.py가 어떤 파일의 모듈로서 실행되면 아래는 실행되지 않음
    app.run("0.0.0.0", debug=True)
    # debug 옵션을 true로 주지 않으면 서버를 수정하면 항상 서버를 껐다가
    # 다시 켜야되는 귀찮음을 감수해야 한다.
    # 0.0.0.0은 외부에서도 접속 가능한 상태를 만들어주는 옵션
