from fastapi import APIRouter, Depends, Query

from model.person import PersonCreate, PersonOut, PersonUpdate
from services.person_service import PersonService, get_person_service

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("/", response_model=PersonOut)
async def adicionar_pessoa(
    person: PersonCreate,
    service: PersonService = Depends(get_person_service),
):
    return await service.criar_pessoa(person)


@router.get("/", response_model=list[PersonOut])
async def listar_pessoas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    name: str | None = None,
    email: str | None = None,
    service: PersonService = Depends(get_person_service),
):
    return await service.listar_pessoas(
        skip=skip,
        limit=limit,
        name=name,
        email=email,
    )


@router.get("/{id}", response_model=PersonOut)
async def obter_pessoa(
    id: str,
    service: PersonService = Depends(get_person_service),
):
    return await service.obter_pessoa(id)


@router.patch("/{id}", response_model=PersonOut)
async def atualizar_pessoa(
    id: str,
    person: PersonUpdate,
    service: PersonService = Depends(get_person_service),
):
    return await service.atualizar_pessoa(id, person)


@router.delete("/{id}")
async def deletar_pessoa(
    id: str,
    service: PersonService = Depends(get_person_service),
):
    await service.deletar_pessoa(id)
    return {"message": "Pessoa removida com sucesso."}
