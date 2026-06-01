import pytest
from fastapi import HTTPException
from api_gateway.middleware.auth import verify_api_key

class MockRequest:
    pass

@pytest.mark.asyncio
async def test_missing_api_key():
    req = MockRequest()
    with pytest.raises(HTTPException) as exc:
        await verify_api_key(req, api_key=None)
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_invalid_api_key():
    req = MockRequest()
    with pytest.raises(HTTPException) as exc:
        await verify_api_key(req, api_key="wrong-key")
    assert exc.value.status_code == 403
