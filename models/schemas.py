from typing import List
from pydantic import BaseModel, EmailStr, Field, validator


class Post(BaseModel):
    userId: int = Field(..., gt=0)
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    userId: int = Field(..., gt=0)


class GeoLocation(BaseModel):
    lat: str
    lng: str


class Address(BaseModel):
    street: str
    suite: str
    city: str
    zipcode: str
    geo: GeoLocation


class Company(BaseModel):
    name: str
    catchPhrase: str
    bs: str


class User(BaseModel):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    email: EmailStr
    address: Address
    phone: str
    website: str
    company: Company

    @validator('phone')
    def validate_phone(cls, v):
        if not v or not v.strip():
            raise ValueError("Invalid phone")
        return v


class Comment(BaseModel):
    postId: int = Field(..., gt=0)
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    email: EmailStr
    body: str = Field(..., min_length=1)


PostList = List[Post]
UserList = List[User]
CommentList = List[Comment]
