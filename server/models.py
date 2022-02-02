from sqlite3.dbapi2 import Date

from mongoengine import *
import datetime

def valid_date(date):
    if date > datetime.date.today():
        raise ValidationError("Invalid date.")

class User(Document):
    google_id = StringField()
    email = EmailField()
    name = StringField(max_length=40)
    birth_date = DateField(validation=valid_date)
    admin = BooleanField()

    def __str__(self):
        return self.email

class TreasureInstance(EmbeddedDocument):
    picture_found = StringField(max_length=2083)
    validated = BooleanField(default=False)
    user = ReferenceField(User, required=True)

class Treasure(Document):
    picture = StringField(max_length=2083)
    coordinates = StringField(max_length=1000)
    clue = StringField(max_length=5000)
    instances = ListField(EmbeddedDocumentField(TreasureInstance))

class GameInstance(EmbeddedDocument):
    complete = BooleanField(default=False)
    user = ReferenceField(User, required=True)

class Game(Document):
    title = StringField(max_length=255)
    description = StringField(max_length=5000)
    picture = StringField(max_length=2083)
    location = StringField(max_length=1000)
    restart_date = DateField()
    #coordinates = ListField(FloatField)
    instances = ListField(EmbeddedDocumentField(GameInstance))
    treasures = ListField(ReferenceField(Treasure))
    creator = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    active = BooleanField(default=True)
    winner = ReferenceField(User, required=False, null=True)

class Message(EmbeddedDocument):
    message = StringField()
    date_sent = DateTimeField()
    read = BooleanField()
    sender = ReferenceField(User, required=False)

class Chat(Document):
    user1 = ReferenceField(User, required=False)
    user2 = ReferenceField(User, required=False)
    messages = ListField(EmbeddedDocumentField(Message))


