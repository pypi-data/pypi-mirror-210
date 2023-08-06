import asyncio
from datetime import timedelta
from typing import Any

import pytest
from aiohttp.test_utils import TestClient
from multidict import CIMultiDict
from pytest import mark
from aiohttp.web import Application, Request, Response
from resotolib.asynchronous.web.auth import check_auth, jwt_from_context
from resotolib.jwt import encode_jwt

# noinspection PyUnresolvedReferences
from aiohttp.pytest_plugin import aiohttp_client


@pytest.fixture
async def loop() -> Any:
    return asyncio.get_running_loop()


@pytest.fixture
async def app_with_auth() -> Application:
    async def hello(_: Request) -> Response:
        jwt = await jwt_from_context()
        # make sure, the context variable is set
        assert jwt["foo"] == "bla"
        assert "exp" in jwt
        return Response(text="Hello, world")

    app = Application(middlewares=[check_auth("test", timedelta(minutes=5), set())])
    app.router.add_get("/", hello)
    return app


@mark.asyncio
async def test_correct_psk(aiohttp_client: Any, app_with_auth: Application) -> None:
    client: TestClient = await aiohttp_client(app_with_auth)
    jwt = encode_jwt({"foo": "bla"}, "test")
    resp = await client.get("/", headers=CIMultiDict({"Authorization": f"Bearer {jwt}"}))
    assert resp.status == 200


@mark.asyncio
async def test_wrong_psk(aiohttp_client: Any, app_with_auth: Application) -> None:
    client: TestClient = await aiohttp_client(app_with_auth)
    jwt = encode_jwt({"foo": "bla"}, "wrong!")
    resp = await client.get("/", headers=CIMultiDict({"Authorization": f"Bearer {jwt}"}))
    assert resp.status == 401


@mark.asyncio
async def test_no_psk(aiohttp_client: Any, app_with_auth: Application) -> None:
    client: TestClient = await aiohttp_client(app_with_auth)
    resp = await client.get("/")
    assert resp.status == 401
