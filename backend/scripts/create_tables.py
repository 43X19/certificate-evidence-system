import app.models
from app.db.base import Base
from app.db.session import engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("database tables created")


if __name__ == "__main__":
    main()