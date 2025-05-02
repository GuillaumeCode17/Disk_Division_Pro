### Main Title Module
import customtkinter as ctk

def title_module(master):
    # Title bar
    master.title_bar = ctk.CTkFrame(
        master, height=60, fg_color="#111111", corner_radius=0
    )
    master.title_bar.pack(fill="x", side="top")

    # Title label with glow vibe
    master.title_label = ctk.CTkLabel(
        master.title_bar,
        text="💾 Ultimate Disk Dominator™",
        font=("Orbitron", 24, "bold"),
        text_color="#03A9F4",  # Neon cyan
    )
    master.title_label.place(relx=0.5, rely=0.5, anchor="center")

    # Search label
    master.search_box_label = ctk.CTkLabel(
        master, text="Search Box :", font=("Segoe UI", 20)
    )
    master.search_box_label.place(relx=0.010, rely=0.130)
