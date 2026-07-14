from datetime import date
from uuid import uuid4

clients = {}
invoices = {}


def create_client(data):
    client_id = str(uuid4())

    client = {
        "id": client_id,
        "name": data["name"],
        "email": data["email"],
        "company": data.get("company", "")
    }

    clients[client_id] = client
    return client


def list_clients():
    return list(clients.values())


def get_client(client_id):
    return clients.get(client_id)


def create_invoice(data):
    invoice_id = str(uuid4())

    invoice = {
        "id": invoice_id,
        "client_id": data["client_id"],
        "project_name": data["project_name"],
        "amount": data["amount"],
        "due_date": data["due_date"],
        "status": data.get("status", "pending")
    }

    invoices[invoice_id] = invoice
    return invoice


def list_invoices(status=None):
    all_invoices = list(invoices.values())

    if status:
        return [
            invoice for invoice in all_invoices
            if invoice["status"] == status
        ]

    return all_invoices


def get_invoice(invoice_id):
    return invoices.get(invoice_id)


def update_invoice_status(invoice_id, status):
    invoice = invoices.get(invoice_id)

    if invoice is None:
        return None

    invoice["status"] = status
    return invoice


def list_overdue_invoices():
    today = date.today().isoformat()

    return [
        invoice for invoice in invoices.values()
        if invoice["due_date"] < today and invoice["status"] != "paid"
    ]