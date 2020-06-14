import html
import uuid
import os
from flask import Flask, request, render_template, make_response, redirect

from peewee import *

db = SqliteDatabase("b.db")


class User(Model):
    id = AutoField()
    username = CharField(unique=True)
    password = CharField()
    token = CharField()

    class Meta:
        database = db


class Note(Model):
    id = AutoField()
    author_id = IntegerField()
    content = TextField()

    class Meta:
        database = db


@db.connection_context()
def initialize():
    db.create_tables([User, Note])
    try:
        Note.create(author_id=0, content=f"here is the flag: {os.getenv('FLAG')}")
    except:
        pass


initialize()


class API:
    @staticmethod
    @db.connection_context()
    def login(username, password) -> str:
        user_objs = User \
            .select() \
            .where(User.username == username)
        if len(user_objs) == 0:
            token = str(uuid.uuid4())
            try:
                User.create(
                    username=username,
                    password=password,
                    token=token,
                )
            except IntegrityError as e:
                print(e)
                return ""
            return token
        user_obj = user_objs[0]
        if user_obj.password != password:
            return ""
        return user_obj.token

    @staticmethod
    @db.connection_context()
    def get_user_detail_by_token(token: str) -> (bool, [int]):
        user_objs = User \
            .select() \
            .where(User.token == token)
        if len(user_objs) == 0:
            return False, 0
        user_obj = user_objs[0]
        _note = Note \
            .select(Note.id) \
            .where(Note.author_id == user_obj.id)
        return True, [x.id for x in _note]

    @staticmethod
    @db.connection_context()
    def add_note(token: str, content: str) -> (bool, str):
        user_objs = User \
            .select() \
            .where(User.token == token)
        if len(user_objs) == 0:
            return False, "Wrong Token"
        user_obj = user_objs[0]

        try:
            Note.create(
                author_id=user_obj.id,
                content=content
            )
        except IntegrityError as e:
            print(e)
            return False, "System error"
        return True, ""

    @staticmethod
    @db.connection_context()
    def get_note_detail(note_id: int) -> (bool, str):
        note_objs = Note \
            .select() \
            .where(Note.id == note_id)
        if len(note_objs) == 0:
            return False, "No such note"
        note_obj = note_objs[0]

        return True, note_obj.content


app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def default():
    if request.method == 'POST':
        token = API.login(request.form["username"], request.form["password"])
        if token:
            resp = make_response(redirect("/"))
            resp.set_cookie("token", token)
            return resp
        else:
            return render_template('login.html',
                                   error_msg="Wrong credential")
        pass
    else:
        token = request.cookies.get("token")

        def go_login():
            return render_template('login.html')

        if token and len(token) > 5:
            is_login, note_ids = API.get_user_detail_by_token(token)
            if not is_login:
                resp = make_response(redirect("/"))
                resp.set_cookie("token", "")
                return resp
            return render_template('home.html', note_ids=note_ids, l=len(note_ids))
        return go_login()


@app.route('/add_note', methods=["POST"])
def add_note():
    token = request.cookies["token"]
    content = request.form["content"]
    is_success, err_message = API.add_note(token, content)
    if is_success:
        return make_response(redirect("/"))
    else:
        return err_message


@app.route('/note/<note_id>', methods=["GET"])
def note(note_id):
    _, content = API.get_note_detail(note_id)
    return render_template("note.html",
                           content=html.escape(content),
                           note_id=html.escape(note_id))


