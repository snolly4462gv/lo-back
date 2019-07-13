from peewee import *

db = SqliteDatabase('data/lo.db')

class DBSessions(Model):
    id = IntegerField(default='')
    token = CharField(default='')


    class Meta:
        database = db # This model uses the "people.db" database.