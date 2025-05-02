from ctypes import windll
from datetime import datetime
import glob
import re
import string
import subprocess
import json, os, threading, time, sys
from tkinter import DISABLED, END, INSERT
from tkinter.font import NORMAL
from turtle import heading, width
import customtkinter as ctk
import threading
import tkinter as tk
import psutil
import pygame
import screeninfo
import win32gui
import win32con
import win32com.client


from pathlib import Path
from PIL import Image, ImageTk
from io import BytesIO
from rich import print
from PIL.Image import Resampling

from src.modules.options.collect_agents import collect_agents
from src.modules.buildui_modules import title_module
from src.modules.options.update_database import update_database
from src.modules.set_monitor import setup_window_position
from src.modules.graphic import Graphic


pygame.mixer.init()


class Disk_Management(ctk.CTk):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 520

    def __init__(self):
        super().__init__()
        Graphic(self)
        self.hidden_disks = ["C:/", "D:/"]
        ### Collect Agents on Disk and Turn it true in databse if connected.
        agent = collect_agents(self.hidden_disks)
        self.list_disk_nb = agent.get_disk_number_list()
        update_database(self.list_disk_nb, self.hidden_disks)
        threading.Thread(
            target=lambda: update_database(self.list_disk_nb, self.hidden_disks)
        ).start()
        current_path = Path(os.getcwd())
        user_options_path = Path(current_path, "src", "databases", "user_options.json")
        # region load user data
        try:
            with open(user_options_path, "r", encoding="utf-8") as f:
                self.user_options = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(user_options_path, "w") as file:
                json.dump({}, file, indent=4)
            new_data = {"monitor_selected": 0}
            with open(user_options_path, "r+") as file:
                data = json.load(file)  # Load existing data
                data.update(new_data)  # Add/Update the new data

                file.seek(0)  # Move the file pointer to the beginning of the file
                json.dump(
                    data, file, indent=4
                )  # Write the updated data back to the file
        # endregion

        self.withdraw()  # Hide the window immediately
        self.title("🔍 DiskVision Pro — Total Drive Control 🔧")
        self.MONITOR = self.user_options["monitor_selected"]
        self.disk_selected = 0
        self.window_options_state = False
        self.current_file_searched_path = ""
        self.x, self.y = setup_window_position(self, self.MONITOR)
        self.y -= 120  ### Personal Modification
        self.x -= 300  ### Personal Modification
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{self.x}+{self.y}")
        self.configure(bg_color="#000000", fg_color="#000000")
        self.bind("<KeyPress-q>", self.quit_program)
        self.resizable(False, False)
        title_module(self)

        # region SEARCH INPUT
        self.search_input_var = tk.StringVar()
        # Search Box Input Field
        self.search_box_input = ctk.CTkEntry(
            self,
            textvariable=self.search_input_var,
            placeholder_text="Enter the name of your file here.",
            corner_radius=0,
            width=600,
            height=40,
            fg_color="#000000",
        )
        self.search_box_input.place(relx=0.150, rely=0.130)
        self.after(500, lambda: self.search_box_input.focus())
        self.bind("<Escape>", self.clear_search_input)
        # endregion

        # region SEARCH RESULTS
        # Scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=750, height=400)
        self.scrollable_frame.place(relx=0.015, rely=0.220)
        items = [
            f"Item {i}" for i in range(1, 20)
        ]  # 30 items for testing self.scrollbar

        self.current_path = os.getcwd()
        self.current_path = Path(
            os.path.join(self.current_path, "src", "databases", "database_disks.json")
        )
        with open(self.current_path, "r") as f:
            self.data = json.load(f)

        def on_search_change(*args):
            def threading_it():
                for widget in self.scrollable_frame.winfo_children():
                    if isinstance(widget, ctk.CTkButton):
                        widget.destroy()
                current_search = self.search_box_input.get()
                if len(current_search) < 3:
                    return
                for disk_name, disk_info in self.data.items():
                    # print(f"Disk: {disk_name}, Used: {disk_info["used"]}")
                    for file_info in disk_info["files"]:
                        if (
                            current_search.lower()
                            in os.path.splitext(file_info["name"])[0].lower()
                        ):
                            current_files = (
                                file_info,
                                disk_info,
                                disk_name,
                                disk_info["used"],
                            )
                            current_path = file_info["path"]
                            current_text_color = ""
                            if current_files[3]:
                                current_text_color = "#000000"
                                text_color = "black"
                            else:
                                current_text_color = "#D50000"
                                text_color = "white"
                            btn_prompt = (
                                f"{self.truncate_middle(f'{current_files[0]['name']}', 40)}\n"
                                f"{self.truncate_middle(f'{current_files[0]['path']}', 50)}\n"
                                f"{'Disk #' + disk_name[6:] + ' Connected!' if current_files[3] else 'Disk #' + disk_name[6:] + ' Disconnected'}"
                            )
                            # Create a button for each item inside the scrollable frame
                            button = ctk.CTkButton(
                                self.scrollable_frame,
                                text=btn_prompt,
                                command=lambda: print("BTN"),
                                fg_color="#000000",
                                text_color="white",
                                font=("Times", 20),
                                width=700,
                                height=100,
                                corner_radius=10,
                                anchor="n",
                            )
                            button.pack(pady=3, padx=5)  # vertical layout with spacing
                            button.bind(
                                "<Button-1>",
                                lambda event, p=current_path: self.open_directory(p),
                            )

            # threading.Thread(target=threading_it).start()
            threading_it()

        self.search_input_var.trace_add("write", on_search_change)

        # region BTN OPTIONS FUNCTION
        def btn_options_function(self):
            settings_ico_path = self.ressource_path(
                os.path.join("src", "icons", "settings_icon.ico")
            )
            original_pil_image = Image.open(settings_ico_path).convert("RGBA")

            self.angle = 0
            self.rotation_speed = 5
            self.target_size = 36
            self.current_size = 36

            self.canvas = ctk.CTkCanvas(
                self,
                width=36,
                height=36,
                bg="black",
                highlightthickness=0,
                cursor="hand2",
            )
            self.canvas.place(relx=0.950, rely=0.160, anchor="center")

            def get_tk_image(size, angle):
                resized = original_pil_image.resize((size, size), Resampling.LANCZOS)
                rotated = resized.rotate(angle, resample=Resampling.BICUBIC)
                return ImageTk.PhotoImage(rotated)

            def update_canvas_image(img, size):
                self.canvas.config(width=size, height=size)
                self.canvas.delete("all")
                self.canvas.create_image(size // 2, size // 2, image=img)
                self.canvas.image = img

                # Recenter canvas based on new size to keep it visually still
                # x_offset = size // 2
                # y_offset = size // 2
                self.canvas.place(relx=0.940, rely=0.160, anchor="center")

            def rotate_icon_forever():
                while True:
                    # Smooth interpolation toward target size
                    if self.current_size != self.target_size:
                        diff = self.target_size - self.current_size
                        step = max(1, abs(diff) // 5)
                        self.current_size += step if diff > 0 else -step

                    tk_img = get_tk_image(self.current_size, self.angle)
                    self.after(0, update_canvas_image, tk_img, self.current_size)
                    self.angle = (self.angle + self.rotation_speed) % 360
                    time.sleep(0.05)

            def on_hover_enter(event):
                self.rotation_speed = 15
                self.target_size = 48

            def on_hover_leave(event):
                self.rotation_speed = 5
                self.target_size = 36

            self.canvas.bind("<Enter>", on_hover_enter)
            self.canvas.bind("<Leave>", on_hover_leave)

            # region OPTIONS WINDOW
            self.window_options = None

            def window_state_function():
                if (
                    self.window_options is None
                    or not self.window_options.winfo_exists()
                ):
                    self.window_options = ctk.CTkToplevel(self)
                    self.window_options.withdraw()  # Hide the window immediately
                    self.window_options.configure(
                        bg_color="#000000", fg_color="#000000"
                    )
                    self.window_options.resizable(False, False)
                    self.window_options.title(" 🛠️ OPTIONS MENU ")
                    self.window_options.geometry(
                        f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{self.x}+{self.y}"
                    )
                    self.window_options.attributes("-topmost", 1)
                    self.output_visible = False

                    content_label = ctk.CTkLabel(
                        self.window_options,
                        text="OPTIONS MENU",
                        text_color="white",
                        fg_color="#333333",
                        corner_radius=10,
                        font=ctk.CTkFont(size=20, weight="bold"),
                        width=200,
                        height=40,
                    )
                    content_label.place(relx=0.020, rely=0.020)

                    inject_btn = ctk.CTkButton(
                        self.window_options,
                        text="INJECT AGENTS",
                        text_color="white",
                        fg_color="#1976D2",
                        corner_radius=10,
                        font=ctk.CTkFont(size=20, weight="bold"),
                        width=200,
                        height=40,
                        cursor="hand2",
                        command=lambda: inject_btn_function(),
                    )
                    inject_btn.place(relx=0.020, rely=0.120)

                    # region Disk Injected and To Inject or not
                    def create_outputbox_set():
                        self.output_box = ctk.CTkTextbox(
                            self.window_options,
                            width=450,
                            height=250,
                            corner_radius=6,
                            wrap="word",
                        )

                        # Scrollable frame
                        self.scrollable_inject_btn = ctk.CTkScrollableFrame(
                            self.window_options, width=200, height=200
                        )

                        items = [
                            f"Item {i}" for i in range(1, 20)
                        ]  # 30 items for testing self.scrollbar

                    def infect_them_btn_function():
                        self.infect_them_btn = ctk.CTkButton(
                            self.scrollable_inject_btn,
                            text="Infect x",
                            width=60,
                            height=20,
                            corner_radius=10,
                            fg_color="#00C853",
                            text_color="black",
                            font=("Times", 20),
                            command=lambda: print("Hey Hey."),
                            anchor="e",
                        )

                    def reveal_and_fade():
                        self.window_options.deiconify()  # Now show the window
                        fade_in()

                    def fade_in():
                        alpha = 0.0
                        increment = 0.05
                        delay = 10  # milliseconds

                        def increase_alpha():
                            nonlocal alpha
                            alpha += increment
                            if alpha <= 1.0:
                                self.window_options.wm_attributes("-alpha", alpha)
                                self.window_options.after(delay, increase_alpha)
                            else:
                                self.window_options.wm_attributes("-alpha", 1.0)

                        increase_alpha()

                    def inject_btn_function():
                        drives = get_all_drives()
                        # print(drives)
                        drives = [
                            "A:/",
                            "B:/",
                            "C:/",
                            "D:/",
                            "E:/",
                            "F:/",
                            "G:/",
                            "H:/",
                            "I:/",
                            "J:/",
                            "K:/",
                            "L:/",
                            "M:/",
                            "N:/",
                            "O:/",
                            "P:/",
                            "Q:/",
                            "R:/",
                            "S:/",
                            "T:/",
                        ]
                        if not self.output_visible:
                            create_outputbox_set()
                            self.output_box.pack(
                                side="top", padx=10, pady=5, anchor="ne"
                            )
                            self.scrollable_inject_btn.place(relx=0.710, rely=0.500)
                            # self.main_btn_infect_canvas.place(relx=0.400, rely=0.500)
                            for drive in drives:
                                current_driver_infection = False

                                ### TEMPORARY
                                infect_them_btn_function()
                                self.infect_them_btn.configure(
                                    text=f"INFECT Disk {drive[:1]}:/"
                                )
                                self.infect_them_btn.pack(side="top", pady=5, padx=5)

                                ###
                                try:
                                    for item in Path(drive).iterdir():
                                        if (
                                            item.is_file()
                                            and item.suffix == ".json"
                                            and "agent_disk" in str(item)
                                        ):
                                            current_driver_infection = True
                                            current_agent_file_path = item
                                        else:
                                            pass
                                    if not current_driver_infection:
                                        self.output_box.insert(
                                            "end", f"Drive {drive} is not infected\n"
                                        )
                                        # infect_them_btn_function()
                                        # self.infect_them_btn.configure(
                                        #     text=f"INFECT Disk {drive[:1]}:/"
                                        # )
                                        # self.infect_them_btn.pack(
                                        #     side="top", pady=5, padx=5
                                        # )

                                    else:
                                        self.output_box.insert(
                                            "end",
                                            f"Drive {drive[:1]} is already infected with the file : {current_agent_file_path}\n",
                                        )
                                        # infect_them_btn_function()
                                        # self.infect_them_btn.configure(
                                        #     text=f"INFECT {drive[:1]}"
                                        # )
                                        # self.infect_them_btn.pack(
                                        #     side="top", pady=5, padx=5
                                        # )
                                except Exception as e:
                                    pass
                                    # print(
                                    #     f"The HARD DRIVE {drive} doesn't seems to exist or be connect\n"
                                    # )
                        else:
                            try:
                                self.output_box.destroy()
                                self.scrollable_inject_btn.place_forget()
                            except Exception as e:
                                print(f"Error {e}")

                        self.output_visible = not self.output_visible

                        # for drive in self.all_drives_temp:
                        #     if drive.split("/")[0] not in self.disk_hidden:
                        #         self.all_drives.append(drive)
                        # print(self.all_drives)

                    def get_all_drives():
                        drives = []
                        bitmask = windll.kernel32.GetLogicalDrives()
                        for i in range(26):
                            if bitmask & (1 << i):
                                drives.append(f"{string.ascii_uppercase[i]}:/")
                        return drives

                    self.after(300, reveal_and_fade)

            self.canvas.bind(
                "<Button-1>",
                lambda event: window_state_function(),
            )
            threading.Thread(target=rotate_icon_forever, daemon=True).start()

        btn_options_function(self)
        # endregion

        self.after(
            500, lambda: self.force_foreground_window("Ultimate Disk Dominator™")
        )
        # self.attributes("-topmost", 1)  # Stay on top
        self.after(200, self.reveal_and_fade)

    def open_directory(self, path):
        if os.path.isfile(path):
            subprocess.run(["explorer", "/select,", os.path.normpath(path)])
        elif os.path.isdir(path):
            os.startfile(path)

    def on_button_click(self, name):
        print(f"You clicked on: {name}")

    # region Ressource Path Function
    def ressource_path(self, relative_path):
        try:
            base_path = getattr(sys, "_MEIPASS", os.getcwd())
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    # endregion

    # region Clear Seach Input Fonction
    def clear_search_input(self, vent=None):
        self.search_input_var.set("")  # Clear the StringVar

    # endregion

    def truncate_middle(self, text, max_length=30):
        if len(text) <= max_length:
            return text
        part_length = (max_length - 3) // 2
        return text[:part_length] + "..." + text[-part_length:]

    def force_foreground_window(self, title):
        shell = win32com.client.Dispatch("WScript.Shell")
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            shell.SendKeys("%")  # Send ALT key (required for foreground change)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)

    def quit_program(self, event=None):
        self.destroy()

    def reveal_and_fade(self):
        self.deiconify()  # Now show the window
        self.fade_in()

    def fade_in(self):
        alpha = 0.0
        increment = 0.05
        delay = 10  # milliseconds

        def increase_alpha():
            nonlocal alpha
            alpha += increment
            if alpha <= 1.0:
                self.wm_attributes("-alpha", alpha)
                self.after(delay, increase_alpha)
            else:
                self.wm_attributes("-alpha", 1.0)

        increase_alpha()


if __name__ == "__main__":
    app = Disk_Management()
    app.mainloop()
