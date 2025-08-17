"""Basic tests for the crypto dashboard application."""
import pytest


def test_requirements_exist():
    """Test that requirements.txt exists and has expected packages."""
    import os
    requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    assert os.path.exists(requirements_path), "requirements.txt should exist"
    
    with open(requirements_path, 'r') as f:
        content = f.read()
        assert 'streamlit' in content, "streamlit should be in requirements"
        assert 'pandas' in content, "pandas should be in requirements"
        assert 'requests' in content, "requests should be in requirements"


def test_app_files_exist():
    """Test that main application files exist."""
    import os
    app_dir = os.path.join(os.path.dirname(__file__), '..', 'app')
    
    main_py = os.path.join(app_dir, 'main.py')
    ws_client_py = os.path.join(app_dir, 'ws_client.py')
    
    assert os.path.exists(main_py), "main.py should exist"
    assert os.path.exists(ws_client_py), "ws_client.py should exist"


def test_readme_exists():
    """Test that README.md exists and has basic content."""
    import os
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    assert os.path.exists(readme_path), "README.md should exist"
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'Crypto Real-Time Dashboard' in content, "Title should be in README"
        assert 'Installation' in content, "Installation section should exist"
