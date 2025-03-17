import json
from . import coolStuff, account_API
from operator import itemgetter
import requests

dbPath = "db\\"

def updateSubRoomData(SubRoomData: dict):
    if SubRoomData["CurrentSaveId"] is not None:
        with open(f"{dbPath}room\\SubRoomdataHistory.json") as f:
            SubRoomdataHistorys = json.load(f)
        for SubRoomdataHistory in SubRoomdataHistorys:
            if SubRoomdataHistory["SubRoomDataSaveId"] == SubRoomData["CurrentSaveId"]:
                CurrentSave = SubRoomdataHistory
                SubRoomData.update({"CurrentSave": CurrentSave})
    return SubRoomData

#cbad71af-0831-44d8-b8ef-69edafa841f6

#cbad71af-0831-44d8-b8ef-69edafa841f6

def updateRoomData(RoomData: dict, playerId=0):
    IsDeveloperOwned = False
    player = account_API.getPlayerById(RoomData["CreatorAccountId"])
    if player["isDeveloper"]:
        IsDeveloperOwned = True
    RoomData.update({
        "IsDeveloperOwned": IsDeveloperOwned
    })
    return RoomData

def GetSubroomSaves(SubRoomId):
    with open(f"{dbPath}room\\Subrooms.json") as f:
        SubRooms1 = json.load(f)
    with open(f"{dbPath}room\\SubRoomdataHistory.json") as f:
        SubRoomdataHistorys = json.load(f)
    saves = []
    for z in SubRoomdataHistorys:
        if z["SubRoomId"] == SubRoomId:
            saves.append(z)
    saves.sort(key=itemgetter("SubRoomDataSaveId"), reverse=True)
    return saves

def getRoomByName(Name: str, playerId=0):
    with open(f"{dbPath}room\\Rooms.json") as f:
        Rooms = json.load(f)
    for x in Rooms:
        x = updateRoomData(x, playerId)
        if x["Name"].lower() == "dormroom":
            if not x["CreatorAccountId"] == int(playerId):
                continue
            if x["Name"].lower() == Name.lower():
                SubRooms = []
                with open(f"{dbPath}room\\Subrooms.json") as f:
                    SubRooms1 = json.load(f)
                for y in SubRooms1:
                    if y["RoomId"] == x["RoomId"]:
                        SubRooms.append(y)
                x.update({"SubRooms": SubRooms})
                return x
        if x["Name"].lower() == Name.lower():
            SubRooms = []
            with open(f"{dbPath}room\\Subrooms.json") as f:
                SubRooms1 = json.load(f)
            for y in SubRooms1:
                if y["RoomId"] == x["RoomId"]:
                    y = updateSubRoomData(y)
                    SubRooms.append(y)
            x.update({"SubRooms": SubRooms})
            return x
    return None

def getRoomsByTag(tag: str, show: bool):
    if tag.lower() == "rro":
        return getAllRROS()
    Rooms2 = []
    with open(f"{dbPath}room\\Rooms.json") as f:
        Rooms = json.load(f)
    for x in Rooms:
        x = updateRoomData(x)
        for tag1 in x["Tags"]:
            if tag1["Tag"] == tag:
                SubRooms = []
                with open(f"{dbPath}room\\Subrooms.json") as f:
                    SubRooms1 = json.load(f)
                for y in SubRooms1:
                    if y["RoomId"] == x["RoomId"]:
                        y = updateSubRoomData(y)
                        SubRooms.append(y)
                x.update({"SubRooms": SubRooms})
                Rooms2.append(x)
    return Rooms2

def getBaseRooms(playerId: int):
    rooms = []
    rooms2 = getRoomsByTag("base", False)
    for room in rooms2:
        rooms.append(room)
    return rooms


def getAllRRooms(show=False):
    Rooms2 = []
    with open(f"{dbPath}room\\Rooms.json") as f:
        Rooms = json.load(f)
    for x in Rooms:
        x = updateRoomData(x)
        if not show:
            if x["Accessibility"] == 0 or x["Accessibility"] == 2 or x["Accessibility"] == 3:
                continue
        SubRooms = []
        with open(f"{dbPath}room\\Subrooms.json") as f:
            SubRooms1 = json.load(f)
        for y in SubRooms1:
            if y["RoomId"] == x["RoomId"]:
                y = updateSubRoomData(y)
                SubRooms.append(y)
        x.update({"SubRooms": SubRooms})
        Rooms2.append(x)
    return Rooms2

def getAllRROS(show=False):
    rooms = getAllRRooms(show)
    goofrooms = []
    for room in rooms:
        if room["IsRRO"]:
            goofrooms.append(room)
    return goofrooms
    

def getRoomById(Id: int, playerId=0):
    with open(f"{dbPath}room\\Rooms.json") as f:
        Rooms = json.load(f)
    for x in Rooms:
        x = updateRoomData(x, playerId)
        if x["RoomId"] == Id:
            SubRooms = []
            with open(f"{dbPath}room\\Subrooms.json") as f:
                SubRooms1 = json.load(f)
            for y in SubRooms1:
                if y["RoomId"] == x["RoomId"]:
                    y = updateSubRoomData(y)
                    SubRooms.append(y)
            x.update({"SubRooms": SubRooms})
            return x
    return None

def getMyRooms(playerID: int):
    with open(f"{dbPath}room\\Rooms.json") as f:
        Rooms = json.load(f)

    myRooms = []

    for room in Rooms:
        room = updateRoomData(room, playerID)
        for Role in room["Roles"]:
            if Role["AccountId"] == playerID:
                if Role["Role"] >= 30:
                    myRooms.append(room)

    return myRooms

def makeNewSave(playerId: int, subRoomId: int, blobName: str, UnityAssetId, Description: str):
    with open(f"{dbPath}room\\SubRoomdataHistory.json") as f:
         SubRoomdataHistorys = json.load(f)

    if UnityAssetId == "":
        UnityAssetId = None

    nextAvailableId = max([x["SubRoomDataSaveId"] for x in SubRoomdataHistorys]) + 1

    with open(f"{dbPath}heartbeat.json") as f:
        heartbeats = json.load(f)
    for heartbeat in heartbeats:
        if heartbeat["playerId"] == playerId:
            platform = heartbeat["platform"]
            deviceClass = heartbeat["deviceClass"]
    CurrentSave = {
        "SubRoomDataSaveId": nextAvailableId,
        "SubRoomId": subRoomId,
        "DataBlob": blobName,
        "SavedByAccountId": playerId,
        "SavedOnPlatform": platform,
        "SavedOnDeviceClass": deviceClass,
        "Description": Description,
        "CreatedAt": coolStuff.getCurrentTime(),
        "UnityAssetId": UnityAssetId
    }
    SubRoomdataHistorys.append(CurrentSave)
    with open(f"{dbPath}room\\SubRoomdataHistory.json", "w") as f:
        json.dump(SubRoomdataHistorys, f, indent=2)
    return CurrentSave


def getSubRoomSaveById(Id: str):
    with open(f"{dbPath}room\\SubRoomdataHistory.json") as f:
        SubRoomdataHistorys = json.load(f)
    for SubRoomdataHistory in SubRoomdataHistorys:
        if SubRoomdataHistory["SubRoomDataSaveId"] == Id:
            return SubRoomdataHistory
    return


def makeDormRoom(playerId: int):
    with open(f"{dbPath}room\\Rooms.json") as f:
        Rooms = json.load(f)

    with open(f"{dbPath}room\\Subrooms.json") as f:
        SubRooms = json.load(f)

    nextAvailableId = max([room["RoomId"] for room in Rooms]) + 1

    newRoom ={
        "Accessibility": 0,
        "CloningAllowed": False,
        "CreatedAt": coolStuff.getCurrentTime(),
        "CreatorAccountId": playerId,
        "CustomWarning": "",
        "DataBlob": None,
        "Description": "Your private room",
        "DisableMicAutoMute": False,
        "DisableRoomComments": False,
        "EncryptVoiceChat": False,
        "ImageName": "lob2a1gpoxeyo68lz97c7hacj.png",
        "IsDorm": True,
        "IsRRO": False,
        "LoadScreenLocked": False,
        "LoadScreens": [],
        "MaxPlayerCalculationMode": 1,
        "MaxPlayers": 4,
        "MinLevel": 0,
        "Name": "DormRoom",
        "PromoExternalContent": [],
        "PromoImages": [],
        "Roles": [
        {
            "AccountId": playerId,
            "Role": 255,
            "InvitedRole": 0
        }
        ],
        "RoomId": nextAvailableId,
        "State": 0,
        "Stats": {
            "CheerCount": 0,
            "FavoriteCount": 0,
            "VisitorCount": 0,
            "VisitCount": 0
        },
        "SupportsJuniors": True,
        "SupportsLevelVoting": False,
        "SupportsMobile": True,
        "SupportsQuest2": True,
        "SupportsScreens": True,
        "SupportsTeleportVR": True,
        "SupportsVRLow": True,
        "SupportsWalkVR": True,
        "Tags": [],
        "Version": 0,
        "WarningMask": 0
    }
    nextAvailableId1 = max([SubRoom["SubRoomId"] for SubRoom in SubRooms]) + 1
    newSubRoom = {
        "SubRoomId": nextAvailableId1,
        "RoomId": nextAvailableId,
        "Name": "Home",
        "IsSandbox": True,
        "MaxPlayers": 4,
        "Accessibility": 1,
        "UnitySceneId": "76d98498-60a1-430c-ab76-b54a29b7a163",
        "CurrentSaveId": None
  }
    
    Rooms.append(newRoom)
    SubRooms.append(newSubRoom)

    with open(f"{dbPath}room\\Rooms.json", "w") as f:
        json.dump(Rooms, f, indent=2)

    with open(f"{dbPath}room\\Subrooms.json", "w") as f:
       json.dump(SubRooms, f, indent=2)

    return True

def canCloneRoom(RoomId: int, playerId: int):
    room = getRoomById(RoomId)
    if room is None:
        return
    if room["CloningAllowed"]:
        return True
    for Role in room["Roles"]:
        if Role["AccountId"] == playerId:
            if Role["Role"] >= 30:
                return True
    return False
    

def CloneRoom(RoomId: int, Name: str, playerId: int):
    roomshit = getRoomByName(Name)
    if roomshit is not None:
        return {"success":False,"error":"A Room Has That Name"}
    
    room = getRoomById(RoomId)
    if room is None:
        return {"success":False,"error":"WTF HOW TF YOU TRYED TO COPY A ROOM WITH NO DATA"}
    
    canCopy = canCloneRoom(RoomId, playerId)
    if not canCopy:
        return {"success":False,"error":":3"}

    with open(f"{dbPath}room\\Rooms.json") as f:
        Rooms = json.load(f)

    with open(f"{dbPath}room\\Subrooms.json") as f:
        SubRooms = json.load(f)

    nextAvailableId = max([room["RoomId"] for room in Rooms]) + 1

    newRoom ={
        "Accessibility": 0,
        "CloningAllowed": False,
        "CreatedAt": coolStuff.getCurrentTime(),
        "CreatorAccountId": playerId,
        "CustomWarning": "",
        "DataBlob": None,
        "Description": room["Description"],
        "DisableMicAutoMute": room["DisableMicAutoMute"],
        "DisableRoomComments": room["DisableRoomComments"],
        "EncryptVoiceChat": room["EncryptVoiceChat"],
        "ImageName": room["ImageName"],
        "IsDorm": False,
        "IsRRO": False,
        "LoadScreenLocked": False,
        "LoadScreens": room["LoadScreens"],
        "MaxPlayerCalculationMode": 1,
        "MaxPlayers": room["MaxPlayers"],
        "MinLevel": room["MinLevel"],
        "Name": Name,
        "PromoExternalContent": [],
        "PromoImages": [],
        "Roles": [
            {
                "AccountId": playerId,
                "Role": 255,
                "InvitedRole": 0
            }
        ],
        "RoomId": nextAvailableId,
        "State": 0,
        "Stats": {
            "CheerCount": 0,
            "FavoriteCount": 0,
            "VisitorCount": 0,
            "VisitCount": 0
        },
        "SupportsJuniors": room["SupportsJuniors"],
        "SupportsLevelVoting": False,
        "SupportsMobile": room["SupportsMobile"],
        "SupportsQuest2": room["SupportsQuest2"],
        "SupportsScreens": room["SupportsScreens"],
        "SupportsTeleportVR": room["SupportsTeleportVR"],
        "SupportsVRLow": room["SupportsVRLow"],
        "SupportsWalkVR": room["SupportsWalkVR"],
        "Tags": [],
        "Version": 0,
        "WarningMask": 0
    }
    nextAvailableId1 = max([SubRoom["SubRoomId"] for SubRoom in SubRooms]) + 1
    for subroom in room["SubRooms"]:
        saveId = None
        if subroom["CurrentSaveId"] is not None:
            Description = f"Cloned from ^{room["Name"]}"
            save = getSubRoomSaveById(subroom["CurrentSaveId"])
            saveData = makeNewSave(playerId, nextAvailableId1, save["DataBlob"], save["UnityAssetId"], Description)
            saveId = saveData["SubRoomDataSaveId"]
        newSubRoom = {
            "SubRoomId": nextAvailableId1,
            "RoomId": nextAvailableId,
            "Name": subroom["Name"],
            "IsSandbox": subroom["IsSandbox"],
            "MaxPlayers": subroom["MaxPlayers"],
            "Accessibility": subroom["Accessibility"],
            "UnitySceneId": subroom["UnitySceneId"],
            "CurrentSaveId": saveId
        }

        newPermission = {
            "subRoomId": nextAvailableId1,
            "permissions": []
        }
        SubRooms.append(newSubRoom)
        nextAvailableId1 += 1
    
    Rooms.append(newRoom)

    with open(f"{dbPath}room\\Rooms.json", "w") as f:
        json.dump(Rooms, f, indent=2)

    with open(f"{dbPath}room\\Subrooms.json", "w") as f:
       json.dump(SubRooms, f, indent=2)

    room111 = getRoomById(nextAvailableId, playerId)

    return {"success":True,"error":"", "value": room111}

def saveSubRoom(roomID:int, subRoomID:int, filename:str, roomDataFilename:str, Description: str, UnityAssetId, playerID:int):
    #return "No"
    myRooms = getMyRooms(playerID)
    for room in myRooms:
        if room["RoomId"] == roomID:
            with open(f"{dbPath}room\\Subrooms.json") as f:
                subRooms = json.load(f)
            
            for subRoom in subRooms:
                if subRoom["SubRoomId"] == subRoomID:
                    CurrentSave = makeNewSave(playerID, subRoomID, filename, UnityAssetId, Description)
                    subRoom.update({
                        "CurrentSaveId": CurrentSave["SubRoomDataSaveId"]
                    })
                    with open(f"{dbPath}room\\Subrooms.json", "w") as f:
                        json.dump(subRooms, f, indent=2)
                    return subRoom
    return "err1"