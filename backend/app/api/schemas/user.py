import pydantic

from ...core import security


class EmailField(pydantic.EmailStr):
    @classmethod
    def validate(cls, email):
        super().validate(email)
        return email.lower()


class PasswordField(pydantic.ConstrainedStr):
    max_length = 128

    @classmethod
    def validate(cls, password):
        super().validate(password)
        return security.check_password_strength(password)


class UserBase(pydantic.BaseModel):
    class Config:
        extra = 'forbid'


class User(UserBase):
    email: EmailField
    phone: pydantic.StrictStr


class UserCreate(User):
    password: PasswordField


class UserGet(User):
    id: pydantic.StrictInt

    class Config:
        extra = 'ignore'


class UserCurrent(UserGet):
    password: PasswordField

    class Config:
        extra = 'ignore'


class UserCurrentGet(UserGet):
    class Config:
        extra = 'ignore'


class UserCurrentPasswordUpdateBody(pydantic.BaseModel):
    old_password: PasswordField
    new_password: PasswordField


class UserCurrentEmailUpdateBody(pydantic.BaseModel):
    password: PasswordField
    email: EmailField


class UserRegistration(User):
    asu_dkr: str
    password: str
