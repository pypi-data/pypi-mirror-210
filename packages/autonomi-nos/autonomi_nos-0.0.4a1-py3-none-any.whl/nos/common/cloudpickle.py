import pickle as cloudpickle
from typing import Any


def dumps(obj: Any):
    return cloudpickle.dumps(obj, protocol=4)


def loads(obj: Any):
    return cloudpickle.loads(obj)
