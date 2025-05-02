from fileinput import filename
import json
import mimetypes
import os
import random
import re
import string

from pprint import pprint
from pathlib import Path
import time
from tinydb import TinyDB
from ctypes import windll

from src.modules.options.collect_agents import collect_agents


class update_database:
    def __init__(self, disk_nb_list, hidden_disk):
        current_path = os.getcwd()
        self.result = {0: [], 1: [], 2: []}
        self.disk_nb_list = disk_nb_list
        self.hidden_disk = hidden_disk
        self.all_drives = self.get_all_drives()
        self.current_disk_number = 0
        database_path = Path(
            os.path.join(current_path, "src", "databases", "database_disks.json")
        )
        with open(database_path, "r") as file:
            self.data = json.load(file)

        self.current_depth = 0
        for drive in self.all_drives:
            self.clear_json_files_once = False 
            if drive not in self.hidden_disk:
                self.walk_dir(drive, self.current_depth)
            self.current_depth = 0

        with open(database_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

        
    def walk_dir(self, current_path, current_depth):
        if current_depth > 1:
            return
        
        for path in self.disk_nb_list:
            if current_path[:3] == list(path.keys())[0]:
                key, value = list(path.items())[0]
                self.current_disk_number = value[5:]
        
        if not self.clear_json_files_once:
            self.data[f"Disk #{self.current_disk_number}"]["files"] = []
            self.clear_json_files_once = True
        
        try:
            excluded_folder = [
                "$RECYCLE.BIN",
                "Machine_Mint",
                "System Volume Information",
            ]
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if not any(name in entry.path for name in excluded_folder):
                        stat = entry.stat(follow_symlinks=False)
                        # Get MIME type (like "text/plain" or "image/png")
                        mime_type, _ = mimetypes.guess_type(entry.path)
                        item = {
                            "path": entry.path,
                            "name": entry.name,
                            "extension": os.path.splitext(entry.name)[
                                1
                            ].lower(),  # e.g., ".txt"
                            "type": (
                                "folder"
                                if entry.is_dir(follow_symlinks=False)
                                else "file"
                            ),
                            "mime": mime_type if mime_type else "unknown",
                            "size_bytes": stat.st_size,
                            "size_kb": round(stat.st_size / 1024, 2),
                            "created": time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime(stat.st_ctime)
                            ),
                            "modified": time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)
                            ),
                            "accessed": time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime(stat.st_atime)
                            ),
                            "readonly": not os.access(entry.path, os.W_OK),
                            "hidden": entry.name.startswith("."),
                            "symlink": entry.is_symlink(),
                        }

                        try:
                            self.data[f"Disk #{self.current_disk_number}"][
                                "files"
                            ].append(item)
                        except Exception as e:
                            # print(f"HOOOOO  NOOOO {e}")
                            pass

                        if not os.path.isfile(entry.path):
                            self.walk_dir(entry.path, current_depth + 1)

                        # # Scan level 1 (directories in the root and files inside them)
                        # try:
                        #     for folder in os.listdir(Path(entry.path)):
                        #         folder_path = os.path.join(Path(entry.path), folder)
                        #         print(folder)
                        #         # if os.path.isdir(folder_path):
                        #         #     self.data[f"Disk #{current_disk_number}"]["files"].append(folder_path)
                        #         # if os.path.isfile(folder_path):
                        #         #     self.data[f"Disk #{current_disk_number}"]["files"].append(folder_path)
                        # except PermissionError:
                        #     print(f"⚠️ Access denied to {folder_path}, skipping...")
                        # except Exception as e:
                        #     print(f"Error scanning level 1: {e}")

                    # # Scan level 2 (directories inside level 1 folders and files inside them)
                    # try:
                    #     for level_1_folder, level_1_items in self.data[
                    #         f"Disk #{current_disk_number}"
                    #     ].items():
                    #         level_1_folder_path = os.path.join(
                    #             Path(entry.path), level_1_folder
                    #         )
                    #         for folder in os.listdir(level_1_folder_path):
                    #             folder_path = os.path.join(level_1_folder_path, folder)
                    #             if os.path.isdir(folder_path):
                    #                 self.data[
                    #                     f"Disk #{current_disk_number}"
                    #                 ].setdefault(level_1_folder, {})[folder] = [
                    #                     f for f in os.listdir(folder_path)
                    #                 ]
                    # except PermissionError:
                    #     print(f"⚠️ Access denied to {folder_path}, skipping...")
                    # except Exception as e:
                    #     print(f"Error scanning level 2: {e}")

                    # print(item["path"][:3])
                    # print(entry)
                    # print(current_disk_number)
                    # print(item)
                    # self.data[f"Disk #{str(current_disk_number)}"]["files"].append(item)
                    # if entry.is_dir(follow_symlinks=False):
                    #     self.walk_dir(entry.path, current_depth + 1)
        except PermissionError:
            pass  # Skip folders/files without permission
        except FileNotFoundError:
            pass  # In case of deleted or disconnected drive parts

    def get_all_drives(self):
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if bitmask & (1 << i):
                drives.append(f"{string.ascii_uppercase[i]}:/")
        return drives
