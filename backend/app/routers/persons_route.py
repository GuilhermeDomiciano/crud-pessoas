from fastapi import APIRouter

from services.person_service import criar_pessoa_service
from model.person import PersonCreate


router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("/")
async def adicionar_pessoa(person: PersonCreate):
    inserted_id = await criar_pessoa_service(person)
    return {"id": str(inserted_id)}
