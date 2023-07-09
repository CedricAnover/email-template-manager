import gooeypie as gp

from threading import Thread
from email.message import EmailMessage
import ssl
import smtplib

import json
from decorator import decorator
from typing import List
from dataclasses import dataclass, asdict

########################################################################################################################
###### Global Variables
TEMPLATES = {} # List of Templates Dict[name:str -> Template]

########################################################################################################################

@dataclass
class Template:
    name : str
    send_to : str # "<email>;<email>;...;<email>"
    subject : str
    message : str

def open_login_window(event):
    print("Opening Login Window ...")
    login_window.show_on_top()

def cancel_login_window(event):
    print("Cancelling Login Window ...")
    login_window.hide()

def ok_login_window(event):
    # Save/Store the Login Details.
    # Check if Login Details are correct.
    if  not (login_pass_inp.text.strip() and login_email_inp.text.strip()):
        app.alert("No Email or Password Given", "You must provide valid email and password", "error")
    else:
        login_window.hide() # Hide the Login Window

def save_template(event):
    global TEMPLATES
    # Update the Template ListBox Widget.

    # New Template Instances based on the current state
    template = Template(tmplt_name_inp.text, send_to_inp.text, subject_inp.text, message_txtbx.text)

    if tmplt_name_inp.text in template_lsbx.items: # If name exits, warn if user wants to overwrite.
        result = app.confirm_yesno("Template Already Exist", "Do you want to overwrite the template?", 'warning')
        if result: # If user want to overwrite
            TEMPLATES[tmplt_name_inp.text] = template # Overwrite
    else: # New template
        if not template.name.strip(): # Check if Template Name is empty
            app.alert("Bad Template Name", "Find a non-empty Name for the Template", "error")
        else:
            # Add the New Template in ListBox
            template_lsbx.add_item(template.name)
            TEMPLATES[template.name] = template

def thread_send_message():
    # https://stackoverflow.com/questions/8856117/how-to-send-email-to-multiple-recipients-using-python-smtplib
    recipients = str(send_to_inp.text)
    recipients = recipients.split(';')  # Remove whitespaces, and split by ';'
    recipients = [recipient.strip() for recipient in recipients]

    em = EmailMessage()
    em["From"] = login_email_inp.text
    em["To"] = ", ".join(recipients)
    em["Subject"] = subject_inp.text
    em.set_content(message_txtbx.text)

    context = ssl.create_default_context()
    # TODO: Create solution for checking user email and match it with appropriate server
    # https://stackoverflow.com/questions/57715289/how-to-fix-ssl-sslerror-ssl-wrong-version-number-wrong-version-number-ssl
    with smtplib.SMTP('smtp-mail.outlook.com', 587) as smtp:
        try:
            smtp.starttls(context=context)
            smtp.login(login_email_inp.text, login_pass_inp.text)
            smtp.sendmail(login_email_inp.text, recipients, em.as_string())
        except Exception as error:
            app.alert("Error Message", str(error), "error")

def send_message(event):
    """Send to Recipients"""
    result = app.confirm_okcancel("Send Email Confirmation", "Are you sure you want to send the email?", "question")
    if result:
        thread = Thread(target=thread_send_message)
        thread.start() # Start thread_send_message() in a separate thread

def template_double_clicked(event):
    global TEMPLATES
    print(event)
    print(TEMPLATES)
    # Get the template from doubl-clicked item.
    template = TEMPLATES[template_lsbx.selected]

    # Update & Fill the Main Window Input and Textbox with the double-clicked template
    send_to_inp.text = template.send_to
    subject_inp.text = template.subject
    message_txtbx.text = template.message
    tmplt_name_inp.text = template.name

    template_lsbx.select_none()  # Dont select any

def delete_template(event):
    """Delete Selected Template"""
    global TEMPLATES
    try:
        result = app.confirm_yesno("Delete Confirmation", "Do you want to delete the template?", 'question')
        if result:
            TEMPLATES.pop(template_lsbx.selected)
            template_lsbx.remove_selected() # Delete Selected
    except Exception as error:
        app.alert("Error Message", str(error), 'error')
    else:
        template_lsbx.select_none() # Dont select any

def delete_all_templates(event):
    """Delete All Templates"""
    global TEMPLATES
    try:
        result = app.confirm_yesno("Delete Confirmation", "Do you want to delete all the  templates?", 'question')
        if result:
            TEMPLATES = {} # Reset TEMPLATES to empty dictionary
            template_lsbx.clear()
    except Exception as error:
        app.alert("Error Message", str(error), 'error')
    else:
        clear(event)

def clear(event):
    """Clear/Reset Contents in Main Window"""
    send_to_inp.text = ''
    subject_inp.text = ''
    message_txtbx.text = ''
    tmplt_name_inp.text = ''

    template_lsbx.select_none() # Dont select any

def OnOpen():
    print("Opening App ...")
    global TEMPLATES
    try:
        with open("templates.json", "r") as file:
            # raw_templates = json.load(file) # List[Dict] Indcluding the Name
            raw_templates = file.read()
            raw_templates = json.loads(raw_templates) # List[Dict] Indcluding the Name
            print(raw_templates)
            TEMPLATES = {_dict['name']:Template(**_dict) for _dict in raw_templates}
            print(TEMPLATES)
            # Update ListBox
            for template_name in TEMPLATES.keys():
                template_lsbx.add_item(template_name)
            print(template_lsbx.items)
    except FileNotFoundError:
        pass
    except Exception as error:
        app.alert("Error Message", str(error), 'error')

def OnClose():
    print("Closing App ...")
    global TEMPLATES
    try:
        with open("templates.json", "w") as file:
            #TEMPLATES # Dict[name -> Dataclass]
            print(TEMPLATES)
            out_temp = [asdict(dc) for _,dc in TEMPLATES.items()] # List[Dict]
            print(out_temp)
            json.dump(out_temp, file) # Save to json file
    except Exception as error:
        app.alert("Error Message", str(error), 'error')
        print(error)
    else:
        return True
########################################################################################################################
###### Main Window Configuration
app = gp.GooeyPieApp('Email Template Manager')
app.set_grid(4, 4) # Set Main Window Grid
app.width = 850
app.height = 450
app.set_resizable(False)
app.set_column_weights(3, 0, 5, 5)
app.set_row_weights(1, 3, 3, 3)

# Create Menu Item 'Login' to ask for user Email Login Details
app.add_menu_item('File', 'Login', open_login_window)

app.add_menu_item('Edit', 'Clear', clear)
app.add_menu_item('Edit', 'Delete', delete_template)
app.add_menu_item('Edit', 'Delete All', delete_all_templates)

########################################################################################################################
###### Login Window
login_window = gp.Window(app, 'Login')
# login_window.width = 800
# login_window.height = 400
login_window.set_grid(3, 3)

login_email_lbl = gp.Label(login_window, "Login: ")
login_window.add(login_email_lbl, 1, 1, align='center', valign='middle', stretch=False, fill=False)
login_email_inp = gp.Input(login_window)
login_window.add(login_email_inp, 1, 2, align="left", valign="middle", stretch=False, fill=True, column_span=2)

login_pass_lbl = gp.Label(login_window, "Password: ")
login_window.add(login_pass_lbl, 2, 1, align='center', valign='middle', stretch=False, fill=False)
login_pass_inp = gp.Secret(login_window)
login_window.add(login_pass_inp, 2, 2, align="left", valign="middle", stretch=False, fill=True, column_span=2)

login_ok_btn = gp.Button(login_window, "Ok", ok_login_window)
login_window.add(login_ok_btn, 3, 2, align='center', valign='middle', stretch=False, fill=False)
login_cancel_btn = gp.Button(login_window, "Cancel", cancel_login_window)
login_window.add(login_cancel_btn, 3, 3, align='center', valign='middle', stretch=False, fill=False)

########################################################################################################################
###### Main Window Widgets
template_lsbx = gp.Listbox(app, []) # Create Listbox Widget for the Templates
template_lsbx.disabled = False
template_lsbx.multiple_selection = False
app.add(template_lsbx, 1, 1, align="center", valign="middle", stretch=True, row_span=4)
template_lsbx.add_event_listener("double_click", template_double_clicked) # Callback when Item is double-clicked

send_to_lbl = gp.Label(app, "Send to: ")
app.add(send_to_lbl, 1, 2, align='center', valign='middle', stretch=False, fill=True)

subject_lbl = gp.Label(app, "Subject: ")
app.add(subject_lbl, 2, 2, align='center', valign='middle', stretch=False, fill=True)

send_to_inp = gp.Input(app)
app.add(send_to_inp, 1, 3, align="left", valign="middle", stretch=False, fill=True, column_span=2)

subject_inp = gp.Input(app)
app.add(subject_inp, 2, 3, align="left", valign="middle", stretch=False, fill=True, column_span=2)

message_txtbx = gp.Textbox(app)
app.add(message_txtbx, 3, 2, align="left", valign="middle", stretch=True, fill=True, column_span=3)

save_tmplt_btn = gp.Button(app, "Save Template", save_template)
app.add(save_tmplt_btn, 4, 2, align="center", valign="middle", stretch=False, fill=False)

send_btn = gp.Button(app, "Send", send_message)
app.add(send_btn, 4, 4, align="center", valign="middle", stretch=False, fill=False)

tmplt_name_inp = gp.Input(app)
app.add(tmplt_name_inp, 4, 3, align="center", valign="middle", stretch=False, fill=False)

########################################################################################################################
app.on_open(OnOpen)
app.on_close(OnClose)

if __name__ == "__main__":
    app.run()