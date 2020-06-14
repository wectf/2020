import datetime
import uuid
from peewee import *
import os
#################################################################################################
# Nothing should be wrong in this file, only here to give you a picture of how everything works #
#################################################################################################
db = SqliteDatabase("data.db")


class User(Model):
    id = AutoField()
    username = CharField(unique=True)
    # user_type can be [Admin, Flag Viewer, Normal User]
    # Admin can promote user to a flag viewer and do whatever they want
    # Flag Viewer can view the flag obviously
    # Normal User can do nothing
    user_type = CharField()
    password = CharField()
    token = CharField()

    class Meta:
        database = db


@db.connection_context()
def initialize():
    db.create_tables([User])
    try:
        User.create(
            username="admin",
            user_type="Admin",
            password=os.getenv("ADMIN_PASSWORD"),
            token=os.getenv("ADMIN_PASSWORD")
        )
    except:
        pass


initialize()


class API:
    @staticmethod
    @db.connection_context()
    def auth(username, password) -> str:
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
                    user_type="Normal User",
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
    def is_admin(token: str) -> (bool, str):
        user_objs = User \
            .select() \
            .where(User.token == token)
        if len(user_objs) == 0:
            return False, "Wrong Token"
        user_obj = user_objs[0]
        if user_obj.user_type == "Admin":
            return True, ""
        return False, "Not Admin..."

    @staticmethod
    @db.connection_context()
    def is_flag_viewer(token: str) -> (bool, str):
        user_objs = User \
            .select() \
            .where(User.token == token)
        if len(user_objs) == 0:
            return False, "Wrong Token"
        user_obj = user_objs[0]
        if user_obj.user_type == "Flag Viewer":
            return True, ""
        return False, "Not flag viewer..."

    @staticmethod
    @db.connection_context()
    def promote_user_to_flag_viewer(token: str, user_token: str) -> (bool, str):
        is_admin, err_message = API.is_admin(token)
        if not is_admin:
            return False, err_message
        User\
            .update(user_type="Flag Viewer")\
            .where(User.token == user_token)\
            .execute()
        return True, ""
