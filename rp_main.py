# from docx import Document
from datetime import date
import imaplib
import quopri
import pdb
import os

USERNAME = os.environ.get("USERNAME_EMAIL")
PASSWORD = os.environ.get("PASSWORD_EMAIL")
SENDER = os.environ.get("SENDER_EMAIL")
REPO = os.environ.get("RECIPE_REPO")


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
            _, response = mail.fetch(email_id, '(UID BODY[TEXT])')  # returns OK [body]
            body_text = quopri.decodestring(get_plain_text(response[0][1]))
            subject = mail.fetch(email_id, '(BODY[HEADER.FIELDS (SUBJECT)])')[1][0][1]
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
    os.chdir("/Users/JLiu2/Dropbox/recipe_repo")
    new_recipe = open(title, 'w')
    new_recipe.write(subject + '\n' + '\n')
    new_recipe.write(body + '\n' + '\n')
    new_recipe.write("Recipe recorded automatically on " + str(date.today()))
    new_recipe.close()
    print "New file titled " + title + " created."


if __name__ == "__main__":
    read(USERNAME, PASSWORD, SENDER)