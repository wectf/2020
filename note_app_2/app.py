import uuid
from flask import Flask, request, render_template, make_response, redirect
from api import API

app = Flask(__name__)


def go_login():
    resp = make_response(redirect("/"))
    resp.set_cookie('token', '', expires=0)
    return resp


@app.route('/', methods=["GET", "POST"])
def default():
    # check whether users are logged in
    token = request.cookies.get("token")
    if token and len(token) > 5:
        # get user notes and in the mean time check correctness of the token
        is_login, note_ids = API.get_user_detail_by_token(token)
        if not is_login:
            # redirect to login page and clear cookies
            resp = make_response(redirect("/"))
            resp.set_cookie("token", "")
            return resp
        return render_template('home.html', note_ids=note_ids, l=len(note_ids), token=token)
    # if it is post req, then it is our precious user trying to login or register
    if request.method == 'POST':
        token = API.auth(request.form["username"], request.form["password"])
        if token:
            # success
            resp = make_response(redirect("/"))
            resp.set_cookie("token", token)
            return resp
        else:
            return render_template('login.html',
                                   error_msg="Wrong credential")
        pass
    else:
        # it is a get request and no correct token provided
        return render_template("login.html")


@app.route('/add_note', methods=["POST"])
def add_note():
    # prevent csrf
    token = request.cookies["token"]
    xsrf = request.form["xsrf"]
    if token != xsrf:
        return "Hi Hacker"
    content = request.form["content"]
    is_success, err_message = API.add_note(token, content)
    if is_success:
        return make_response(redirect("/"))
    else:
        return err_message


@app.route('/note/<note_id>', methods=["GET"])
def note(note_id):
    token = request.cookies["token"]
    _, content = API.get_note_detail(token, note_id)
    return render_template("note.html",
                           content=content,
                           note_id=note_id)


@app.route("/logout", methods=["POST"])
def logout():
    return go_login()

