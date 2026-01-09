from fastapi import Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from cache.cache_service import delete, get_json, incr, set_json
from cache.keys import LIST_VERSION_KEY, person_key, persons_list_key
from errors import bad_request, conflict, not_found, server_error
from model.person import PersonCreate, PersonUpdate
from repository.person_repo import PersonRepository, get_person_repository
from settings import settings


class PersonService:
    def __init__(self, repo: PersonRepository):
        self._repo = repo

    async def criar_pessoa(self, person: PersonCreate):
        try:
            created = await self._repo.criar_pessoa(person)
            if settings.cache.upper() == "ON":
                created_id = created.get("id") if isinstance(created, dict) else None
                if created_id:
                    await delete(person_key(created_id))
                await incr(LIST_VERSION_KEY)
            return created
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
        cache_on = settings.cache.upper() == "ON"
        cache_key = None
        if cache_on:
            version = await get_json(LIST_VERSION_KEY)
            if not isinstance(version, int):
                version = await incr(LIST_VERSION_KEY)
                if version is None:
                    version = 1
                    await set_json(LIST_VERSION_KEY, version, None)
            params = {
                "skip": skip,
                "limit": limit,
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
            }
            cache_key = persons_list_key(version, params)
            cached = await get_json(cache_key)
            if cached is not None:
                return cached
        try:
            result = await self._repo.listar_pessoas(
                skip=skip,
                limit=limit,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            if cache_on and cache_key:
                await set_json(
                    cache_key,
                    result,
                    settings.cache_ttl_list_seconds,
                )
            return result
        except Exception as exc:
            raise server_error() from exc

    async def obter_pessoa(self, id: str):
        cache_on = settings.cache.upper() == "ON"
        cache_key = person_key(id)
        if cache_on:
            cached = await get_json(cache_key)
            if cached is not None:
                return cached
        try:
            person = await self._repo.obter_pessoa(id)
            if person is None:
                raise not_found("Pessoa nao encontrada.")
            if cache_on:
                await set_json(
                    cache_key,
                    person,
                    settings.cache_ttl_person_seconds,
                )
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
            if settings.cache.upper() == "ON":
                await delete(person_key(id))
                await incr(LIST_VERSION_KEY)
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
            if settings.cache.upper() == "ON":
                await delete(person_key(id))
                await incr(LIST_VERSION_KEY)
            return True
        except ValueError as exc:
            raise bad_request("id invalido") from exc
        except Exception as exc:
            raise server_error() from exc


def get_person_service(
    repo: PersonRepository = Depends(get_person_repository),
) -> PersonService:
    return PersonService(repo)
