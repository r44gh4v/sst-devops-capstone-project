EXPENSE = {"title": "Lunch", "amount": 250, "category": "Food", "spent_on": "2026-10-10"}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_create_and_list(client):
    created = client.post("/api/expenses", json=EXPENSE)
    assert created.status_code == 201
    assert created.json()["title"] == "Lunch"
    listed = client.get("/api/expenses")
    assert len(listed.json()) == 1


def test_invalid_expense_rejected(client):
    response = client.post("/api/expenses", json={**EXPENSE, "amount": -5})
    assert response.status_code == 422


def test_update_expense(client):
    expense_id = client.post("/api/expenses", json=EXPENSE).json()["id"]
    response = client.put(f"/api/expenses/{expense_id}", json={**EXPENSE, "amount": 300})
    assert response.status_code == 200
    assert response.json()["amount"] == 300


def test_delete_expense(client):
    expense_id = client.post("/api/expenses", json=EXPENSE).json()["id"]
    assert client.delete(f"/api/expenses/{expense_id}").status_code == 204
    assert client.get(f"/api/expenses/{expense_id}").status_code == 404


def test_summary(client):
    client.post("/api/expenses", json=EXPENSE)
    client.post("/api/expenses", json={**EXPENSE, "title": "Cab", "amount": 150, "category": "Travel"})
    data = client.get("/api/expenses/summary").json()
    assert data["total"] == 400
    assert data["count"] == 2
    assert data["by_category"] == {"Food": 250, "Travel": 150}


def test_metrics(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
