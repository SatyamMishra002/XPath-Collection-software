import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import sys
from Xpath_finder import ChromeDriver
import database
from country_list import *
import time
import global_var
# from LoginForm import LoginForm

class GUIApp:
    
    def __init__(self, root, columns):
        self.root = root
        self.root.title("TOT-Configure")
        self.root.state('zoomed')

        # Create frame for input fields
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Link ID input field
        self.tender_id_label = tk.Label(self.input_frame, text="Link ID:")
        self.tender_id_label.pack(side=tk.LEFT, padx=(0, 8), pady=5)
        self.tender_id_entry = tk.Entry(self.input_frame)
        self.tender_id_entry.pack(side=tk.LEFT, padx=(0, 8), pady=5)

        # Tender Link input field
        self.tender_link_label = tk.Label(self.input_frame, text="Tender Link:")
        self.tender_link_label.pack(side=tk.LEFT, padx=(0, 8), pady=5)
        self.tender_link_entry = tk.Entry(self.input_frame, width=60)
        self.tender_link_entry.pack(side=tk.LEFT, padx=(0, 8), pady=5)

        # Flag dropdown
        self.flag_label = tk.Label(self.input_frame, text="Status:")
        self.flag_label.pack(side=tk.LEFT, padx=(0, 8), pady=5)
        self.flag_var = tk.StringVar(root)
        self.flag_var.set("N")  # Default value
        self.flag_combobox = ttk.Combobox(self.input_frame, textvariable=self.flag_var, values=["Y", "N", "H"])
        self.flag_combobox.pack(side=tk.LEFT, padx=(0, 8), pady=5)

        # Country dropdown
        # self.country_label = tk.Label(self.input_frame, text="Region\Country:")
        # self.country_label.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        # self.countrydd_var = tk.StringVar()
        # self.countrydd_var.set("Select Country")  # Default value
        # self.country_combobox = ttk.Combobox(self.input_frame, textvariable=self.countrydd_var, values=["Africa", "Algeria"])
        # self.country_combobox.pack(side=tk.LEFT, padx=(0, 10), pady=5)

        # Country dropdown
        self.country_label = tk.Label(self.input_frame, text="Region/Country:")
        self.country_label.pack(side=tk.LEFT, padx=(0, 8), pady=5)
        self.countrydd_var = tk.StringVar(root)
        self.countrydd_var.set("Select Country")  # Default value
        self.country_combobox = ttk.Combobox(self.input_frame, textvariable=self.countrydd_var, values=self.get_country_list())
        self.country_combobox.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        self.country_list = self.get_country_list()
        self.country_combobox['values'] = self.country_list

        # Bind the event to handle dynamic filtering
        self.country_combobox.bind('<KeyRelease>', self.on_keyrelease)

        #error dropdown 
        self.error_label = tk.Label(self.input_frame, text="Select_Error:")
        self.error_label.pack(side=tk.LEFT, padx=(0, 4), pady=5)
        self.errordd_var = tk.StringVar(root)
        self.errordd_var.set("ErrorType")  # Default value
        self.error_combobox = ttk.Combobox(self.input_frame, textvariable=self.errordd_var, values=['Select_Error','XPath Issue','WebsiteIssue Type1',' WebsiteIssue Type2'])
        self.error_combobox.pack(side=tk.LEFT, padx=(0, 10), pady=5)

        # Create Treeview widget
        self.tree = ttk.Treeview(root, columns=columns, show='headings')

        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=20, anchor='center' )

        # Apply border style to the Treeview heading cells
        style = ttk.Style()
        style.theme_use("default")  # Use default theme to ensure consistent appearance
        style.configure("Treeview.Heading", borderwidth=1, relief="solid")

        style.configure("Configure.TButton", foreground="blue", font=("Arial", 10, "underline"))

        # Configure border around Treeview cells
        style.configure("Treeview.Cell", borderwidth=1, relief="solid")

        # Pack the Treeview
        self.tree.pack(expand=True, fill='both')

        # Search button
        self.search_button = tk.Button(self.input_frame, text="Search", command=self.search_data)
        self.search_button.pack(side=tk.LEFT, padx=(0, 10), pady=5)


        # exit button
        self.exit_button = tk.Button(root, text="Exit", font=("Arial", 10), command=self.exit_app)
        self.exit_button.pack(side="right", padx=5, pady=5)

        # user_details button
        self.show_details_button = tk.Button(root, text="My Report",font=("Arial", 10), command=self.show_user_details)
        self.show_details_button.pack(side="right", padx=5, pady=5)

        # Next button
        self.next_button = tk.Button(root, text="Next", command=self.next_data)
        self.next_button.pack(side="right", padx=5, pady=5)

        # Previous button
        self.previous_button = tk.Button(root, text="Previous", command=self.previous_data)
        self.previous_button.pack(side="right", padx=5, pady=5)



        # Initialize offset for pagination
        self.offset = 0

        # Add loading label
        self.loading_label = tk.Label(root, text="Loading Data...", font=("Arial", 16), bg="red")
        # self.loading_label.place(relx=0.5, rely=0.5, anchor='center')
        self.loading_label.pack_forget()  # Initially hidden

        # Create a footer frame
        self.footer_frame = tk.Frame(root)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # Total count label
        self.total_count_label = tk.Label(self.footer_frame, text="Total Records: 0", anchor='e')
        self.total_count_label.pack(side=tk.LEFT, padx=(0, 10))

        # Error message label
        self.error_label = tk.Label(self.footer_frame, text="", fg="white", font=("Arial", 16), bg="red")
        self.error_label.pack(side=tk.LEFT, padx=(0, 10))
        self.error_label.pack_forget()  # Initially hidden

        # Populate Treeview with data
        self.search_data()

        # Bind Treeview "Configure" button click event
        # self.tree.tag_bind("configure_button", "<Button-1>", self.configure_app)
        # self.tree.tag_bind("configure_button", "<Double-1>", self.configure_app)
        self.tree.bind("<Double-1>", self.configure_app)

    def get_country_list(self):
        return [
                "Global", "Africa-101","Afghanistan-103401", "Algeria-101301","American Samoa-105401","Albania-104301", "Andorra-104302", "Angola-101201", "Anguilla-102201", 
                "Antigua and Barbuda-102202","Aland Islands-104201", "Argentina-102401", "Armenia-103501", "Aruba-102203", "Asia-103", "Australia and New Zealand-1051", 
                "Australia-105101",  "Austria-104401", "Azerbaijan-103502","Americas-102", 
                
                "Bahamas-102204","Bhutan-103403","Brunei Darussalam-103301", "Bahrain-103503", "Bangladesh-103402", "Barbados-102205", "Belarus-104101", "Belgium-104402", 
                "Belize-102101", "Benin-101501", "Bermuda-102301", "Bhutan-103403", "Bolivia (Plurinational State of)-102402", "Bonaire, Saint Eustatius and Saba-102206","Bosnia and Herzegovina-104303", "Botswana-101401", "Brazil-102403", "Bouvet Island-102404","British Indian Ocean Territory-102208",  "Bulgaria-104102", "Burkina Faso-101502", "Burundi-101101", 
                
                "Cabo Verde-101503", "Cambodia-103302", "Cameroon-101202", "Canada-102302", "Cayman Islands-102209", "Central Africa-1012", "Central African Republic-101203", "Central America-1021", "Chile-102405","China-103201" , "Colombia-102406", "Comoros-101102", "Congo-101205", 
                "Cook Islands-105402","Cocos (Keeling) Islands-105403", "Costa Rica-102102", "Cote d'Ivoire-101504", "Croatia-104304", "Cuba-102210","China,Macao Special Administrative Region-103203",  
                "Curacao-102211", "Cyprus-103504", "Czech Republic-104103","Christmas Island-104202", 

                "DR Congo-101206","Denmark-104203", "Djibouti-101103", "Dominica-102212", "Dominican Republic-102213",

                "Eastern Africa-1011", "Eastern Asia-1032", "Eastern Europe-1041","Europe-104", "Ecuador-102407", "Egypt-101302", "El Salvador-102103", "Equatorial Guinea-101207", "Eritrea-101104", "Estonia-104204", "Ethiopia-101105", 
                
                "Falkland Islands (Malvinas)-102408", "Faroe Islands-104205", "Fiji-105201", "Finland-104206", "France-104403", "French Guiana-102409", "French Polynesia-105404", "French Southern Territories-105413",
                 
                "Gabon-101208", "Gambia-101505", "Georgia-103505", "Germany-104404", "Ghana-101506", "Gibraltar-104305", "Greece-104306", "Greenland-102303", "Grenada-102214", "Guadeloupe-102215", "Guam-105301", "Guatemala-102104", "Guernsey-104207", "Guinea-101507", "Guinea-Bissau-101508", 
                "Guyana-102410",
                 
                "Haiti-102216", "Heard Island And Mcdonald Islands-105412", "Honduras-102105", "Hong Kong-103202", 
                "Hungary-104104",
                 
                 "Iceland-104208", "India-103404",   "Iraq-103506", "Ireland-104209", "Isle of Man-104210", "Israel-103507",  "Indonesia-103303", "Iran (Islamic Republic of)-103405", "Italy-104308" ,

                "Japan-103205", "Jersey-104211", "Jordan-103508","Jamaica-102217",
                 
                "Kazakhstan-103101", "Kenya-101106", "Kiribati-105302", 
                "Korea (Democratic People's Republic of)-103204", "Korea (Republic of)-103207", "Kuwait-103509", "Kyrgyzstan-103102", 
                
                "Lao People's Democratic Republic-103304", "Latvia-104212", "Lebanon-103510", "Lesotho-101402", "Liberia-101509", "Libyan Arab Jamahiriya-101303", "Liechtenstein-104405", "Lithuania-104213", "Luxembourg-104406",

                "Madagascar-101107", "Malawi-101108",
                "Mali-101510", "Holy See (Vatican City State)-104307 ","Malta-104309", "Marshall Islands-105303", "Martinique-102218", "Mauritania-101511","Malaysia-103305", "Mauritius-101109", "Mayotte-101110", "Mexico-102106", "Micronesia-105304", "Moldova-104106","Melenesia-1052", "Monaco-104407", "Mongolia-103206", "Montenegro-104310", "Montserrat-102219", "Morocco-101304","Micronesia-1053", "Mozambique-101111", "Myanmar-103306", 
                
                "Namibia-101403", "Nauru-105305", "New Zealand-105102","Netherlands-104408", "New Caledonia-105202", "Norfolk Island-105103", "Nicaragua-102107", "Niger-101512", "Nigeria-101513", "Niue-105405",  "Northern Africa-1013", "Northern America-1023", "Northern Europe-1042", "Northern Mariana Islands-105306", "Norway-104214", "Nepal-103407",
                
                "Oman-103512", "Oceania-105"

                "Philippines-103307","Pakistan-103408", "Palau-105307", "Polynesia-1054","Pitcairn-105406", "Palestine-103511", "Panama-102108", "Papua New Guinea-105203", "Paraguay-102411", 
                "Peru-102412",  "Poland-104105", "Portugal-104311", "Puerto Rico-102220", 
                
                "Qatar-103513",

                "Reunion-101112", "Romania-104107", "Russian Federation-104108", "Rwanda-101113", 
                
                "Saint Barthelemy-102221", "Saint Helena-101514", "Saint Kitts and Nevis-102222", "Saint Lucia-102223", "Saint Martin (French part)-102224", "Saint Pierre and Miquelon-102304", "Saint Vincent and the Grenadines-102225", "Samoa-105407", "San Marino-104312", "Sao Tome and Principe-101209", "Saudi Arabia-103514", "Senegal-101515", "Serbia-104313", "Seychelles-101114", "Sierra Leone-101516", "Singapore-103308", "Slovakia-104109", "Slovenia-104314", "Solomon Islands-105204", 
                "Somalia-101115", "South Africa-101404", "South America-1024", "South-Eastern Asia-1033", "Southern Asia-1034", "Southern Africa-1014", "Southern Asia-103", "Southern Europe-1043", "South Georgia And The South Sandwich Islands-102414", "Spain-104315", "Sri Lanka-103409","South Sudan, The Republic Of-101305", "Sudan-101306", "Suriname-102413", "Svalbard and Jan Mayen Islands-104215", 
                "Swaziland-101405", "Sweden-104216", "Switzerland-104409", "Syrian Arab Republic-103515","Sint Maarten (Dutch part)-102226",

                "Tajikistan-103103", "Tanzania-101117", "Thailand-103309","Timor-Leste-103310" ,  "Togo-101517", "Tokelau-105408", 
                "Tonga-105409", "Trinidad and Tobago-102227", "Tunisia-101307", "Turkey-103516", "Turkmenistan-103104", 
                "Turks and Caicos Islands-102228", "Tuvalu-105410", "The former Yugoslav Republic of Macedonia-104111",
                
                "Uganda-101116", "Ukraine-104110", "United Arab Emirates-103517", 
                "United Kingdom of Great Britain and Northern Ireland-104217", "United States of America-102305", 
                "United States Minor Outlying Islands-102416", "United States Virgin Islands-102229", "Uruguay-102415", 
                "Uzbekistan-103105", 
                
                "Vanuatu-105205","Virgin Islands, British-102207","Viet Nam-103311", "Venezuela (Bolivarian Republic of)-102417", 

                "Western Africa-1015","Wallis and Futuna Islands-105411", "Western Asia-1035", "Western Europe-1044", "Western Sahara-101308", 
                "Yemen-103518",
                 
                "Zambia-101118", "Zimbabwe-101119"
            ]

    

    def table_data(self, query,query_count):

        conn = None
        try:
            self.loading_label.pack() # Show the loading label
            self.root.update()  # Update the UI to show the label      

            # Connect to MySQL database
            conn = database.DB_Connection()
            cursor = conn.cursor()
            # Execute the query
            cursor.execute(query)

            # Clear existing data in the Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Fetch and insert new data into Treeview
            rows = cursor.fetchall()
            for row in rows:
                # row_dict = dict(zip([desc[0] for desc in cursor.description], row))
                # country_code = row_dict.get('country')
                country_code = row['country']
                country_name = country_mapping.get(country_code, "Unknown")
                row['country'] = country_name
                # self.tree.insert("", "end", values=row + ("Configure",), tags="configure_button")
                row_values = tuple(row.values())  # Convert dictionary values to tuple
                self.tree.insert("", "end", values=row_values)# Insert data into Treeview
                # values_with_configure = row_values + ("Configure",)
                # self.tree.insert("", "end", values=values_with_configure, tags="configure_button")

            
            cursor.execute(query_count)
            result = cursor.fetchall()[0]
            total_count = result['TotalData']
            # Update the total count label
            self.total_count_label.config(text=f"Total Records: {total_count}")        

        except Exception as e:
            print("Error connecting to MySQL database:", e)

        finally:
            if conn:
                cursor.close()
                conn.close()
            self.loading_label.pack_forget()

    def search_data(self):
        # Retrieve search criteria
        tender_id = self.tender_id_entry.get()
        tender_link = self.tender_link_entry.get()
        country_value = self.countrydd_var.get()
        flag_value = self.flag_var.get()
        country_id = '' if country_value == "Select Country" or country_value == "Global" else country_value.split('-')[-1].strip()
        country_code =  find_country_codes(country_id, region_data)
        errorType1 = self.errordd_var.get()
        errorType = '' if errorType1.strip() == 'ErrorType' or errorType1.strip() == 'Select_Error'  else errorType1.strip()

        # Construct the base SQL query
        query = "SELECT tl.ID, tl.tender_link,tl.country, td.compare_error, td.error_date, tl.added_WPW FROM dms_wpw_tenderlinks tl LEFT JOIN dms_wpw_tenderlinksdata td ON tl.id = td.tlid "

        # Build the WHERE clause based on provided criteria
        conditions = []
        conditions.append("tl.process_type = 'Web Watcher'")
        if tender_id:
            conditions.append(f"tl.ID = '{tender_id}'")
            flag_value = ''
            country_code = ''
            tender_link = ''
            errorType = ''
        if tender_link:
            if len(tender_link) < 3  :
                self.error_label.config(text="Enter 3 or more characters in link field...")
                self.error_label.pack()
                self.root.update()
                # time.sleep(1)
                # self.error_label.pack_forget()
                return 
                
                # self.total_count_label.config(text=f"Enter or more character in link field...")
            elif len(tender_link)>0:
                self.error_label.pack_forget()
                conditions.append(f"tl.tender_link like '%{tender_link}%'")  
            else:
                self.error_label.pack_forget()
                conditions.append(f"tl.tender_link like '%{tender_link}%'") 
            # flag_value = ''
            # country = ''
        self.error_label.pack_forget()
        if flag_value:
            if errorType:
                conditions.append(f"tl.added_WPW = 'Y'")
            else:    
                conditions.append(f"tl.added_WPW = '{flag_value}'")
            # country = ''
        if country_code:
            if len(country_code) == 1:
                conditions.append(f"tl.`country` = '{country_code[0]}'")
            else:
                country_code_str = ", ".join([f"'{code}'" for code in country_code])
                conditions.append(f"tl.`country` IN ({country_code_str})")
            # flag_value = ''
        if errorType:
            if errorType == 'XPath Issue':
                errorType = 'XPath error'
            elif errorType == 'WebsiteIssue Type1' :
                errorType =  'unable to load url'  
            else:
                errorType = 'net::err_'

            conditions.append(f"td.compare_error like '{errorType.strip()}%'")


        # Concatenate all conditions with 'AND'
        where_clause = '1'
        if conditions:
            where_clause = " AND ".join(conditions)
        query += f"WHERE {where_clause} ORDER BY tl.ID ASC LIMIT 50 OFFSET {self.offset}"
        query_count = f"SELECT COUNT(tl.ID) AS TotalData FROM dms_wpw_tenderlinks tl LEFT JOIN dms_wpw_tenderlinksdata td ON tl.id = td.tlid WHERE {where_clause}"

        # Populate Treeview with data
        self.table_data(query,query_count)

    def configure_app(self, event):
        # col = self.tree.identify_column(event.x)  # Identify the clicked column
        # if col == '#6':  # Check if the clicked column is the "Action" column
        #     ROW_ID = self.tree.identify_row(event.y)  # Identify the clicked row
        #     item = self.tree.item(ROW_ID)
        #     if item and "Configure" in item["values"]:
        #         # Extract the tender_link value from the clicked row
        #         tender_link = item['values'][1]  # Assuming the tender_link is at index 1 in the values tuple
        #         tender_id_check = item['values'][0]
        #         id = tender_id_check

        #         ChromeDriver(tender_link,True,id)
            
        col = self.tree.identify_column(event.x)  # Identify the clicked column
        if col :  # Check if the clicked column is the "Action" column
            ROW_ID = self.tree.identify_row(event.y)  # Identify the clicked row
            item = self.tree.item(ROW_ID)
            # if item and "Status" in item["values"]:
            if item  :

                self.tree.tag_configure('highlight', background='lightblue')
                self.tree.item(ROW_ID, tags=('highlight',))
                
                def on_success_callback(ROW_ID):
                    self.tree.tag_configure('highlight', background='lightgreen')
                    self.tree.item(ROW_ID, tags=('highlight',))

                def on_Button_click_loader_callback():
                    self.error_label.config(text="Processing...")
                    self.error_label.pack()
                    self.root.update()

                def on_Button_click_remove_loader_callback():  
                    self.error_label.pack_forget()


                # Extract the tender_link value from the clicked row
                tender_link = item['values'][1]  # Assuming the tender_link is at index 1 in the values tuple
                tender_id_check = item['values'][0]
                id = tender_id_check

                ChromeDriver(tender_link,True,id,ROW_ID,on_success_callback,on_Button_click_loader_callback,on_Button_click_remove_loader_callback)
                


    def show_user_details(self):
        conn = database.DB_Connection()
        cursor = conn.cursor()
        
        # Define the work_done_count variable in the outer scope
        work_done_count = {"Y": 0, "N": 0, "H": 0}
        username = "Unknown"  # Default username
        
        # Function to update the counts based on the selected date filter
        def update_counts(date_filter_from=None,date_filter_to = None):
            conn = database.DB_Connection()
            cursor = conn.cursor()
            nonlocal work_done_count, username
            
            query_base = """SELECT u.name, a.activity_ref, COUNT(a.activity_ref) AS activity_count 
                            FROM `dms_wpw_user_activity` a
                            LEFT JOIN dms_wpw_user u ON a.user_id = u.user_id
                            WHERE a.user_id = {user_id}"""
            
            # Apply date filter if provided
            if date_filter_from and date_filter_to:
                query_base += f" AND DATE(a.activity_date) between  '{date_filter_from}' and '{date_filter_to}'"
            
            query_base += " GROUP BY u.name, a.activity_ref"
            
            query = query_base.format(user_id=global_var.user_id)
            cursor.execute(query)
            result = cursor.fetchall()
            
            if result:
                username = result[0]['name']  # Update the username
                work_done_count = {"Y": 0, "N": 0, "H": 0}
                for row in result:
                    activity_ref = row['activity_ref']
                    count = row['activity_count']
                    if activity_ref in work_done_count:
                        work_done_count[activity_ref] = count
            
            # Update labels
            details_window.title(f"Welcome {username}")
            y_count_label.config(text=f"Saved: {work_done_count['Y']}")
            n_count_label.config(text=f"Reject: {work_done_count['N']}")
            h_count_label.config(text=f"Hold: {work_done_count['H']}")
            total_of_counts.config(text=f"Total Activities: {work_done_count['Y'] + work_done_count['N'] + work_done_count['H']}")
            
            cursor.close()
            conn.close()

        # Create a new Toplevel window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Welcome {username}")
        details_window.geometry("300x200")

        # Frame for date input and search button
        filter_frame = tk.Frame(details_window)
        filter_frame.pack(anchor='w', pady=10, padx=10)
        
        # From Date selection date picker
        date_var_from = tk.StringVar(details_window)
        date_var_from.set(datetime.now().strftime("%Y-%m-%d"))  # Default to current date
        date_entry_from = DateEntry(filter_frame, textvariable=date_var_from, date_pattern='yyyy-mm-dd')
        date_entry_from.pack(side='left', padx=5)

        # to Date selection date picker
        date_var_to = tk.StringVar(details_window)
        date_var_to.set(datetime.now().strftime("%Y-%m-%d"))  # Default to current date
        date_entry_to = DateEntry(filter_frame, textvariable=date_var_to, date_pattern='yyyy-mm-dd')
        date_entry_to.pack(side='left', padx=5)
        
        # Search button to filter data
        search_button = tk.Button(filter_frame, text="Search", command=lambda:  update_counts(date_var_from.get(),date_entry_to.get()))
        search_button.pack(side='left')

        y_count_label = tk.Label(details_window, text=f"Saved: {work_done_count['Y']}", font=("Arial", 14))
        y_count_label.pack(anchor='w', padx=10, pady=2)

        n_count_label = tk.Label(details_window, text=f"Reject: {work_done_count['N']}", font=("Arial", 14))
        n_count_label.pack(anchor='w', padx=10, pady=2)

        h_count_label = tk.Label(details_window, text=f"Hold: {work_done_count['H']}", font=("Arial", 14))
        h_count_label.pack(anchor='w', padx=10, pady=2)

        # Total of counts
        total_of_counts = tk.Label(details_window, text=f"Total Activities: {work_done_count['Y'] + work_done_count['N'] + work_done_count['H']}", font=("Arial", 14))
        total_of_counts.pack(anchor='w', padx=10)

        # OK button to close the window
        ok_button = tk.Button(details_window, text="OK", command=details_window.destroy)
        ok_button.pack(anchor='e', pady=1, padx=1)
        
        # Initial update
        update_counts(date_var_from.get(),date_entry_to.get())


    def previous_data(self):
        if self.offset > 0:
            self.offset -= 100
            self.search_data()

    def next_data(self):
        self.offset += 100
        self.search_data()

    def exit_app(self):
        self.root.quit()
        sys.exit()

    def on_keyrelease(self, event):
        value = event.widget.get()
        matching_countries = [country for country in self.country_list if country.lower().startswith(value.lower())]
        self.country_combobox['values'] = matching_countries
        if matching_countries:
            self.country_combobox.event_generate('<Down>')




if __name__ == "__main__":
    root = tk.Tk()
    columns = ['Link_Id', 'Tender_Link', 'Country', 'Error', 'Error_Date', 'Status']
    app = GUIApp(root, columns)
    root.mainloop()