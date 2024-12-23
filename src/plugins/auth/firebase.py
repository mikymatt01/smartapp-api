from fastapi import Depends, HTTPException
from fastapi import security
from firebase_admin import auth
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .schema import Auth
import os
security = HTTPBearer()

#authentication
def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Auth:
    """
    Verify the Firebase token and return the decoded token
    """
    try:
        INTERNAL_KEY = os.getenv('INTERNAL_KEY')
        #print(f"Received token: {credentials.credentials}")
        if credentials.credentials == INTERNAL_KEY:
            decoded_token = {
                'uid': 'admin',
                'email': 'admin',
                'role': 'admin',
            }
        else:
            decoded_token = auth.verify_id_token(credentials.credentials)
        #print(f"Decoded token: {decoded_token}")
        # Verify the token with Firebase Admin
        #auth.verify_id_token(credentials.credentials)
        return Auth(**decoded_token)
    except Exception as e:
        print(e)
        #print(f"Error verifying token: {e}")
        raise HTTPException(status_code=401, detail="Invalid Firebase token") from e

#autorization
def verify_firebase_token_and_role(required_role: str):
    """
    Verify the Firebase token and check if the user has the required role
    """
    def role_verifier(credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            #print(f"Received token: {credentials.credentials}")
            decoded_token = auth.verify_id_token(credentials.credentials)
            #print(f"Decoded token: {decoded_token}")
            # Check if user has the required role
            user_role = decoded_token.get("role")
            if user_role != required_role:
                raise HTTPException(status_code=403, detail=f"Insufficient permissions. Required role: {required_role}")
            elif required_role == "USER":
                print(f"User is a valid user")
            else:
                print(f"User has the required role: {required_role}")
            return decoded_token
        except Exception as e:
            print(f"Error verifying token: {e}")
            raise HTTPException(status_code=401, detail="Invalid Firebase token") from e
    return role_verifier