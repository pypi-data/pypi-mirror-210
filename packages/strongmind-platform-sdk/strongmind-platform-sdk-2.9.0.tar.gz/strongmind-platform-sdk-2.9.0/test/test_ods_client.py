import json
import unittest

import requests
from expects import *
from faker import Faker
from mockito import unstub, when, verify, mock, verifyStubbedInvocationsAreUsed
from requests import HTTPError, Response

from platform_sdk.clients.ods_client import OneRosterDataStoreClient
from platform_sdk.shared.utilities import get_plural_oneroster_type
from test.helpers.test_helpers import create_http_error

fake = Faker()


class TestOdsClient(unittest.TestCase):
    def setUp(self) -> None:
        self.base_url = fake.domain_name()
        self.key = fake.uuid4()
        self.target = OneRosterDataStoreClient(base_url=self.base_url,
                                               key=self.key)

    def tearDown(self) -> None:
        unstub()

    def test_get_from_url_as_dict(self):
        """
        Given we have a data_type and a sourced_id
        When we call the ods for a class
        Then we should receive a class without the validation of the oneroster_client
        """
        # Arrange
        data_type = fake.word(
            ext_word_list=['class', 'user', 'academicSession', 'course', 'enrollment', 'lineItem', 'org',
                           'demographic'])
        sourced_id = fake.uuid4()
        plural_data_type = get_plural_oneroster_type(data_type)
        url = f"{self.base_url}/{plural_data_type}/{sourced_id}"
        headers = {'x-functions-key': self.key}
        expected = {
            fake.word(): fake.word()
        }
        actual_response = requests.Response()
        actual_response.status_code = 200
        actual_response._content = f'{{"{data_type}": {json.dumps(expected)}}}'.encode()
        when(requests).get(url=url, headers=headers).thenReturn(actual_response)

        # Act
        response_json = self.target.get_data_as_dict(data_type=data_type, sourced_id=sourced_id)

        # Assert
        verify(requests, times=1).get(url=url, headers=headers)
        expect(response_json).to(equal(expected))

    def test_get_from_url_as_dict_raises_http_error_with_dependency_name(self):
        """
        Given we have a data_type and a sourced_id
        When we call the ods and receive an error code
        Then we should raise an error with dependency name
        """
        # Arrange
        http_error = create_http_error(500)
        data_type = fake.word(
            ext_word_list=['class', 'user', 'academicSession', 'course', 'enrollment', 'lineItem', 'org',
                           'demographic'])
        sourced_id = fake.uuid4()
        url = f"{self.base_url}/{get_plural_oneroster_type(data_type)}/{sourced_id}"
        when(requests).get(url=url, headers=self.target._headers()).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)

        # Act
        with self.assertRaises(HTTPError) as context:
            self.target.get_data_as_dict(data_type=data_type, sourced_id=sourced_id)

        # Assert
        expect(getattr(context.exception, 'dependency_name', None)).to(equal('OneRosterDataStore'))

    def test_post_data_raises_http_error_with_dependency_name(self):
        """
        When we post to the ods and receive an error code
        Then we should raise an error with dependency name
        """
        # Arrange
        http_error = create_http_error(500)
        data_type = fake.word(
            ext_word_list=['class', 'user', 'academicSession', 'course', 'enrollment', 'lineItem', 'org',
                           'demographic'])
        url = f"{self.base_url}/{data_type}"
        when(requests).post(url, headers=self.target._headers(), json={}).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)

        # Act
        with self.assertRaises(HTTPError) as context:
            self.target._post_data(data={}, data_type=data_type)

        # Assert
        expect(getattr(context.exception, 'dependency_name', None)).to(equal('OneRosterDataStore'))

    def test_post_data_sends_data_to_ods(self):
        """
        When we post to the ods
        Then we post the correct payload and headers to the ODS
        """
        # Arrange
        data_type = fake.word(
            ext_word_list=['classes', 'users', 'academicSessions', 'courses', 'enrollments', 'lineItems', 'orgs',
                           'demographics'])
        url = f"{self.base_url}/{data_type}"
        payload = {
            fake.word(): fake.word()
        }
        response = mock(Response)
        when(response).raise_for_status()
        when(requests).post(url, headers=self.target._headers(), json=payload).thenReturn(response)

        # Act
        self.target._post_data(data=payload, data_type=data_type)

        # Assert
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_delete_data_raises_http_error_with_dependency_name(self):
        """
        When we send a DELETE to the ods and receive an error code
        Then we should raise an error with dependency name
        """
        # Arrange
        http_error = create_http_error(500)
        data_type = fake.word(
            ext_word_list=['classes', 'users', 'academicSessions', 'courses', 'enrollments', 'lineItems', 'orgs',
                           'demographics'])
        uuid = fake.uuid4()
        url = f"{self.base_url}/{data_type}/{uuid}"
        when(requests).delete(url, headers=self.target._headers()).thenReturn(http_error.response)
        when(http_error.response).raise_for_status().thenRaise(http_error)

        # Act
        with self.assertRaises(HTTPError) as context:
            self.target._delete(uuid, data_type=data_type)

        # Assert
        expect(getattr(context.exception, 'dependency_name', None)).to(equal('OneRosterDataStore'))

    def test_posts_enrollments(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/enrollments"
        payload = {fake.domain_word(): fake.random_int()}
        response = mock({'raise_for_status': lambda: None, 'status_code': 200, 'status': '200 OK'}, spec=Response,
                        strict=True)
        when(requests).post(url, headers=self.target._headers(), json=payload).thenReturn(response)

        # Act
        self.target.post_enrollment(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_delete_enrollments(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        uuid = fake.uuid4()
        url = f"{self.base_url}/enrollments/{uuid}"
        response = mock({'raise_for_status': lambda: None, 'status_code': 204, 'status': '204 No Content'},
                        spec=Response,
                        strict=True)
        when(requests).delete(url, headers=self.target._headers()).thenReturn(response)

        # Act
        self.target.delete_enrollment(uuid)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).delete(url, headers={'x-functions-key': self.key})

    def test_post_users(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/users"
        payload = {fake.domain_word(): fake.random_int()}
        response = mock({'raise_for_status': lambda: None, 'status_code': 200, 'status': '200 OK'}, spec=Response,
                        strict=True)
        when(requests).post(url, headers=self.target._headers(), json=payload).thenReturn(response)

        # Act
        self.target.post_user(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_delete_users(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        uuid = fake.uuid4()
        url = f"{self.base_url}/users/{uuid}"
        response = mock({'raise_for_status': lambda: None, 'status_code': 204, 'status': '204 No Content'},
                        spec=Response,
                        strict=True)
        when(requests).delete(url, headers=self.target._headers()).thenReturn(response)

        # Act
        self.target.delete_user(uuid)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).delete(url, headers={'x-functions-key': self.key})

    def test_post_demographics(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/demographics"
        payload = {fake.domain_word(): fake.random_int()}
        response = mock({'raise_for_status': lambda: None, 'status_code': 200, 'status': '200 OK'}, spec=Response,
                        strict=True)
        when(requests).post(url, headers=self.target._headers(), json=payload).thenReturn(response)

        # Act
        self.target.post_demographic(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_post_courses(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/courses"
        payload = {fake.domain_word(): fake.random_int()}
        response = mock({'raise_for_status': lambda: None, 'status_code': 200, 'status': '200 OK'}, spec=Response,
                        strict=True)
        when(requests).post(url, headers=self.target._headers(), json=payload).thenReturn(response)

        # Act
        self.target.post_course(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_delete_courses(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        uuid = fake.uuid4()
        url = f"{self.base_url}/courses/{uuid}"
        response = mock({'raise_for_status': lambda: None, 'status_code': 204, 'status': '204 No Content'},
                        spec=Response,
                        strict=True)
        when(requests).delete(url, headers=self.target._headers()).thenReturn(response)

        # Act
        self.target.delete_course(uuid)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).delete(url, headers={'x-functions-key': self.key})

    def test_post_classes(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/classes"
        payload = {fake.domain_word(): fake.random_int()}
        response = mock({'raise_for_status': lambda: None, 'status_code': 200, 'status': '200 OK'}, spec=Response,
                        strict=True)
        when(requests).post(url, headers=self.target._headers(), json=payload).thenReturn(response)

        # Act
        self.target.post_class(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_delete_classes(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        uuid = fake.uuid4()
        url = f"{self.base_url}/classes/{uuid}"
        response = mock({'raise_for_status': lambda: None, 'status_code': 204, 'status': '204 No Content'},
                        spec=Response,
                        strict=True)
        when(requests).delete(url, headers=self.target._headers()).thenReturn(response)

        # Act
        self.target.delete_class(uuid)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).delete(url, headers={'x-functions-key': self.key})

    def test_post_academic_sessions(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/academicSessions"
        payload = {fake.domain_word(): fake.random_int()}
        response = mock({'raise_for_status': lambda: None, 'status_code': 200, 'status': '200 OK'}, spec=Response,
                        strict=True)
        when(requests).post(url, headers=self.target._headers(), json=payload).thenReturn(response)

        # Act
        self.target.post_academic_session(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)

    def test_post_orgs(self):
        """
        Client submits via HTTP with the x-functions-key header
        """
        # Arrange
        url = f"{self.base_url}/orgs"
        payload = {fake.domain_word(): fake.random_int()}
        response = mock({'raise_for_status': lambda: None, 'status_code': 200, 'status': '200 OK'}, spec=Response,
                        strict=True)
        when(requests).post(url, headers=self.target._headers(), json=payload).thenReturn(response)

        # Act
        self.target.post_org(payload)

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).post(url, headers={'x-functions-key': self.key}, json=payload)
