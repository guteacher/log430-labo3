"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import pytest
from store_manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    result = client.get('/health')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

def test_stock_flow(client):
    assert "Le test n'est pas encore là" == 1