from tkinter import ttk, Menu

# IP_Addr = get("https://api.ipify.org").content.decode("utf8")
# options.add_argument('headless')


class Graphic:
    def __init__(self, main):
        super().__init__()

        # MENU INIT __--:
        menubar = Menu(main)
        # notebook = ttk.Notebook(self, cursor="hand2")
        main.configure(
            bg="black",
            highlightbackground="#696969",
            highlightthickness=0,
            highlightcolor="#f5f5f5",
            menu=menubar,
        )
        main.style = ttk.Style()
        main.style.theme_create(
            "Cloud",
            settings={
                ".": {
                    "configure": {"background": "#aeb0ce", "font": "red"}
                },  # All colors except for active tab-button
                "TNotebook": {
                    "configure": {
                        "background": "black",  # color behind the notebook
                        "tabmargins": [
                            0,
                            10,
                            0,
                            0,
                        ],  # [left margin, upper margin, right margin, margin beetwen tab and frames]
                    }
                },
                "TNotebook.Tab": {
                    "configure": {
                        "background": "grey",  # Color of non selected tab-button
                        "padding": [
                            5,
                            2,
                        ],  # [space beetwen text and horizontal tab-button border, space between text and vertical tab_button border]
                        "font": "white",
                        "configure": {"foreground": "white"},
                    },
                    "map": {
                        "foreground": [("selected", "white"), ("!disabled", "grey")],
                        "background": [
                            ("selected", "#00293d"),
                            ("!disabled", "#004353"),
                        ],
                        "font": [
                            ("selected", "Times 14 bold"),
                            ("!disabled", "Times 10"),
                        ],
                    },
                },
                # "Horizontal.TProgressbar": {
                #     "configure": {
                #         "background": "#1e90ff",
                #         "troughcolor": "black",
                #         "thickness": 25,
                #         "padding": [2, 2],
                #     }
                # },
            },
        )

        main.style.theme_use("Cloud")
