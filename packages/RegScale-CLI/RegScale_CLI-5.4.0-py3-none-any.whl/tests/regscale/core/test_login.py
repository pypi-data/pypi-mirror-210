"""Test the login module."""
from unittest.mock import patch, MagicMock

from regscale.core import login

PATH = "regscale.core.login"


@patch(f"{PATH}.post", return_value=MagicMock())
def test_get_regscale_token(mock_post):
    """Test that get_regscale_token will return"""
    user = "bart"
    pw = "simpson"
    data = {"id": "drink if you can", "auth_token": "one must imagine Sisyphus happy."}
    mock_response = MagicMock()
    mock_response.json = MagicMock()
    mock_response.json.return_value = data
    mock_post.return_value = mock_response
    uid, token = login.get_regscale_token(
        username=user, password=pw, domain="oink.login"
    )
    mock_post.assert_called_with(
        "oink.login/api/authentication/login",
        json={
            "userName": user,
            "password": pw,
            "oldPassword": "",
        },
        headers={
            "Content-Type": "application/json",
            "accept": "application/json",
            "authorization": "yo dawg I heard you like auth, so I put auth in your auth so you can auth while you auth",
        },
    )
    assert uid == data["id"]
    assert token == data["auth_token"]
