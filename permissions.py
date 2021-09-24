import os

owner_id = int(os.environ["owner"])

def is_owner(user):
    return user.id == owner_id
