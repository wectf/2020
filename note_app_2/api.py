import os
import uuid
from peewee import *

########################################
# Nothing should be wrong in this file #
########################################

db = SqliteDatabase("core.db")


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

# save the flag
@db.connection_context()
def initialize():
    db.create_tables([User, Note])
    try:
        User.create(username="admin", password=os.getenv("PASSWORD"), token=os.getenv("PASSWORD"))
        Note.create(author_id=1, content=f"here is the flag: {os.getenv('FLAG')}")
    except:
        pass


initialize()


class API:
    @staticmethod
    @db.connection_context()
    def auth(username, password) -> str:
        # taking in username and password, if not registered, then registered, otherwise compare with the associated
        # password. a token of form UUID-UUID is returned to authenticate user.
        user_objs = User \
            .select() \
            .where(User.username == username)
        if len(user_objs) == 0:
            token = f"{str(uuid.uuid4())}-{str(uuid.uuid4())}"
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
        # return (is token provided correct, [IDs of notes of the user associated to the token])
        user_objs = User \
            .select() \
            .where(User.token == token)
        if len(user_objs) == 0:
            return False, []
        user_obj = user_objs[0]
        _note = Note \
            .select(Note.id) \
            .where(Note.author_id == user_obj.id).limit(50) # 50 is enough my darling
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
    def get_note_detail(token: str, note_id: int) -> (bool, str):
        # get note by its ID
        user_objs = User \
            .select() \
            .where(User.token == token)
        if len(user_objs) == 0:
            return False, "Wrong Token"
        user_obj = user_objs[0]
        note_objs = Note \
            .select() \
            .where(Note.id == note_id, Note.author_id == user_obj.id)
        if len(note_objs) == 0:
            return False, "No such note or no enough privileges"
        note_obj = note_objs[0]
        return True, note_obj.content
