# -*- coding: utf-8 -*-

"""
bandwidth

This file was automatically generated by APIMATIC v3.0 (
 https://www.apimatic.io ).
"""

from bandwidth.api_helper import APIHelper
from bandwidth.configuration import Server
from bandwidth.http.api_response import ApiResponse
from bandwidth.webrtc.controllers.base_controller import BaseController
from bandwidth.http.auth.web_rtc_basic_auth import WebRtcBasicAuth
from bandwidth.webrtc.models.accounts_participants_response import AccountsParticipantsResponse
from bandwidth.webrtc.models.participant import Participant
from bandwidth.webrtc.models.session import Session
from bandwidth.webrtc.models.subscriptions import Subscriptions
from bandwidth.exceptions.api_exception import APIException
from bandwidth.webrtc.exceptions.error_exception import ErrorException


class APIController(BaseController):

    """A Controller to access Endpoints in the bandwidth API."""

    def __init__(self, config, call_back=None):
        super(APIController, self).__init__(config, call_back)

    def create_participant(self,
                           account_id,
                           body=None):
        """Does a POST request to /accounts/{accountId}/participants.

        Create a new participant under this account.
        Participants are idempotent, so relevant parameters must be set in
        this function if desired.

        Args:
            account_id (string): Account ID
            body (Participant, optional): Participant parameters

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/participants'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            'accept': 'application/json',
            'content-type': 'application/json; charset=utf-8'
        }

        # Prepare and execute request
        _request = self.config.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 400:
            raise APIException('Bad Request', _response)
        elif _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        decoded = APIHelper.json_deserialize(_response.text, AccountsParticipantsResponse.from_dictionary)
        _result = ApiResponse(_response, body=decoded)
        return _result

    def get_participant(self,
                        account_id,
                        participant_id):
        """Does a GET request to /accounts/{accountId}/participants/{participantId}.

        Get participant by ID.

        Args:
            account_id (string): Account ID
            participant_id (string): Participant ID

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/participants/{participantId}'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False},
            'participantId': {'value': participant_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            'accept': 'application/json'
        }

        # Prepare and execute request
        _request = self.config.http_client.get(_query_url, headers=_headers)
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif _response.status_code == 404:
            raise APIException('Not Found', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        decoded = APIHelper.json_deserialize(_response.text, Participant.from_dictionary)
        _result = ApiResponse(_response, body=decoded)
        return _result

    def delete_participant(self,
                           account_id,
                           participant_id):
        """Does a DELETE request to /accounts/{accountId}/participants/{participantId}.

        Delete participant by ID.

        Args:
            account_id (string): Account ID
            participant_id (string): TODO: type description here.

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. No
                Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/participants/{participantId}'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False},
            'participantId': {'value': participant_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare and execute request
        _request = self.config.http_client.delete(_query_url)
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif _response.status_code == 404:
            raise APIException('Not Found', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        # Return appropriate type
        return ApiResponse(_response)

    def create_session(self,
                       account_id,
                       body=None):
        """Does a POST request to /accounts/{accountId}/sessions.

        Create a new session.
        Sessions are idempotent, so relevant parameters must be set in this
        function if desired.

        Args:
            account_id (string): Account ID
            body (Session, optional): Session parameters

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/sessions'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            'accept': 'application/json',
            'content-type': 'application/json; charset=utf-8'
        }

        # Prepare and execute request
        _request = self.config.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 400:
            raise APIException('Bad Request', _response)
        elif _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        decoded = APIHelper.json_deserialize(_response.text, Session.from_dictionary)
        _result = ApiResponse(_response, body=decoded)
        return _result

    def get_session(self,
                    account_id,
                    session_id):
        """Does a GET request to /accounts/{accountId}/sessions/{sessionId}.

        Get session by ID.

        Args:
            account_id (string): Account ID
            session_id (string): Session ID

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/sessions/{sessionId}'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False},
            'sessionId': {'value': session_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            'accept': 'application/json'
        }

        # Prepare and execute request
        _request = self.config.http_client.get(_query_url, headers=_headers)
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif _response.status_code == 404:
            raise APIException('Not Found', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        decoded = APIHelper.json_deserialize(_response.text, Session.from_dictionary)
        _result = ApiResponse(_response, body=decoded)
        return _result

    def delete_session(self,
                       account_id,
                       session_id):
        """Does a DELETE request to /accounts/{accountId}/sessions/{sessionId}.

        Delete session by ID.

        Args:
            account_id (string): Account ID
            session_id (string): Session ID

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. No
                Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/sessions/{sessionId}'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False},
            'sessionId': {'value': session_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare and execute request
        _request = self.config.http_client.delete(_query_url)
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif _response.status_code == 404:
            raise APIException('Not Found', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        # Return appropriate type
        return ApiResponse(_response)

    def list_session_participants(self,
                                  account_id,
                                  session_id):
        """Does a GET request to /accounts/{accountId}/sessions/{sessionId}/participants.

        List participants in a session.

        Args:
            account_id (string): Account ID
            session_id (string): Session ID

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/sessions/{sessionId}/participants'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False},
            'sessionId': {'value': session_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            'accept': 'application/json'
        }

        # Prepare and execute request
        _request = self.config.http_client.get(_query_url, headers=_headers)
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif _response.status_code == 404:
            raise APIException('Not Found', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        decoded = APIHelper.json_deserialize(_response.text, Participant.from_dictionary)
        _result = ApiResponse(_response, body=decoded)
        return _result

    def add_participant_to_session(self,
                                   account_id,
                                   session_id,
                                   participant_id,
                                   body=None):
        """Does a PUT request to /accounts/{accountId}/sessions/{sessionId}/participants/{participantId}.

        Add a participant to a session.
        Subscriptions can optionally be provided as part of this call.

        Args:
            account_id (string): Account ID
            session_id (string): Session ID
            participant_id (string): Participant ID
            body (Subscriptions, optional): Subscriptions the participant
                should be created with

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. No
                Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/sessions/{sessionId}/participants/{participantId}'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False},
            'sessionId': {'value': session_id, 'encode': False},
            'participantId': {'value': participant_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            'content-type': 'application/json; charset=utf-8'
        }

        # Prepare and execute request
        _request = self.config.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif _response.status_code == 404:
            raise APIException('Not Found', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        # Return appropriate type
        return ApiResponse(_response)

    def remove_participant_from_session(self,
                                        account_id,
                                        session_id,
                                        participant_id):
        """Does a DELETE request to /accounts/{accountId}/sessions/{sessionId}/participants/{participantId}.

        Remove a participant from a session.
        This will automatically remove any subscriptions the participant has
        associated with this session.

        Args:
            account_id (string): Account ID
            session_id (string): Session ID
            participant_id (string): Participant ID

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. No
                Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/sessions/{sessionId}/participants/{participantId}'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False},
            'sessionId': {'value': session_id, 'encode': False},
            'participantId': {'value': participant_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare and execute request
        _request = self.config.http_client.delete(_query_url)
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif _response.status_code == 404:
            raise APIException('Not Found', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        # Return appropriate type
        return ApiResponse(_response)

    def get_participant_subscriptions(self,
                                      account_id,
                                      session_id,
                                      participant_id):
        """Does a GET request to /accounts/{accountId}/sessions/{sessionId}/participants/{participantId}/subscriptions.

        Get a participant's subscriptions.

        Args:
            account_id (string): Account ID
            session_id (string): Session ID
            participant_id (string): Participant ID

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/sessions/{sessionId}/participants/{participantId}/subscriptions'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False},
            'sessionId': {'value': session_id, 'encode': False},
            'participantId': {'value': participant_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            'accept': 'application/json'
        }

        # Prepare and execute request
        _request = self.config.http_client.get(_query_url, headers=_headers)
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif _response.status_code == 404:
            raise APIException('Not Found', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        decoded = APIHelper.json_deserialize(_response.text, Subscriptions.from_dictionary)
        _result = ApiResponse(_response, body=decoded)
        return _result

    def update_participant_subscriptions(self,
                                         account_id,
                                         session_id,
                                         participant_id,
                                         body=None):
        """Does a PUT request to /accounts/{accountId}/sessions/{sessionId}/participants/{participantId}/subscriptions.

        Update a participant's subscriptions.
        This is a full update that will replace the participant's
        subscriptions. First call `getParticipantSubscriptions` if you need
        the current subscriptions. Call this function with no `Subscriptions`
        object to remove all subscriptions.

        Args:
            account_id (string): Account ID
            session_id (string): Session ID
            participant_id (string): Participant ID
            body (Subscriptions, optional): Initial state

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. No
                Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        # Prepare query URL
        _url_path = '/accounts/{accountId}/sessions/{sessionId}/participants/{participantId}/subscriptions'
        _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
            'accountId': {'value': account_id, 'encode': False},
            'sessionId': {'value': session_id, 'encode': False},
            'participantId': {'value': participant_id, 'encode': False}
        })
        _query_builder = self.config.get_base_uri(Server.WEBRTCDEFAULT)
        _query_builder += _url_path
        _query_url = APIHelper.clean_url(_query_builder)

        # Prepare headers
        _headers = {
            'content-type': 'application/json; charset=utf-8'
        }

        # Prepare and execute request
        _request = self.config.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
        WebRtcBasicAuth.apply(self.config, _request)
        _response = self.execute_request(_request)

        # Endpoint and global error handling using HTTP status codes.
        if _response.status_code == 400:
            raise APIException('Bad Request', _response)
        elif _response.status_code == 401:
            raise APIException('Unauthorized', _response)
        elif _response.status_code == 403:
            raise APIException('Access Denied', _response)
        elif _response.status_code == 404:
            raise APIException('Not Found', _response)
        elif (_response.status_code < 200) or (_response.status_code > 208):
            raise ErrorException('Unexpected Error', _response)
        self.validate_response(_response)

        # Return appropriate type
        return ApiResponse(_response)
