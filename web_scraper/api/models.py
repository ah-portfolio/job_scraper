from pydantic import BaseModel, Field, RootModel
from enum import Enum
from uuid import UUID
from api import exemple


class ContractType(Enum):
    contractor = "contractor"
    permanent = "permanent"
    fixed_term = "fixed-term"

class SessionIdResponses(RootModel):
    root: dict[str, UUID] = Field(exemple={"session_id": UUID("9b2edcfc-e59d-4b5a-9eb4-8d53ae2116b2")})

class JobFilters(BaseModel):
    job_title: str = Field(..., exemple="Software engineer")
    contracts: list[ContractType]  = Field(..., exemple=["contractor"])
    location: str = Field(..., exemple="Lyon")

class AddtionalInfo(BaseModel):
    job_url: str
    additional_info: list[str]

class AddtionalInfoResponses(RootModel):
     root: dict[UUID, list[AddtionalInfo]] = Field(..., 
                                            example=exemple.AddtionalInfoResponse)

class BasicInfo(BaseModel):
    company: str
    date: str
    job_title: str
    job_description: str
    skills: list[str]
    job_url: str

class BasicInfoResponses(RootModel):
     root: dict[UUID, list[BasicInfo]] = Field(..., 
                                            example=exemple.BasicInfoResponse)
