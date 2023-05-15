# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:02:36 2023

@author: kribbel
"""
import sys
sys.path.append('/plainbi/backend')
sys.path.append('C:/users/kribbel/plainbi/backend')

import pytest
from plainbi_backend.api import create_app

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('flask_test.cfg')

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!
            
def test_version(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/api/version')
    assert response.status_code == 200
    assert b"0.1" in response.data


def test_version2(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/api/version')
    assert response.status_code == 200
    assert b"0.1" in response.data
