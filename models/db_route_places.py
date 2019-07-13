from peewee import *

db = SqliteDatabase('data/lo.db')

class DBRoutePlaces(Model):
    id_route = IntegerField(default=0)
    id_place = IntegerField(default=0)


    class Meta:
        database = db # This model uses the "people.db" database.