from fastapi import Depends

from errors import bad_request, not_found
from model.address import AddressBase, AddressOut
from repository.address_repo import AddressRepository, get_address_repository


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
            return created
        except ValueError as exc:
            raise bad_request("id invalido") from exc


def get_address_service(
    repo: AddressRepository = Depends(get_address_repository),
) -> AddressService:
    return AddressService(repo)
