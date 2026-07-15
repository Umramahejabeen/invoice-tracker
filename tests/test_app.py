from app.app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_create_client():
    client = app.test_client()

    response = client.post(
        "/clients",
        json={
            "name": "Riya Sharma",
            "email": "riya@example.com",
            "company": "Sharma Designs"
        }
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Riya Sharma"
    assert data["email"] == "riya@example.com"
    assert "id" in data


def test_list_clients():
    client = app.test_client()

    client.post(
        "/clients",
        json={
            "name": "Aman Verma",
            "email": "aman@example.com",
            "company": "Verma Studio"
        }
    )

    response = client.get("/clients")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1


def test_get_client_by_id():
    client = app.test_client()

    create_response = client.post(
        "/clients",
        json={
            "name": "Neha Patel",
            "email": "neha@example.com",
            "company": "Patel Consulting"
        }
    )

    created_client = create_response.get_json()
    client_id = created_client["id"]

    response = client.get(f"/clients/{client_id}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == client_id
    assert data["name"] == "Neha Patel"


def test_create_invoice():
    client = app.test_client()

    client_response = client.post(
        "/clients",
        json={
            "name": "Karan Mehta",
            "email": "karan@example.com",
            "company": "Mehta Media"
        }
    )
    client_id = client_response.get_json()["id"]

    response = client.post(
        "/invoices",
        json={
            "client_id": client_id,
            "project_name": "Website Build",
            "amount": 25000,
            "due_date": "2026-08-01"
        }
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["client_id"] == client_id
    assert data["project_name"] == "Website Build"
    assert data["status"] == "pending"
    assert "id" in data


def test_list_invoices():
    client = app.test_client()

    response = client.get("/invoices")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_invoice_by_id():
    client = app.test_client()

    client_response = client.post(
        "/clients",
        json={
            "name": "Sara Khan",
            "email": "sara@example.com",
            "company": "Khan Studio"
        }
    )
    client_id = client_response.get_json()["id"]

    invoice_response = client.post(
        "/invoices",
        json={
            "client_id": client_id,
            "project_name": "Brand Design",
            "amount": 18000,
            "due_date": "2026-08-10"
        }
    )
    invoice_id = invoice_response.get_json()["id"]

    response = client.get(f"/invoices/{invoice_id}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == invoice_id
    assert data["project_name"] == "Brand Design"


def test_update_invoice_status():
    client = app.test_client()

    client_response = client.post(
        "/clients",
        json={
            "name": "Dev Rao",
            "email": "dev@example.com",
            "company": "Rao Apps"
        }
    )
    client_id = client_response.get_json()["id"]

    invoice_response = client.post(
        "/invoices",
        json={
            "client_id": client_id,
            "project_name": "Mobile App",
            "amount": 45000,
            "due_date": "2026-08-15"
        }
    )
    invoice_id = invoice_response.get_json()["id"]

    response = client.patch(
        f"/invoices/{invoice_id}/status",
        json={"status": "paid"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "paid"


def test_overdue_invoices():
    client = app.test_client()

    client_response = client.post(
        "/clients",
        json={
            "name": "Old Client",
            "email": "old@example.com",
            "company": "Old Studio"
        }
    )
    client_id = client_response.get_json()["id"]

    client.post(
        "/invoices",
        json={
            "client_id": client_id,
            "project_name": "Old Project",
            "amount": 10000,
            "due_date": "2025-01-01"
        }
    )

    response = client.get("/invoices/overdue")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    