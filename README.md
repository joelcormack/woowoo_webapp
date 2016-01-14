WooWoo WebApp
=============

Automates organising the order process of a WooWoo product through simple yes or no emails, date input forms and b2b communication. 

Detailed Process:
----------------
1. Customer completes an order with WooWoo
2. A WooWoo rep updates Zoho to reflect this by setting the potential stage to closed won (probability 100%)
3. This triggers an alert in Zoho which calls a webhook
4. The webhook sends a GET request to the WooWoo WebApp passing the unique ID of the potential that triggered it
5. The WebApp then contacts the Zoho API using stored credentials and retrieves the data linked to the ID it received
6. This data is used to create an instance of an Installation and saved to the database
7. The creation of an installation trggers an email to the CONTRACTOR whcih asks them to confirm if the calculated potential date
8. Whether confirmed or not the CONTRACTOR is sent another email with a link to a form to set the installation and delivery dates
9. When the dates have been set an email is sent to the SUPPLIER asking them to confirm the generated pickup date
10. A purchase order is sent at the same time to the SUPPLIER using the Kashflow API and detilas of the installation pulled from Zoho
11. Once the SUPPLIER confirms the date an email is sent to the SHIPPING COMPANY asking them to confirm the pickup and delivery dates
12. The SHIPPING COMPANY replies with a receipt by email which is forwarded to the inbox of the webapp
13. The webapp then scrapes the PDF for two dates matching the delivery adn pockup dates
14. Once these dates have been confirmed then a final email is sent to the CONTRACTOR, CUSTOMER and WOOWOO REP summarising the dates
