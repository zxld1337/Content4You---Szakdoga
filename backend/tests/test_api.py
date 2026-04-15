from fastapi.testclient import TestClient
import pytest
from main import app  

# virtuális kliens, teszteléshez
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    """
    TESZT 1: A szerver alapvető elérhetőségének vizsgálata.
    Elvárás: 200 státuszkód és a megfelelő JSON üzenet.
    """
    response = client.get("/")
    
    # Ellenőrizzük, hogy sikeres-e a válasz
    assert response.status_code == 200
    
    # Ellenőrizzük, hogy a válasz tartalma megegyezik-e
    assert response.json() == {"message": "Content API is live!"}


def test_protected_posts_endpoint_without_auth(client):
    """
    TESZT 2: Védett végpont tesztelése.
    Hívást indit a /api/posts végpontot JWT token nélkül.
    Elvárás: 401 Unauthorized hiba.
    """
    response = client.get("/api/posts")
    
    assert response.status_code == 401    
    assert response.json() == {"detail": "Not authenticated"}


def test_user_login_returning_tokens(client):
    """
    TESZT 3: Bejelentkezés tesztelése 
    Hívást indit a /api/auth/login végpontra helyes hitelesítő adatokkal.
    Elvárás: 200 státuszkód és a JWT token süti formájában való visszaküldése    
    """
    
    # json adatok a bejelentkezéshez
    login_payload = {
        "username": "testuser",
        "password": "testpassword123" 
    }
    
    # POST kérés a login végpontra
    login_response = client.post("/api/auth/login", json=login_payload)
    
    # Bejelentkezés sikerességének vizsgálata
    assert login_response.status_code == 200
    
    # Biztosítjuk, hogy a süti tényleg megérkezett
    assert len(login_response.cookies) > 0