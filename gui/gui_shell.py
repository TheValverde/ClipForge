# gui_shell.py

import tkinter as tk
from tkinter import ttk
from .comprehensive_app import ComprehensiveApp  # relative import from the same package

def main():
    root = tk.Tk()
    root.title("Clip Farming Tool - Dark Mode")

    style = ttk.Style(root)

    # 1) Create a custom dark theme for ttk widgets
    style.theme_create("DarkTheme", parent="clam", settings={
        "TFrame": {
            "configure": {
                "background": "#2B2B2B",
                "borderwidth": 0,
                "relief": "flat",
            }
        },
        "TNotebook": {
            "configure": {
                "background": "#2B2B2B",
                "tabmargins": [2, 5, 2, 0],
                "borderwidth": 0,
                "relief": "flat",
                "highlightthickness": 0,
            }
        },
        "TNotebook.Tab": {
            "configure": {
                "padding": [10, 5],
                "background": "#2B2B2B",
                "foreground": "#FFFFFF",
                "borderwidth": 0,
                "relief": "flat",
                "focuscolor": "",
            },
            "map": {
                "background": [("selected", "#3C3F41")],
                "foreground": [("selected", "#FFFFFF")],
                "focuscolor": [("focus", "")],
            }
        },
        "TButton": {
            "configure": {
                "background": "#3C3F41",
                "foreground": "#FFFFFF",
                "padding": 6,
                "borderwidth": 0,
                "relief": "flat",
                "focuscolor": "",
            },
            "map": {
                "background": [("active", "#444444")],
                "foreground": [("active", "#FFFFFF")],
                "focuscolor": [("focus", "")],
            }
        },
        "TCheckbutton": {
            "configure": {
                "background": "#2B2B2B",
                "foreground": "#FFFFFF",
                "focuscolor": "",
                "borderwidth": 0,
            }
        },
        "TCombobox": {
            "configure": {
                "selectbackground": "#3C3F41",
                "fieldbackground": "#3C3F41",
                "background": "#3C3F41",
                "foreground": "#FFFFFF",
                "arrowsize": 16,
                "relief": "flat",
                "borderwidth": 0,
            }
        },
        "TScale": {
            "configure": {
                "background": "#2B2B2B",
                "borderwidth": 0,
                "relief": "flat",
            }
        },
        "TProgressbar": {
            "configure": {
                "background": "#3C3F41",
                "troughcolor": "#2B2B2B",
                "borderwidth": 0,
                "relief": "flat",
            }
        },
        "TLabel": {
            "configure": {
                "background": "#2B2B2B",
                "foreground": "#FFFFFF",
                "borderwidth": 0,
                "relief": "flat",
            }
        },
    })

    # 2) Activate the custom theme
    style.theme_use("DarkTheme")

    # 3) Apply dark defaults for classic Tk widgets (Spinbox, Text, Canvas, etc.)
    root.option_add("*Background", "#2B2B2B")
    root.option_add("*Foreground", "#FFFFFF")
    root.option_add("*Button.Background", "#3C3F41")
    root.option_add("*Button.Foreground", "#FFFFFF")
    root.option_add("*Entry.Background", "#3C3F41")
    root.option_add("*Entry.Foreground", "#FFFFFF")
    root.option_add("*Spinbox.Background", "#3C3F41")
    root.option_add("*Spinbox.Foreground", "#FFFFFF")
    root.option_add("*Text.Background", "#3C3F41")
    root.option_add("*Text.Foreground", "#FFFFFF")
    root.option_add("*Canvas.Background", "#2B2B2B")
    root.option_add("*selectBackground", "#5C5F61")  # highlight color for selected text
    root.option_add("*selectForeground", "#FFFFFF")
    root.configure(bg="#2B2B2B")

    # 4) Instantiate the main app container and run
    app = ComprehensiveApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
