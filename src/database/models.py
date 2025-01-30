from peewee import *
import datetime

db = SqliteDatabase('autojs.db')

class BaseModel(Model):
    class Meta:
        database = db

class Device(BaseModel):
    device_id = CharField(unique=True)
    device_name = CharField(null=True)
    last_connected = DateTimeField(default=datetime.datetime.now)

class Script(BaseModel):
    name = CharField()
    path = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)
    description = TextField(null=True)

class ExecutionLog(BaseModel):
    script = ForeignKeyField(Script, backref='logs')
    device = ForeignKeyField(Device, backref='logs')
    start_time = DateTimeField(default=datetime.datetime.now)
    end_time = DateTimeField(null=True)
    status = CharField()  # success/failed
    log_content = TextField() 