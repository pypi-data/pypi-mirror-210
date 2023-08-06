import contextlib
import typing

import pytest
import sqlalchemy.orm


class ExplicitCommit(Exception):
    """
    Raised when a commit is explicitly called on a session.
    """


@contextlib.contextmanager
def fsm(
    db_url: typing.Union[str, sqlalchemy.engine.url.URL],
    namespace: typing.Any,
    symbol_name: str,
    *,
    create_engine_kwargs: typing.Optional[typing.Mapping] = None,
) -> typing.Generator:
    """
    :param db_url: url of the test.py database
    :param namespace: namespace where the original session_maker is located
    :param symbol_name: name of the original session_maker symbol
    :param create_engine_kwargs: keyword arguments to pass to sqlalchemy.create_engine
    :return: a context manager that can be used as a session_maker
    """
    if create_engine_kwargs is None:
        create_engine_kwargs = {}

    engine = sqlalchemy.create_engine(
        url=db_url,
        **create_engine_kwargs,
    )
    session_maker = sqlalchemy.orm.sessionmaker(
        bind=engine,
        autoflush=False,
    )

    def forbidden_commit() -> typing.NoReturn:
        raise ExplicitCommit(
            "To use fake session, rely on autocommit. "
            "See: method sqlalchemy.engine.Connection.begin() → RootTransaction"
        )

    with session_maker() as session_singleton:
        session_singleton.commit = forbidden_commit  # type: ignore

        class SessionContextManager:
            def __enter__(self) -> sqlalchemy.orm.Session:
                return session_singleton

            def __exit__(
                self, exc_type: typing.Any, exc_val: typing.Any, exc_tb: typing.Any
            ) -> None:
                session_singleton.flush()

            @classmethod
            def begin(cls) -> "SessionContextManager":
                return cls()

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(namespace, symbol_name, SessionContextManager)
            yield SessionContextManager
