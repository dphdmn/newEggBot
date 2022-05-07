import os
from helper import serialize
from database import db

owner_id = int(os.environ["owner"])

def is_owner(user):
    return user.id == owner_id

def is_egg_admin(user):
    key = "permissions/egg_admin"

    if key not in db:
        db[key] = serialize.serialize([owner_id])

    admins = serialize.deserialize(db[key])
    return user.id in admins
