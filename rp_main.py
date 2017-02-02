# from docx import Document
# from apscheduler.schedulers.background import BackgroundScheduler
from httplib2 import Http
from apiclient import discovery, errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from email.mime.text import MIMEText
from datetime import date
import random
import base64
import mimetypes
import httplib2
import imaplib
import quopri
import pdb
import os

USERNAME = os.environ.get("USERNAME_EMAIL")
PASSWORD = os.environ.get("PASSWORD_EMAIL")
SENDER = os.environ.get("SENDER_EMAIL")
REPO = os.environ.get("RECIPE_REPO")

################## GMAIL OAUTH ############################
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


credentials = get_credentials()
service = discovery.build('gmail', 'v1', http=credentials.authorize(Http()))
########################################################################


def read(USERNAME, PASSWORD, SENDER):
    # USERNAME = USERNAME of gmail that accepts the recipes and commands
    # PASSWORD = PASSWORD of said gmail account
    # SENDER = for security purposes, only get text body from certain SENDER
    # SENDER format = "First Last <SENDER@gmail.com>"

    # connecting to gMail's imap, logging in and going into INBOX
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(USERNAME, PASSWORD)
    mail.select('INBOX')  # going into the inbox

    status, response = mail.search(None, 'UNSEEN')  # only looking at unread emails
    new_email_ids = response[0].split()  # response is a list of string ['1 2 3 4']
    print "New Emails Found: " + str(len(response[0].split()))

    for email_id in new_email_ids:
        sender_mail = mail.fetch(email_id, '(BODY[HEADER.FIELDS (FROM)])')[1][0][1]  # 'From: Google <no-reply@accounts.google.com>'
        if sender_mail[6:].strip() == SENDER:
            subject = mail.fetch(email_id, '(BODY[HEADER.FIELDS (SUBJECT)])')[1][0][1]
            _, response = mail.fetch(email_id, '(UID BODY[TEXT])')  # returns OK [body]
            subject = subject[9:].strip()
            body_text = quopri.decodestring(get_plain_text(response[0][1]))
            if subject.lower() == "recipe request":
                get_recipe(body_text)
            else:
                make_new_txt_file(body_text, subject[9:].strip())


def get_plain_text(text):
    # takes in a massive string like an email body
    # removes the headers, text/html portion
    # returns a cleaned up text of the email body
    first_line_break = text.index('\r')
    gibberish = text[:first_line_break]
    second_gibberish_index = text.index(gibberish, first_line_break)
    start_index = text.index('\r\n\r\n')
    plain_text = text[(start_index):second_gibberish_index].strip()
    return plain_text


def make_new_txt_file(body, subject):
    # takes in the body of the email and writes it into a word doc
    # saves under the name of the subject of the email
    # time stamped
    title = subject.lower() + " " + str(date.today()) + '.txt'
    os.chdir(REPO)
    new_recipe = open(title, 'w')
    new_recipe.write(subject + '\n' + '\n')
    new_recipe.write(body + '\n' + '\n')
    new_recipe.write("Recipe recorded automatically on " + str(date.today()))
    new_recipe.close()
    print "New file titled " + title + " created."


def get_recipe(ingredients):
    # takes a string of ingredients separated by comma
    # converts string into list of ingredients
    # finds recipes in the repo with matching ingredients
    # picks 1 randomly
    # returns the recipe as a string
    ingredients_lst = ingredients.split(",")
    ingredients = []
    for ingredient in ingredients_lst:
        ingredients.append(ingredient.strip())
    recipes = {"all": []}  # dictionary to hold the recipes containing the ingredients
    recipe_found = False
    for ingredient in ingredients:
        recipes[ingredient] = []
    files = os.listdir(REPO)
    for afile in files:
        if afile[-4:] == ".txt":
            afile = REPO+afile
            ingredients_matched = []
            for i in range(len(ingredients)):
                if ingredients[i] in open(afile).read():
                    print "We found the ingredient"
                    recipe_found = True
                    ingredients_matched.append(i)
                    recipes[ingredients[i]].append(afile)
                    if len(ingredients_matched) == len(ingredients):
                        recipes["all"].append(afile)
                else:
                    print "we did not find the ingredient"
                    continue

    if recipe_found:
        if len(recipes["all"]) != 0:
            choosen_recipe = recipes["all"][random.randint(0, len(recipes["all"])-1)]
        else:
            category = get_ingredient_category(ingredients)
            choosen_recipe = recipes[category]
    else:
        choosen_recipe = "No recipe found.txt"

    sender = USERNAME+"@gmail.com"
    to = SENDER
    subject = choosen_recipe[33:]
    message_text = open(choosen_recipe, 'r').read()
    email = create_message(sender, to, subject, message_text)
    sent_email = send_message(service, "me", email)
    print "******" + str(sent_email) + "********"


def get_ingredient_category(ingredients):
    """ get a dictionary of ingredients and their recipes
    returns a category of ingredient that isn't "all" or have no recipes
    """
    category = random.choice(ingredients.keys())
    if category == "all" or len(ingredients[category]) == 0:
        get_ingredient_category(ingredients)
    else:
        return category


def create_message(sender, to, subject, message_text):
    """Create a message for an email.
    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def send_message(service, user_id, message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error


if __name__ == "__main__":
    read(USERNAME, PASSWORD, SENDER)
