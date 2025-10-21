import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from fileApp import FileApp



class SigninPage(tk.Frame):
    def __init__(self, parent, on_signin_success, file_app,**kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.configure(background='#7548d4')
        #4eacf3
        self.on_signin_success = on_signin_success
        self.file_app = file_app

        self.image = tk.PhotoImage(file = 'login.png')
        tk.Label(self, image = self.image, bg ='white').place(x=30,y=140)

        self.frame = tk.Frame(self, width = 350, height = 334, bg="white") 
        self.frame.place(x=430,y=140)

        self.login_label = tk.Label(self.frame, text="Sign In", font=('Arial', 16 , 'bold'), bg = 'white', fg = '#0b64a7')
        self.login_label.place(x = 70, y = 90)

        self.username_label = tk.Label(self.frame, text="Username", font=('Arial', 12 , 'bold'), bg = 'white', fg = 'Black')
        self.username_label.place(x = 70, y = 130)

        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(self.frame, textvariable=self.username_var, border = 0, bg = 'white')
        self.username_entry.place(x = 70, y = 150)

        self.private_key_label = tk.Label(self.frame, text="Private Key", font=('Arial', 12 , 'bold'), bg = 'white', fg = 'Black')
        self.private_key_label.place(x = 70, y = 185)

        self.private_key_var = tk.StringVar()
        self.private_key_entry = tk.Entry(self.frame, textvariable=self.private_key_var, show = '*' ,border = 0, bg = 'white')
        self.private_key_entry.place(x = 70, y = 205)
        

        # tk.Frame(self.frame, width =1, height = 334,bg = 'gray').place(x=0,y=0)

        self.signin_button = tk.Button(self.frame, text="Sign In", command = self.handle_signin, border = 0, relief = 'flat', bg = '#4eacf3', fg = 'white')
        self.signin_button.place(x = 165, y = 230)

        self.empty_label = tk.Label(self.frame, text="", font=('Arial', 12 ), bg = 'white', fg = 'Black')
        self.empty_label.place(x = 110, y = 270)

    def handle_signin(self):
        print('Signin Button Pressed!')
        # self.username_var.set()
        # self.private_key_var.set()
        username = self.username_var.get()
        private_key = self.private_key_var.get()
        if username and private_key:
            try:
                self.file_app = FileApp.login(username, private_key)
                print(self.file_app.groups)
                # self.file_app
                self.on_signin_success(self.file_app)
            except ValueError as e:
                messagebox.showerror(title='Error Loging in!', message=e)

            except FileNotFoundError:
                try:
                    self.file_app.sign_up(username, private_key)
                    self.on_signin_success(self.file_app)

                except Exception as e:
                    messagebox.showerror(title='Error Signing in!', message=e)


    def show(self):
        self.pack(fill=tk.BOTH, expand=True)
    
    def update_label_text(self, text):
        self.empty_label.config(text=text)

    def hide(self):
        self.pack_forget()