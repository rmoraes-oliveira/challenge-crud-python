def test_list_users(client):
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    body = response.json()

    assert "items" in body
    assert "page" in body
    assert "size" in body


def test_create_user(client):
    payload = {"name": "Rodrigo", "email": "rodrigo@test.com", "age": 30}

    response = client.post("/api/v1/users/", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Rodrigo"
    assert body["email"] == "rodrigo@test.com"
    assert body["age"] == 30

    # Create user same email, return error
    response = client.post("/api/v1/users/", json=payload)
    assert response.status_code == 409


def test_find_user_by_id(client):
    payload = {"name": "Maria", "email": "maria@test.com", "age": 25}

    created = client.post("/api/v1/users/", json=payload)
    user_id = created.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == user_id
    assert body["name"] == "Maria"


def test_update_user(client):
    created = client.post(
        "/api/v1/users/", json={"name": "Joao", "email": "joao@test.com", "age": 20}
    )
    user_id = created.json()["id"]

    created_2 = client.post(
        "/api/v1/users/", json={"name": "Joao", "email": "joao1@test.com", "age": 20}
    )
    user_id_2 = created_2.json()["id"]

    response = client.put(f"/api/v1/users/{user_id}", json={"name": "Joao Silva"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Joao Silva"
    assert body["email"] == "joao@test.com"

    response = client.put(f"/api/v1/users/{user_id_2}", json={"email": "joao@test.com"})

    print(response.json())
    print(response.status_code)
    assert response.status_code == 409


def test_delete_user(client):
    created = client.post(
        "/api/v1/users/", json={"name": "Carlos", "email": "carlos@test.com", "age": 40}
    )
    user_id = created.json()["id"]

    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 404
