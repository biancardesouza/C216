def test_health_retorna_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rota_inexistente_retorna_404(client):
    response = client.get("/nao-existe")

    assert response.status_code == 404
