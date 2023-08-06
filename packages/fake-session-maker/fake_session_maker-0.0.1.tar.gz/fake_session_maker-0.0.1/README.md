<p align="center">
    <a href="https://pypi.org/project/fake_session_maker" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/fake_session_maker.svg?color=%2334D058" alt="Supported Python versions">
    </a>
    <a href="https://pycqa.github.io/isort/" target="_blank">
        <img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336" alt="Imports: isort">
    </a>
    <a href="https://pypi.org/project/fake_session_maker" target="_blank">
        <img src="https://img.shields.io/pypi/dm/fake_session_maker" alt="PyPI - Downloads">
    </a>
</p>

# fake_session_maker

Create a SQLAlchemy session_maker that won't commit to db for testing purposes.

## Usage

```python
# conftest.py
import pytest

from fake_session_maker import fsm

import db

@pytest.fixture
def fake_session_maker():
    with fsm(
            db_url=TEST_DB_URL, 
            namespace=db, 
            symbol_name="session_maker",
    ) as fake_session_maker:
        # the fake_session_maker won't auto-commit after transaction
        # and rollback after transaction
        yield fake_session_maker

# service.py
import db

def create_user(name: str):
    # start transaction with autocommit
    with db.session_maker.begin() as session:
        session.add(db.User(name=name))
    return "success"

# test_service.py
import service

def test_create_user(fake_session_maker):
    result = service.create_user('test')
    assert result == 'success'
    with fake_session_maker() as session:
        assert session.query(db.User).count() == 1

def test_empty_user_table(fake_session_maker):
    with fake_session_maker() as session:
        assert session.query(db.User).count() == 0
```