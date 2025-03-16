from flask import Flask, request, jsonify, send_file, redirect, make_response, url_for, render_template, Response, abort, session
from flask_sock import Sock
from flask_cors import CORS
import asyncio
import functools
import json
import requests
import random
import colorama
import datetime
from colorama import Fore
import os
import threading
import time
import base64
import sys
from enum import Enum
import jwt
from dotenv import load_dotenv
from functools import wraps
import uuid

from OldRecRoom import auth, account_API, Logger, items_API, websocket, coolStuff, enums, room_API

load_dotenv()

dbPath = "db\\"

name = f"{__name__}.py"

DefaultAvatar = items_API.getDefaultAvatar()

debug = True

def Results(list: list):
    return {"Results": list, "TotalResults": len(list)}

def NeedToken(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        bearerToken = request.headers.get("Authorization")
        if bearerToken is None:
            return abort(401)
        if not bearerToken.startswith("Bearer "):
            return abort(401)
        token = bearerToken.split("Bearer ")[1]
        try:
            tokenData = jwt.decode(jwt=token, key=os.getenv("JWT_KEY"), algorithms="HS256")
        except:
            return abort(401)

        return func(*args, **kwargs, playerId=int(tokenData["sub"]))
    return decorated

def CanUseToken(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        bearerToken = request.headers.get("Authorization")
        if bearerToken is None:
            return func(*args, **kwargs, playerId=0)
        if not bearerToken.startswith("Bearer "):
            return func(*args, **kwargs, playerId=0)
        token = bearerToken.split("Bearer ")[1]
        try:
            tokenData = jwt.decode(jwt=token, key=os.getenv("JWT_KEY"), algorithms="HS256")
        except:
            return func(*args, **kwargs, playerId=0)

        return func(*args, **kwargs, playerId=int(tokenData["sub"]))
    return decorated

def NeedLoginLock(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        LoginLock = request.form.get("LoginLock")
        if LoginLock is None:
            return "LoginLock", 400
        try:
            uuidOBJ = uuid.UUID(LoginLock, version=4)
        except ValueError:
            return "LoginLock", 400
        return func(*args, **kwargs)
    return decorated

def NeedBestHttp(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        return func(*args, **kwargs)
    return decorated

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
sock = Sock(app)
CORS(app)

@app.errorhandler(500)
def q405(e):
    data = {"Message":"An error has occurred."}
    return jsonify(data), 500


@app.route("/debug/kick/all", methods=["GET"])
def test():
    websocket.sendToAllPlayers(websocket.makeNotification(websocket.MessageTypes2.ModerationQuitGame, {}))
    return "Done kicked all players"

@app.route("/api/versioncheck/v4", methods=["GET"])
def apiversioncheckv4():
    return jsonify({"VersionStatus":0})

@app.route("/api/config/v1/amplitude", methods=["GET"])
def apiconfigv1amplitud():
    return jsonify({
          "AmplitudeKey": "e1693a1003671058b6abc356c8ba8d59",
          "UseRudderStack": True,
          "RudderStackKey": "23NiJHIgu3koaGNCZIiuYvIQNCu",
          "UseStatSig": True,
          "StatSigKey": "client-SBZkOrjD3r1Cat3f3W8K6sBd11WKlXZXIlCWj6l4Aje",
          "StatSigEnvironment": 0
        }
    )

@app.route("/api/gameconfigs/v1/all", methods=["GET"])
def apigameconfigsv1all():
    with open(f"{dbPath}gameconfigs.json") as f:
        GC = json.load(f)
    return jsonify(GC)

@app.route("/api/auth/eac/challenge", methods=["GET"])
def apiautheacchallenge():
    return jsonify("AQAAAHsg7mW5FQEE9HVl9EKMWXrqDzQxUCdgV/IPuQfbRgTx+cGnQqhhAgv1RvpihEC77gQ29JdoGFn2806Q+QPEj7nYg9C8pynbaiSVO8rKLJPvROsHuSXVJpQMv3TD8KyK3Y+n5bb86vAb5kRdZGD//uC8HY+D9jJLlEfTUlU=")

@app.route("/api/avatar/v1/defaultunlocked", methods=["GET"])
def apiavatarv1defaultunlocked():
    return jsonify(DefaultAvatar)

@app.route("/api/auth/cachedlogin/forplatformid/<int:Platform>/<PlatformId>", methods=["GET"])
def apiauthcachedloginforplatformid(Platform, PlatformId):
    if Platform != 0:
        return abort(404)
    with open(f"{dbPath}auth\\cachedlogins.json") as f:
        cachedlogins = json.load(f)
    logins = []
    for cachedlogin in cachedlogins:
        if cachedlogin["platform"] == Platform:
            if cachedlogin["platformId"] == PlatformId:
                logins.append(cachedlogin)
    if logins == []:
        return "", 500
    return jsonify(logins)

@app.route("/api/accounts/account/bulk", methods=["GET"])
def apiaccountsaccountbulk():
    ids = request.args.getlist("id")
    accs = []
    for accid in ids:
        accid = int(accid)
        acc = account_API.getPlayerById(accid)
        if acc is None:
            continue
        accs.append(acc)
    return jsonify(accs)

@app.route("/api/auth/connect/token", methods=["POST"])
def apiauthconnecttoken():
    grant_type = request.form["grant_type"]
    client_id = request.form["client_id"]
    client_secret = request.form["client_secret"]
    if client_id != "recroom":
        return abort(403)
    if client_secret != "VxZ53kgbbEaRoZAeMe00MagtgD12GLL2":
        return abort(403)
    if grant_type == "Test":
        pass
    elif grant_type == "cached_login":
        account_id = int(request.form["account_id"])
        platform = int(request.form["platform"])
        platform_id = request.form["platform_id"]
        device_id = request.form["device_id"]
        device_class = request.form["device_class"]
        return jsonify(auth.makeLogin(account_id, platform, platform_id, device_class, device_id, request.form))
    return abort(500)

@app.route("/api/accounts/account/me", methods=["GET"])
@NeedToken
def apiaccountsaccountme(playerId):
    print(playerId)
    acc = account_API.getPlayerById(playerId)
    if acc is None:
        return abort(500)
    return jsonify(acc)

@app.route("/api/datacollection/data/event", methods=["POST"])
@NeedToken
def apidatacollectiondataevent(playerId):
    #print(request.form.to_dict())
    return jsonify({"success":True, "errorId":None,"error":None})

@app.route("/api/datacollection/data/heartbeat", methods=["POST"])
@NeedToken
def apidatacollectiondataheartbeat(playerId):
    #print(request.form.to_dict())
    return jsonify({"success":True, "errorId":None,"error":None})

@app.route("/api/objectives/v1/myprogress", methods=["GET"])
@NeedToken
def apiobjectivesv1myprogress(playerId):
    return jsonify({"Objectives": [], "ObjectiveGroups":[]})

@app.route("/api/customAvatarItems/v1/isCreationAllowedForAccount", methods=["GET"])
@NeedToken
def picustomAvatarItemsv1isCreationAllowedForAccount(playerId):
    return jsonify({"success":False,"error_id":"API.CustomAvatarItem.SubscriptionInvalid","error":"You do not have an active RR+ subscription."})

@app.route("/api/PlayerReporting/v1/moderationBlockDetails", methods=["GET"])
@NeedToken
def apiPlayerReportingv1moderationBlockDetails(playerId):
    return jsonify({"ReportCategory":0,"Duration":0,"GameSessionId":0,"Message":None,"IsHostKick":False,"PlayerIdReporter":None,"IsBan":False,"IsVoiceModAutoban":False,"IsDeviceBan":False,"IsWarning":False,"VoteKickReason":None,"TimeoutStartedAt":None,"AssociatedAccountUsername":None})

@app.route("/api/players/v2/progression/bulk", methods=["GET"])
def apiplayersv2progressionbulk():
    ids = request.args.getlist("id")
    accs = []
    for accid in ids:
        accid = int(accid)
        acc = account_API.getPlayerById(accid)
        if acc is None:
            continue
        accs.append({"PlayerId": acc["accountId"], "Level": 0, "XP": 0})
    return jsonify(accs)

@app.route("/api/matchmaking/player/login", methods=["POST"])
@NeedToken
@NeedLoginLock
def apimatchmakingplayerlogin(playerId):
    return ""

@app.route("/api/notify/hub/v1/negotiate", methods=["POST"])
@NeedToken
def apinotifyhubv1negotiate(playerId):
    bearerToken = request.headers.get("Authorization")
    token = bearerToken.split("Bearer ")[1]
    url = f"https://meowapi-test.oldrecroom.com/notification"
    print(url)
    return jsonify({"negotiateVersion": 0,"connectionId":str(playerId),"availableTransports": [{"transport": "WebSockets","transferFormats": ["Text","Binary"]}]})

@app.route("/api/playersettings/playersettings", methods=["GET", "PUT"])
@NeedToken
def apiplayersettingsv1playersettings(playerId):
    if request.method == "PUT":
        Json = request.form
        print(dict(Json))
        key = Json["key"]
        Value = Json["value"]
        with open(f"{dbPath}settings.json", "r") as f:
            PlayerSettings = json.load(f)
        for x in PlayerSettings:
            if x["id"] == playerId:
                for y in x["settingsData"]:
                    if y["Key"] == key:
                        y["Value"] = Value
                        with open(f"{dbPath}settings.json", "w") as f:
                            json.dump(PlayerSettings, f, indent=2)
                        return jsonify(""), 200
                x["settingsData"].append({"Key":key,"Value":Value})
                with open(f"{dbPath}settings.json", "w") as f:
                    json.dump(PlayerSettings, f, indent=2)
                return jsonify(""), 200
    else:
        playerId = playerId
        with open(f"{dbPath}settings.json") as f:
            settings = json.load(f)
        for setting in settings:
            if int(setting["id"]) == int(playerId):
                return jsonify(setting["settingsData"])
        return abort(500)
    return abort(405)

@app.route("/api/avatar/v2", methods=["GET"])
@NeedToken
def apiavatarv2(playerId):
    with open(f"{dbPath}avatar_data.json") as f:
        avatars = json.load(f)
    for avatar in avatars:
        if int(avatar["id"]) == int(playerId):
            return jsonify(avatar["avatarData"])
    return abort(500)

@app.route("/api/avatar/v4/items", methods=["GET"])
@NeedToken
def apiavatarv4items(playerId):
    return jsonify(DefaultAvatar)

@app.route("/api/playerReputation/v2/bulk", methods=["GET"])
@NeedToken
def apiplayerReputationv2bulk(playerId):
    ids = request.args.getlist("id")
    accs = []
    for id in ids:
        acc = account_API.getPlayerByIdV2(int(id))
        if acc is None:
            continue
        data = {
            "AccountId": acc["accountId"],
        }
        data.update(acc["Rep"])
        accs.append(data)
    return jsonify(accs)

@app.route("/api/checklist/v1/current", methods=["GET"])
@NeedToken
def apichecklistv1current(playerId):
    return jsonify([])

@app.route("/api/auth/role/developer/<int:PlayerId>", methods=["GET"])
@NeedToken
def apiauthroledeveloper(playerId, PlayerId):
    return jsonify(True)

@app.route("/api/avatar/v1/defaultbaseavataritems", methods=["GET"])
@NeedToken
def apiavatarv1defaultbaseavataritems(playerId):
    return jsonify([])

@app.route("/econ/customAvatarItems/v1/owned", methods=["GET"])
@NeedToken
def econcustomAvatarItemsv1owned(playerId):
    return jsonify(Results([]))

@app.route("/api/relationships/v2/get", methods=["GET"])
@NeedToken
def apirelationshipsv2get(playerId):
    return jsonify([])


@app.route("/api/matchmaking/player/heartbeat", methods=["POST"])
@NeedToken
@NeedLoginLock
def apimatchmakingplayerheartbeat(playerId):
    with open(f"{dbPath}heartbeat.json") as f:
        heartbeats = json.load(f)
    for heartbeat in heartbeats:
        if int(heartbeat["playerId"]) == int(playerId):
            heartbeat.update({
                "serverTime": coolStuff.datetimeToTicks(datetime.datetime.utcnow())
            })
            print(heartbeat)
            return jsonify(heartbeat)
    return abort(500)

@app.route("/api/matchmaking/player", methods=["GET"])
@NeedToken
def apimatchmakingplayer(playerId):
    with open(f"{dbPath}heartbeat.json") as f:
        heartbeats = json.load(f)
    ids = request.args.getlist("id")
    heartbeats = []
    for accid in ids:
        accid = int(accid)
        acc = account_API.getPlayerById(accid)
        if acc is None:
            continue
        for heartbeat in heartbeats:
            if int(heartbeat["playerId"]) == int(accid):
                heartbeat.update({
                    "serverTime": coolStuff.datetimeToTicks(datetime.datetime.utcnow())
                })
                heartbeats.append(heartbeat)
    return jsonify(heartbeats)

@app.route("/api/chat/thread", methods=["GET"])
@NeedToken
def apichathread(playerId):
    return jsonify([])

@app.route("/api/clubs/announcements/v2/mine/unread", methods=["GET"])
@NeedToken
def apilubsannouncementsv2mineunread(playerId):
    return jsonify([])

@app.route("/api/clubs/club/mine/member", methods=["GET"])
@NeedToken
def apiclubsclubmineember(playerId):
    return jsonify([])

@app.route("/api/matchmaking/player/exclusivelogin", methods=["POST"])
@NeedToken
@NeedLoginLock
def apimatchmakingplayerexclusivelogin(playerId):
    return jsonify("")


@app.route("/api/config/v2", methods=["GET"])
def apiconfigv2():
    with open(f"{dbPath}DailyObjectives.json") as f:
        DailyObjectives = json.load(f)
    data = {
        "ShareBaseUrl": "https://zestrec.oldrecroom.com/{0}",
        "LevelProgressionMaps": [
            {
                "Level": 1,
                "RequiredXp": 2,
                "GiftDropId": 1
            }
        ],
        "DailyObjectives": [
            DailyObjectives["Monday"],
            DailyObjectives["Tuesday"],
            DailyObjectives["Wednesday"],
            DailyObjectives["Thursday"],
            DailyObjectives["Friday"],
            DailyObjectives["Saturday"],
            DailyObjectives["Sunday"]
        ],
        "ServerMaintenance": {
            "StartsInMinutes": 0
        },
        "AutoMicMutingConfig": {
            "MicSpamVolumeThreshold": 1.125,
            "MicVolumeSampleInterval": 0.25,
            "MicVolumeSampleRollingWindowLength": 7,
            "MicSpamSamplePercentageForWarning": 0.8,
            "MicSpamSamplePercentageForWarningToEnd": 0.2,
            "MicSpamSamplePercentageForForceMute": 0.8,
            "MicSpamSamplePercentageForForceMuteToEnd": 0.2,
            "MicSpamWarningStateVolumeMultiplier": 0.25
        },
        "StorefrontConfig": {
            "MinPlayerLevelForGifting": 15
        },
        "RoomKeyConfig": {
            "MaxKeysPerRoom": 10
        },
        "RoomCurrencyConfig": {
            "AwardCurrencyCooldownSeconds": 10
        }
    }
    return jsonify(data)


@app.route("/api/PlayerReporting/v1/hile", methods=["POST"])
@NeedToken
def apiPlayerReportingv1hile(playerId):
    Message = request.form["Message"]
    try:
        Type = enums.PlayerReportingTypes(int(request.form["Type"]))
    except ValueError:
        return abort(400)
    print(Type.name)
    if Type.value == enums.PlayerReportingTypes.AppData_Boot_UnableToVerifySignatures.value:
        return jsonify(False)
    return jsonify(True)

@app.route("/api/messages/v2/get", methods=["GET"])
@NeedToken
def apimessagesv2get(playerId):
    return jsonify([])

@app.route("/api/config/v1/backtrace", methods=["GET"])
@NeedToken
def apiconfigv1backtrace(playerId):
    return jsonify({"ReportBudget":0,"FilterType":0,"SampleRate":0.025,"LogLineCount":50,"CaptureNativeCrashes":1,"ANRThresholdMs":0,"MessageCount":1000,"MessageRegex":"^Cannot set the parent of the GameObject .* while its new parent|^\\\u003E\\x2010x\\:\\x20|\\'LabelTheme\\' contains missing PaletteTheme reference on","VersionRegex":".*"})


@app.route("/api/rooms/rooms", methods=["GET"])
@CanUseToken
def apiroomsrooms(playerId):
    name = request.args["name"]
    room = room_API.getRoomByName(name, playerId=playerId)
    if room is None:
        return abort(404)
    return jsonify(room)

@app.route("/api/rooms/rooms/<int:RoomId>", methods=["GET"])
@CanUseToken
def room(playerId, RoomId):
    room = room_API.getRoomById(RoomId, playerId)
    if room is None:
        return abort(404)
    return jsonify(room)


@app.route("/cdn/config/LoadingScreenTipData", methods=["GET"])
def cdnconfigLoadingScreenTipData():
    return jsonify([])

@app.route("/api/quickPlay/v1/getandclear", methods=["GET"])
def apiquickPlayv1getandclear():
    return jsonify(None)

@app.route("/api/clubs/announcements/v2/subscription/mine/unread", methods=["GET"])
def apiclubsannouncementsv2subscriptionmineunread():
    return jsonify([])

@app.route("/api/matchmaking/matchmake/none", methods=["POST"])
@NeedToken
@NeedLoginLock
def matchmakenone(playerId):
    with open(f"{dbPath}heartbeat.json") as f:
        heartbeats = json.load(f)
    for heartbeat in heartbeats:
        if heartbeat["playerId"] == int(playerId):
            heartbeat.update({
                "lastOnline": coolStuff.getCurrentTime(),
                "roomInstance": None,
                "isOnline": True
            })
            with open(f"{dbPath}heartbeat.json", "w") as f:
                json.dump(heartbeats, f, indent=2)
    return jsonify({"correlationId": None})

@app.route("/api/announcement/v1/get", methods=["GET"])
@NeedToken
def apiannouncementv1get(playerId):
    return jsonify([])

@app.route("/api/matchmaking/player/photonregionpings", methods=["PUT"])
@NeedToken
def apimatchmakingplayerphotonregionpings(playerId):
    return jsonify("")

@app.route("/api/PlayerReporting/v1/voteToKickReasons", methods=["GET"])
@NeedToken
def apiPlayerReportingv1voteToKickReasons(playerId):
    return jsonify([])

@app.route("/api/avatar/v3/saved", methods=["GET"])
@NeedToken
def apiavatarv3saved(playerId):
    return jsonify([])

@app.route("/api/equipment/v2/getUnlocked", methods=["GET"])
@NeedToken
def apiequipmentv2getUnlocked(playerId):
    return jsonify([])

@app.route("/api/rooms/rooms/createdby/me", methods=["GET"])
@NeedToken
def apiroomsroomscreatedbyme(playerId):
    return jsonify(room_API.getMyRooms(playerId))

@app.route("/api/consumables/v2/getUnlocked", methods=["GET"])
@NeedToken
def apiconsumablesv2getUnlocked(playerId):
    return jsonify([])

@app.route("/api/avatar/v2/gifts", methods=["GET"])
@NeedToken
def apiavatarv2gifts(playerId):
    return jsonify([])

@app.route("/api/gamerewards/v1/pending", methods=["GET"])
@NeedToken
def apigamerewardsv1ending(playerId):
    return jsonify([])

@app.route("/api/roomkeys/v1/mine", methods=["GET"])
@NeedToken
def apiroomkeysv1mine(playerId):
    return jsonify([])

@app.route("/api/playerevents/v1/all", methods=["GET"])
@NeedToken
def apiplayereventsv1all(playerId):
    return jsonify({"Created":[],"Responses":[]})

@app.route("/api/CampusCard/v1/UpdateAndGetSubscription", methods=["POST"])
@NeedToken
def apiCampusCardv1UpdateAndGetSubscription(playerId):
    return jsonify({"subscription":None,"platformAccountSubscribedPlayerId":None})

@app.route("/api/subscriptionseasons/v1/seasons/current", methods=["GET"])
@NeedToken
def apisubscriptionseasonsv1seasonscurrent(playerId):
    return jsonify({
    "SubscriptionSeasonId":"d011bb29-62c4-4322-bc62-ac48de295206",
    "Name":"Test",
    "ImageName":"5oha7hq81vwhvac4mm2hc03cu.png",
    "StartAt":"2025-01-03T22:00:00Z",
    "NextSeasonStart":None,
    "Milestones":[]
})

@app.route("/api/customAvatarItems/v1/isRenderingEnabled", methods=["GET"])
@NeedToken
def apicustomAvatarItemsv1isRenderingEnabled(playerId):
    return jsonify(True)

@app.route("/api/customAvatarItems/v1/isCreationEnabled", methods=["GET"])
@NeedToken
def apicustomAvatarItemsv1isCreationEnabled(playerId):
    return jsonify(True)

def sendPings(ws):
    while True:
        time.sleep(7)
        #print("sent Ping")
        websocket.sendPing(ws)

@sock.route("/api/notify/hub/v1")
def notify(ws):
    print(request.args["id"])
    websocket.players.append({
        "playerId": request.args["id"],
        "uuid": str(uuid.uuid4()),
        "ws": ws
    })
    threading.Thread(target=sendPings, args=(ws,)).start()
    while True:
        data = ws.receive()
        if not bytes(data).endswith(b"\x1e"):
            ws.close()
            return
        data = bytes(data).replace(b"\x1e", b"")
        print("received data: " + str(data))
        try:
            dataJson = dict(json.loads(data.decode()))
        except:
            ws.close()
            return
        type1 = dataJson.get("type")
        if type1 is not None:
            if type1 == websocket.MessageTypes.Invocation.value:
                if dataJson["target"] == "SubscribeToPlayers":
                    invocationId = dataJson["invocationId"]
                    websocket.send({"type": websocket.MessageTypes.Completion.value,"invocationId": str(invocationId),"result": None}, ws)
        #ws.send(data)


def run():
    Port = 9020
    Ip = "0.0.0.0"
    Logger.log(Logger.Levels.INFO, "Starting")
    app.run(str(Ip), int(Port), debug)#, ssl_context='adhoc')

run()