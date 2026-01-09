from fastapi import Depends

from errors import bad_request, not_found
from model.phone import PhoneBase, PhoneOut, PhoneUpdate
from repository.phone_repo import PhoneRepository, get_phone_repository


class PhoneService:
    def __init__(self, repo: PhoneRepository):
        self._repo = repo

    async def criar_telefones(
        self,
        id_person: str,
        phones: list[PhoneBase]
    ) -> list[PhoneOut]:
        try:
            created = await self._repo.criar_telefones(id_person, phones)
            if created is None:
                raise not_found("Pessoa não encontrada")
            return created
        except ValueError as exc:
            raise bad_request("id inválido") from exc

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
                raise not_found("Telefone não encontrado.")
            return updated
        except ValueError as exc:
            raise bad_request("id inválido") from exc

    async def deletar_telefone(self, person_id: str, phone_id: str) -> bool:
        try:
            deleted = await self._repo.deletar_telefone(person_id, phone_id)
            if not deleted:
                raise not_found("Telefone não encontrado.")
            return True
        except ValueError as exc:
            raise bad_request("id inválido") from exc

def get_phone_service(
    repo: PhoneRepository = Depends(get_phone_repository),
) -> PhoneService:
    return PhoneService(repo)


