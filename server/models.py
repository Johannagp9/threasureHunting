from mongoengine import *

class User(Document):
    name = BooleanField()

class TreasureInstance(Document):
    picture_found = StringField(max_length=2083)
    validate = BooleanField()

class Treasure(Document):
    picture = StringField(max_length=2083)
    coordinates = StringField(max_length=1000)
    clue = StringField(max_length=5000)
    instances = ListField(EmbeddedDocumentField(TreasureInstance))

class GameInstance(EmbeddedDocument):
    complete = BooleanField()
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)

class Game(Document):
    title = StringField(max_length=255)
    description = StringField(max_length=5000)
    picture = StringField(max_length=2083)
    coordinates = StringField(max_length=1000)
    instances = ListField(EmbeddedDocumentField(GameInstance))
    treasures = ListField(EmbeddedDocumentField(Treasure))
    creator = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    active = BooleanField()
    winner =  ReferenceField(User, required=False)

class Message(EmbeddedDocument):
    message = StringField()
    sender = BooleanField()
    date = DateTimeField()

class Chat(Document):
    sender = ReferenceField(User, required=True)
    receiver = ReferenceField(User, required=True)
    messages = ListField(EmbeddedDocumentField(Message))
