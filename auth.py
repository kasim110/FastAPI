import secrets
from fastapi import HTTPException

from jwt import DecodeError, ExpiredSignatureError
import jwt


def verify_token(user_token):
    try:
        decoded_token = jwt.decode(user_token, "your-secret-key", algorithms=["HS256"])
        return True
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token is Expired")
    except DecodeError:
        raise HTTPException(status_code=401, detail="Invalid Token")
