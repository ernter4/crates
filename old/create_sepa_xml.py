import csv
import datetime

import requests
from markdown_it.presets import gfm_like
billing_date ='2025-12-31'
with open ('sepa.csv')as csvfile :
    reader = csv.reader(csvfile,delimiter=';')
    for row in reader:
        customer ={
            "first_name": row[0].split(',')[1]
            ,"last_name": row[0].split(',')[0]
            ,"sepa_mandate": True
            ,"iban": row[2]
            ,"sepa_mandate_date": datetime.datetime.strptime(row[4],'%d.%m.%Y').strftime('%Y-%m-%d')
        }
        response = requests.post("http://localhost:8000/accounting/customer/",json=customer)
        customer= response.json()
        invoice={
            "customer_id": customer['id'],
            "invoice_number": int(row[7].split('_')[1].split(' ')[0]),
            "billing_date": billing_date,
            "amount": row[6].replace(',','.')
            }
        response = requests.post("http://localhost:8000/accounting/invoice/",json=invoice)

    response = requests.post("http://localhost:8000/accounting/export/",json={
        "description": "sepa",
        "start_date": billing_date,
        "end_date": billing_date
    })
    print(response.json())