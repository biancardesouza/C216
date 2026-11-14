FRONTEND = "http://localhost:5173"


def test_preflight_from_allowed_origin(client):
    response = client.options(
        "/items/",
        headers={
            "Origin": FRONTEND,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND
    assert "POST" in response.headers["access-control-allow-methods"]


def test_simple_request_from_allowed_origin(client):
    response = client.get("/items/", headers={"Origin": FRONTEND})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND


def test_unknown_origin_is_not_allowed(client):
    origin = "http://malicioso.example"

    preflight = client.options(
        "/items/",
        headers={"Origin": origin, "Access-Control-Request-Method": "POST"},
    )
    response = client.get("/items/", headers={"Origin": origin})

    assert preflight.status_code == 400
    assert "access-control-allow-origin" not in preflight.headers
    assert "access-control-allow-origin" not in response.headers
