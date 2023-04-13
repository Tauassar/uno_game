import logging
import typing

import sqlalchemy

from ...core import postgres
from .. import schemas
from .. import security
from . import Base


logger = logging.getLogger(__name__)


class UserAlreadyExists(Exception):
    """Raises when user with provided identity already exists."""


class UserDoesNotExist(Exception):
    """Raises when user records aren't present in the table."""


class UserEmailAlreadyInUse(Exception):
    """Raises when tried to set occupied user email"""


class User(Base):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.Text(), nullable=False, unique=True)
    phone = sqlalchemy.Column(sqlalchemy.Text(), nullable=False, unique=True)
    password = sqlalchemy.Column(sqlalchemy.Text(), nullable=False)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean(), default=True, nullable=False)


def user_query():
    return sqlalchemy.select(User)


async def user_create(
    user: schemas.UserRegistration,
):
    password_hash = security.compute_password_hash(user.password)
    user_data = user.dict()
    user_data['password'] = password_hash

    user = User(
        **user_data,
    )

    session = postgres.get_session()
    async with session.begin():
        try:
            session.add(user)
            await session.commit()

        except sqlalchemy.exc.IntegrityError as e:
            await session.rollback()
            # check for subclass of IntegrityConstraintViolationError
            # 23 stands for sqlstate = '23000'
            if e.orig.sqlstate.startswith('23'):
                raise UserAlreadyExists from e
            raise e

    await session.refresh(user)
    return user.__dict__


async def user_get(
    user_id: int,
) -> typing.Optional[User]:
    query = user_query().filter(
        User.id == user_id,
        User.is_active == True,
    )

    result = await postgres.get_session().execute(query)
    user = result.scalars().first()

    if not user:
        return None

    return user


async def user_delete_all():
    await postgres.get_session().execute(sqlalchemy.delete(User))


async def user_list():
    result = await postgres.get_session().execute(user_query())
    return result.scalars().all()


# async def user_register(
#     user: schemas.UserRegistration,
#     is_superuser: bool = False,
# ):
#     password_hash = security.compute_password_hash(user.password)
#     user_data = user.dict()
#     user_data['password'] = password_hash
#     user_data['is_superuser'] = is_superuser
#     user_data['is_active'] = True
#     user_data['is_manager'] = False
#     user_data['is_client'] = True
#     user_data['role_id'] = None
#
#     query = User.insert().values(**user_data).returning(*User.c)
#
#     session = postgres.get_session()
#     async with session.transaction():
#         try:
#             created_user = await session.fetch_one(query)
#         except asyncpg.exceptions.UniqueViolationError as e:
#             if e.constraint_name == 'user_email_key':
#                 raise UserAlreadyExists from e
#             elif e.constraint_name == 'user_phone_key':
#                 raise UserAlreadyExists from e
#             raise e
#
#     print({**created_user})
#
#     return await user_get(created_user['id'])
#
#
# async def user_list(
#     limit: typing.Optional[int] = None,
#     filters: typing.Optional[UserFilters] = None,
# ):
#     query = User.select().where(User.c.is_active.is_(True))
#
#     query = query.order_by(User.c.first_name, User.c.last_name, User.c.id)
#
#     if filters is not None:
#         query = query.where(filters)
#
#     if limit:
#         query = query.limit(limit)
#
#     users = await postgres.get_session().fetch_all(query)
#
#     return [
#         {**user}
#         for user in users
#     ]
#
#
#
#
async def user_get_by_email(email: str):
    query = user_query().where(
        User.email == email.lower(),
        User.is_active == True,
    )

    users = await postgres.get_session().execute(query)

    (user,) = users.first()

    if not user:
        return None

    return {
        **user.__dict__,
    }
