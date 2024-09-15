import os
import sys
import global_var
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from TOTS3UploadLibrary.upload import UploadFile
from selenium.common.exceptions import TimeoutException
import re
from selenium.common.exceptions import WebDriverException
import boto3
import database
import wx
app = wx.App()
# HTML Code
html_code = """
<div id="tot_div_02" style="display: flex; flex-direction: column; !important ;">
    <div id="tot_input_div" style="text-align: center; !important ;">
         <input type="text" id="tot_xpathInput" style="width: 100%; max-width: 782px; height: 30px; background: white; !important ;">
    </div>
    <div id="tot_buttons_div" style="text-align: center; margin-top: 6px ; font-size: 14px; margin-right: 63px; overflow: auto; !important ;">
        <button id="tot_enabDisablink" style="background-color: #990505; background : #990505; height:31px; color: white;  max-width: 100%; margin-left: 30px ; !important ;"> Enable-link </button>
        <button id="tot_Copy" style="background-color: #990505;background : #990505; height:31px; color: white;  max-width: 100%; margin-left: 30px; !important ;">Copy-Xpath</button>
        <button id="tot_expandElement" style="background-color: #990505;background : #990505; height: 31px;color: white; max-width: 100%; margin-left: 30px ;!important ;">Expand-Element</button>
        <button id="tot_saveButton" style="background-color: #990505;background : #990505; height:31px; color: white;  max-width: 100%; margin-left: 30px ; !important ;">Save</button>
        <button id="tot_holdButton" style="background-color: #990505;background : #990505; height:31px; color: white;  max-width: 100%; margin-left: 30px ; !important ;">Hold</button>
        <button id="tot_done" style="background-color: #990505;background : #990505; height: 31px;color: white;max-width: 100%; margin-left: 30px ; !important ;">Close</button>
    </div>
</div>
"""

# css code
css_code = """
<style>
    .tot_highlighted {
        background-color: #80fa73 !important;
        background : #990505  !important;
        outline: 2px solid red !important;
    }

    [dir='ltr'] button {
    float: none !important;
    }

</style>

"""

# Javascript Code
js_code = f"""

//Define Variables

var htmlCode = {repr(html_code)};
var cssCode = {repr(css_code)};

var combinedCode = cssCode + htmlCode;


var inputElement = document.createElement('div');
inputElement.innerHTML = combinedCode;
document.body.appendChild(inputElement);
inputElement.id = 'tot_div_01';
inputElement.style.cssText = 'position: fixed; bottom: 0; background-color: #b5b5b5;background : #b5b5b5;z-index: 2147483647; border: 1px solid black; width: 100%; max-width: 864px; margin:0px 232px; padding: 10px; box-sizing: border-box; !important ;';

var xpathInput = inputElement.querySelector('#tot_xpathInput');
var saveButton = inputElement.querySelector('#tot_saveButton');
var linkButton = inputElement.querySelector('#tot_enabDisablink');
var ExpandElementButton = inputElement.querySelector('#tot_expandElement');
var copyButton = inputElement.querySelector('#tot_Copy');
var done = inputElement.querySelector('#tot_done');
var hold = inputElement.querySelector('#tot_holdButton');

var hoveredElement = null;
var linksEnabled = false;


// Define Function
//Mouse Hover function
document.addEventListener('mousemove', function (e) {{
    var target = e.target;
    if (target !== hoveredElement) {{
        // MouseLeave
        if (hoveredElement) {{
            hoveredElement.style.cssText = hoveredElement.originalStyle;
            hoveredElement = null;
        }}

        if (target) {{
            if (
                target.id !== 'tot_div_02' && target.id !== 'tot_input_div' && target.id !== 'tot_xpathInput' &&  target.id !== 'tot_buttons_div' && target.id !== 'tot_enabDisablink' && target.id !== 'tot_saveButton' && target.id !== 'tot_shortElement' && target.id !== 'tot_expandElement' && target.id !== 'tot_div_01' && target.id !== 'tot_Copy' && target.id !== 'tot_done' && target.id !== 'tot_holdButton'
            ) {{
                hoveredElement = target;
                hoveredElement.originalStyle = target.style.cssText;
                target.style.cssText += 'BORDER-BOTTOM: red 2px solid; BORDER-LEFT:red 2px solid; BACKGROUND-COLOR: #c8ffc2;BACKGROUND: #c8ffc2; BORDER-TOP: red 2px solid; BORDER-RIGHT:red 2pxx solid ; !important ;';
            }}
        }}
    }}
}});


// Div click Function 
document.onclick = function (event) {{
    if (event === undefined) event = window.event;

    var target = 'target' in event ? event.target : event.srcElement;

    if (
        target.id !== 'tot_div_02' && target.id !== 'tot_input_div' && target.id !== 'tot_xpathInput' &&  target.id !== 'tot_buttons_div' && target.id !== 'tot_enabDisablink' && target.id !== 'tot_saveButton' && target.id !== 'tot_shortElement' && target.id !== 'tot_expandElement' && target.id !== 'tot_div_01' && target.id !== 'tot_Copy' && target.id !== 'tot_done' && target.id !== 'tot_holdButton'
    ) {{
        var xpath = getPathTo(target);
        xpathInput.value = xpath;
        highlightElement(xpathInput.value)

    }}
}};


//get Xpath 
function getPathTo(element) {{
    if (element.id !== '' && element.id !== undefined) {{
        return "//*[@id='"+element.id+"']";
    }}
    if (!element) {{
        return '/html[1]'; // Check if element is null
    }}
    if (element.tagName.toLowerCase() === 'html') {{
        return '/html[1]'; // Handle html element separately
    }}
    if (element.tagName.toLowerCase() === 'body') {{
        return '/html[1]/body[1]'; // Handle body element separately
    }}

    var ix = 0;
    var siblings = (element.parentNode && element.parentNode.childNodes) ? element.parentNode.childNodes : null;
    if (!siblings) {{
        return getPathTo(element.parentNode) + '/' + element.tagName.toLowerCase() + '[1]'; // If no siblings, return the path for the parent node
    }}

    for (var i = 0; i < siblings.length; i++) {{
        var sibling = siblings[i];
        if (sibling === element) {{
            return getPathTo(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
        }}
        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {{
            ix++;
        }}
    }}
}}


// Save button function
saveButton.addEventListener('click', function() {{
    var xpath = xpathInput.value;
    if (xpath.trim() !== '') {{
        window.xPathValue = xpath;
    }}
}});

//Enab-Disab-link function
function disableLinks() {{
    var links = document.getElementsByTagName('a');
    for (var i = 0; i < links.length; i++) {{
        links[i].style.pointerEvents = 'none';
    }}
}}
linkButton.addEventListener('click', function() {{
    var links = document.getElementsByTagName('a');
    for (var i = 0; i < links.length; i++) {{
        if (linksEnabled) {{
            links[i].style.pointerEvents = 'none';
            linkButton.textContent = 'Enable-Link';
        }} else {{
            links[i].style.pointerEvents = 'auto';
            linkButton.textContent = 'Disable-Link';
        }}
    }}
    linksEnabled = !linksEnabled;
}});


// ExpandElement function
ExpandElementButton.addEventListener('click', function () {{
    var xpathValue = xpathInput.value;

    // Shorten the XPath
    var shortenedXPath = ExpandElement(xpathValue);
    xpathInput.value = shortenedXPath;
    highlightElement(xpathInput.value)

}});

function ExpandElement(xpath) {{
    var lastIndex = xpath.lastIndexOf('/');
    if (lastIndex !== -1) {{
        return xpath.substring(0, lastIndex);
    }}    
    return xpath;
}}


// Copy button function
copyButton.addEventListener('click', function () {{
    copyToClipboard(xpathInput.value);
}});

function copyToClipboard(text) {{
    var textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
}}


// Function to highlight the element
function highlightElement(xpath) {{
    // Remove 'tot_highlighted' class from all elements
    var highlightedElements = document.querySelectorAll('.tot_highlighted');
    highlightedElements.forEach(function (element) {{
        element.classList.remove('tot_highlighted');
    }});

    // Add 'tot_highlighted' class to the new target
    var target = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

    if (target) {{
        target.classList.add('tot_highlighted');
    }} else {{
        console.error("Target element not found.");
    }}
}}

// done button function
done.addEventListener('click', function () {{
    window.xPathValue = 'DONE';
}});


// hpld button function
hold.addEventListener('click', function () {{
    window.xPathValue = 'hold';
}});

//Function calling

disableLinks();

"""

# Python Codpyt
def ChromeDriver(url, loop, tlid,ROW_ID,on_success_callback,on_Button_click_loader_callback,on_Button_click_remove_loader_callback):

    conn = database.DB_Connection()
    try:
        value = []
        # driver = webdriver.Chrome('chromedriver.exe')
        chrome_options = Options()
        # chrome_options.binary_location = "/usr/bin/google-chrome"  # Update if needed
        chrome_service = Service('chromedriver.exe')
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.maximize_window()

        def inject(driver, url, js_code):
            try:
                driver.get(url)
                driver.execute_script(js_code)
            except TimeoutException as e:
                print(f'Timeout error in accessing URL on driver.get(): {e}')
                driver.execute_script(js_code)
            except Exception as e:
                if 'ERR_CONNECTION_TIMED_OUT' in str(e):
                    print(f'Connection timed out: {e.msg}')
                    driver.execute_script(js_code)
                if "Failed to set the 'innerHTML' property on 'Element" in str(e) :
                    wx.MessageBox("Please click on 'Advanced', then click on 'proceed to ('link')'  then wait for 5 second  then click OK !!\n\nGo for another link..!!\n\nERROR: " + str(e.msg), str("Webwatcher"), wx.OK | wx.ICON_ERROR)
                    time.sleep(5)
                    driver.execute_script(js_code)    
                else:
                    # print(f'An error occurred: {e.msg}')
                    wx.MessageBox("Unable to load the link, close the browser directly..!!\n\nGo for another link..!!\n\nERROR: " + str(e.msg), str("Webwatcher"), wx.OK | wx.ICON_ERROR)
            for i in range(10):
                value.append("")

        initial_url = url
        inject(driver, initial_url, js_code)

        while loop:
            try:
                if not driver or not driver.window_handles:
                    print("Driver is not open. Exiting the loop.")
                    loop = False
                    break

                current_url = driver.current_url

                # this part is commented  because there are some links which changes on every load 
                # if current_url != initial_url:
                #     inject(driver, current_url, js_code)
                #     initial_url = current_url

                change_target_js = """
                    var links = document.getElementsByTagName('a');
                    for (var i = 0; i < links.length; i++) {{
                    if (links[i].getAttribute('target') === '_blank') {{
                    links[i].setAttribute('target', '_self');
                    }}
                }}
                """
                driver.execute_script(change_target_js)

                xpath_value = driver.execute_script("return window.xPathValue;")
                if xpath_value == "DONE":
                    print("Done button clicked. Closing the driver.")
                    # driver.execute_script("window.xPathValue = null;")
                    driver.quit()
                    loop = False
                    break
                elif xpath_value == "hold":
                    on_Button_click_loader_callback()
                    driver.minimize_window()
                    print("Hold  button clicked.")
                    update_column_links(tlid, "H" , conn)
                    # insert in activity table / insert_into_user_activity_tbl(tlid, "H")
                    insert_into_user_activity_tbl(tlid, "H",conn,ROW_ID,on_success_callback,on_Button_click_remove_loader_callback)
                    loop = False
                    driver.execute_script("window.xPathValue = null;")
                    driver.quit()
                    break
                elif xpath_value is not None:
                    on_Button_click_loader_callback()
                    driver.minimize_window()
                    if xpath_value.strip():
                        print(xpath_value)
                        Element = driver.find_element(By.XPATH, xpath_value)
                        value[0] = xpath_value
                        outer_html = Element.get_attribute("outerHTML")
                        value[1] = cleanhtml(outer_html)
                        value[2] = driver.title
                        value[3] = initial_url
                        value[4] = tlid
                        is_found = check_duplication(value,conn)
                        filename = createFile(value)
                        value[5] = filename
                        if is_found:
                            update_into_links_data(value,conn)
                        else:
                            insert_into_links_data(value,conn)
                        loop = False
                        # insert in activity table / insert_into_user_activity_tbl(tlid, "Y")
                        insert_into_user_activity_tbl(tlid, "Y",conn,ROW_ID,on_success_callback,on_Button_click_remove_loader_callback)
                        driver.execute_script("window.xPathValue = null;")
                        driver.quit()
                        break
            except WebDriverException as e:
                print("Browser window closed unexpectedly. Exiting the loop.",e.msg)
                driver.quit()
                break
    except WebDriverException as we:
        print(f"Error occurred while accessing the URL: {we}", url)
        


def check_duplication(value,conn):
    try:
        # conn = database.DB_Connection()
        cursor = conn.cursor()
        query2 = "SELECT * from dms_wpw_tenderlinksdata where tlid = %s LIMIT 1"
        cursor.execute(query2, value[4])
        data = cursor.fetchall()
        if len(data) >= 1:
            return True
        else:
            return False
    except Exception as e:
        print(e)

def createFile(value):
    filename = ""
    try:
        Fileid = "".join([str(value[4]) + "-" + "newhtmlfile"])
        current_directory = "C:\\webpagewatcherfiles\\"
        if not os.path.exists(current_directory):
            os.makedirs(current_directory)
        for filename in os.listdir(current_directory):
            try:
                os.unlink(os.path.join(current_directory, filename))
            except: pass
        filename = Fileid + ".html"
        Path = current_directory + filename
        file1 = open(Path, "w", encoding="utf-8")
        Final_Doc = value[1]
        file1.write(Final_Doc)
        file1.close()
        upload_to_s3(Path, "webpagewatcher")
        print("File upload to s3 successful")
        os.unlink(Path) # unlink file/Path
        print("File deleted from local successfully.")
        return filename

    except Exception as e:
        print(e)
    return filename

def insert_into_links_data(value,conn):
    try:
        CheckDuration = "-"
        CompareBy = "Text"
        ChangesLimit = "-"
        # conn = database.DB_Connection()
        cursor = conn.cursor()
        query = "INSERT INTO dms_wpw_tenderlinksdata (`tlid`, `Title`, `Url`, `XPath`, `CheckDuration`, `CompareBy`, `ChangesLimit`, `newHtmlPath`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            value[4],
            value[2],
            value[3],
            value[0],
            CheckDuration,
            CompareBy,
            ChangesLimit,
            value[5],
        )
        cursor.execute(query, values)
        conn.commit()
        print("Data inserted in tenderlinksdata tbl successfully.")
        update_column_links(value[4], "Y", conn)
    except Exception as e:
        print(e)

def update_column_links(id, action,conn):
    try:
        # conn = database.DB_Connection()
        cursor = conn.cursor()
        if action == "H":
            query = "UPDATE dms_wpw_tenderlinks SET added_WPW = %s WHERE ID = %s"
            values = (action, id)
        else:
            query = "UPDATE dms_wpw_tenderlinks SET added_WPW = %s WHERE ID = %s"
            values = (action, id)
        cursor.execute(query, values)
        conn.commit()
        print("Data updated successfully.")
    
    except Exception as e:
        print(e)

def update_into_links_data(value,conn):
    try:
        CheckDuration = "-"
        CompareBy = "Text"
        ChangesLimit = "-"
        compare_error = ""
        error_date = ""
        # conn = database.DB_Connection()
        cursor = conn.cursor()
        query = "UPDATE dms_wpw_tenderlinksdata SET `Title` = %s, `Url` = %s, `XPath` = %s, `CheckDuration` = %s, `CompareBy` = %s, `ChangesLimit` = %s, `newHtmlPath` = %s, compare_error = %s, error_date = %s WHERE `tlid` = %s"
        values = (
            value[2],
            value[3],
            value[0],
            CompareBy,
            ChangesLimit,
            value[5],
            value[4],
            compare_error,
            error_date
            )
        cursor.execute(query, values)
        conn.commit()
        print("Data Updated in tenderlinksdata tbl successfully.")
        update_column_links(value[4], "Y", conn)
    except Exception as e:
        print(e)

def insert_into_user_activity_tbl(tlid,action,conn,ROW_ID,on_success_callback,on_Button_click_remove_loader_callback):
    try:
        activity_name = 'SelectHtmlElement'
        ip_address = get_public_ip()
        userid = global_var.user_id
        # conn = database.DB_Connection()
        cursor = conn.cursor()
        query = "INSERT INTO dms_wpw_user_activity (`tlid`, `activity_name`, `activity_ref`, `user_id`, `ip_address`) VALUES (%s, %s, %s, %s, %s)"
        values = (
            tlid,
            activity_name,
            action,
            userid,
            ip_address
        )
        cursor.execute(query, values)
        conn.commit()
        print("Data inserted in dms_wpw_user_activity tbl successfully.")
        #on_success_callback TO HIGHLIGHT THE ROW 
        on_Button_click_remove_loader_callback()
        on_success_callback(ROW_ID)
    except Exception as e:
        print(e)

    finally :
        cursor.close()  
        conn.close()  

def upload_to_s3(filepath, directory):
    loop = 0
    while loop == 0:
        try:
            result = UploadFile(filepath, directory)
            if result == True:
                loop = 1  # success
            else:
                print("Error while uploading file on S3 Bucket..!")
                time.sleep(10)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(
                "Error ON : ",
                sys._getframe().f_code.co_name + "--> " + str(e),
                "\n",
                exc_type,
                "\n",
                fname,
                "\n",
                exc_tb.tb_lineno,
            )
            time.sleep(10)

# def hold_button(id):
#     conn = database.DB_Connection()
#     cursor = conn.cursor()
#     query = "UPDATE dms_wpw_tenderlinks SET added_WPW = %s WHERE ID = %s"
#     values = ("H",id)
#     cursor.execute(query, values)
#     conn.commit()

def cleanhtml(raw_html):
    cleantext = re.sub(r"\s+", " ", raw_html)
    cleantext = cleantext.replace('\r','').replace('\n','').replace('\t','').strip()
    return cleantext

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()  # Raise an error for bad status codes
        ip = response.json()['ip']
        return ip
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None    