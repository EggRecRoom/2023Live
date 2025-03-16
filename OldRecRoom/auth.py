import datetime
import os
import jwt
import json

from . import coolStuff

dbPath = "db\\"

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
            "cached_login"
        ]
    }
    refreshExp = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    refreshExptime = timeshit(refreshExp)
    refresh_tokenData = {
        "exp": refreshExptime,
        "iss": "https://auth.rec.net/",
        "sub": sub,
        "auth_time": time,
        "iat": time,
    }
    access_token = jwt.encode(payload=jwtD, key=os.getenv("JWT_KEY"))
    refresh_token = jwt.encode(payload=refresh_tokenData, key=os.getenv("JWT_KEY"))
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "key":""
    }
    return data


def makeLogin(account_id: int, platform: int, platform_id: str, device_class: int, device_id: str, info):
    with open(f"{dbPath}accounts.json", encoding="utf8") as f:
        players = json.load(f)
    with open(f"{dbPath}auth\\cachedlogins.json") as f:
        cachedlogins = json.load(f)
    login = False
    for cachedlogin in cachedlogins:
        if cachedlogin["platform"] == platform:
            if cachedlogin["platformId"] == platform_id:
                if cachedlogin["accountId"] == account_id:
                    login = True
    if not login:
        return {
            "error_description":"",
            "error": "No cached login"
        }
    for player in players:
        if account_id == player["accountId"]:
            print(device_id)
            if not device_id in player["deviceIds"]:
                print("yay")
                return {
                    "error_description":"",
                    "error": "Femboy"
                }
            
            with open(f"{dbPath}heartbeat.json") as f:
                heartbeats = json.load(f)
            for heartbeat in heartbeats:
                if heartbeat["playerId"] == int(account_id):
                    #print(info)
                    heartbeat.update({
                        "lastOnline": coolStuff.getCurrentTime(),
                        "appVersion": info.get("ver"),
                        "platform": int(platform),
                        "deviceClass": int(device_class)
                    })
                    with open(f"{dbPath}heartbeat.json", "w") as f:
                        json.dump(heartbeats, f, indent=2)
            roles = ["gameClient"]
            if player["canUseScreenShare"]:
                roles.append("screenshare")
            if player["isModerator"]:
                roles.append("moderator")
            if player["isDeveloper"]:
                roles.append("developer")
            if player["canUseKeepsakes"]:
                roles.append("keepsake")
            scopes = [
                ""
            ]

            authToekn = makeToken(str(account_id), roles, scopes)
            
            return {
                "access_token": authToekn["access_token"],
                "error_description": "",
                "error": "",
                "refresh_token": authToekn["refresh_token"],
                "key": authToekn["key"]
            }
    return {
        "error_description":"",
        "error": "Femboy yay"
    }