from fastapi import APIRouter, Query

from services.person_service import (
    criar_pessoa_service, 
    listar_pessoas_service, 
    obter_pessoa_service,
    atualizar_pessoa_service,
    deletar_pessoa_service
    )
from model.person import PersonCreate, PersonUpdate


router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("/")
async def adicionar_pessoa(person: PersonCreate):
    created = await criar_pessoa_service(person)
    return created

@router.get("/")
async def listar_pessoas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return await listar_pessoas_service(skip=skip, limit=limit)

@router.get("/{id}")
async def obter_pessoa(id: str):
    return await obter_pessoa_service(id)

@router.patch("/{id}")
async def atualizar_pessoa(id: str, person: PersonUpdate):
    return await atualizar_pessoa_service(id, person)

@router.delete("/{id}")
async def deletar_pessoa(id: str):
    await deletar_pessoa_service(id)
    return {"message": "Pessoa removida com sucesso."}
