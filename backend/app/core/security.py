from . import conf


def check_password_strength(password: str) -> str:
    """Check provided password strength"""

    is_strong = True
    has_numeric = False

    if any([
        len(password) < conf.security.min_password_length,
        password.lower() == password,
        password.upper() == password,
    ]):
        is_strong = False

    for char in password:
        if char.isdigit():
            has_numeric = True

    if not is_strong or not has_numeric:
        raise ValueError(
            f'Must have at least {conf.security.min_password_length} characters, '
            'and contain at least one number, one uppercase letter and one lowercase letter',
        )

    return password
