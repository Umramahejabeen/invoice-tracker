from flask import Flask, jsonify, request

from app.models import (
    create_client,
    create_invoice,
    get_client,
    get_invoice,
    list_clients,
    list_invoices,
    list_overdue_invoices,
    update_invoice_status,
)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "Invoice Tracker API is running successfully",
            "status": "healthy",
            "version": "1.0.0",
            "available_endpoints": {
                "health": "/health",
                "clients": {
                    "GET": "/clients",
                    "POST": "/clients",
                },
                "client_by_id": "/clients/<client_id>",
                "invoices": {
                    "GET": "/invoices",
                    "POST": "/invoices",
                },
                "invoice_by_id": "/invoices/<invoice_id>",
                "overdue_invoices": "/invoices/overdue",
                "update_invoice_status": "/invoices/<invoice_id>/status",
            },
        }
    ), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/clients", methods=["POST"])
def add_client():
    data = request.get_json()

    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "name and email are required"}), 400

    client = create_client(data)
    return jsonify(client), 201


@app.route("/clients", methods=["GET"])
def get_clients():
    return jsonify(list_clients()), 200


@app.route("/clients/<client_id>", methods=["GET"])
def get_client_by_id(client_id):
    client = get_client(client_id)

    if client is None:
        return jsonify({"error": "client not found"}), 404

    return jsonify(client), 200


@app.route("/invoices", methods=["POST"])
def add_invoice():
    data = request.get_json()

    required_fields = ["client_id", "project_name", "amount", "due_date"]

    if not data or any(field not in data for field in required_fields):
        return jsonify(
            {
                "error": (
                    "client_id, project_name, amount, "
                    "and due_date are required"
                )
            }
        ), 400

    if get_client(data["client_id"]) is None:
        return jsonify({"error": "client not found"}), 404

    invoice = create_invoice(data)
    return jsonify(invoice), 201


@app.route("/invoices", methods=["GET"])
def get_invoices():
    status = request.args.get("status")
    return jsonify(list_invoices(status=status)), 200


@app.route("/invoices/overdue", methods=["GET"])
def get_overdue_invoices():
    return jsonify(list_overdue_invoices()), 200


@app.route("/invoices/<invoice_id>", methods=["GET"])
def get_invoice_by_id(invoice_id):
    invoice = get_invoice(invoice_id)

    if invoice is None:
        return jsonify({"error": "invoice not found"}), 404

    return jsonify(invoice), 200


@app.route("/invoices/<invoice_id>/status", methods=["PATCH"])
def change_invoice_status(invoice_id):
    data = request.get_json()

    if not data or "status" not in data:
        return jsonify({"error": "status is required"}), 400

    allowed_statuses = ["pending", "paid", "overdue"]

    if data["status"] not in allowed_statuses:
        return jsonify(
            {"error": "status must be pending, paid, or overdue"}
        ), 400

    invoice = update_invoice_status(invoice_id, data["status"])

    if invoice is None:
        return jsonify({"error": "invoice not found"}), 404

    return jsonify(invoice), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
