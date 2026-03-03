# test_config.py
import os
from unittest.mock import patch, mock_open

def test_load_github_token():
    with patch('builtins.open', mock_open(read_data='GITHUB_TOKEN=ghp_test123\n')):
        with patch.dict(os.environ, {}, clear=True):
            from config import GITHUB_TOKEN
            assert GITHUB_TOKEN == 'ghp_test123'

def test_load_github_token_missing():
    with patch('builtins.open', mock_open(read_data='OTHER_VAR=value\n')):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.GITHUB_TOKEN is None or config.GITHUB_TOKEN == ''
