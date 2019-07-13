from peewee import *

from models.db_user import DBUser
from models.db_sessions import DBSessions
from models.db_place import DBPlace
from models.db_route import DBRoute
from models.db_route_places import DBRoutePlaces


try:
    db = SqliteDatabase('data/lo.db')
    db.create_tables([DBUser])
    db.create_tables([DBSessions])
    db.create_tables([DBPlace])
    db.create_tables([DBRoute])
    db.create_tables([DBRoutePlaces])

except Exception as ex:
    pass