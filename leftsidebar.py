import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, dialog

class SidebarLeft(tk.Frame):
    def __init__(self, parent, file_app, **kwargs):
        tk.Frame.__init__(self, parent,**kwargs)
        self.configure(background='#25274d', width=200)
        self.parent = parent
        self.file_app = file_app

        self.create_group_button = tk.Button(self, text="Create Group", command=self.create_group)
        self.create_group_button.pack(side=tk.TOP, pady=7.5, padx=20)

        self.create_group_button.configure(
            bg="#a8d0e6",  # Background color
            fg="#000000",  # Text color
            font=("Arial", 12, "bold"),  # Font settings
            relief=tk.RAISED,  # Border style
            padx=10,  # Padding
            pady=5
        )

        separator = tk.Canvas(self, height=1, width=140, bg='black')
        separator.pack()

        self.group_list_box = tk.Listbox(self, selectmode=tk.SINGLE)
        self.group_list_box.pack(side=tk.TOP, fill=tk.X, padx=20, pady=7.5)
        self.group_list_box.bind("<<ListboxSelect>>", self.on_select)

        self.group_items = {}
        self.update_group_list()

    def create_group(self):
        print(self.file_app.groups)
        print('Create Group button Pressed!')
        group_name = simpledialog.askstring("Create Group", "Enter Group Name:")
        if group_name:
            consensus_threshold = simpledialog.askinteger("Create Group", "Enter Consensus Threshold:")
            if consensus_threshold is not None:
                try:
                    self.file_app.create_group(group_name, consensus_threshold)
                    self.update_group_list()
                    self.parent.new_group(group_name)
                except Exception as e:    
                    raise Exception(e)
                    # messagebox.showerror("Error creating Group!", e)

    def generate_group_list(self):
        print('generating group items...')
        for group in self.file_app.groups.values():
            self.group_items[group.name] = group.address
        print(self.file_app.groups)

    def on_select(self, event):
        selected_group_name = self.group_list_box.get(tk.ANCHOR)
        group_address = self.group_items[selected_group_name]
        self.parent.update_curr_group(group_address)
        print("Selected item:", selected_group_name, "type: ", type(selected_group_name))

    def update_group_list(self):
        self.generate_group_list()
        self.group_list_box.delete(0, tk.END)
        for item in self.group_items.keys():
            self.group_list_box.insert(tk.END, item)
        print('group list updated')