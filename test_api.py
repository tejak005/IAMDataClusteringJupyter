from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_login():
    response = client.post("/api/auth/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    print("Login OK")

def test_search():
    response = client.get("/api/identities/search?query=test&limit=10")
    assert response.status_code == 200
    print("Search parsed ok, found", len(response.json()), "results")
    if len(response.json()) > 0:
        print("First result:", response.json()[0])

def test_recommendation():
    response = client.post("/api/recommendations/predict", json={
        "department": "Engineering",
        "job_title": "Software Engineer",
        "location": "Remote"
    })
    assert response.status_code == 200
    print("Prediction parsed ok:", response.json())

def test_anomalies():
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    print("Anomalies parsed ok, found", len(response.json()), "results")

def test_clusters():
    response = client.get("/api/clusters")
    assert response.status_code == 200
    print("Clusters parsed ok, found", len(response.json()), "results")

if __name__ == "__main__":
    test_login()
    test_search()
    test_recommendation()
    test_anomalies()
    test_clusters()
