from fastapi import APIRouter, Depends

from auth.dependencies import require_scopes
from model.address import AddressBase, AddressOut, AddressUpdate
from services.address_service import AddressService, get_address_service

router = APIRouter(prefix="/persons/{id}/addresses", tags=["addresses"])

@router.post(
    "/",
    response_model=list[AddressOut],
    response_model_by_alias=True,
)
async def adicionar_enderecos(
    id: str,
    addresses: list[AddressBase],
    service: AddressService = Depends(get_address_service),
    principal: dict = Depends(require_scopes(["persons:write"])),
):
    return await service.criar_enderecos(id, addresses)


@router.patch(
    "/{addressId}",
    response_model=AddressOut,
    response_model_by_alias=True,
)
async def atualizar_endereco(
    id: str,
    addressId: str,
    address: AddressUpdate,
    service: AddressService = Depends(get_address_service),
    principal: dict = Depends(require_scopes(["persons:write"])),
):
    return await service.atualizar_endereco(id, addressId, address)


@router.delete("/{addressId}")
async def deletar_endereco(
    id: str,
    addressId: str,
    service: AddressService = Depends(get_address_service),
    principal: dict = Depends(require_scopes(["persons:write"])),
):
    await service.deletar_endereco(id, addressId)
    return {"message": "Endereço removido com sucesso."}
