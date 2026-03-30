from faker import Faker
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import User
from random import randint

fake = Faker("pt_BR")

def seed_users(total=500):
    db: Session = SessionLocal()

    users = []
    for i in range(total):
        name = fake.name()
        email = f"{fake.user_name()}{i}@example.com"

        user = User(
            name=name,
            email=email,
            age=randint(18,65)
        )
        users.append(user)

    db.add_all(users)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_users()