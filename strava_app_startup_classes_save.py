# packages
import tkinter as tk
from tkinter import ttk
import webbrowser
import requests
import time
from threading import Timer
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# global variables
strava_color = "#FC4C02"
user_info = {}
firebase_initialized = False
t = Timer
label_message = tk.Label
logged_in_user = ""


# classes
class Roots(tk.Tk):
	def __init__(self, title, size, relx, rely, resizable, topmost):
		super(Roots, self).__init__()
		self.screen_width = int(self.winfo_screenwidth())
		self.screen_height = int(self.winfo_screenheight())
		self.iconbitmap("strava_challenges_icon.ico")
		self.title(title)
		self.geometry(f"{size}+{int((self.screen_width - int(size[:size.find('x')])) * relx)}+"
					  f"{int((self.screen_height - int(size[size.find('x') + 1:])) * rely)}")
		self.resizable(width=resizable, height=resizable)
		self.attributes("-topmost", topmost)
		self.focus_force()

	@staticmethod
	def message(text="", delay=0, color=""):
		global t
		global label_message

		def delete_message():
			try:
				label_message.place_forget()
			except tk.TclError:
				pass
			except RuntimeError:
				pass

		label_message.configure(text=text, fg=color)
		label_message.place(width=300, height=25, x=200, y=150)
		t = Timer(delay, delete_message)
		t.start()


root_startup = Roots("Strava challenges", "700x500", 0.5, 0.5, False, True)


class Toplevels(tk.Toplevel):
	global root_startup

	def __init__(self, title, size, relx, rely, resizable, topmost):
		super(Toplevels, self).__init__(root_startup)
		self.screen_width = int(self.winfo_screenwidth())
		self.screen_height = int(self.winfo_screenheight())
		self.iconbitmap("strava_challenges_icon.ico")
		self.title(title)
		if size == "max":
			self.state("zoomed")
			self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
		else:
			self.geometry(f"{size}+{int((self.screen_width - int(size[:size.find('x')])) * relx)}+"
						  f"{int((self.screen_height - int(size[size.find('x') + 1:])) * rely)}")
		self.resizable(width=resizable, height=resizable)
		self.attributes("-topmost", topmost)
		self.focus_force()
		self.protocol("WM_DELETE_WINDOW", self.on_close)

	def on_close(self):
		self.destroy()
		root_startup.deiconify()


class Labels(tk.Label):
	def __init__(self, master, text, bg, fg, font, width, height, x, y):
		super(Labels, self).__init__(master)
		self.configure(text=text, bg=bg, fg=fg, font=font, justify="center")
		self.place(width=width, height=height, x=x, y=y)


class VariableLabels(tk.Label):
	def __init__(self, master, textvariable, bg, fg, font, width, height, x, y):
		super(VariableLabels, self).__init__(master)
		self.configure(textvariable=textvariable, bg=bg, fg=fg, font=font, justify="center")
		self.place(width=width, height=height, x=x, y=y)
		self.textvariable_name = textvariable


class Buttons(tk.Button):
	def __init__(self, master, text, bg, fg, font, command, width, height, x, y):
		super(Buttons, self).__init__(master)
		self.configure(text=text, bg=bg, fg=fg, font=font, command=command)
		self.place(width=width, height=height, x=x, y=y)
		self.bg = bg

	def enter(self, color):
		self.configure(bg=color)

	def leave(self, _):
		self.configure(bg=self.bg)

	def hover(self, color):
		self.bind("<Enter>", lambda event: self.enter(color))
		self.bind("<Leave>", self.leave)


class Entries(tk.Entry):
	def __init__(self, master, textvariable, font, width, height, x, y, show="", state="normal"):
		super(Entries, self).__init__(master)
		self.configure(textvariable=textvariable, font=font, justify="center", show=show, state=state)
		self.place(width=width, height=height, x=x, y=y)
		if state == "disabled":
			self.configure(disabledbackground="gray")

	def password_focus(self, _):
		self.delete(0, "end")
		self.configure(show="*", fg="black")

	def clear_entry(self, message=""):
		self.bind("<FocusIn>", self.password_focus)
		self.delete(0, "end")
		self.master.focus_force()
		self.configure(show="", fg="red")
		self.insert(0, message)


class Frames(tk.Frame):
	def __init__(self, master, bg, width, height, x, y):
		super(Frames, self).__init__(master)
		self.configure(bg=bg)
		if width == "fill":
			width = self.master.winfo_width()
		if height == "fill":
			height = self.master.winfo_height()
		self.place(width=width, height=height, x=x, y=y)


class LabelFrames(tk.LabelFrame):
	def __init__(self, master, text, bg, fg, font, width, height, x, y):
		super(LabelFrames, self).__init__(master)
		self.configure(text=text, bg=bg, fg=fg, font=font)
		self.place(width=width, height=height, x=x, y=y)


class ComboBoxes(ttk.Combobox):
	def __init__(self, master, textvariable, font, values, width, height, x, y):
		super(ComboBoxes, self).__init__(master)
		self.configure(textvariable=textvariable, font=font, values=values, justify="center")
		self.place(width=width, height=height, x=x, y=y)


class DropdownButtons(Frames):
	def __init__(self, master, bg, width, height, x, y, text, fg, font, dropdown_button_list):
		super(DropdownButtons, self).__init__(master, bg, width, height, x, y)
		self.label = Labels(self, text, bg, fg, font, width, height, 0, 0)
		self.label.configure(borderwidth=1, relief="solid")
		self.dropdown_buttons = []
		self.width = width
		self.height = height
		self.bg = bg

		for index, button in enumerate(dropdown_button_list, 2):
			self.dropdown_buttons.append(Buttons(self, button[0], bg, fg, font, button[1], self.width, 25, 0, 25*int(index)))
			self.place_configure(height=25 * int(index))
		self.bind("<Enter>", self.show_buttons)
		self.bind("<Leave>", self.hide_buttons)
		self.hide_buttons()

	def hide_buttons(self, _=None):
		self.place_configure(height=self.height)
		for dropdown_button in self.dropdown_buttons:
			dropdown_button.place_forget()

	def show_buttons(self, _=None):
		for index, dropdown_button in enumerate(self.dropdown_buttons, 2):
			dropdown_button.place(width=self.width, height=25, x=0, y=25*int(index))
			self.place_configure(height=25 + 25 * int(index))

	def enter(self, color):
		self.show_buttons()
		self.label.configure(bg=color)

	def leave(self, _):
		self.hide_buttons()
		self.label.configure(bg=self.bg)

	def hover(self, color):
		self.bind("<Enter>", lambda event: self.enter(color))
		self.bind("<Leave>", self.leave)


# functions
def test_connection():
	global firebase_initialized
	try:
		requests.get("https://google.com", timeout=5)
		print("Connected")
		if not firebase_initialized:
			cred = credentials.Certificate("strava_challenges_app_key.json")
			firebase_admin.initialize_app(cred, {
				"databaseURL": "https://strava-challenges-app.firebaseio.com/"
			})
			firebase_initialized = True
		return True
	except requests.ConnectionError:
		return False


def startup_screen():
	global root_startup
	global label_message
	# screen settings
	root_startup.configure(bg=strava_color)

	def registration():
		if test_connection():
			root_startup.withdraw()
			registration_screen()
		else:
			print("No internet connection")
			root_startup.message("No internet connection", 3, "red")

	def login():
		if test_connection():
			root_startup.withdraw()
			login_screen()
		else:
			print("No internet connection")
			root_startup.message("No internet connection", 3, "red")

	def leave():
		global t
		if t is not None:
			t.cancel
		root_startup.destroy()

	# screen widgets
	label_login = Labels(root_startup, "Strava Challenges", strava_color, "indigo", "Trebuchet 30", 350, 50, 175, 100)
	button_registration = Buttons(root_startup, "Registration", "white", "black", "Trebuchet 15", registration, 150, 50,
								  275, 199)
	button_login = Buttons(root_startup, "Login", "white", "black", "Trebuchet 15", login, 150, 50, 275, 251)
	label_message = tk.Label(root_startup, text="No internet connection", bg="white", fg="red", font="Trebuchet")
	button_quit = Buttons(root_startup, "Quit strava Challenges", "white", "black", None, leave, None, None, 0, 475)

	# widget actions

	# show screen
	root_startup.mainloop()


def registration_screen():
	# screen settings
	root_regis = Toplevels("Strava Challenges registration", "350x450", 1 / 20, 0.5, False, True)
	root_regis.configure(bg=strava_color)

	# variables
	account_name = tk.StringVar()
	url = tk.StringVar()
	password = tk.StringVar()
	confirm_password = tk.StringVar()

	# functions
	def open_auth_page():
		auth_page_url = "https://www.strava.com/oauth/authorize?client_id=48127&response_type" \
						"=code&redirect_uri=http://url-to-paste&response_type=code&scope=activity:read_all"
		webbrowser.open(auth_page_url, new=0, autoraise=True)

	def message_acc_label(message, color):
		account_name.set(message)
		label_account_name.configure(fg=color)

	def url_to_name(_):
		if test_connection():
			if len(str(entry_url.get())) == 102:
				global user_info
				code = str(entry_url.get())[33:-29]
				params = {
					"client_id": 48127,
					"client_secret": "30a93b55c8231833e4f4ad98fb64e871689dc1c9",
					"code": code,
					"grant_type": "authorization_code"
				}
				user_info = requests.post("https://www.strava.com/oauth/token", params=params)
				if user_info.status_code == 200:
					message_acc_label(user_info.json()["athlete"]["username"], "black")
					entry_password.configure(state="normal")
					entry_password_confirm.configure(state="normal")
					entry_password.focus()
				else:
					message_acc_label("Url not correct", "red")
			else:
				message_acc_label("Url not correct", "red")
		else:
			cancel(True, "No internet connection", 3, "red")

	def clear_password(message):
		entry_password.clear_entry(message)
		entry_password_confirm.clear_entry()

	def add_account(_=None):
		if len(entry_password.get()) == 0:
			clear_password("No password entered")
		elif len(entry_password.get()) <= 3:
			clear_password("Password too short")
		elif entry_password.get() != entry_password_confirm.get():
			clear_password("Passwords don't match")
		else:
			ref = db.reference("Users")
			if ref.get() is not None and account_name.get() in dict(ref.get()).keys():
				cancel(True, "Account already registered", 3, "red")
			else:
				ref.child(user_info.json()["athlete"]["username"].lower()).set({
					"password": password.get(),
					"refresh_token": user_info.json()["refresh_token"],
					"access_token": user_info.json()["access_token"],
					"id": user_info.json()["athlete"]["id"]
				})
				with open("local_users.file", "r+") as f:
					content = f.read()
					f.seek(0, 0)
					f.write(str(user_info.json()["athlete"]["username"]).lower() + "\n" + content)
					del content
				root_regis.destroy()
				root_startup.deiconify()
				root_startup.message("Account created", 3, "blue")
				print("Account added")

	def cancel(import_message=False, text="", delay=0, color=""):
		root_regis.destroy()
		root_startup.deiconify()
		if import_message:
			root_startup.message(text, delay, color)

	# screen widgets
	frame_auth = LabelFrames(root_regis, "Authorization", strava_color, "white", "Trebuchet 14", 325, 163, 12.5, 0)
	frame_account = LabelFrames(root_regis, "Create account", strava_color, "white", "Trebuchet 14", 325, 188, 12.5,
								163)
	label_auth_expl = Labels(frame_auth, "Go to the authorization page\nto register your strava account.",
							 strava_color, "white", "Trebuchet 15", 300, 50, 12.5, 0)
	button_auth_page = Buttons(frame_auth, "Authorization page", "white", "black", "Trebuchet", open_auth_page, 300, 25, 12.5,
							   50)
	label_url_expl = Labels(frame_auth, "Paste the redirected url + enter.", strava_color, "white", "Trebuchet 15", 300,
							25, 12.5, 75)
	entry_url = Entries(frame_auth, url, "Trebuchet 12", 300, 25, 12.5, 100)
	label_username = Labels(frame_account, "Username", strava_color, "white", "Trebuchet 15", 300, 25, 12.5, 0)
	label_account_name = VariableLabels(frame_account, account_name, "white", "black", "Trebuchet 12", 300, 25, 12.5,
										25)
	label_password = Labels(frame_account, "Enter a password", strava_color, "white", "Trebuchet 15", 300, 25, 12.5, 50)
	entry_password = Entries(frame_account, password, "Trebuchet 12", 300, 25, 12.5, 75, "*", "disabled")
	label_password_confirm = Labels(frame_account, "Confirm your password", strava_color, "white", "Trebuchet 15", 300,
									25, 12.5, 100)
	entry_password_confirm = Entries(frame_account, confirm_password, "Trebuchet 12", 300, 25, 12.5, 125, "*",
									 "disabled")
	button_create_account = Buttons(root_regis, "Create account", "white", "black", "Trebuchet 15", add_account, 300, 50,
									25, 363)
	button_cancel = Buttons(root_regis, "Cancel", "white", "black", None, cancel, None, None, 0, 425)

	# widget actions
	entry_url.bind("<Return>", url_to_name)
	message_acc_label("No url entered", "red")
	entry_password_confirm.bind("<Return>", add_account)


def login_screen():
	# screen settings
	root_login = Toplevels("Strava challenges login", "350x237", 0.5, 0.5, False, True)
	root_login.configure(bg=strava_color)

	# variables
	with open("local_users.file", "r") as f:
		options = f.read().splitlines()
	username = tk.StringVar()
	password = tk.StringVar()

	def login(_=None):
		ref = db.reference("Users")
		if username.get() not in dict(ref.get()).keys():
			entry_password.clear_entry("User does not exist")
		elif password.get() != ref.child(username.get()).child("password").get():
			entry_password.clear_entry("Password is not correct")
		else:
			global logged_in_user
			if username.get() not in options:
				options.insert(0, username.get())
			user = options.pop(options.index(username.get()))
			options.insert(0, user)
			with open("local_users.file", "w") as f:
				f.writelines(option + "\n" for option in options)
				options.insert(0, username.get())
			logged_in_user = username.get()
			print("Logged in")
			root_login.destroy()
			main_screen()

	def cancel(import_message=False, text="", delay=0, color=""):
		root_login.destroy()
		root_startup.deiconify()
		if import_message:
			root_startup.message(text, delay, color)

	# screen widgets
	frame_login = LabelFrames(root_login, "Login", strava_color, "white", "Trebuchet 15", 325, 200, 12.5, 0)
	label_username = Labels(frame_login, "Username", strava_color, "white", "Trebuchet 15", 300, 25, 12.5, 0)
	combobox_username = ComboBoxes(frame_login, username, "Trebuchet 15", options, 300, 25, 12.5, 25)
	label_password = Labels(frame_login, "Password", strava_color, "white", "Trebuchet 15", 300, 25, 12.5, 50)
	entry_password = Entries(frame_login, password, "Trebuchet 15", 300, 25, 12.5, 75, "*")
	button_login = Buttons(frame_login, "Log in", "white", "black", "Trebuchet 15", login, 300, 50, 12.5, 112)
	button_cancel = Buttons(root_login, "Cancel", "white", "black", None, cancel, None, None, 0, 212)

	# widget actions
	entry_password.bind("<FocusIn>", entry_password.password_focus)
	entry_password.bind("<Return>", login)
	with open("local_users.file", "r") as f:
		if f.read().strip("\n ") != "":
			combobox_username.current(0)

	# show screen
	root_login.mainloop()


def main_screen():
	# screen settings
	root_main = Toplevels("Strava Challenges", "max", 0, 0, True, False)
	root_main.configure(bg="white")

	# variables

	# functions
	def access_token():
		ref = db.reference("Users")
		refresh_token = ref.child(f"{logged_in_user}/refresh_token").get()

		params = {
			"client_id": 48127,
			"client_secret": "30a93b55c8231833e4f4ad98fb64e871689dc1c9",
			"grant_type": "refresh_token",
			"refresh_token": refresh_token
		}
		_access_token = dict(requests.post("https://www.strava.com/oauth/token", params=params).json())["access_token"]
		ref.child(f"{logged_in_user}/access_token").update({"access_token": _access_token})
		print(_access_token)
		return _access_token

	def challenge_create(_=None):
		ref = db.reference("Users")
		_id = ref.child(f"{logged_in_user}/id").get()
		params = {
			"page": 1,
			"per_page": 200
		}
		headers = {"Authorization": "Bearer " + access_token()}
		routes = requests.get(f"https://www.strava.com/api/v3/athletes/{_id}/routes", params=params, headers=headers)
		print(routes.json())

	def challenge_join():
		pass

	def challenge_submit():
		pass

	def account_settings():
		pass

	def account_logout():
		pass

	def notifications_show():
		pass

	def notifications_clear():
		pass

	# widgets
	dropdown_frame = Frames(root_main, strava_color, "fill", 50, 0, 0)
	button_home = Buttons(root_main, "Home", strava_color, "white", "Trebuchet 15", None, 100, 50, 0, 0)
	dropdown_challange = DropdownButtons(root_main, strava_color, 100, 50, 100, 0, "Challenge", "white",
										"Trebuchet 15", [["Create", None], ["Join", None], ["Submit", None]])
	dropdown_account = DropdownButtons(root_main, strava_color, 100, 50, 200, 0, "Account",
										"white", "Trebuchet 15", [["settings", None],["Log out", None]])
	dropdown_notifications = DropdownButtons(root_main, strava_color, 150, 50, 300, 0, "Notifications", "white",
											"Trebuchet 15", [["show", None],["clear", None]])
	label_username = Labels(root_main, logged_in_user, strava_color, "white", "Trebuchet 15", 200, 50, 450, 0)

	# widget actions
	button_home.configure(borderwidth=1, relief="solid")
	button_home.hover("DarkOrange1")
	dropdown_menu = [dropdown_account, dropdown_challange, dropdown_notifications]
	for dropdown_button in dropdown_menu:
		dropdown_button.hover("DarkOrange1")
		for button in dropdown_button.dropdown_buttons:
			button.configure(borderwidth=1, relief="solid")
			button.hover("DarkOrange1")

	root_main.bind("<Map>", lambda event :print("HI"))

	# show screen
	root_main.mainloop()


# start app
startup_screen()
# main_screen()
