from fastapi import Depends

from cache.cache_service import delete, incr
from cache.keys import LIST_VERSION_KEY, person_key
from errors import bad_request, not_found
from model.phone import PhoneBase, PhoneOut, PhoneUpdate
from repository.phone_repo import PhoneRepository, get_phone_repository
from settings import settings


class PhoneService:
    def __init__(self, repo: PhoneRepository):
        self._repo = repo

    async def criar_telefones(
        self,
        id_person: str,
        phones: list[PhoneBase],
    ) -> list[PhoneOut]:
        try:
            created = await self._repo.criar_telefones(id_person, phones)
            if created is None:
                raise not_found("Pessoa nao encontrada")
            if settings.cache.upper() == "ON":
                await delete(person_key(id_person))
                await incr(LIST_VERSION_KEY)
            return created
        except ValueError as exc:
            raise bad_request("id invalido") from exc

    async def atualizar_telefone(
        self,
        person_id: str,
        phone_id: str,
        phone: PhoneUpdate,
    ) -> PhoneOut:
        if not phone.model_dump(exclude_unset=True):
            raise bad_request("Nenhum campo para atualizar")
        try:
            updated = await self._repo.atualizar_telefone(person_id, phone_id, phone)
            if updated is None:
                raise not_found("Telefone nao encontrado.")
            if settings.cache.upper() == "ON":
                await delete(person_key(person_id))
                await incr(LIST_VERSION_KEY)
            return updated
        except ValueError as exc:
            raise bad_request("id invalido") from exc

    async def deletar_telefone(self, person_id: str, phone_id: str) -> bool:
        try:
            deleted = await self._repo.deletar_telefone(person_id, phone_id)
            if not deleted:
                raise not_found("Telefone nao encontrado.")
            if settings.cache.upper() == "ON":
                await delete(person_key(person_id))
                await incr(LIST_VERSION_KEY)
            return True
        except ValueError as exc:
            raise bad_request("id invalido") from exc


def get_phone_service(
    repo: PhoneRepository = Depends(get_phone_repository),
) -> PhoneService:
    return PhoneService(repo)
