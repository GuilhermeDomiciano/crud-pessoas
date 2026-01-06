from fastapi import APIRouter, Depends

from model.address import AddressBase, AddressOut
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
):
    return await service.criar_enderecos(id, addresses)
