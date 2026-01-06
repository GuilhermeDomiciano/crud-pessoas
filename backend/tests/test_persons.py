import pytest

pytestmark = pytest.mark.anyio


async def test_cria_lista_busca_por_id(client):
    payload = {"name": "Maria Silva", "email": "maria@example.com"}
    create_resp = await client.post("/persons/", json=payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    person_id = created["id"]

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
    payload = {"name": "Joao Santos", "email": "joao@example.com"}
    create_resp = await client.post("/persons/", json=payload)
    person_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/persons/{person_id}",
        json={"name": "Joao Pedro"},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["name"] == "Joao Pedro"
    assert updated["email"] == payload["email"]


async def test_delete(client):
    payload = {"name": "Carla Souza", "email": "carla@example.com"}
    create_resp = await client.post("/persons/", json=payload)
    person_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/persons/{person_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Pessoa removida com sucesso."

    get_resp = await client.get(f"/persons/{person_id}")
    assert get_resp.status_code == 404


async def test_duplicate_email_conflict(client):
    payload = {"name": "Ana Lima", "email": "ana@example.com"}
    first_resp = await client.post("/persons/", json=payload)
    assert first_resp.status_code == 200

    dup_resp = await client.post(
        "/persons/",
        json={"name": "Ana Carolina", "email": "ana@example.com"},
    )
    assert dup_resp.status_code == 409
