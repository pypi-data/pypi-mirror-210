import datetime
from typing import List

from dateutil.tz import gettz
from google.protobuf.timestamp_pb2 import Timestamp

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..entities.pat import PersonalAccessToken


class PersonalAccessTokens:
    def __init__(self, stub):
        self._stub = stub

    def generate(self, name: str, description: str, expiry_date: str = None, timezone: str = None) -> str:
        """Generate a personal access token for the currently logged-in user.

        Args:
            name: (str) A token name.
            description: (str) A description about the token.
            expiry_date: (str) Object represents a date string with format dd/MM/yyyy. Default is None.
            timezone: (str) Object represents a time zone name (Eg: 'America/Chicago'). Default is None.

        Returns:
            str: A token string for authentication.

        Typical example:
            token_str = client.auth.pats.generate(name="background_jobs", description="some description",
              expiry_date="<dd/MM/yyyy>", timezone=None)

        Raises:
            Exception: Invalid timezone.
            ValueError: Expiry date must be in the format: dd/MM/yyyy.

        For more details:
            https://docs.h2o.ai/feature-store/latest-stable/docs/api/authentication.html#authentication-via-personal-access-tokens-pats
        """
        request = pb.GenerateTokenRequest()
        request.name = name
        request.description = description
        if expiry_date:
            try:
                if timezone:
                    desired_timezone = gettz(timezone)
                    if not desired_timezone:
                        raise Exception("Invalid timezone id: '{}'".format(timezone))
                else:
                    desired_timezone = None
                expiration = datetime.datetime.strptime(expiry_date, "%d/%m/%Y").astimezone(desired_timezone)
                timestamp = Timestamp()
                timestamp.FromDatetime(expiration)
                request.expiry_date.CopyFrom(timestamp)
            except ValueError:
                raise Exception("Expiry date must be in the format: dd/MM/yyyy")
        response = self._stub.GenerateToken(request)
        return response.token

    def list(self) -> List[PersonalAccessToken]:
        """Return a generator which obtains the personal access tokens owned by current user, lazily.

        Returns:
            Iterable[PersonalAccessToken]: A generator iterator object consists of personal access tokens.

        Typical example:
            client.auth.pats.list()
        """
        request = pb.ListPersonalAccessTokensRequest()
        while request:
            response = self._stub.ListPersonalAccessTokens(request)
            if response.next_page_token:
                request.page_token = response.next_page_token
            else:
                request = None
            for pat in response.personal_access_tokens:
                yield PersonalAccessToken(self._stub, pat)

    def get(self, token_id: str) -> PersonalAccessToken:
        """Obtain a particular personal access token.

        Args:
            token_id: (str) A unique id of a token object.

        Returns:
            PersonalAccessToken: A token object.

        Typical example:
            client.auth.pats.get("token_id")
        """
        request = pb.TokenRequest()
        request.token_id = token_id
        response = self._stub.GetToken(request)
        return PersonalAccessToken(self._stub, response.token)

    def __repr__(self):
        return "This class wraps together methods working with Personal Access Tokens (PATs)"
