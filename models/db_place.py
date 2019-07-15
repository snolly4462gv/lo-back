from peewee import *

db = SqliteDatabase('data/lo.db')

class DBPlace(Model):
    id = AutoField()
    title = CharField(default='')
    description = CharField(default='')
    lat = DoubleField(default=0)
    lng = DoubleField(default=0)
    image = TextField(default='')
    type = TextField(default='')


    class Meta:
        database = db # This model uses the "people.db" database.