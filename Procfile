web: gunicorn phone_bills.billingapi.wsgi:app
worker: python phone_bills/billingmq/run_consumers.py
