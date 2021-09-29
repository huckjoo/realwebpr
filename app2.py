from main import *


@app.route("/delete_comments", methods=["POST"])
def delete_comments():
    id = request.form["id"]
    db.comments.delete_one({"_id": ObjectId(id)})
    return jsonify(result="success")


@app.route("/comment_list/<root_id>")
def comment_list(root_id):
    comments = db.comments.find({"root_id": str(root_id)}).sort("pubdate", -1)
    comment_list = []
    for c in comments:
        comment = {
            "id": str(c.get("_id")),
            "name": c.get("name"),
            "comment": c.get("comment"),
            "root_id": c.get("root_id"),
            "pubdate": filter.format_datetime(c.get("pubdate")),
        }
        comment_list.append(comment)

    return jsonify(response="success", lists=comment_list)


@app.route("/list")
def board_lists():

    # 페이지 값(default=1)
    page = request.args.get("page", 1, type=int)
    # 한페이지당 몇개의 게시물을 출력할지
    limit = request.args.get("limit", 7, type=int)
    datas = db.board.find({}).skip((page - 1) * limit).limit(limit).sort("pubdate", -1)
    # 게시물의 총 개수
    tot_count = db.board.find({}).count()
    # 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / limit)
    # 페이지 블럭 5개씩 표기
    block_size = 5
    # 현재 블럭 위치
    block_num = int((page - 1) / block_size)
    # 블럭의 시작 위치
    block_start = int((block_size * block_num) + 1)
    # 블럭의 끝 위치
    block_last = math.ceil(block_start + (block_size - 1))

    return render_template(
        "list2.html",
        datas=datas,
        limit=limit,
        page=page,
        block_start=block_start,
        block_last=block_last,
        last_page_num=last_page_num,
    )


@app.route("/comments", methods=["POST"])
def board_comments():
    name = request.form["name"]
    comment = request.form["comment"]
    root_id = request.form["root_id"]
    current_utc_time = round(datetime.utcnow().timestamp() * 1000)
    post = {
        "name": name,
        "comment": comment,
        "root_id": str(root_id),
        "pubdate": current_utc_time,
    }
    db.comments.insert_one(post)
    return redirect(url_for("board_view", idx=root_id))


@app.route("/delete/<idx>", methods=["GET", "POST"])
def delete(idx):
    db.board.delete_one({"_id": ObjectId(idx)})
    return redirect(url_for("board_lists", idx=idx))


@app.route("/edit/<idx>", methods=["GET", "POST"])
def edit(idx):
    if request.method == "GET":
        data = db.board.find_one({"_id": ObjectId(idx)})
        return render_template("edit2.html", data=data)
    else:
        name = request.form["name"]
        title = request.form["title"]
        contents = request.form["contents"]
        db.board.update_one(
            {"_id": ObjectId(idx)},
            {"$set": {"name": name, "title": title, "contents": contents}},
        )
        return redirect(url_for("board_view", idx=idx))


@app.route("/view/<idx>", methods=["GET", "POST"])
def board_view(idx):
    if request.method == "GET":
        page = request.args.get("page")
        # data = db.board.find_one({"_id": ObjectId(idx)})
        data = db.board.find_one_and_update(
            {"_id": ObjectId(idx)},
            {"$inc": {"view": 1}},
            return_document=True,
        )  # return_document=True는 적용된 후에 data를 받는것을 의미
        if data is not None:
            result = {
                "id": data.get("_id"),
                "name": data.get("name"),
                "title": data.get("title"),
                "contents": data.get("contents"),
                "pubdate": data.get("pubdate"),
                "view": data.get("view"),
            }
        return render_template("view2.html", result=result, page=page)


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
