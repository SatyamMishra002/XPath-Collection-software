import tkinter as tk
from tkinter import ttk
import database
from ConfigurGui import GUIApp
import global_var
from  Xpath_finder import get_public_ip

class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("400x250")

        # Create and configure styles
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12), padding=5)
        style.configure('TEntry', font=('Arial', 12))

        # Create frame for the login form
        form_frame = ttk.Frame(self, padding="10 10 10 10")
        form_frame.pack(expand=True, fill=tk.BOTH)

        # Create and place the username label and entry
        username_label = ttk.Label(form_frame, text="UserName")
        username_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.EW)

        # Create and place the password label and entry
        password_label = ttk.Label(form_frame, text="Password:")
        password_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)

        # Success/Failure message label
        self.message_label = ttk.Label(form_frame, text="", font=('Arial', 12))
        self.message_label.grid(row=2, columnspan=2, pady=10)

        # Create and place the login button
        login_button = ttk.Button(form_frame, text="Login", command=self.validate_login)
        login_button.grid(row=3, columnspan=2, pady=20)

        # Configure column weight to ensure proper resizing
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=2)

    def validate_login(self):
        system_Ip_address = get_public_ip()     
        userid = self.username_entry.get()
        password = self.password_entry.get()

        if userid.strip() == '' or password.strip() == '':
            self.message_label.config(text="Please enter Username and Password..!", foreground="red")
            return False

        try:
            # Connect to MySQL database
            # query = f"SELECT * FROM dms_wpw_user WHERE username = '{userid}' AND password = '{password}' AND usertype = 'SelectHtmlElement' "
            query = "SELECT * FROM dms_wpw_user WHERE username = %s AND password = %s AND usertype = 'SelectHtmlElement'"
            conn = database.DB_Connection()# Connect to MySQL database
            cursor = conn.cursor()
            cursor.execute(query, (userid, password))# Execute the parameterized query
            rows = cursor.fetchall()# Fetch all results
        except Exception as e:
            print('Error connecting to database:', e)
            if conn:
                cursor.close()
                conn.close()

        if len(rows) > 0:
            
            if rows[0]["activeuser"] == 'N':
                self.message_label.config(text="This account is deactivated", foreground="red")
            
            elif rows[0]['ip_address'] == '':
                global_var.user_id = rows[0]["user_id"]
                self.message_label.config(text="Login Successful", foreground="green")
                self.after(1000, self.start_gui_app)  # Start GUIApp after login success

            else:
                userIPAdd = rows[0]['ip_address']
                ipaddressArr = [ip.strip() for ip in userIPAdd.split(',')]
                if system_Ip_address in ipaddressArr:
                    global_var.user_id = rows[0]["user_id"]
                    self.message_label.config(text="Login Successful", foreground="green")
                    self.after(1000, self.start_gui_app)  # Start GUIApp after login success
                else:
                    self.message_label.config(text="Login not allowed from this system", foreground="red")

        else:
            self.message_label.config(text="Invalid username or password", foreground="red")

    def start_gui_app(self):
        self.destroy()  # Close the login window
        root = tk.Tk()
        columns = ['Link_Id', 'Tender_Link','Country', 'Error', 'Error_Date', 'Status']
        app = GUIApp(root, columns)
        root.mainloop()

if __name__ == "__main__":
    app = LoginForm()
    app.mainloop()
