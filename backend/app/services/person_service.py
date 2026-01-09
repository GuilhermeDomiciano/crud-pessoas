from fastapi import Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from errors import bad_request, conflict, not_found, server_error
from model.person import PersonCreate, PersonUpdate
from repository.person_repo import PersonRepository, get_person_repository


class PersonService:
    def __init__(self, repo: PersonRepository):
        self._repo = repo

    async def criar_pessoa(self, person: PersonCreate):
        try:
            return await self._repo.criar_pessoa(person)
        except DuplicateKeyError as exc:
            raise conflict("Email ja cadastrado.") from exc
        except Exception as exc:
            raise server_error() from exc

    async def listar_pessoas(
        self,
        skip: int = 0,
        limit: int = 50,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ):
        try:
            return await self._repo.listar_pessoas(
                skip=skip,
                limit=limit,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
        except Exception as exc:
            raise server_error() from exc

    async def obter_pessoa(self, id: str):
        try:
            person = await self._repo.obter_pessoa(id)
            if person is None:
                raise not_found("Pessoa nao encontrada.")
            return person
        except ValueError as exc:
            raise bad_request("id invalido") from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise server_error() from exc

    async def atualizar_pessoa(self, id: str, person: PersonUpdate):
        try:
            if not person.model_dump(exclude_unset=True):
                raise bad_request("Nenhum campo para atualizar")
            updated = await self._repo.atualizar_pessoa(id, person)
            if updated is None:
                raise not_found("Pessoa nao encontrada.")
            return updated
        except ValueError as exc:
            raise bad_request("id invalido") from exc
        except DuplicateKeyError as exc:
            raise conflict("Email ja cadastrado.") from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise server_error() from exc

    async def deletar_pessoa(self, id: str):
        try:
            deleted = await self._repo.deletar_pessoa(id)
            if deleted is None:
                raise not_found("Pessoa nao encontrada.")
            return True
        except ValueError as exc:
            raise bad_request("id invalido") from exc
        except Exception as exc:
            raise server_error() from exc


def get_person_service(
    repo: PersonRepository = Depends(get_person_repository),
) -> PersonService:
    return PersonService(repo)


