import pytest


@pytest.mark.asyncio
async def test_analytics_not_found(client):
    response = await client.get("/api/v1/analytics/doesnotexist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_analytics_returns_data(client):
    create_resp = await client.post(
        "/api/v1/shorten",
        json={"original_url": "https://example.com/analytics"},
    )
    short_code = create_resp.json()["short_code"]

    response = await client.get(f"/api/v1/analytics/{short_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == short_code
    assert data["original_url"] == "https://example.com/analytics"
    assert data["click_count"] == 0
    assert isinstance(data["recent_clicks"], list)
