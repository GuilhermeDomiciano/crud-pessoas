from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from errors import bad_request, conflict, not_found, server_error
from model.person import PersonCreate, PersonUpdate
from repository.person_repo import (
    criar_pessoa, 
    listar_pessoas, 
    obter_pessoa, 
    atualizar_pessoa,
    deletar_pessoa
    )


async def criar_pessoa_service(person: PersonCreate):
    try:
        return await criar_pessoa(person)
    except DuplicateKeyError as exc:
        raise conflict("Email já cadastrado.") from exc
    except Exception as exc:
        raise server_error() from exc
    
async def listar_pessoas_service(
    skip: int = 0,
    limit: int = 50,
    name: str | None = None,
    email: str | None = None,
):
    try:
        return await listar_pessoas(skip=skip, limit=limit, name=name, email=email)
    except Exception as exc:
        raise server_error() from exc

async def obter_pessoa_service(id: str):
    try:
        person = await obter_pessoa(id)
        if person is None:
            raise not_found("Pessoa não encontrada.")
        return person
    except ValueError as exc:
        raise bad_request("id inválido") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise server_error() from exc

async def atualizar_pessoa_service(id: str, person: PersonUpdate):
    try:
        if not person.model_dump(exclude_unset=True):
            raise bad_request("Nenhum campo para atualizar")
        updated = await atualizar_pessoa(id, person)
        if updated is None:
            raise not_found("Pessoa não encontrada.")
        return updated
    except ValueError as exc:
        raise bad_request("Id inválido") from exc
    except DuplicateKeyError as exc:
        raise conflict("Email já cadastrado.") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise server_error() from exc

async def deletar_pessoa_service(id: str):
    try:
        deleted = await deletar_pessoa(id)
        if deleted is None:
            raise not_found("Pessoa não encontrada.")
        return True
    except ValueError as exc:
        raise bad_request("id inválido") from exc
    except Exception as exc:
        raise server_error() from exc
