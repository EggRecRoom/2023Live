import json
import os

dbPath = "db\\"

def getPlayerById(Id: int):
    with open(f"{dbPath}accounts.json", encoding="utf8") as f:
        players = json.load(f)

    for player in players:
        if player["accountId"] == Id:
            del player["canUseKeepsakes"]
            del player["canUseScreenShare"]
            del player["discord"]
            del player["deviceIds"]
            del player["Level"]
            del player["XP"]
            del player["Rep"]
            del player["bio"]
            del player["password"]
            return player
    return None

def getPlayerByIdV2(Id: int):
    with open(f"{dbPath}accounts.json", encoding="utf8") as f:
        players = json.load(f)

    for player in players:
        if player["accountId"] == Id:
            return player
    return None