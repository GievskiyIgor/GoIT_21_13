from typing import Optional

from jose import JWTError, jwt  # type: ignore
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import config


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password:str):
        return self.pwd_context.hash(password)
    
    async def create_access_token (self, data: dict, expires_delta: Optional[float] = None):
        
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})   
        
        encode_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
        return encode_access_token     
    
    
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
       
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
            
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})   
        
        encode_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
        return encode_refresh_token   
    
    async def decode_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithm=[self.ALGORITHM])
            
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token", )
            
        except:
           
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", )      
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)): 
        
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", 
                                              headers={"WWW-Authenticate": "Bearer"}, )
        
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithm=[self.ALGORITHM])
            
            if payload["scope"] =="access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else: 
                raise credentials_exception    
        except JWTError as err:
            raise credentials_exception
        
        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        
        return user

    def create_email_token(self, data:dict):
        
        to_encode = data.copy()
        
        expire = datetime.utcnow() + timedelta(days=1)
            
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})   
        
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
        return token 
    
    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithm=[self.ALGORITHM])
            
            email = payload["sub"]
                
            return email
        
        except JWTError as err:
            print(err)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid token for email verification")    
      

auth_service = Auth()
            
        