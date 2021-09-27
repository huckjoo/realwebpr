from flask import Flask, render_template
from flask import request
from flask_pymongo import PyMongo

from datetime import datetime

app = Flask(__name__)
# flask-pymongo사용법
app.config["MONGO_URI"] = "mongodb://localhost:27017/realweb"
mongo = PyMongo(app)


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
        x = board.insert_one(post)
        print(x.inserted_id)
        return str(x.inserted_id)
    else:
        return render_template("write.html")


# entry point(진입점)
if __name__ == "__main__":  # app.py가 직접 실행되면 아래가 실행됨
    # 만약 app.py가 어떤 파일의 모듈로서 실행되면 아래는 실행되지 않음
    app.run("0.0.0.0", debug=True)
    # debug 옵션을 true로 주지 않으면 서버를 수정하면 항상 서버를 껐다가
    # 다시 켜야되는 귀찮음을 감수해야 한다.
    # 0.0.0.0은 외부에서도 접속 가능한 상태를 만들어주는 옵션
