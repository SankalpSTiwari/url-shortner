import pytest


@pytest.mark.asyncio
async def test_shorten_url(client):
    response = await client.post(
        "/api/v1/shorten",
        json={"original_url": "https://example.com/very/long/path"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert "short_url" in data
    assert data["original_url"] == "https://example.com/very/long/path"
    assert data["expires_at"] is None


@pytest.mark.asyncio
async def test_shorten_url_with_ttl(client):
    response = await client.post(
        "/api/v1/shorten",
        json={"original_url": "https://example.com/ttl", "ttl_seconds": 3600},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["expires_at"] is not None


@pytest.mark.asyncio
async def test_shorten_custom_alias(client):
    response = await client.post(
        "/api/v1/shorten",
        json={"original_url": "https://example.com/custom", "custom_alias": "my-link"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == "my-link"


@pytest.mark.asyncio
async def test_custom_alias_conflict(client):
    await client.post(
        "/api/v1/shorten",
        json={"original_url": "https://example.com/a", "custom_alias": "conflict"},
    )
    response = await client.post(
        "/api/v1/shorten",
        json={"original_url": "https://example.com/b", "custom_alias": "conflict"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_redirect(client):
    create_resp = await client.post(
        "/api/v1/shorten",
        json={"original_url": "https://example.com/redirect"},
    )
    short_code = create_resp.json()["short_code"]

    response = await client.get(f"/api/v1/{short_code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/redirect"


@pytest.mark.asyncio
async def test_not_found(client):
    response = await client.get("/api/v1/notexist", follow_redirects=False)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_url(client):
    create_resp = await client.post(
        "/api/v1/shorten",
        json={"original_url": "https://example.com/delete"},
    )
    short_code = create_resp.json()["short_code"]

    delete_resp = await client.delete(f"/api/v1/{short_code}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/{short_code}", follow_redirects=False)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
