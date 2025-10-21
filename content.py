import os
import tkinter as tk
from PIL import ImageTk, Image

import subprocess

REPOPATH = 'repos'

def open_folder(path):
    try:
        subprocess.Popen(['xdg-open', path])
    except OSError:
        print("Unable to open the folder.")


class Content(tk.Frame):
    def __init__(self, parent, file_app,**kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.configure(background='#464866')
        
        self.parent = parent
        self.file_app = file_app

        self.file_frame = tk.Frame(self, bg='#464866')
        self.file_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Open Folder", command=self.open_folder)
        self.context_menu.add_command(label="Revert", command=self.revert_change)
        # self.context_menu.add_command(label="Delete", command=self.delete_folder)

        self.bind("<Button-3>", self.show_context_menu)

        self.bind("<Button-1>", self.hide_context_menu)

        self.file_frame.pack(side=tk.TOP, padx=10, pady=10 ,anchor='nw')
        self.file_icons = {}  # Dictionary to store file icons
        # self.create_file_widgets('repos')

    def create_file_widgets(self):
        if not self.parent.curr_group:
            return
        folder_name = os.path.join(REPOPATH, self.parent.curr_group.name)
        
        for widget in self.file_frame.winfo_children():
            widget.destroy()

        files = os.listdir(folder_name)
        for file_name in files:
            file_frame = tk.Frame(self.file_frame, bg='white')
            file_frame.pack(side=tk.LEFT, padx=10, pady=10)

            if os.path.isdir(os.path.join(folder_name, file_name)):
                file_type = 'folder'
            else:
                file_type = 'file'
            
            file_icon = self.get_file_icon(file_type)

            icon_label = tk.Label(file_frame, image=file_icon, bg='white')
            icon_label.image = file_icon  # Store the reference to avoid image garbage collection
            icon_label.pack()

            name_label = tk.Label(file_frame, text=file_name, font=('Arial', 12), bg='white')
            name_label.pack()

            file_frame.bind("<Button-3>", self.show_context_menu)

    def get_file_icon(self, file_type):
        if file_type in self.file_icons:
            return self.file_icons[file_type]
       
        if file_type == 'file':
            icon_path = 'icons/file.png'  # Replace with the path to your text file icon image
        elif file_type == 'folder':
            icon_path = 'icons/folder.png'  # Replace with the path to your image file icon image

        image = Image.open(icon_path)
        image = image.resize((30, 30))
        icon = ImageTk.PhotoImage(image)
        self.file_icons[file_type] = icon
        return icon
    
    def view_change(self, proposal):
        print('View change from content class')
        if self.parent.curr_group:
            path = self.parent.curr_group.view_change(proposal['id'])
            open_folder(os.path.join(path, self.parent.curr_group.name))
    
    def open_folder(self):
        if self.parent.curr_group:
            open_folder(os.path.join(REPOPATH, self.parent.curr_group.name))

    def revert_change(self):
        # try:
        if self.parent.curr_group:
            print('reverting change')
            self.parent.curr_group.revert_change()
            self.create_file_widgets()


    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def hide_context_menu(self, event):
        self.context_menu.unpost()

    def update_content_view(self):
        self.create_file_widgets()


if __name__ == '__main__':
    root = tk.Tk()
    content = Content(root, '')
    content.pack()
    root.mainloop()
