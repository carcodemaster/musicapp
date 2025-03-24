from fastapi import Header, HTTPException
import jwt as jwt

def auth_middleware(x_auth_token: str = Header(None)):
    try:
        if not x_auth_token:
            raise HTTPException(status_code=401, detail="No auth token, access denied")

        verified_token = jwt.decode(x_auth_token, 'password_key', ['HS256'])

        if not verified_token:
            raise HTTPException(status_code=401, detail="Token Verification Failed")

        uid = verified_token.get('id')
        return {uid: uid, 'token': x_auth_token}

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token is not Valid")