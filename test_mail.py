import os, sys
import requests
import urllib2
import urlparse

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders

def post_mail(url, send_from, send_to, subject, text, files=[]):
    assert isinstance(files, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    m = msg.as_string()
    print send_to
    u = urlparse.urljoin(url, "/_ah/mail/" + urllib2.quote(send_to))
    print u
    requests.post(u, data=m, headers={'content-type':'multipart/alternative'})


if __name__ == '__main__':
    if len(sys.argv) < 6:
        print >> sys.stderr, "Usage: test_mail.py urlbase fromaddr toaddr subject body file1 [..filen]"
        print >> sys.stderr, 'E.g. test_mail.py http://localhost:8080 test@example.com something@appname.appspotmail.com "Sample Subject" "Sample Body" file1.csv file2.csv'
        sys.exit(1)

    url = sys.argv[1]
    sender = sys.argv[2]
    receiver = sys.argv[3]
    subject = sys.argv[4]
    body = sys.argv[5]
    files = sys.argv[6:]

    post_mail(url, sender, receiver, subject, body, files)