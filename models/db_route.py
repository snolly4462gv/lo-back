from peewee import *

db = SqliteDatabase('data/lo.db')

class DBRoute(Model):
    id = AutoField()
    title = CharField(default='')
    description = CharField(default='')
    total_places = DoubleField(default=0)
    image = TextField(default='')


    class Meta:
        database = db # This model uses the "people.db" database.