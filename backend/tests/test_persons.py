import pytest

pytestmark = pytest.mark.anyio


async def test_cria_lista_busca_por_id(client):
    payload = {
        "firstName": "Maria",
        "lastName": "Silva",
        "email": "maria@example.com",
        "documentNumber": "12345678900",
        "addresses": [{"line1": "Rua A, 123", "city": "Sao Paulo"}],
        "phoneNumbers": [{"type": "mobile", "number": "11999990000"}],
    }
    create_resp = await client.post("/persons/", json=payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    person_id = created["id"]
    assert isinstance(created["addresses"][0]["_id"], str)
    assert isinstance(created["phoneNumbers"][0]["_id"], str)

    list_resp = await client.get("/persons/")
    assert list_resp.status_code == 200
    persons = list_resp.json()
    assert any(p["id"] == person_id for p in persons)

    get_resp = await client.get(f"/persons/{person_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == person_id
    assert fetched["email"] == payload["email"]


async def test_update_parcial(client):
    payload = {
        "firstName": "Joao",
        "lastName": "Santos",
        "email": "joao@example.com",
        "documentNumber": "98765432100",
    }
    create_resp = await client.post("/persons/", json=payload)
    person_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/persons/{person_id}",
        json={"lastName": "Pedro"},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["lastName"] == "Pedro"
    assert updated["email"] == payload["email"]


async def test_delete(client):
    payload = {
        "firstName": "Carla",
        "lastName": "Souza",
        "email": "carla@example.com",
        "documentNumber": "11223344556",
    }
    create_resp = await client.post("/persons/", json=payload)
    person_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/persons/{person_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Pessoa removida com sucesso."

    get_resp = await client.get(f"/persons/{person_id}")
    assert get_resp.status_code == 404


async def test_duplicate_email_conflict(client):
    payload = {
        "firstName": "Ana",
        "lastName": "Lima",
        "email": "ana@example.com",
        "documentNumber": "99887766554",
    }
    first_resp = await client.post("/persons/", json=payload)
    assert first_resp.status_code == 200

    dup_resp = await client.post(
        "/persons/",
        json={
            "firstName": "Ana",
            "lastName": "Carolina",
            "email": "ana@example.com",
            "documentNumber": "22334455667",
        },
    )
    assert dup_resp.status_code == 409
