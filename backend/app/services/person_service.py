from pymongo.errors import DuplicateKeyError

from errors import conflict, server_error
from model.person import PersonCreate
from repository.person_repo import criar_pessoa


async def criar_pessoa_service(person: PersonCreate):
    try:
        return await criar_pessoa(person)
    except DuplicateKeyError as exc:
        raise conflict("Email ja cadastrado.") from exc
    except Exception as exc:
        raise server_error() from exc
