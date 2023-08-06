import redis
from datetime import datetime
import socket
import getpass


def logstream(
    redis_port,
    redis_host,
    redis_username,
    redis_password,
    appname="logstream",
    maxlength=None,
    **params,
):
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        username=redis_username,
        password=redis_password,
        decode_responses=True,
    )

    # Identify the user
    user = getpass.getuser()

    # User Profile Key
    userkey = f"{appname}:profile:{user}"

    # App Stream
    streamkey = f"{appname}"

    # Check if the profile already exists for this app,
    # if not, create the profile
    if r.exists(userkey) == 0:
        r.hset(userkey, mapping={"user": user, "counter": 0})

    r.hincrby(userkey, "counter", 1)

    info = {
        "unix_utc_ts": datetime.utcnow().timestamp(),
        "utc_ts": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "appname": appname,
        "user": userkey,
        "host": socket.gethostname(),
    }

    r.xadd(streamkey, {**info, **params}, maxlen=maxlength)
