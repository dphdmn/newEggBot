import base64
import pickle
import zlib

def serialize(obj):
    pickled = pickle.dumps(obj)
    compressed = zlib.compress(pickled)
    result = base64.b64encode(compressed).decode()
    return result

def deserialize(str):
    compressed = base64.b64decode(str.encode())
    pickled = zlib.decompress(compressed)
    result = pickle.loads(pickled)
    return result
