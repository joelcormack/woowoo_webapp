from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from django_mailbox.models import Message, MessageAttachment
import re

def extract_dates(message):
    """
    extracts two specifically formatted dates from pdf file
    """
    attachment = message.attachments.first()
    filename = attachment.document.url
    fp = open(filename, 'rb')
    resman = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(resman, retstr, codec=codec, laparams=laparams)
    #fp = file(filename, 'rb')
    interpreter = PDFPageInterpreter(resman, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, 
            pagenos, 
            maxpages=maxpages, 
            password=password,
            caching=caching, 
            check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    le_date = re.findall('Le\s([0-9]{0,2}[\/][0-9]{0,2}[\/][0-9]{4})', text)

    fp.close()
    device.close()
    retstr.close()
    print text
    print "Extracted dates:"
    dates = []
    for group in le_date:
        print group
        dates.append(group)
    return dates
