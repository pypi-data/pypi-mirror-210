import sqlite3

import pytest
import sqlalchemy
import sqlalchemy.orm

from fake_session_maker import fsm


class Namespace:
    engine = sqlalchemy.create_engine(
        "sqlite:///tests/test.db",
        echo=True,
    )
    session_maker = sqlalchemy.orm.sessionmaker(bind=engine)


@pytest.fixture(autouse=True, scope="session")
def db_migrate():
    with sqlite3.connect("./tests/test.sqlite") as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        con.commit()
    yield
    with sqlite3.connect("./tests/test.sqlite") as con:
        cur.execute("DROP TABLE users")
        con.commit()


@pytest.fixture
def fake_session_maker():
    with fsm(
        db_url="sqlite:///tests/test.sqlite",
        namespace=Namespace,
        symbol_name="session_maker",
    ) as fake_session_maker:
        # the fake_session_maker won't auto-commit after transaction
        # and rollback after transaction
        yield fake_session_maker


def create_user(name: str):
    with Namespace.session_maker.begin() as session:
        session.execute(sqlalchemy.text("INSERT INTO users (name) VALUES (:name)"), {"name": name})
    return "success"


@pytest.mark.parametrize("name", ["Joe", "Jane"])
def test_isolation(fake_session_maker, name):
    result = create_user(name)
    assert result == "success"
    with fake_session_maker() as session:
        assert session.execute(sqlalchemy.text("SELECT * FROM users")).fetchall() == [(1, name)]
