import json

dbPath = "db\\"

def getDefaultAvatar():
    with open(f"{dbPath}AvatarItems.json") as f:
        items = json.load(f)
    with open(f"{dbPath}AvatarItemsDefaultIds.json") as f:
        Default = json.load(f)
    items1 = []
    for item in items:
        if int(item["AvatarItemId"]) in Default:
            items1.append(item)
    return items1

def getAvatar():
    with open(f"{dbPath}AvatarItems.json") as f:
        items = json.load(f)
    return items