# 'irene-pro'

This is my customized user interface which is rooted from tkinter package.
nothing big that I did from here that is different from what already in tkinter, but I rather set my default parameters and 
styles for those rooted to ttk, example Combobox.

this is the first version, and later I will keep making extra-improvement including adding default icons to buttons and other
cool stuffs until it will be large package or framework in coming years.

=========how to use the package======
from irene-pro import widgets, logic

# create button
button = widgets.btn(master = root, text = 'send')
button.pack(side = LEFT)

# create table gui
table = widgets.Table_gui(parent = root)

# login and signup template has been added too
sign = widgets.LoginSignup(master)
# get the sign_in_btn
login_btn = sign.Login_btn()
# call a function if the validation is successfully
login_btn.config(command = sign.validate_login(callback = func_to_call, saved_username, saved_password))

# SQLITE3 DATABASE ADDED IN LOGIC LIBRALY

