from fileinput import filename
import json
import os
import random
import re
import string

from pprint import pprint
from pathlib import Path
from tinydb import TinyDB
from ctypes import windll


class collect_agents:
    def __init__(self, disk_hidden):
        self.current_disk_number = 0
        self.current_disk_letter = r"C:/"
        self.current_path = Path(os.getcwd())
        self.disks_nb_left = list(range(51))
        self.current_disk_number_list = []
        self.data = None
        self.json_path = ""

        # Looping to get rid of those already used.
        def get_out_used_disk_nb():
            self.json_path = Path(
                os.path.join(
                    self.current_path, "src", "databases", "database_disks.json"
                )
            )
            # Load or create file
            if self.json_path.exists():
                try:
                    with open(self.json_path, "r") as f:
                        self.data = json.load(f)
                except json.JSONDecodeError:
                    self.data = {}
                    # Ensure structure for all disks
                    for i in self.disks_nb_left:
                        key = f"Disk #{i}"
                        if key not in self.data:
                            self.data[key] = {"used": False, "files": []}
            else:
                self.data = {}
                # Ensure structure for all disks
                for i in self.disks_nb_left:
                    key = f"Disk #{i}"
                    if key not in self.data:
                        self.data[key] = {"used": False, "files": []}

            # Save updated structure
            with open(self.json_path, "w") as f:
                json.dump(self.data, f, indent=4)

        get_out_used_disk_nb()

        self.disk_hidden = [Path(d).drive for d in disk_hidden]  # normalize
        self.all_drives_temp = self.get_all_drives()
        self.all_drives = []
        for drive in self.all_drives_temp:
            if drive.split("/")[0] not in self.disk_hidden:
                self.all_drives.append(drive)
        self.collect_or_create_json(self.all_drives)

    def get_all_drives(self):
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if bitmask & (1 << i):
                drives.append(f"{string.ascii_uppercase[i]}:/")
        return drives

    def collect_or_create_json(self, all_drives):
        with open(self.json_path, "r") as f:
            self.data = json.load(f)
        database_json_path = Path(self.current_path, "src", "database")
        current_disk_nb = 0

        all_disk_list = []
        for drive in all_drives:
            try:
                for item in Path(drive).iterdir():
                    if (
                        item.is_file()
                        and item.suffix == ".json"
                        and "agent_disk" in str(item)
                    ):
                        # print(item)
                        match = re.search(r"agent_disk_(\d+)\.json", str(item))
                        if match:
                            current_disk_nb = int(
                                match.group(1)
                            )  # This gives you the number as an integer
                            self.current_disk_number_list.append(
                                {drive: f"Disk {current_disk_nb}"}
                            )
                        # print(current_disk_nb)
                        for disk in self.data:
                            disk_nb_str = str(current_disk_nb)
                            disk_nb_int = int(current_disk_nb)
                            if disk == f"Disk #{disk_nb_str}":
                                self.data[disk]["used"] = True
                                all_disk_list.append(disk)
                                if disk_nb_int in self.disks_nb_left:
                                    self.disks_nb_left.remove(disk_nb_int)

                            if disk not in all_disk_list:
                                self.data[disk]["used"] = False
                    else:
                        disk_exist = False
            except (PermissionError, OSError):
                pass  # Skip drives that can't be accessed

            # if not disk_exist:
            #     cur_nb = random.choice(self.disks_nb_left)
            #     with open(f"{drive}/agent_disk_{cur_nb}.json", "w") as f:
            #         json.dump({}, f, indent=4)

        # print(all_disk_list)
        with open(self.json_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_disk_number_list(self):
        return self.current_disk_number_list
