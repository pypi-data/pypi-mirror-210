from redis import Redis

def connect():
    red = Redis(
        host="mgmt.ebdesk.com",
        port=6379,
        password="r3dis@2o2!",
        db=14
    )
    return red