import time

from argus_api.authentication import SessionTokenAuth
from argus_api.session import ArgusAPISession

try:
    import requests_oauthlib
except (ImportError, ModuleNotFoundError) as err:
    # Raise ... from None here to remove the exception chain
    # when the stack is rendered.
    raise RuntimeError(
        "Tried to import argus_api.authentication.oauth, "
        "but 'requests_oauthlib' is not installed. "
        "Install it with 'pip install argus-api[oauth]"
    ) from None


class OAuth2Auth(SessionTokenAuth):
    """SessionTokenAuth, but read the token from the given requests_oauthlib.OAuth2Session.

    Will authenticate towards Argus using the token from the supplied requests_oauthlib.OAuth2Session.
    When making a request, it will set the SessionTokenAuth `session_token` to `oauth_session.access_token`.

    If the oauth session `expires_at` is less than the current time, and refresh token and refresh URL is set,
    then attempt to fetch a new token before returning the headers.

    """

    # requests_oauthlib has many major helper functions that make the process
    # of fetching and refreshing tokens a lot easier, but they are implemented
    # directly in the session object. To save work, the session is stored
    # here to re-use that logic.
    _oauth_session: requests_oauthlib.OAuth2Session

    def __init__(self, oauth_session: requests_oauthlib.OAuth2Session):
        """

        :param oauth_session: The requests_oauthlib.OAuth2Session to get the
            session token from.
        """
        self._oauth_session = oauth_session

        super().__init__(self._oauth_session.access_token)

    @property
    def oauth_session_token(self):
        return self._oauth_session.token

    @oauth_session_token.setter
    def oauth_session_token(self, token):
        self._oauth_session.token = token

    def should_refresh(self) -> bool:
        return (
            self._oauth_session.token.get("expires_at", 0) < time.time()
            and self._oauth_session.token.get("refresh_token")
            and self._oauth_session.auto_refresh_url
        )

    def refresh(self, session: "ArgusAPISession") -> None:
        self._oauth_session.refresh_token(
            self._oauth_session.auto_refresh_url,
            **self._oauth_session.auto_refresh_kwargs,
        )
        self.session_token = self._oauth_session.access_token

        self.authenticate_session(session)
