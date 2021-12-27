def test_auth_headers(app_store_api_client):
    assert app_store_api_client.jwt in app_store_api_client.generate_auth_headers()['Authorization']
