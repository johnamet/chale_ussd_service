from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def generate_bulk_pdf(data_list):
    receipt = BulkQRcodePDF(data)
    receipt_stream = receipt.create_receipt()
