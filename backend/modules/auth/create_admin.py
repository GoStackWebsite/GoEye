"""Create a dashboard user from the command line (the first admin cannot sign up through the API).

    python -m backend.modules.auth.create_admin admin@example.com

The password is asked for interactively so it never appears in the shell history.
"""
import asyncio
import sys
from getpass import getpass

from backend.core.database import SessionLocal, create_tables
from backend.core.security import hash_password
from backend.modules.auth.models import User
from backend.modules.auth.repository import UserRepository

MIN_PASSWORD_LENGTH = 8


async def create_user(email: str, password: str) -> None:
    await create_tables()
    async with SessionLocal() as session:
        repo = UserRepository(session)
        if await repo.get_by_email(email):
            raise SystemExit(f"A user with email {email} already exists")
        await repo.add(User(email=email, password_hash=hash_password(password)))


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m backend.modules.auth.create_admin <email>")
    email = sys.argv[1]
    password = getpass("Password: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise SystemExit(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    if password != getpass("Repeat password: "):
        raise SystemExit("Passwords do not match")
    asyncio.run(create_user(email, password))
    print(f"User {email} created")


if __name__ == "__main__":
    main()
