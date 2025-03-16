import datetime
import subprocess

def datetimeToTicks(dt):
    """Converts a Python datetime object to .NET ticks."""
    epoch = datetime.datetime(1, 1, 1)
    delta = dt - epoch
    return int(delta.total_seconds() * 10000000)


def clearScreen():
    subprocess.run("cls", shell=True)

def getCurrentTime():
  now = datetime.datetime.now()
  currentTime = now.isoformat()
  return currentTime