# test_github_client.py
from unittest.mock import patch, MagicMock

def test_get_github_client():
    with patch('github_client.Github') as mock_github:
        mock_client = MagicMock()
        mock_github.return_value = mock_client

        from github_client import get_github_client
        client = get_github_client('fake_token')

        mock_github.assert_called_once_with('fake_token')
        assert client == mock_client

def test_get_github_client_no_token():
    from github_client import get_github_client

    with patch('github_client.GITHUB_TOKEN', ''):
        try:
            client = get_github_client()
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert 'GITHUB_TOKEN' in str(e)
