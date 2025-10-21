import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from content import open_folder

REPOPATH = 'repos'
PERMISSION = ['READ', 'WRITE', 'INVITE']
PERMISSIONMAP = {
    'READ': 1,
    'WRITE': 2,
    'INVITE': 3
}
# struct proposal here
    # 'title': f'Proposal {i}',
    # 'description': proposal['proposalMessage'],
    # 'id': i



class RightSidebar(tk.Frame):
    def __init__(self, parent, file_app,**kwargs):
        tk.Frame.__init__(self, parent, width=20, **kwargs)
        self.configure(background='#25274d')
        self.parent = parent
        self.file_app = file_app
        # self.update_members()
        self.notifications_button = tk.Button(self, text='Notifications', command=self.show_received_invite_notification, width=20, bg ='#a8d0e6')
        self.notifications_button.pack(side=tk.TOP, pady=10)

        separator = tk.Canvas(self, height=1, width=180, bg='black')
        separator.pack()

        self.users_frame = tk.Frame(self, bg='white')
        self.users_frame.pack(side=tk.TOP, pady=10)

        self.num_users_frame = tk.Frame(self, bg='#def2f1', highlightthickness=0)
        self.num_users_frame.pack(side=tk.TOP, pady=10)

        self.num_members = tk.IntVar()
        self.num_members.set(0)

        num_members_label = tk.Label(self.num_users_frame, text='Number of Users:' ,bg='#def2f1')
        num_members_label.pack(side=tk.LEFT)

        num_members_value = tk.Label(self.num_users_frame, textvariable=self.num_members, bg='#f7f9fb')
        num_members_value.pack(side=tk.LEFT)

        separator = tk.Canvas(self, height=1, width=180, bg='black')
        separator.pack()

        self.proposals_frame = tk.Frame(self, bg='#25274d')
        self.proposals_frame.pack(side=tk.TOP, pady=10)
        # self.update_proposals()

        separator = tk.Canvas(self, height=1, width=180, bg='black')
        separator.pack()

        self.invite_frame = tk.Frame(self, bg='#25274d',width=20)
        self.invite_frame.pack(side=tk.TOP, pady=10)

        self.invite_button = tk.Button(self.invite_frame, text='Invite', command=self.show_invite_popup, bg='#a8d0e6', width=20)
        self.invite_button.pack(side=tk.TOP, pady=5)

        separator = tk.Canvas(self, height=1, width=180, bg='black')
        separator.pack()

        # create propose frame
        self.propose_frame = tk.Frame(self, bg='#25274d')
        self.propose_frame.pack(side=tk.TOP, pady=10)

        # Create propose button
        self.propose_button = tk.Button(self.propose_frame, text='Propose', command=self.show_propose_popup, bg='#a8d0e6', width=20)
        self.propose_button.pack(side=tk.TOP, pady=5)

        self.proposal_buttons = []

    def show_received_invite_notification(self):
        popup = tk.Toplevel(self)
        popup.configure(background='#464866')
        popup.title("Notifications")
        popup.geometry("300x200+{}+{}".format(int(popup.winfo_screenwidth() / 2 - 150),
                                          int(popup.winfo_screenheight() / 2 - 100)))

        groups = []
        self.file_app.get_invites()
        for address, invite in self.file_app.invites.items():
            group_dict = {
                'groupAddress': address,
                'groupName': invite[0],
                'permission': invite[1]
            }
            groups.append(group_dict)

        for group in groups:
            # Create a button for each group
            group_button = tk.Button(popup, text=group['groupName'], command=lambda g=group: self.show_popup_window_for_invite_notification(popup,g))
            group_button.pack(side=tk.TOP, pady=5)

    def show_popup_window_for_invite_notification(self, window, group):
        window.destroy()
        popup = tk.Toplevel()
        popup.configure(background='#464866')
        popup.geometry("200x100+{}+{}".format(int(popup.winfo_screenwidth() / 2 - 350),
                                          int(popup.winfo_screenheight() / 2 - 100)))
        groupname_label = tk.Label(popup, text=f"Group Name: {group['groupName']}", bg='white')
        groupname_label.pack(padx=10, pady=5)
        
        permission_label = tk.Label(popup, text=f"Permission: {group['permission']}", bg='white')
        permission_label.pack(padx=10, pady=5)

        accept_button = tk.Button(popup, text='Accept', command=lambda: self.handle_invite_accepted_rejected(popup, group, 'Accepted'))
        accept_button.pack(side=tk.LEFT, padx=10, pady=10)

        reject_button = tk.Button(popup, text='Reject', command=lambda: self.handle_invite_accepted_rejected(popup, group, 'Rejected'))
        reject_button.pack(side=tk.LEFT, padx=10, pady=10)


    def handle_invite_accepted_rejected(self, window, group, action):
        try:
            group_address = group['groupAddress']
            if action == 'Accepted':
                self.file_app.accept_invite(group_address)
                self.parent.invite_accepted(group['groupName'])
            elif action == 'Rejected':
                self.file_app.reject(group_address)

        except Exception as e:
           messagebox.showerror('Error Accepting/Rejecting invite!', e)
        
        finally:
            window.destroy()

        
    def show_proposal_popup(self, proposal):
        # Create a popup window for each proposal
        popup = tk.Toplevel(self)
        popup.configure(background='#464866')

        popup.geometry("300x200+{}+{}".format(int(popup.winfo_screenwidth() / 2 - 150),
                                          int(popup.winfo_screenheight() / 2 - 100)))

        # Proposal title
        title_label = tk.Label(popup, text=proposal['title'], bg='#ffffff')
        title_label.pack(padx=10, pady=10)

        # Proposal description
        description_label = tk.Label(popup, text=proposal['description'], bg='white')
        description_label.pack(padx=10, pady=10)
        
        # Create accept button
        accept_button = tk.Button(popup, text='Accept', command=lambda: self.accept_proposal(proposal))
        accept_button.pack(side=tk.RIGHT, padx=10, pady=10,)

        # Create reject button
        reject_button = tk.Button(popup, text='Reject', command=lambda: self.reject_proposal(proposal))
        reject_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Create view button
        view_button = tk.Button(popup, text='View', command=lambda: self.view_proposal(proposal))
        view_button.pack(side=tk.LEFT, padx=10, pady=10)


    def view_change_proposal(self, proposal):
        messagebox.showinfo('View/Change Proposal', f'Viewing proposal: {proposal}')
        self.parent.content.view_change(proposal)

    def accept_proposal(self, proposal):
        # self.parent.curr_group.proposal_accepted(proposal['id'])
        self.parent.curr_group.vote(proposal['id'], True)
        messagebox.showinfo('Accept Proposal', f'Accepting proposal: {proposal}')
        self.update_proposals()

    def reject_proposal(self, proposal):
        self.parent.curr_group.vote(proposal['id'], False)
        messagebox.showinfo('Reject Proposal', f'Rejecting proposal: {proposal}')
        self.update_proposals()
    
    def view_proposal(self, proposal):
       temp_path = self.parent.curr_group.view_change(proposal['id'])
       open_folder(temp_path)

    def show_invite_popup(self):
        if not self.parent.curr_group:
            messagebox.showerror('No group Selected', 'Select a Group')
            return
        popup = tk.Toplevel()
        popup.title("Invite User")
        popup.geometry("300x200")

        popup.geometry("300x200+{}+{}".format(int(popup.winfo_screenwidth() / 2 - 150),
                                          int(popup.winfo_screenheight() / 2 - 100)))

        self.file_app.get_users_infos()
        self.registered_users = self.file_app.user_address_name_dict.values()
        # self.registered_users = ['Ana', 'Ava']
        username_var = tk.StringVar()
        username_label = tk.Label(popup, text="Username:")
        username_label.pack()
        username_entry = AutocompleteEntry(popup, completevalues=self.registered_users)
        username_entry.pack()

        permission_label = tk.Label(popup, text="Permission:")
        permission_label.pack()

        permission_var = tk.StringVar()
        permission_combobox = ttk.Combobox(popup, textvariable=permission_var, values=PERMISSION)
        permission_combobox.pack()

        def invite_user():
            username = username_entry.get()
            permission = permission_var.get()
            # permission = PERMISSIONMAP[permission]
            # user_dict = {}
            for user in self.file_app.users:
                if user['username'] == username:
                    if self.parent.curr_group_address:
                        self.file_app.groups[self.parent.curr_group_address].invite(user, permission)
                    else:
                        print('Select a group!')
                        messagebox.showerror('Select Group', 'No group selected')
                    break
            else:
                print('Failed to invite')
            print("Inviting User:", username)
            print("Permission:", permission)
            popup.destroy()

        invite_button = tk.Button(popup, text="Invite", command=invite_user)
        invite_button.pack()

        popup.mainloop()

    def update_members(self):
        if self.parent.curr_group:
            print('updating members!')
            self.users = []
            for user in self.parent.curr_group.users:
                self.users.append(user['username'])
            for widget in self.users_frame.winfo_children():
                widget.destroy()
            for user in self.users:
                user_label = tk.Label(self.users_frame, text=user)
                user_label.pack(side=tk.TOP, pady=5)

    def update_proposals(self):
        if not self.parent.curr_group:
            return
        
        print('updating proposals')
    #     self.proposals = [{'title': 'Proposal 1', 'description': 'Proposal 1 description'},
    #               {'title': 'Proposal 2', 'description': 'Proposal 2 description'},
    #               {'title': 'Proposal 3', 'description': 'Proposal 3 description'}]  # Replace with your array or function
        # for button in self.proposal_buttons:
        #     button.destroy()
        
        for widget in self.proposals_frame.winfo_children():
            widget.destroy()
        try:
            self.proposals = []
            for i, proposal in enumerate(self.parent.curr_group.proposals):
                if proposal['status'] == 0 and proposal['voted'] == False:
                    self.proposals.append({
                    'title': f'Proposal {i}',
                    'description': proposal['proposalMessage'],
                    'id': i
                    })
            print(self.proposals)
            for proposal in self.proposals:
                proposal_button = tk.Button(self.proposals_frame, text=proposal['title'], command=lambda p=proposal: self.show_proposal_popup(p))
                proposal_button.pack(side=tk.TOP, pady=5)
                self.proposal_buttons.append(proposal_button)
        except Exception as e:
            messagebox.showerror("Error updating proposals", e)
    
    def show_propose_popup(self):
        files = os.listdir(os.path.join(REPOPATH, self.parent.curr_group.name))
        if not self.parent.curr_group and files:
            # messagebox.showerror("No group selected", "Select a Group")
            return
        # Create a popup window for proposing
        popup = tk.Toplevel(self)
        popup.configure(background='white')
        popup.title("proposals")
        popup.geometry("300x200+{}+{}".format(int(popup.winfo_screenwidth() / 2 - 150),
                                            int(popup.winfo_screenheight() / 2 - 100)))

        # Proposal description entry
        description_label = tk.Label(popup, text='Proposal Description:', bg='white')
        description_label.pack(padx=10, pady=10)

        description_entry = tk.Entry(popup)
        description_entry.pack(padx=10, pady=10)

        # Propose button
        propose_button = tk.Button(popup, text='Propose', command=lambda: self.propose(description_entry.get(), popup))
        propose_button.pack(padx=10, pady=10)

    def propose(self, description, popup_window):
        # Handle the proposed description
        popup_window.destroy()
        self.parent.curr_group.propose(description)
        self.parent.curr_group.proposals[-1]['voted'] = True
        self.parent.content.update_content_view()
        self.update_view()


    def update_view(self):
        self.update_proposals()
        self.update_members()

class AutocompleteEntry(tk.Entry):
    def __init__(self, master, completevalues=[], **kwargs):
        self.completevalues = completevalues
        self.var = tk.StringVar()
        super().__init__(master, textvariable=self.var, **kwargs)
        self.var.trace('w', self.on_entry_change)
        self.completions = []
        self.autocomplete_listbox = None

    def on_entry_change(self, *args):
        search_term = self.var.get()
        self.completions = [value for value in self.completevalues if value.startswith(search_term)]
        self.update_completions()

    def update_completions(self):
        if self.autocomplete_listbox:
            self.autocomplete_listbox.destroy()
        if self.completions:
            self.autocomplete_listbox = tk.Listbox(self.master)
            self.autocomplete_listbox.bind('<Double-Button-1>', self.autocomplete)
            self.autocomplete_listbox.bind('<Return>', self.autocomplete)
            for completion in self.completions:
                self.autocomplete_listbox.insert(tk.END, completion)
            self.autocomplete_listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
        else:
            self.autocomplete_listbox = None

    def autocomplete(self, event=None):
        if self.autocomplete_listbox:
            selected_index = self.autocomplete_listbox.curselection()
            if selected_index:
                selected_value = self.autocomplete_listbox.get(selected_index)
                self.var.set(selected_value)
        self.autocomplete_listbox.destroy()
        self.focus_set()

    def next_completion(self):
        if self.completions:
            current_index = self.completions.index(self.get())
            next_index = (current_index + 1) % len(self.completions)
            self.var.set(self.completions[next_index])


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("React App")
        self.geometry("800x600")

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.right_sidebar = RightSidebar(self.container, '')
        self.right_sidebar.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

if __name__ == '__main__':
    app = App()
    app.mainloop()
