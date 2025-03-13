import datetime
import os

def timeshit(iso):
    time = datetime.datetime.fromisoformat(str(iso))
    unixTimestamp = int(time.timestamp())
    return unixTimestamp

def makeToken(sub: str, roles: list, scopes: list):
    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=int(os.getenv("JWT_EXP")))# ik utcnow is deprecated
    exptime = timeshit(exp)
    time = timeshit(datetime.datetime.utcnow())
    jwtD = {
        "exp": exptime,
        "iss": "https://auth.rec.net/",
        "client_id": "recnet",
        "role": roles,
        "sub": sub,
        "auth_time": time,
        "idp": "local",
        "iat": time,
        "scope": scopes,
        "amr": [
            "pwd"
        ]
    }
    return jwtD