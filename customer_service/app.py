import os
from flask import Flask, request, render_template, make_response, redirect
from api import API


app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def default():
    if request.method == 'POST':
        # login / register
        token = API.auth(request.form["username"], request.form["password"])
        if token:
            # success then proceed to homepage with token
            resp = make_response(redirect("/"))
            resp.set_cookie("token", token)
            return resp
        else:
            # failed : (
            return render_template('login.html',
                                   error_msg="Wrong credential")
        pass
    else:
        token = request.cookies.get("token")

        def go_login():
            return render_template('login.html')

        if token and len(token) > 5:
            # logged in
            is_fv, err_message = API.is_flag_viewer(token)
            if not is_fv:
                if err_message == "Wrong Token":
                    # hacker
                    resp = make_response(redirect("/"))
                    resp.set_cookie("token", "")
                    return resp
                # not a flag viewer
                return render_template('home.html', no_flag=True)
            # flag viewer
            return render_template('home.html', no_flag=False, flag=os.getenv("FLAG"))
        # not logged in
        return go_login()


@app.route('/promote', methods=["POST"])
def promote():
    token = request.cookies["token"]
    user_token = request.form["user_token"]
    is_success, err_message = API.promote_user_to_flag_viewer(token, user_token)
    if is_success:
        return make_response(redirect("/"))
    else:
        return err_message

