from peewee import *

db = SqliteDatabase('data/lo.db')

class DBUser(Model):
    id = AutoField(default='')
    email = CharField(default='')
    password = CharField(default='')


    class Meta:
        database = db # This model uses the "people.db" database.