from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    id_token: str
    client_id: str | None = None        # for audience validation
    refresh_token: str | None = None    # only sent if user grants Drive scope
    storage_provider: str | None = "spyme_cloud"  # spyme_cloud | google_drive | local_only


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
