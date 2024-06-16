import enum
from datetime import date

from sqlalchemy import String, Integer,ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship 

class Base(DeclarativeBase):
    pass

class Role(enum.Enum):
    admin: str = "admin"
    moderator:str = "moderator"
    user:str = "user"
    
    
class User():
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    
    create_at: Mapped[date] = mapped_column("crete_at", DateTime,default=func.now())
    
    update_at: Mapped[date] = mapped_column("update_at", DateTime,default=func.now(), onupdate=func.now())
    
    role: Mapped[Enum] = relationship("role", Enum(Role), default=Role.user, nullable=True)
    

class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(150))
    last_name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(150))
    phone_number: Mapped[str] = mapped_column(String(30))
    birthday: Mapped[str] = mapped_column(String(30))
    data: Mapped[bool] = mapped_column(default=False, nullable=True)
    
    create_at: Mapped[date] = mapped_column("crete_at", DateTime,default=func.now(), nullable=True)
    
    update_at: Mapped[date] = mapped_column("update_at", DateTime,default=func.now(), onupdate=func.now(), nullable=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_id"),nullable=True)
    
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")