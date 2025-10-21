import tkinter as tk
class Navbar(tk.Frame):
    def __init__(self, parent, file_app,**kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.configure(background='#aaabb8', height=50, bd=1, relief='solid')

        self.file_app = file_app
        # Create the username frame with a border
        self.username_frame = tk.Frame(self, bg='#aaabb8', bd=1, relief='solid')
        self.username_frame.pack(side='left', padx=10, pady=5)

        self.username_label = tk.Label(self.username_frame, text='Username:', bg='#a8d0e6')
        self.username_label.pack(side='left')

        self.username = tk.StringVar()
        self.username.set(self.file_app.username)  

        self.signed_in_label = tk.Label(self.username_frame, textvariable=self.username, bg='#f7f9fb')
        self.signed_in_label.pack(side='left')

        self.user_address_frame = tk.Frame(self, bg='#aaabb8', bd=1, relief='solid')
        self.user_address_frame.pack(side='left', padx=10, pady=5)

        self.address_label = tk.Label(self.user_address_frame, text='Address:', bg='#a8d0e6')
        self.address_label.pack(side='left')

        self.address = tk.StringVar()
        self.address.set(self.file_app.user_address)  # Default value

        self.signed_in_address_label = tk.Label(self.user_address_frame, textvariable=self.address, bg='#f7f9fb')
        self.signed_in_address_label.pack(side='left')
