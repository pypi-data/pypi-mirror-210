from collections import OrderedDict

import pkg_resources
from directory_client_core.authentication import AuthenticatorNegotiator
from directory_client_core.base import AbstractAPIClient


class UserAPIClient(AbstractAPIClient):
    endpoints = {
        'session_user': 'api/v1/session-user/',
        'oauth2_user_profile': 'oauth2/user-profile/v1/',
        'last_login': 'api/v1/last-login/',
        'check_password': 'api/v1/password-check/',
        'regenerate_verification': 'api/v1/verification-code/regenerate/',
        'verify_verification': 'api/v1/verification-code/verify/',
        'user_create': 'api/v1/user/',
        'user_create_profile': 'api/v1/user/profile/',
        'user_update_profile': 'api/v1/user/profile/update/',
        'user_page_views': 'api/v1/user/page-view/',
        'user_lesson_completed': 'api/v1/user/lesson-completed/',
        'user_questionnaire': 'api/v1/user/questionnaire/',
        'user_data': 'api/v1/user/data/',
    }
    version = pkg_resources.get_distribution(__package__).version

    def get_session_user(self, session_id, authenticator=None):
        return self.get(
            url=self.endpoints['session_user'],
            params={'session_key': session_id},
            authenticator=authenticator,
        )

    def get_oauth2_user_profile(self, bearer_token):
        return self.get(
            url=self.endpoints['oauth2_user_profile'], authenticator=AuthenticatorNegotiator(bearer_token=bearer_token)
        )

    def regenerate_verification_code(self, data, authenticator=None):
        return self.post(
            url=self.endpoints['regenerate_verification'],
            data=data,
            authenticator=authenticator,
        )

    def verify_verification_code(self, data, authenticator=None):
        return self.post(
            url=self.endpoints['verify_verification'],
            data=data,
            authenticator=authenticator,
        )

    def check_password(self, session_id, password, authenticator=None):
        url = self.endpoints['check_password']
        data = OrderedDict([('session_key', session_id), ('password', password)])
        return self.post(
            url,
            data,
            authenticator=authenticator,
        )

    def get_last_login(self, start=None, end=None, authenticator=None):
        params = {}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        params = params or None

        return self.get(
            url=self.endpoints['last_login'],
            params=params,
            authenticator=authenticator,
        )

    def create_user(self, email, password, authenticator=None, mobile_phone_number=None):
        url = self.endpoints['user_create']
        data = OrderedDict([('email', email), ('password', password), ('mobile_phone_number', mobile_phone_number)])
        return self.post(
            url,
            data,
            authenticator=authenticator,
        )

    def create_user_profile(self, sso_session_id, data):
        authenticator = AuthenticatorNegotiator(sso_session_id=sso_session_id)
        url = self.endpoints['user_create_profile']
        return self.post(url, data, authenticator=authenticator)

    def update_user_profile(self, sso_session_id, data):
        authenticator = AuthenticatorNegotiator(sso_session_id=sso_session_id)
        url = self.endpoints['user_update_profile']
        return self.patch(url, data, authenticator=authenticator)

    def set_user_page_view(self, sso_session_id, service, page):
        authenticator = AuthenticatorNegotiator(sso_session_id=sso_session_id)
        url = self.endpoints['user_page_views']
        return self.post(url, {'service': service, 'page': page}, authenticator=authenticator)

    def get_user_page_views(self, sso_session_id, service, page):
        authenticator = AuthenticatorNegotiator(sso_session_id=sso_session_id)
        url = self.endpoints['user_page_views']
        return self.get(url, {'service': service, 'page': page}, authenticator=authenticator)

    def get_user_lesson_completed(self, sso_session_id, service, lesson_page):
        authenticator = AuthenticatorNegotiator(sso_session_id=sso_session_id)
        url = self.endpoints['user_lesson_completed']
        return self.get(url, {'service': service, 'lesson': lesson_page}, authenticator=authenticator)

    def set_user_lesson_completed(self, sso_session_id, service, lesson_page, lesson, module):
        authenticator = AuthenticatorNegotiator(sso_session_id=sso_session_id)
        url = self.endpoints['user_lesson_completed']
        return self.post(
            url,
            {
                'service': service,
                'lesson_page': lesson_page,
                'lesson': lesson,
                'module': module,
            },
            authenticator=authenticator,
        )

    def delete_user_lesson_completed(self, sso_session_id, service, lesson):
        authenticator = AuthenticatorNegotiator(sso_session_id=sso_session_id)
        url = self.endpoints['user_lesson_completed']
        return self.delete(url, {'service': service, 'lesson': lesson}, authenticator=authenticator)

    def get_user_questionnaire(self, sso_session_id, service):
        url = self.endpoints['user_questionnaire']
        return self.get(url, {'service': service}, authenticator=AuthenticatorNegotiator(sso_session_id=sso_session_id))

    def set_user_questionnaire_answer(self, sso_session_id, service, question_id, answer):
        url = self.endpoints['user_questionnaire']
        return self.post(
            url,
            {'service': service, 'question_id': question_id, 'answer': answer},
            authenticator=AuthenticatorNegotiator(sso_session_id=sso_session_id),
        )

    def get_user_data(self, sso_session_id, name):
        url = self.endpoints['user_data']
        return self.get(url, {'name': name}, authenticator=AuthenticatorNegotiator(sso_session_id=sso_session_id))

    def set_user_data(self, sso_session_id, data, name):
        url = self.endpoints['user_data']
        return self.post(
            url, {'data': data, 'name': name}, authenticator=AuthenticatorNegotiator(sso_session_id=sso_session_id)
        )
