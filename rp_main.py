from docx import Document
import imaplib
from email import parser
from bs4 import BeautifulSoup
import quopri
import numpy as np
import pdb


def read(username, password, sender):
    # username = username of gmail that accepts the recipes and commands
    # password = password of said gmail account
    # sender = for security purposes, only get text body from certain sender
    # sender format = "First Last <sender@gmail.com>"
    # connecting to gMail's imap, logging in and going into INBOX
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(username, password)
    mail.select('INBOX')  # going into the inbox

    status, response = mail.search(None, 'UNSEEN')  # only looking at unread emails
    new_email_ids = response[0].split()  # response is a list of string ['1 2 3 4']
    print response

    for e_id in new_email_ids:
        sender = mail.fetch(e_id, '(BODY[HEADER.FIELDS (FROM)])')[1][0][1]  # 'From: Google <no-reply@accounts.google.com>'
        print sender, type(sender)
        if sender[6:].strip() == sender:
            _, response = mail.fetch(e_id, '(UID BODY[TEXT])')  # returns OK [body]
            print quopri.decodestring(get_plain_text(response[0][1]))
            subject = mail.fetch(e_id, '(BODY[HEADER.FIELDS (SUBJECT)])')[1][0][1]
            print sender, subject

    # Mark them as seen
    # for e_id in unread_msg_nums:
    #     mail.store(e_id, '+FLAGS', '\Seen')


def get_plain_text(text):
    first_line_break = text.index('\r')
    gibberish = text[:first_line_break]
    second_gibberish_index = text.index(gibberish, first_line_break)
    start_index = text.index('\r\n\r\n')
    plain_text = text[(start_index):second_gibberish_index].strip()
    return plain_text