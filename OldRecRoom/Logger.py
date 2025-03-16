import colorama
from colorama import Fore
from enum import Enum

colorama.init(autoreset=True)

class Levels(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

def log(level: Levels, msg: str):
    if level.value == 0:
        print(f"{Fore.WHITE}Debug: {msg}")
    elif level.value == 1:
        print(f"{Fore.WHITE}{msg}")
    elif level.value == 2:
        print(f"{Fore.YELLOW}{msg}")
    elif level.value == 3:
        print(f"{Fore.RED}Error: {msg}")
    elif level.value == 4:
        print(f"{Fore.LIGHTRED_EX}{msg}")
    else:
        return False
    return True