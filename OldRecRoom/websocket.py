import json
from enum import Enum
from flask_sock import Sock
from uuid import uuid4

from . import Logger


players = []
Subscribes = [
    {
        "id": str(uuid4()),
        "players": []
    }
]

sep = "\u001e"

class MessageTypes2(Enum):
    RelationshipChanged = 1
    MessageReceived = 2
    MessageDeleted = 3
    PresenceHeartbeatResponse = 4
    RefreshLogin = 5
    Logout = 6
    SubscriptionUpdateProfile = 11
    SubscriptionUpdatePresence = 12
    SubscriptionUpdateGameSession = 13
    SubscriptionUpdateRoom = 15
    SubscriptionUpdateRoomPlaylist = 16
    ModerationQuitGame = 20
    ModerationUpdateRequired = 21
    ModerationKick = 22
    ModerationKickAttemptFailed = 23
    ModerationRoomBan = 24
    ServerMaintenance = 25
    GiftPackageReceived = 30
    GiftPackageReceivedImmediate = 31
    GiftPackageRewardSelectionReceived = 32
    ProfileJuniorStatusUpdate = 40
    RelationshipsInvalid = 50
    StorefrontBalanceAdd = 60
    StorefrontBalanceUpdate = 61
    StorefrontBalancePurchase = 62
    ConsumableMappingAdded = 70
    ConsumableMappingRemoved = 71
    PlayerEventCreated = 80
    PlayerEventUpdated = 81
    PlayerEventDeleted = 82
    PlayerEventResponseChanged = 83
    PlayerEventResponseDeleted = 84
    PlayerEventStateChanged = 85
    ChatMessageReceived = 90
    CommunityBoardUpdate = 95
    CommunityBoardAnnouncementUpdate = 96
    InventionModerationStateChanged = 100
    FreeGiftButtonItemsAdded = 110
    LocalRoomKeyCreated = 120
    LocalRoomKeyDeleted = 121

class MessageTypes(Enum):
    Handshake = 0
    Invocation = 1
    StreamItem = 2
    Completion = 3
    StreamInvocation = 4
    CancelInvocation = 5
    Ping = 6
    Close = 7


def makeNotification(id: MessageTypes2, msg: dict):
    argument = {
        "id": id.name,
        "msg": msg
    }
    return {
        "type": MessageTypes.Invocation.value,
        "target": "Notification",
        "arguments": [
            json.dumps(argument)
        ]
    }

def SubscribeToPlayers(myPlayerId: int, playerIds: int, invocationId, myws):
    for x in playerIds:
        if x == myPlayerId:
            pass
        Subscribes[0]["players"].append({
            "playerId": x,
            "ws": None
        })
    send({"type":MessageTypes.Completion.value,"invocationId":str(invocationId),"result":None}, myws)


def sendToAllPlayers(jsonData):
    for x in players:
        try:
            send(jsonData, x["ws"])
        except:
            Logger.log(Logger.Levels.ERROR, f"Oh No ws error with {x["ws"]}")

def send(jsonData: dict, ws):
    sendData = json.dumps(jsonData)
    sendDataSTR = sendData + "\u001e"
    try:
        ws.send(sendDataSTR)
        print(f"sent \"{sendDataSTR}\" to {ws}")
    except:
        ws.close(None, None)


def sendPing(ws):
    pingData = {"type": MessageTypes.Ping.value}
    send(pingData, ws)