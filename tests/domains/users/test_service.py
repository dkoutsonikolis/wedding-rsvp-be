import pytest

from domains.users.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from domains.users.jwt import create_access_token, create_refresh_token
from domains.users.service import UsersService


@pytest.mark.asyncio
async def test__register__stores_bcrypt_hash(users_service: UsersService):
    # Arrange
    email = "svc@example.com"
    password = "password123"
    # Act
    user = await users_service.register(email=email, password=password)
    # Assert
    assert user.email == email
    assert user.password_hash
    assert user.password_hash != password


@pytest.mark.asyncio
async def test__register__email_already_registered(users_service: UsersService):
    # Arrange
    await users_service.register(email="dup@example.com", password="password123")
    # Act
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        await users_service.register(email="dup@example.com", password="password123")
    # Assert
    assert "dup@example.com" in str(exc_info.value)


@pytest.mark.asyncio
async def test__register__case_normalized_duplicate(users_service: UsersService):
    # Arrange
    await users_service.register(email="First@Example.COM", password="password123")
    # Act
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        await users_service.register(email="first@example.com", password="password123")
    # Assert
    assert "first@example.com" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test__authenticate__correct_password(users_service: UsersService):
    # Arrange
    await users_service.register(email="auth@example.com", password="password123")
    # Act
    user = await users_service.authenticate(email="auth@example.com", password="password123")
    # Assert
    assert user.email == "auth@example.com"


@pytest.mark.asyncio
async def test__authenticate__wrong_password(users_service: UsersService):
    # Arrange
    await users_service.register(email="auth2@example.com", password="password123")
    # Act
    with pytest.raises(InvalidCredentialsError) as exc_info:
        await users_service.authenticate(email="auth2@example.com", password="wrong")
    # Assert
    assert "Invalid email or password" in str(exc_info.value)


@pytest.mark.asyncio
async def test__authenticate__unknown_email(users_service: UsersService):
    # Arrange
    # (no user row)
    # Act
    with pytest.raises(InvalidCredentialsError) as exc_info:
        await users_service.authenticate(email="missing@example.com", password="password123")
    # Assert
    assert "Invalid email or password" in str(exc_info.value)


@pytest.mark.asyncio
async def test__authenticate_token__valid_signed_payload(users_service: UsersService):
    # Arrange
    user = await users_service.register(email="tok@example.com", password="password123")
    token = create_access_token(user_id=user.id, email=user.email)
    # Act
    loaded = await users_service.authenticate_token(token)
    # Assert
    assert loaded.id == user.id
    assert loaded.email == "tok@example.com"


@pytest.mark.asyncio
async def test__authenticate_token__rejects_refresh_token(users_service: UsersService):
    # Arrange
    user = await users_service.register(email="rtok@example.com", password="password123")
    refresh = create_refresh_token(user_id=user.id, email=user.email)
    # Act
    with pytest.raises(InvalidCredentialsError) as exc_info:
        await users_service.authenticate_token(refresh)
    # Assert
    assert "Invalid authentication credentials" in str(exc_info.value)


@pytest.mark.asyncio
async def test__authenticate_refresh_token__valid(users_service: UsersService):
    # Arrange
    user = await users_service.register(email="rvalid@example.com", password="password123")
    refresh = create_refresh_token(user_id=user.id, email=user.email)
    # Act
    loaded = await users_service.authenticate_refresh_token(refresh)
    # Assert
    assert loaded.id == user.id


@pytest.mark.asyncio
async def test__authenticate_refresh_token__rejects_access_token(users_service: UsersService):
    # Arrange
    user = await users_service.register(email="racc@example.com", password="password123")
    access = create_access_token(user_id=user.id, email=user.email)
    # Act
    with pytest.raises(InvalidCredentialsError) as exc_info:
        await users_service.authenticate_refresh_token(access)
    # Assert
    assert "Invalid refresh token" in str(exc_info.value)


@pytest.mark.asyncio
async def test__authenticate_token__not_a_jwt(users_service: UsersService):
    # Arrange
    token = "not-a-jwt"
    # Act
    with pytest.raises(InvalidCredentialsError) as exc_info:
        await users_service.authenticate_token(token)
    # Assert
    assert "Invalid authentication credentials" in str(exc_info.value)
