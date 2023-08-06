"""Define models used for interacting with the platform."""
from typing import Union, Optional
from os import getenv

from pydantic import BaseModel, SecretStr

from regscale.core.login import get_regscale_token
from regscale.core.utils.urls import generate_regscale_domain_url


class RegScaleAuth(BaseModel):
    """Define the authorization of a RegScale Authorization of a RegScale auth method for authorizing.
    You can define it specifically:
    >>> rsa = RegScaleAuth(user_id='manic', auth_token='moose')
    or if the proper envars are setup
    >>> rsa = RegScaleAuth.authenticate() # optional arguments, defaults to envars
    """

    domain: str
    user_id: str
    auth_token: SecretStr
    username: Optional[str] = None
    password: Optional[SecretStr] = None

    @property
    def token(self):
        """Render the token as a property
        Since this is a property, it can be referred to thusly:
        >>> rsa = RegScaleAuth('macho', 'mosquito')
        >>> print(rsa)
        RegScaleAuth(username='macho', password='**********')
        >>> rsa.token
        'mosquito'
        """
        return self.auth_token.get_secret_value()

    @classmethod
    def authenticate(
        cls,
        username: Optional[str] = None,
        password: Optional[Union[str, SecretStr]] = None,
        domain: Optional[str] = None,
    ):
        """Authenticate with RegScale and return a token and a user_id."""
        # TODO - better implementation and retrieval, but at what stage?
        if username is None:
            # should refactor to `get_username` method to account for other storage methods
            username = getenv("REGSCALE_USER") or getenv("REGSCALE_USERNAME")
        if not username:
            raise ValueError(
                "username could not be derived from the environment",
                " check upstream scripts for failure to pass to here or ",
                "setup the proper environment variables mentioned in the ",
                "documentation.",
            )
        if password is None:
            # should refactor to `get_password` method to account for other storage methods
            password = getenv("REGSCALE_PASSWORD") or getenv("REGSCALE_PASS")
        if not password:
            raise ValueError(
                "password could not be found in either environment variable checked and the string was not "
                "passed to this function, check your script logic."
            )
        if domain is None:
            # should refactor to `get_domain` method to account for other storage methods
            domain = generate_regscale_domain_url()
        if isinstance(password, str):
            password = SecretStr(password)
        # now we create this `auth` object
        # FIXME - why does it need oldPassword
        # TODO - HttpBasicAuth at minimum
        uid, auth_token = get_regscale_token(
            username=username, password=password.get_secret_value(), domain=domain
        )
        return cls(
            user_id=uid,
            auth_token=auth_token,
            domain=domain,
            username=username,
            password=password,
        )

    def refresh(self):
        """Refresh the token."""
        uid, auth_token = get_regscale_token(
            self.username,
            password=self.token,
            domain=self.domain,
        )
        self.user_id = uid
        self.auth_token = SecretStr(auth_token)
