import logging

from google.appengine.api import mail
from google.appengine.api import taskqueue
import webapp2

from dateutil import *
from model import *

REMINDER = """
Hello Carbonista,

Let us know what you've been up to.
"""


class ReminderEmail(webapp2.RequestHandler):
    def get(self):
        all_users = User.all().filter("enabled =", True).fetch(500)
        for user in all_users:
            # TODO: Check if one has already been submitted for this period.
            taskqueue.add(url='/onereminder', params={'email': user.email})


class OneReminderEmail(webapp2.RequestHandler):
    def post(self):
        mail.send_mail(sender="snippets <snippets@crb-snippets-test.appspotmail.com>",
                       to=self.request.get('email'),
                       subject="It's Snippet time!!!",
                       body=REMINDER)

    def get(self):
        post(self)


class DigestEmail(webapp2.RequestHandler):
    def get(self):
        all_users = User.all().filter("enabled =", True).fetch(500)
        for user in all_users:
            taskqueue.add(url='/onedigest', params={'email': user.email})


class OneDigestEmail(webapp2.RequestHandler):
    def __send_mail(self, recipient, body):
        mail.send_mail(sender="snippets <snippets@crb-snippets-test.appspotmail.com>",
                       to=recipient,
                       subject="*** Snippets Delivery *** :)",
                       body=body)

    def __snippet_to_text(self, snippet):
        divider = '-' * 30
        return '%s\n%s\n%s' % (snippet.user.pretty_name(), divider, snippet.text)

    def get(self):
        post(self)

    def post(self):
        user = user_from_email(self.request.get('email'))
        d = date_for_retrieval()
        all_snippets = Snippet.all().filter("date =", d).fetch(500)
        all_users = User.all().fetch(500)
        following = compute_following(user, all_users)
        logging.info(all_snippets)
        body = '\n\n\n'.join([self.__snippet_to_text(s) for s in all_snippets if s.user.email in following])
        if body:
            self.__send_mail(user.email, 'https://crb-snippets-test.appspot.com\n\n' + body)
        else:
            logging.info(user.email + ' not following anybody.')
