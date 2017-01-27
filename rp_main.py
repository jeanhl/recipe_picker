from docx import Document
import imaplib
from email import parser
from bs4 import BeautifulSoup
import quopri
import numpy as np
import pdb

def read(username, password):
    # Login to INBOX
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(username, password)  
    imap.select('INBOX')

    # Use search(), not status()
    status, response = imap.search(None, 'UNSEEN')
    unread_msg_nums = response[0].split()

    # Print the count of all unread messages
    print len(unread_msg_nums)

    # Print all unread messages from a certain sender of interest
    # status, response = imap.search(None, 'UNSEEN')  # OK ['email_id']

    # unread_msg_nums = response[0].split()
    da = []
    for e_id in unread_msg_nums:
        _, response = imap.fetch(e_id, '(UID BODY[TEXT])')  # OK [ response, in this case, body]
        # print "_, response", _, response[0][0], response[0][1]
        #text2 = BeautifulSoup(response[0][1], 'lxml')
        print quopri.decodestring(get_plain_text(response[0][1]))
        # print "--------------------------------", quopri.decodestring(response[0][1]), "--------------------------------"
        # print text2.get_text()
        da.append(response[0][1])
        print imap.fetch(e_id, '(BODY[HEADER.FIELDS (FROM)])')[1][0][1]  # 'From: Google <no-reply@accounts.google.com>''
        subject = imap.fetch(e_id, '(BODY[HEADER.FIELDS (SUBJECT)])')[1][0][1]
        print subject
    # print da

    # Mark them as seen
    # for e_id in unread_msg_nums:
    #     imap.store(e_id, '+FLAGS', '\Seen')


def get_plain_text(text):
    first_line_break = text.index('\r')
    gibberish = text[:first_line_break]
    second_gibberish_index = text.index(gibberish, first_line_break)
    printable_index = text.index('quoted-printable')
    plain_text = text[(printable_index + 16):second_gibberish_index].strip()
    return plain_text