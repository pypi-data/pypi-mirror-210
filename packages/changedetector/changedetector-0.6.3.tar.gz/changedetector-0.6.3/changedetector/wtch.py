from watchdog.events import FileSystemEventHandler

import time
import json


class WatchForHandler(FileSystemEventHandler):
    def __init__(self, miliseconds):
        super().__init__()
        self.changes = {}
        self.createList = []
        self.modifyList = []
        self.deleteList = []
        self.jsonFile = f"{miliseconds}-changes.json"
        self.seconds = miliseconds / 1000
        self.endTime = time.time() + self.seconds + 2

    def on_any_event(self, event):
        if self.endTime > time.time():
            if event.is_directory:
                return None

            elif event.event_type == "created":
                # Take any action here when a file is first created.
                self.createList.append(event.src_path)

            elif event.event_type == "modified":
                # Taken any action here when a file is modified.
                self.modifyList.append(event.src_path)

            elif event.event_type == "deleted":
                # Taken any action here when a file is deleted.
                self.deleteList.append(event.src_path)

        self.changes["created"] = self.createList
        self.changes["modified"] = self.modifyList
        self.changes["deleted"] = self.deleteList
        print(self.changes)
        with open(self.jsonFile, "w") as f:
            json.dump(self.changes, f)

    def getChanges(self):
        return self.changes
