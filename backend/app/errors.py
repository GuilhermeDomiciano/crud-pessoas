from fastapi import HTTPException

def bad_request(msg: str): raise HTTPException(400, msg)
def not_found(msg: str): raise HTTPException(404, msg)
def conflict(msg: str): raise HTTPException(409, msg)