import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

PERMISSION = ['DEFAULT', 'READ', 'WRITE', 'INVITE']
PERMISSIONMAP = {
    'DEFAULT': 0,
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
        tk.Frame.__init__(self, parent, width=400, **kwargs)
        self.configure(background='blue')
        self.parent = parent
        self.file_app = file_app
        # self.update_members()
        self.notifications_button = tk.Button(self, text='Notifications', command=self.show_received_invite_notification)
        self.notifications_button.pack(side=tk.TOP, pady=10)

        self.users_frame = tk.Frame(self, bg='white')
        self.users_frame.pack(side=tk.TOP, pady=10)

        self.num_users_frame = tk.Frame(self, bg='white')
        self.num_users_frame.pack(side=tk.TOP, pady=10)

        self.num_members = tk.IntVar()
        self.num_members.set(0)

        num_members_label = tk.Label(self.num_users_frame, text='Number of Users:')
        num_members_label.pack(side=tk.LEFT)

        num_members_value = tk.Label(self.num_users_frame, textvariable=self.num_members)
        num_members_value.pack(side=tk.LEFT)

        self.proposals_frame = tk.Frame(self, bg='white')
        self.proposals_frame.pack(side=tk.TOP, pady=10)
        # self.update_proposals()

        self.invite_frame = tk.Frame(self, bg='white')
        self.invite_frame.pack(side=tk.TOP, pady=10)

        self.invite_button = tk.Button(self.invite_frame, text='Invite', command=self.show_invite_popup)
        self.invite_button.pack(side=tk.TOP, pady=5)

    def show_received_invite_notification(self):
        popup = tk.Toplevel(self)
        popup.configure(background='white')
        popup.geometry("300x200+{}+{}".format(int(popup.winfo_screenwidth() / 2 - 150),
                                          int(popup.winfo_screenheight() / 2 - 100)))

        groups = []
        for invite in self.file_app.invites.values():
            groups.append(invite)

        for group in groups:
            # Create a button for each group
            group_button = tk.Button(popup, text=group, command=lambda g=group: self.show_popup_window_for_invite_notification(g))
            group_button.pack(side=tk.TOP, pady=5)

    def show_popup_window_for_invite_notification(self, group):
        popup = tk.Toplevel()
        popup.configure(background='white')
        popup.geometry("200x100+{}+{}".format(int(popup.winfo_screenwidth() / 2 - 350),
                                          int(popup.winfo_screenheight() / 2 - 100)))
        groupname_label = tk.Label(popup, text="Group Name:", bg='white')
        groupname_label.pack(padx=10, pady=5)
        
        permission_label = tk.Label(popup, text="Permission:", bg='white')
        permission_label.pack(padx=10, pady=5)

        accept_button = tk.Button(popup, text='Accept', command=lambda: self.handle_invite_accepted_rejected(group, 'Accepted'))
        accept_button.pack(side=tk.LEFT, padx=10, pady=10)

        reject_button = tk.Button(popup, text='Reject', command=lambda: self.handle_invite_accepted_rejected(group, 'Rejected'))
        reject_button.pack(side=tk.LEFT, padx=10, pady=10)


    def handle_invite_accepted_rejected(self, group, action):
        try:
            group_address = ''
            for key, val in self.file_app.invites.items():
                if val['groupName'] == group['groupName']:
                    group_address = key
                    if action == 'Accepted':
                        self.file_app.accept_invite(group_address)
                        self.parent.invite_accepted(group['groupName'])
                    elif action == 'Rejected':
                        self.file_app.reject(group_address)
                    break
            else:
                raise ValueError(f'No group with {group["groupName"]} exists')

        except Exception as e:
           messagebox.showerror('Error Accepting invite!', e)
        
    def show_proposal_popup(self, proposal):
        # Create a popup window for each proposal
        popup = tk.Toplevel(self)
        popup.configure(background='white')

        popup.geometry("300x200+{}+{}".format(int(popup.winfo_screenwidth() / 2 - 150),
                                          int(popup.winfo_screenheight() / 2 - 100)))

        # Proposal title
        title_label = tk.Label(popup, text=proposal['title'], bg='white')
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
        # Create a new window to display the proposal details
        view_window = tk.Toplevel(self)
        view_window.configure(background='white')
        view_window.title("Proposal Details")

        # Create labels to display the proposal details
        title_label = tk.Label(view_window, text="Title:", bg='white')
        title_label.pack(padx=10, pady=10)
        title_value_label = tk.Label(view_window, text=proposal['title'], bg='white')
        title_value_label.pack(padx=10, pady=10)

        description_label = tk.Label(view_window, text="Description:", bg='white')
        description_label.pack(padx=10, pady=10)
        description_value_label = tk.Label(view_window, text=proposal['description'], bg='white')
        description_value_label.pack(padx=10, pady=10)

        close_button = tk.Button(view_window, text='Close', command=view_window.destroy)
        close_button.pack(padx=10, pady=10)

    def show_invite_popup(self):
        popup = tk.Toplevel()
        popup.title("Invite User")
        popup.geometry("300x200")

        popup.geometry("300x200+{}+{}".format(int(popup.winfo_screenwidth() / 2 - 150),
                                          int(popup.winfo_screenheight() / 2 - 100)))

        self.registered_users = self.file_app.user_address_name_dict.values()
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
            permission = PERMISSIONMAP[permission]
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
            self.file_app.invite()
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
        if self.parent.curr_group:
            print('updating proposalas')
    #     self.proposals = [{'title': 'Proposal 1', 'description': 'Proposal 1 description'},
    #               {'title': 'Proposal 2', 'description': 'Proposal 2 description'},
    #               {'title': 'Proposal 3', 'description': 'Proposal 3 description'}]  # Replace with your array or function
            try:
                self.proposals = []
                for i, proposal in enumerate(self.parent.curr_group.proposals):
                    if proposal['status'] == 0 and proposal['voted'] == False:
                        self.proposals.append({
                        'title': f'Proposal {i}',
                        'description': proposal['proposalMessage'],
                        'id': i
                        })

                for proposal in self.proposals:
                    proposal_button = tk.Button(self.proposals_frame, text=proposal['title'], command=lambda p=proposal: self.show_proposal_popup(p))
                    proposal_button.pack(side=tk.TOP, pady=5)
            except Exception as e:
                messagebox.showerror("Error updating proposals", e)
    
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
