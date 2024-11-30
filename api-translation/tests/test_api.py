import requests


def test_api():
    """Test the translation service API response."""
    data = {
        'message': 'You are crazy!!!'
    }
    resp = requests.post('http://api-translation-service:7000', json=data)
    assert resp.status_code == 200
    resp_data = resp.json()
    assert len(resp_data) == 1
    assert resp_data['translated_message'] == 'You are crazy!!!'
