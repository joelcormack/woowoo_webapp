from django.conf import settings
from datetime import datetime, timedelta

from suds.client import Client, WebFault

#import logging
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
class KashFlow:

    def __init__(self, url=settings.KF_API_URL,
            username=settings.KF_USERNAME,
            password=settings.KF_PASSWORD,
            recipient=settings.KF_TEST_RECIPIENT_NAME,
            recipient_id=settings.KF_TEST_RECIPIENT_ID):
        self.url = url
        self.username = username
        self.password = password
        self.recipient =  recipient
        self.recipient_id = recipient_id

        self.client = Client(url)

    def create_purchase_order(self, ref=" "):

        now = datetime.utcnow().replace(microsecond=0)
        due = now + timedelta(days=30)

        invoice = self.client.factory.create('Invoice')
        invoice.InvoiceDBID = 0
        invoice.InvoiceNumber = 0
        invoice.InvoiceDate = now.isoformat()
        invoice.DueDate = due.isoformat()
        invoice.Customer = self.recipient
        invoice.CustomerID = self.recipient_id
        invoice.Paid = 0
        invoice.CustomerReference = ref
        invoice.EstimateCategory = ''
        invoice.SuppressTotal = 0
        invoice.ProjectID = 0
        invoice.CurrencyCode = 'EUR'
        invoice.ExchangeRate = 1.3947
        invoice.ReadableString = ''
        invoice.Lines = ''
        invoice.NetAmount = 0
        invoice.VATAmount = 0
        invoice.AmountPaid = 0
        invoice.CustomerName = ''
        invoice.PermaLink = ''
        invoice.DeliveryAddress = ''
        invoice.UseCustomDeliveryAddress = False
        try:
            purchase_order_added = self.client.service.InsertReceipt(self.username, self.password, invoice)
            print "purchase_order_added", purchase_order_added
            receipt_number = purchase_order_added.InsertReceiptResult
            print receipt_number
        except WebFault, e:
            print e
        return receipt_number

    def add_item(self, receipt_number, quantity, charge_type ,description, price):
        invoice_line = self.client.factory.create('InvoiceLine')
        invoice_line.Quantity = quantity
        invoice_line.Description = description
        invoice_line.Rate = price
        invoice_line.ChargeType = charge_type
        invoice_line.VatRate = 0
        invoice_line.VatAmount = 0
        invoice_line.ProductID = 0
        invoice_line.Sort = 0
        invoice_line.ProjID = 0
        invoice_line.LineID = 0
        invoice_line.ValuesInCurrency = 1
        try:
            invoice_line_added = self.client.service.InsertReceiptLineFromNumber(self.username, self.password, receipt_number, invoice_line)
        except WebFault, e:
            print e

    def add_note(self, receipt_number, note):
        address = self.client.factory.create('InvoiceLine')
        address.Quantity = 0
        address.Description = note
        address.Rate = 0
        address.ChargeType = 0
        address.VatRate = 0
        address.VatAmount = 0
        address.ProductID = 0
        address.Sort = 0
        address.ProjID = 0
        address.LineID = 0
        address.ValuesInCurrency = 0
        try:
            invoice_line_added = self.client.service.InsertReceiptLineFromNumber(self.username, self.password, receipt_number, address)
        except WebFault, e:
            print e


    def send_purchase_order(self, receipt_number):
        try:
            emailed_purchase_order = self.client.service.EmailPurchaseOrder(self.username, self.password, receipt_number, 'joel.greta@gmail.com', 'Joel Cormack', 'Invoice Hello', 'Hi heres your invoice', 'joel@joelcormack.com')
        except WebFault, e:
            print e
        print "trying with purchase number: ", emailed_purchase_order
        #return emailed_purchased_order.Status
