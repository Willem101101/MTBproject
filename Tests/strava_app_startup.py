# packages
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import webbrowser
import requests
import time
import socket
from threading import Timer
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# global variables
strava_color = "#FC4C02"
user_info = {}
firebase_initialized = False
t = Timer


# functions
def test_connection():
    global firebase_initialized
    try:
        socket.create_connection(("Google.com", 80))
        if not firebase_initialized:
            cred = credentials.Certificate("strava_challenges_app_key.json")
            firebase_admin.initialize_app(cred, {
                "databaseURL": "https://strava-challenges-app.firebaseio.com/"
            })
            firebase_initialized = True
        return True
    except OSError:
        return False


def startup_screen(import_message=False, text="", delay=0, color=""):
    # screen settings
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.iconbitmap("strava_challenges_icon.ico")
    root.title("Strava challenges")
    root.geometry("700x500+" + str(int((screen_width / 2) - 350)) + "+" + str(int((screen_height / 2) - 250)))
    root.configure(bg=strava_color)
    root.resizable(width=False, height=False)
    root.attributes("-topmost", True)
    root.focus_force()

    # functions
    def message(text_, delay_, color_):
        global t

        def delete_message():
            try:
                label_message.place_forget()
            except tk.TclError:
                pass
            except RuntimeError:
                pass

        label_message.configure(text=text_, fg=color_)
        label_message.place(width=300, height=25, x=200, y=150)
        t = Timer(delay_, delete_message)
        t.start()

    def registration():
        if test_connection():
            root.destroy()
            registration_screen()
        else:
            print("No internet connection")
            message("No internet connection", 3, "red")

    def login():
        if test_connection():
            root.destroy()
            login_screen()
        else:
            print("No internet connection")
            message("No internet connection", 3, "red")

    def leave():
        global t
        if t is not None:
            t.cancel
        root.destroy()

    # screen widgets
    label_login = tk.Label(
        root, text="Strava Challenges", bg=strava_color, fg="indigo", font="Trebuchet 30"
    ).place(width=350, height=50, x=175, y=100)
    button_registration = tk.Button(
        root, text="Registration", bg="white", font="Trebuchet", command=registration
    ).place(width=150, height=50, x=275, y=199)
    button_login = tk.Button(
        root, text="Login", bg="white", font="Trebuchet", command=login
    ).place(width=150, height=50, x=275, y=251)
    label_message = tk.Label(root, text="No internet connection", bg="white", fg="red", font="Trebuchet")
    button_quit = tk.Button(
        root, text="Quit Strava Challenges", bg="white", fg="black", command=leave
    ).place(x=0, y=475)

    # widget actions
    if import_message:
        message(text, delay, color)

    # show screen
    tk.mainloop()


def registration_screen():
    # screen settings
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.iconbitmap("strava_challenges_icon.ico")
    root.title("Strava challenges registration")
    root.geometry("350x450+" + str(int((screen_width / 7) - 165)) + "+" + str(int((screen_height / 2) - 225)))
    root.configure(bg=strava_color)
    root.resizable(width=False, height=False)
    root.attributes("-topmost", True)
    root.focus_force()

    # variables
    account_name = tk.StringVar()
    url = tk.StringVar()
    password = tk.StringVar()
    confirm_password = tk.StringVar()

    # functions
    def open_auth_page():
        auth_page_url = "https://www.strava.com/oauth/authorize?client_id=48127&response_type" \
                        "=code&redirect_uri=http://url-to-paste&approval_prompt=force"
        webbrowser.open(auth_page_url, new=0, autoraise=True)

    def label_acc_message(message, color):
        account_name.set(message)
        label_account_name.configure(fg=color)

    def url_to_name(event):
        if test_connection():
            if len(str(entry_url.get())) == 84:
                global user_info
                code = str(entry_url.get())[33:-11]
                params = {
                    "client_id": 48127,
                    "client_secret": "30a93b55c8231833e4f4ad98fb64e871689dc1c9",
                    "code": code,
                    "grant_type": "authorization_code"
                }
                user_info = requests.post("https://www.strava.com/oauth/token", params=params)
                if user_info.status_code == 200:
                    account_info = user_info
                    label_acc_message(user_info.json()["athlete"]["username"], "black")
                    entry_password.configure(state="normal")
                    entry_confirm_password.configure(state="normal")
                    entry_password.focus()
                else:
                    label_acc_message("Url not correct", "red")
            else:
                label_acc_message("Url not correct", "red")
        else:
            cancel(True, "No internet connection", 3, "red")

    def clear_password(message):
        entry_password.delete(0, "end")
        entry_confirm_password.delete(0, "end")
        entry_password.focus_displayof()
        entry_password.configure(show="", fg="red")
        entry_password.insert(0, message)
        button_done.focus()

    def add_account(event=None):
        if len(entry_password.get()) == 0:
            clear_password("No password entered")
        elif len(entry_password.get()) <= 3:
            clear_password("Password too short")
        elif entry_password.get() != entry_confirm_password.get():
            clear_password("Passwords don't match")
        else:
            ref = db.reference("Users")
            if ref.get() is not None and account_name.get() in dict(ref.get()).keys():
                cancel(True, "Account already registered", 3, "red")
            else:
                ref.child(user_info.json()["athlete"]["username"].lower()).set({
                    "password": password.get(),
                    "refresh_token": user_info.json()["refresh_token"],
                    "access_token": user_info.json()["access_token"]
                })
                with open("../local_users.file", "r+") as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write(str(user_info.json()["athlete"]["username"]).lower() + "\n" + content)
                    del content
                root.destroy()
                startup_screen(True, "Account added", 3, "blue")
                print("Account added")

    def password_focus(event):
        entry_password.delete(0, "end")
        entry_confirm_password.delete(0, "end")
        entry_password.configure(show="*", fg="black")

    def cancel(import_message=False, text="", delay=0, color=""):
        root.destroy()
        startup_screen(import_message, text, delay, color)

    # screen widgets
    frame_auth = tk.LabelFrame(
        root, text="Authorization", bg=strava_color, fg="white", font="Trebuchet 14"
    ).place(width=325, height=163, x=12.5, y=0)
    frame_account = tk.LabelFrame(
        root, text="Create account", bg=strava_color, fg="white", font="Trebuchet 14"
    ).place(width=325, height=188, x=12.5, y=163)
    label_auth_exp = tk.Label(
        frame_auth, text="Go to the authorization page\nto registrate your strava account.",
        bg=strava_color, fg="white", font="Trebuchet 15", justify="center").place(width=300, height=50, x=25, y=25)
    button_auth_page = tk.Button(
        frame_auth, text="Authorization page", bg="white", fg="black", command=open_auth_page
    ).place(width=300, height=25, x=25, y=75)
    label_url_exp = tk.Label(
        frame_auth, text="Paste the redirected url + enter.", bg=strava_color, fg="white", font="Trebuchet 15",
        justify="center").place(width=300, height=25, x=25, y=100)
    entry_url = tk.Entry(frame_auth, justify="center", font="Trebuchet 12", textvariable=url)
    label_username = tk.Label(
        frame_account, text="Username", bg=strava_color, fg="white", font="Trebuchet 15", justify="center"
    ).place(width=300, height=25, x=25, y=188)
    label_account_name = tk.Label(
        frame_account, textvariable=account_name, bg="white", fg="black", font="Trebuchet 12", justify="center")
    label_enter_password = tk.Label(
        frame_account, text="Enter a password", bg=strava_color, fg="white", font="Trebuchet 15", justify="center"
    ).place(width=300, height=25, x=25, y=238)
    entry_password = tk.Entry(
        frame_account, justify="center", font="Trebuchet 12", textvariable=password, state="disabled",
        disabledbackground="gray", show="*")
    label_confirm_password = tk.Label(
        frame_account, text="Confirm your password", bg=strava_color, fg="white", font="Trebuchet 15", justify="center"
    ).place(width=300, height=25, x=25, y=288)
    entry_confirm_password = tk.Entry(
        frame_account, justify="center", font="Trebuchet 12", textvariable=confirm_password, state="disabled",
        disabledbackground="gray", show="*")
    button_done = tk.Button(root, text="Create account", bg="white", fg="black", font="Trebuchet", command=add_account)
    button_cancel = tk.Button(root, text="Cancel", bg="white", fg="black", command=cancel).place(x=0, y=425)

    # widget actions
    entry_url.bind("<Return>", url_to_name)
    entry_url.place(width=300, height=25, x=25, y=125)
    label_acc_message("No url entered", "red")
    label_account_name.place(width=300, height=25, x=25, y=213)
    entry_password.bind("<FocusIn>", password_focus)
    entry_password.place(width=300, height=25, x=25, y=263)
    entry_confirm_password.bind("<Return>", add_account)
    entry_confirm_password.place(width=300, height=25, x=25, y=313)
    button_done.place(width=300, height=37, x=25, y=375)

    # show screen
    tk.mainloop()


def login_screen():
    # screen settings
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.iconbitmap("strava_challenges_icon.ico")
    root.title("Strava challenges login")
    root.geometry("350x200+" + str(int((screen_width / 2) - 175)) + "+" + str(int((screen_height / 2) - 100)))
    root.configure(bg=strava_color)
    root.resizable(width=False, height=False)
    root.attributes("-topmost", True)
    root.focus_force()

    # variables
    with open("../local_users.file", "r") as f:
        options = f.read().splitlines()
    username = tk.StringVar()
    password = tk.StringVar()

    # functions
    def entry_password_message(message):
        password.set(message)
        entry_password.configure(fg="red", show="")
        combobox_username.focus_force()

    def entry_password_clear(event):
        password.set("")
        entry_password.configure(fg="black", show="*")

    def login(event=None):
        ref = db.reference("Users")
        if username.get() not in dict(ref.get()).keys():
            entry_password_message("User does not exist")
        elif password.get() != ref.child(username.get()).child("password").get():
            entry_password_message("Password is not correct")
        else:
            with open("../local_users.file", "r") as f:
                content = f.readlines()
                user = content.pop(content.index(username.get() + "\n"))
                content.insert(0, user)
            with open("../local_users.file", "w") as f:
                f.writelines(content)
            print("Logged in")
            pass

    def cancel(import_message=False, text="", delay=0, color=""):
        root.destroy()
        startup_screen(import_message, text, delay, color)

    # screen widgets
    frame_login = tk.LabelFrame(root, text="Login", font="Trebuchet 15", bg=strava_color, fg="white").place(width=300)
    label_username = tk.Label(
        root, text="Username", bg=strava_color, fg="white", font="Trebuchet 15", justify="center"
    ).place(width=300, height=25, x=25, y=0)
    combobox_username = ttk.Combobox(root, values=options, textvariable=username, font="Trebuchet 15", justify="center")
    label_password = tk.Label(
        root, text="Password", bg=strava_color, fg="white", font="Trebuchet 15", justify="center"
    ).place(width=300, height=25, x=25, y=50)
    entry_password = tk.Entry(root, textvariable=password, font="Trebuchet 15", show="*", justify="center")
    button_login = tk.Button(
        root, text="Log in", font="Trebuchet 15", justify="center", bg="white", fg="black", command=login
        ).place(width=300, height=50, x=25, y=112)
    button_cancel = tk.Button(root, text="Cancel", bg="white", fg="black", command=cancel).place(x=0, y=175)

    # widget actions
    with open("../local_users.file", "r") as f:
        if f.read().strip("\n ") != "":
            combobox_username.current(0)
    combobox_username.place(width=300, height=25, x=25, y=25)
    entry_password.bind("<FocusIn>", entry_password_clear)
    entry_password.bind("<Return>", login)
    entry_password.place(width=300, height=25, x=25, y=75)

    # show screen
    root.mainloop()


def main_screen():
    # screen settings
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.iconbitmap("strava_challenges_icon.ico")
    root.title("Strava challenges")
    root.configure(bg="white")
    root.geometry(str(screen_width) + "x" + str(screen_height))
    root.state("zoomed")
    root.focus_force()

    # variables

    # functions
    def dropdown1_1():
        pass

    # widgets
    frame_dropmenu = tk.Frame(root, bg=strava_color).place(width=root.winfo_width(), height=50, x=0, y=0)
    dropdown1 = tk.Button(frame_dropmenu, bg=strava_color, fg="white", text="dropdownbutton", command=dropdown1_1)

    # widget actions
    dropdown1.place(width=100, height=50, x=0, y=0)

    # show screen
    root.mainloop()


# start app
startup_screen()
# main_screen()
