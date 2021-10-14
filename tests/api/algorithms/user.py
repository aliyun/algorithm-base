from ab.utils.algorithm import algorithm
from ab.services import user

@algorithm('user')
def current_user():
    return user.get_current_user(required=False)
