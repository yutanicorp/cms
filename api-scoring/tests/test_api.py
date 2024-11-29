import requests


def test_api():
    """Test the scoring service API response."""
    data = {
        'message': 'Completely bonkers!'
    }
    resp = requests.post('http://api-scoring-service:8000', json=data)
    assert resp.status_code == 200
    resp_data = resp.json()
    assert len(resp.data) == 1
    assert 0 <= resp_data['score'] <= 1
