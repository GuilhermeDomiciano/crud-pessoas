from fastapi import Depends

from cache.cache_service import delete, incr
from cache.keys import LIST_VERSION_KEY, person_key
from errors import bad_request, not_found
from model.address import AddressBase, AddressOut, AddressUpdate
from repository.address_repo import AddressRepository, get_address_repository
from settings import settings


class AddressService:
    def __init__(self, repo: AddressRepository):
        self._repo = repo

    async def criar_enderecos(
        self,
        id_person: str,
        addresses: list[AddressBase],
    ) -> list[AddressOut]:
        try:
            created = await self._repo.criar_enderecos(id_person, addresses)
            if created is None:
                raise not_found("Pessoa nao encontrada.")
            if settings.cache.upper() == "ON":
                await delete(person_key(id_person))
                await incr(LIST_VERSION_KEY)
            return created
        except ValueError as exc:
            raise bad_request("id invalido") from exc

    async def atualizar_endereco(
        self,
        person_id: str,
        address_id: str,
        address: AddressUpdate,
    ) -> AddressOut:
        if not address.model_dump(exclude_unset=True):
            raise bad_request("Nenhum campo para atualizar")
        try:
            updated = await self._repo.atualizar_endereco(person_id, address_id, address)
            if updated is None:
                raise not_found("Endereco nao encontrado.")
            if settings.cache.upper() == "ON":
                await delete(person_key(person_id))
                await incr(LIST_VERSION_KEY)
            return updated
        except ValueError as exc:
            raise bad_request("id invalido") from exc

    async def deletar_endereco(self, person_id: str, address_id: str) -> bool:
        try:
            deleted = await self._repo.deletar_endereco(person_id, address_id)
            if not deleted:
                raise not_found("Endereco nao encontrado.")
            if settings.cache.upper() == "ON":
                await delete(person_key(person_id))
                await incr(LIST_VERSION_KEY)
            return True
        except ValueError as exc:
            raise bad_request("id invalido") from exc


def get_address_service(
    repo: AddressRepository = Depends(get_address_repository),
) -> AddressService:
    return AddressService(repo)
