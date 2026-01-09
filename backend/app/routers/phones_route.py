from fastapi import APIRouter, Depends

from auth.dependencies import require_scopes
from model.phone import PhoneBase, PhoneOut, PhoneUpdate
from services.phone_service import PhoneService, get_phone_service

router = APIRouter(prefix="/persons/{id}/phones", tags=["phone"])

@router.post(
    "/",
    response_model=list[PhoneOut],
    response_model_by_alias=True,
)
async def adicionar_telefones(
    id: str,
    phones: list[PhoneBase],
    service: PhoneService = Depends(get_phone_service),
    principal: dict = Depends(require_scopes(["persons:write"])),
):
    return await service.criar_telefones(id, phones)

@router.patch(
    "/{phoneId}",
    response_model=PhoneOut,
    response_model_by_alias=True,
)
async def atualizar_telefone(
    id: str,
    phoneId: str,
    phone: PhoneUpdate,
    service: PhoneService = Depends(get_phone_service),
    principal: dict = Depends(require_scopes(["persons:write"])),
):
    return await service.atualizar_telefone(id, phoneId, phone)


@router.delete("/{phoneId}")
async def deletar_telefone(
    id: str,
    phoneId: str,
    service: PhoneService = Depends(get_phone_service),
    principal: dict = Depends(require_scopes(["persons:write"])),
):
    await service.deletar_telefone(id, phoneId)
    return {"message": "Telefone removido com sucesso."}


