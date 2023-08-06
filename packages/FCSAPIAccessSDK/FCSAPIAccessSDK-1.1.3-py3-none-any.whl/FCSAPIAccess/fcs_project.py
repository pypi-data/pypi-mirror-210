"""
WARNING: THIS MODULE IS GENERATED! ALL CHANGES WILL BE DISCARDED
"""

import requests
import urllib.parse


class FangCloudServicesAPI:
    """
    Welcome to the FangCloudServices API!
    
    If you have any questions or encounter any issues, please do not hesitate to reach out.
    
    To obtain the credentials to use this API, please see the *Acquiring Project API Credentials* section of the *Setup Guide*.
    """

    url_base = "https://fangcloudservices.pythonanywhere.com/api/v1"

    def __init__(self, access_token):
        self.headers = {'Authorization': 'Bearer {}'.format(access_token)}
        self._status_check = lambda x, y: None

    def _check_status(self, r: requests.Response, retry: callable):
        check = self._status_check(r, retry)
        
        if "json" in r.headers['content-type']:
            result = r.json()
            
        else:
            result = r.text
        
        return result if check is None else check
        
    def _url_encode(self, text: str) -> str:
        return urllib.parse.quote_plus(str(text))
    
    def get_all_email_addresses(self, user) -> dict:
        """
        Retrieves the email addresses linked to a specified user.
        :param user: The ID of the user
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/email?user={}".format(self._url_encode(user)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_all_email_addresses(**local_vars))
        
    def create_email_address(self, user, email) -> dict:
        """
        Links the specified email address to the specified user.
        
        This will cause the confirmation email to be sent to the new email address.
        :param user:
        :param email:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/email", 
            headers=headers,
            json={
                "email": email,
                "user": user
            }
        )
        
        return self._check_status(r, lambda: self.create_email_address(**local_vars))
        
    def update_email_address(self, id, user, email) -> dict:
        """
        Updates a user's existing email address
        :param id: The ID of the email address
        :param user:
        :param email:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/email?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "email": email,
                "user": user
            }
        )
        
        return self._check_status(r, lambda: self.update_email_address(**local_vars))
        
    def remove_email_address(self, id, user) -> dict:
        """
        
        :param id: The ID of the email address to remove
        :param user: The ID of the user ascociated with the email address
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/email?id={}&user={}".format(self._url_encode(id), self._url_encode(user)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_email_address(**local_vars))
        
    def validate_token(self, token, minified) -> dict:
        """
        Takes the specified access token which is provided by your API client, and returns the data related to the user's account.
        
        This endpoint will also detect expired and invalid tokens.
        :param token: The token you wish to validate
        :param minified: If a minified response should be created
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/token?token={}&minified={}".format(self._url_encode(token), self._url_encode(minified)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.validate_token(**local_vars))
        
    def list_directories(self) -> dict:
        """
        Lists all of the directories in the project-level file storage.
        
        **Note**: Directories for individual users will appear automatically when a file is uploaded to their location, or when a list of their directory is requested.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/file", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.list_directories(**local_vars))
        
    def list_user_directory(self) -> dict:
        """
        Retrieves a list of files stored under the specified user.
        
        Note that the `user_id` parameter can be replaced with `project` to interact with the project specific directory.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/file/[user_id]", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.list_user_directory(**local_vars))
        
    def upload_file(self) -> dict:
        """
        Upload many files to a single user which is specified in the URL.
        
        Note that the `user_id` parameter can be replaced with `project` to interact with the project specific directory.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        raise NotImplementedError('The requested endpoint is not ready for use')

    def get_file(self) -> dict:
        """
        Retrieves the contents of the specified file.
        
        Note that the `user_id` parameter can be replaced with `project` to interact with the project specific directory.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/file/[user_id]/[filename]", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_file(**local_vars))
        
    def upload_file(self) -> dict:
        """
        Uploads the provided file with the specified filename. If many files are uploaded, only one will be saved.
        
        Note that the `user_id` parameter can be replaced with `project` to interact with the project specific directory.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        raise NotImplementedError('The requested endpoint is not ready for use')

    def update_file(self) -> dict:
        """
        Writes the raw data sent in the request to the specified file. The old file will be overwritten and all previous content will be lost. This action can not be undone.
        
        If the file does not exist, a new one will be created
        
        Note that the `user_id` parameter can be replaced with `project` to interact with the project specific directory.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "text/plain"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/file/[user_id]/[filename]", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.update_file(**local_vars))
        
    def remove_file(self) -> dict:
        """
        Removes the specified file. This action can not be undone.
        
        Note that the `user_id` parameter can be replaced with `project` to interact with the project specific directory.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/file/[user_id]/[filename]", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_file(**local_vars))
        
    def get_all_users(self) -> dict:
        """
        Returns a list of every user. Includes connected accounts, email addresses, and their user role.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_all_users(**local_vars))
        
    def get_user(self, id) -> dict:
        """
        This endpoint retrieves a single user who has the specified ID.
        :param id: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_user(**local_vars))
        
    def search_users(self, username, display_name, email, primary_email, password_reset, reset_password_on_login, user_role, active) -> dict:
        """
        This endpoint retrieves a single user who has the specified ID.
        :param username: 
        :param display_name: 
        :param email: 
        :param primary_email: 
        :param password_reset: 
        :param reset_password_on_login: 
        :param user_role: 
        :param active: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user/search?username={}&display_name={}&email={}&primary_email={}&password_reset={}&reset_password_on_login={}&user_role={}&active={}".format(self._url_encode(username), self._url_encode(display_name), self._url_encode(email), self._url_encode(primary_email), self._url_encode(password_reset), self._url_encode(reset_password_on_login), self._url_encode(user_role), self._url_encode(active)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.search_users(**local_vars))
        
    def create_user(self, data, username, email, user_role, password, mailing_lists, dob, favourite_color) -> dict:
        """
        StartFragment
        
        Sets the properties of a new user.
        
        If the requested `user_role` or `mailing_list` IDs do not correspond to an existing user role or mailing list, you will receive a 404 error and the update will not be made.
        
        Note that `dob` and `favorite_color` are cusom user fields specific to this project. Use your own fields in their place if you have specified any.
        :param data:
        :param username:
        :param email:
        :param user_role:
        :param password:
        :param mailing_lists:
        :param dob:
        :param favourite_color:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user", 
            headers=headers,
            json={
                "data": data,
                "dob": dob,
                "email": email,
                "favourite_color": favourite_color,
                "mailing_lists": mailing_lists,
                "password": password,
                "user_role": user_role,
                "username": username
            }
        )
        
        return self._check_status(r, lambda: self.create_user(**local_vars))
        
    def update_user(self, id, data, username, primary_email, user_role, active) -> dict:
        """
        Updates the properties of the specified user. Note that sending up the `data` JSON blob will overwrite the existing data so be sure to merge the data before sending.
        
        **Note** that this action can not be undone.
        
        If the requested `user_role` or `primary_email` IDs do not correspond to an existing user role or email address, you will receive a 404 error and the update will not be made.
        
        Finally, unlike most of the other endpoints, there are no mandatory values in the JSON body, so you only need to send what you want to change.
        :param id: 
        :param data:
        :param username:
        :param primary_email:
        :param user_role:
        :param active:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "active": active,
                "data": data,
                "primary_email": primary_email,
                "user_role": user_role,
                "username": username
            }
        )
        
        return self._check_status(r, lambda: self.update_user(**local_vars))
        
    def get_all_email_categories(self) -> dict:
        """
        
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/email_category", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_all_email_categories(**local_vars))
        
    def create_email_category(self, name) -> dict:
        """
        
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/email_category", 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.create_email_category(**local_vars))
        
    def update_email_category(self, id, name) -> dict:
        """
        
        :param id: 
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/email_category?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.update_email_category(**local_vars))
        
    def remove_email_category(self, id) -> dict:
        """
        
        :param id: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/email_category?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_email_category(**local_vars))
        
    def get_email_addresses_subscribed_to_a_category(self, category) -> dict:
        """
        
        :param category: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/mailing_list?category={}".format(self._url_encode(category)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_email_addresses_subscribed_to_a_category(**local_vars))
        
    def get_categories_subscribed_to_by_an_email_address(self, email) -> dict:
        """
        
        :param email: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/mailing_list?email={}".format(self._url_encode(email)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_categories_subscribed_to_by_an_email_address(**local_vars))
        
    def subscribe_to_category(self, email, category) -> dict:
        """
        
        :param email: 
        :param category: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/mailing_list?email={}&category={}".format(self._url_encode(email), self._url_encode(category)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.subscribe_to_category(**local_vars))
        
    def subscribe_to_all_categories(self, email) -> dict:
        """
        
        :param email: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/mailing_list?email={}".format(self._url_encode(email)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.subscribe_to_all_categories(**local_vars))
        
    def remove_subscription_from_category(self, email, category) -> dict:
        """
        
        :param email: 
        :param category: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/mailing_list?email={}&category={}".format(self._url_encode(email), self._url_encode(category)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_subscription_from_category(**local_vars))
        
    def remove_subscription_from_all_categories(self, email) -> dict:
        """
        
        :param email: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/mailing_list?email={}".format(self._url_encode(email)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_subscription_from_all_categories(**local_vars))
        
    def get_external_accounts(self) -> dict:
        """
        This endpoint lists the external accounts your project allows users to log in with
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/external_account", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_external_accounts(**local_vars))
        
    def connect_new_external_account(self, id) -> dict:
        """
        Allow users to log in with an external account. If you wish to specify your own credentials for the authentication process, include them in the request JSON as `credentials`.
        
        Note that we will never show you your credentials after you have submitted them.
        :param id: The ID of the platform to integrate with
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/external_account?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.connect_new_external_account(**local_vars))
        
    def update_account_connection(self, id, credentials) -> dict:
        """
        This endpoint allows you to update and change the credentials associated with a linked account.
        
        Note that we will never show you your credentials after you have submitted them.
        
        If you wish to use the default credentials for the authentication process, omit the `credentials` property in the request JSON
        :param id: 
        :param credentials:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/external_account?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "credentials": credentials
            }
        )
        
        return self._check_status(r, lambda: self.update_account_connection(**local_vars))
        
    def unlink_account(self, id) -> dict:
        """
        This endpoint allows you to unlink a third party linked account.
        
        **WARNING**! Any user who previously logged in with the unlinked account will no longer be able to log in, unless they have linked another means of log in.
        
        Be sure you know what you are doing before performing this action. This **CAN NOT** be undone!
        :param id: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/external_account?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.unlink_account(**local_vars))
        
    def get_requirements(self) -> dict:
        """
        Retrieves the password requirements set for your users when they sign up.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/password_requirements", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_requirements(**local_vars))
        
    def change_requirements(self, min_length, numbers, special_chars, upper_lower_chars, store_last_passwords) -> dict:
        """
        Allows you to change the password requirements which your users must meet when creating a new account.
        :param min_length:
        :param numbers:
        :param special_chars:
        :param upper_lower_chars:
        :param store_last_passwords:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/password_requirements", 
            headers=headers,
            json={
                "min_length": min_length,
                "numbers": numbers,
                "special_chars": special_chars,
                "store_last_passwords": store_last_passwords,
                "upper_lower_chars": upper_lower_chars
            }
        )
        
        return self._check_status(r, lambda: self.change_requirements(**local_vars))
        
    def get_settings(self) -> dict:
        """
        Retrieves your project settings
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_settings(**local_vars))
        
    def change_settings(self, id, default_data, default_user_role, name, privacy_policy, terms_of_service, ignore_expired_tokens, access_token_prefix, enable_password_login, alert_channel, allow_registration) -> dict:
        """
        Changes your project settings
        :param id: 
        :param default_data:
        :param default_user_role:
        :param name:
        :param privacy_policy:
        :param terms_of_service:
        :param ignore_expired_tokens:
        :param access_token_prefix:
        :param enable_password_login:
        :param alert_channel:
        :param allow_registration:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "access_token_prefix": access_token_prefix,
                "alert_channel": alert_channel,
                "allow_registration": allow_registration,
                "default_data": default_data,
                "default_user_role": default_user_role,
                "enable_password_login": enable_password_login,
                "ignore_expired_tokens": ignore_expired_tokens,
                "name": name,
                "privacy_policy": privacy_policy,
                "terms_of_service": terms_of_service
            }
        )
        
        return self._check_status(r, lambda: self.change_settings(**local_vars))
        
    def copy_settings(self, from_id) -> dict:
        """
        
        :param from_id: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/import?from_id={}".format(self._url_encode(from_id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.copy_settings(**local_vars))
        
    def get_scopes(self) -> dict:
        """
        Retrieves the full list of scopes available to your account.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/scope", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_scopes(**local_vars))
        
    def create_scope(self, tag, display) -> dict:
        """
        Creates a new scope. Note that no user roles will be able to access the scope until you allow access.
        :param tag:
        :param display:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/scope", 
            headers=headers,
            json={
                "display": display,
                "tag": tag
            }
        )
        
        return self._check_status(r, lambda: self.create_scope(**local_vars))
        
    def update_scope(self, id, tag, display) -> dict:
        """
        Update the tag and display name of a scope.
        
        Changing the tag may have unexpected consequences when authenticating, however, user roles will keep their access to the scopes.
        :param id: The ID of the scope
        :param tag:
        :param display:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/scope?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "display": display,
                "tag": tag
            }
        )
        
        return self._check_status(r, lambda: self.update_scope(**local_vars))
        
    def delete_scope(self, id) -> dict:
        """
        Deletes the specified scope.
        
        **WARNING:** This can not be undone
        :param id: The ID of the scope
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/scope?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.delete_scope(**local_vars))
        
    def get_fields(self) -> dict:
        """
        Returns the additional fields a user must fill when they are registering.
        
        All of the responses of these fields can be found in the user data JSON blob.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_fields", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_fields(**local_vars))
        
    def add_field(self, validation, name, json_name) -> dict:
        """
        Adds an additional fields a user must fill when they are registering.
        
        All of the responses of these fields can be found in the user data JSON blob.
        :param validation:
        :param name:
        :param json_name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_fields", 
            headers=headers,
            json={
                "json_name": json_name,
                "name": name,
                "validation": validation
            }
        )
        
        return self._check_status(r, lambda: self.add_field(**local_vars))
        
    def update_field(self, id, validation, name, json_name) -> dict:
        """
        Updates an additional fields a user must fill when they are registering.
        
        All of the responses of these fields can be found in the user data JSON blob.
        :param id: The ID of the validation you wish to update
        :param validation:
        :param name:
        :param json_name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_fields?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "json_name": json_name,
                "name": name,
                "validation": validation
            }
        )
        
        return self._check_status(r, lambda: self.update_field(**local_vars))
        
    def delete_field(self, id) -> dict:
        """
        Removes an additional fields a user must fill when they are registering.
        
        All of the responses of these fields can be found in the user data JSON blob.
        :param id: The ID of the validation you wish to delete
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_fields?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.delete_field(**local_vars))
        
    def get_role_scopes(self, id) -> dict:
        """
        Returns the scopes which a user roll may access.
        
        See the `scope` endpoint to manage your scopes
        :param id: The ID of the role
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_roles/scopes?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_role_scopes(**local_vars))
        
    def add_role_scope(self, id, scope) -> dict:
        """
        Grants a user roll access to a scope
        
        See the `scope` endpoint to manage your scopes
        :param id: The ID of the role
        :param scope:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_roles/scopes?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "scope": scope
            }
        )
        
        return self._check_status(r, lambda: self.add_role_scope(**local_vars))
        
    def remove_role_scope(self, id, scope) -> dict:
        """
        Revokes access for a role to access a scope
        
        See the `scope` endpoint to manage your scopes
        :param id: The ID of the role
        :param scope: The ID of the scope
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_roles/scopes?id={}&scope={}".format(self._url_encode(id), self._url_encode(scope)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_role_scope(**local_vars))
        
    def get_roles(self) -> dict:
        """
        Returns a list of your user roles
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_roles", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_roles(**local_vars))
        
    def add_role(self, name) -> dict:
        """
        Creates a new user role
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_roles", 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.add_role(**local_vars))
        
    def update_role(self, id, name) -> dict:
        """
        Renames the specified user role
        :param id: 
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_roles?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.update_role(**local_vars))
        
    def delete_user_role(self, id, validation, name, json_name) -> dict:
        """
        Removes a user role.
        
        **WARNING**: a user role can not be deleted if users are assigned to the role, or if it is the default role.
        :param id: 
        :param validation:
        :param name:
        :param json_name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/user_roles?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "json_name": json_name,
                "name": name,
                "validation": validation
            }
        )
        
        return self._check_status(r, lambda: self.delete_user_role(**local_vars))
        
    def get_validations(self, custom) -> dict:
        """
        Returns either your custom RegEx validations, or the premade validations which can be used in any project
        :param custom: If the result set should include only your custom validations
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/validation?custom={}".format(self._url_encode(custom)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_validations(**local_vars))
        
    def get_scopes(self, id) -> dict:
        """
        Retrieves a list of the scopes enabled for the specified application
        :param id: The ID of the application
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/applications/scope?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_scopes(**local_vars))
        
    def add_scope(self, id, scope) -> dict:
        """
        Enables a scope to the specified application
        :param id: The ID of the application
        :param scope:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/applications/scope?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "scope": scope
            }
        )
        
        return self._check_status(r, lambda: self.add_scope(**local_vars))
        
    def remove_scope(self, id, scope) -> dict:
        """
        Disables the specified scope from the specified application
        :param id: The ID of the application
        :param scope: The scope to disable
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/applications/scope?id={}&scope={}".format(self._url_encode(id), self._url_encode(scope)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_scope(**local_vars))
        
    def get_applications(self, user) -> dict:
        """
        Returns a list of your applications (for your system. These applications do not have access to your Fang account)
        :param user: The ID of the user you wish to list applications for. If not specified, your applications will be used.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/applications?user={}".format(self._url_encode(user)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_applications(**local_vars))
        
    def create_app(self, user, name) -> dict:
        """
        Creates a new applications (for your system. These applications do not have access to your Fang account)
        :param user: The ID of the user you wish to list applications for. If not specified, your applications will be used.
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/applications?user={}".format(self._url_encode(user)), 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.create_app(**local_vars))
        
    def update_app(self, id, user, name) -> dict:
        """
        Updates the information of an application (for your system. These applications do not have access to your Fang account)
        :param id: 
        :param user: The ID of the user you wish to list applications for. If not specified, your applications will be used. The redundnacy of specifying both is for added security.
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/applications?id={}&user={}".format(self._url_encode(id), self._url_encode(user)), 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.update_app(**local_vars))
        
    def regenerate_tokens(self, id, user) -> dict:
        """
        Regenerates the `client_id` and `client_secret` of your application (for your system. These applications do not have access to your Fang account)
        :param id: 
        :param user: The ID of the user you wish to list applications for. If not specified, your applications will be used. The redundnacy of specifying both is for added security.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "PATCH", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/applications?id={}&user={}".format(self._url_encode(id), self._url_encode(user)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.regenerate_tokens(**local_vars))
        
    def delete_app(self, id, user) -> dict:
        """
        Removes the specified application (for your system. These applications do not have access to your Fang account)
        :param id: 
        :param user: The ID of the user you wish to list applications for. If not specified, your applications will be used. The redundnacy of specifying both is for added security.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/applications?id={}&user={}".format(self._url_encode(id), self._url_encode(user)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.delete_app(**local_vars))
        
    def get_auto_auth(self) -> dict:
        """
        Returns a list of applications which new users authorize access to by default
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/auto_auth", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_auto_auth(**local_vars))
        
    def create_auto_auth(self, app) -> dict:
        """
        Sets a new application which new users authorize access to by default
        :param app:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/auto_auth", 
            headers=headers,
            json={
                "app": app
            }
        )
        
        return self._check_status(r, lambda: self.create_auto_auth(**local_vars))
        
    def remove_auto_auth(self, app) -> dict:
        """
        Revokes an application which new users authorize access to by default
        :param app: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/auto_auth?app={}".format(self._url_encode(app)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_auto_auth(**local_vars))
        
    def get_scopes(self, id) -> dict:
        """
        Retrieves a list of the scopes enabled for the specified application
        :param id: The ID of the application
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api/scope?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_scopes(**local_vars))
        
    def add_scope(self, id, scope) -> dict:
        """
        Enables a scope to the specified application
        :param id: The ID of the application
        :param scope:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api/scope?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "scope": scope
            }
        )
        
        return self._check_status(r, lambda: self.add_scope(**local_vars))
        
    def remove_scope(self, id, scope) -> dict:
        """
        Disables the specified scope from the specified application
        :param id: The ID of the application
        :param scope: The scope to disable
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api/scope?id={}&scope={}".format(self._url_encode(id), self._url_encode(scope)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_scope(**local_vars))
        
    def get_sessions(self, id) -> dict:
        """
        Retrieves a list of active sessions for a specified application
        :param id: The ID of the application
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api/session?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_sessions(**local_vars))
        
    def expire_session(self, id, session) -> dict:
        """
        Expires the specified session. It can be refreshed via the refresh token flow.
        
        Note that it is possible to expire the session you are currently using for API Access. Doing so will cause the token to expire, but it can be refreshed.
        :param id: The ID of the application
        :param session: The ID of the session to expire
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api/session?id={}&session={}".format(self._url_encode(id), self._url_encode(session)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.expire_session(**local_vars))
        
    def refresh_token(self, id, session) -> dict:
        """
        Refreshes the specified session and returns the new access and refresh tokens.
        :param id: The ID of the application
        :param session: The ID of the session to refresh
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "PATCH", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api/session?id={}&session={}".format(self._url_encode(id), self._url_encode(session)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.refresh_token(**local_vars))
        
    def remove_session(self, id, session) -> dict:
        """
        Revokes an active sessions for a specified application.
        
        Note that it is possible to revoke the session you are currently using for API Access. Doing so will cause the token to expire and it can not be refreshed.
        
        This action can not be undone.
        :param id: The ID of the application
        :param session: The ID of the session to revoke
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api/session?id={}&session={}".format(self._url_encode(id), self._url_encode(session)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_session(**local_vars))
        
    def remove_all_sessions(self, id) -> dict:
        """
        Revokes an active sessions for a specified application.
        
        Note that it is possible to revoke the session you are currently using for API Access. Doing so will cause the token to expire and it can not be refreshed.
        
        This action can not be undone.
        :param id: The ID of the application
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api/session?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_all_sessions(**local_vars))
        
    def get_tokens(self) -> dict:
        """
        Retrieves a list of your API applications which can be used to access FangCloudServices API
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_tokens(**local_vars))
        
    def create_token(self, name) -> dict:
        """
        Creates a new API application which can be used to access FangCloudServices API
        
        Note that the response contains the `client_id` and `client_secret`. This is the only time you will be able to see them, unless you regenerate them.
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api", 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.create_token(**local_vars))
        
    def rename_token(self, id, name) -> dict:
        """
        Updates an existing API applications which can be used to access FangCloudServices API
        :param id: 
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.rename_token(**local_vars))
        
    def regenerate_token(self, id) -> dict:
        """
        Regenerates the `client_id` and `client_secret` of an existing API application which can be used to access FangCloudServices API
        
        Note that the response contains the `client_id` and `client_secret`. This is the only time you will be able to see them, unless you regenerate them.
        :param id: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "PATCH", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.regenerate_token(**local_vars))
        
    def remove_token(self, id) -> dict:
        """
        Removes an existing API applications which can be used to access FangCloudServices API
        :param id: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/api?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_token(**local_vars))
        
    def get_limits(self) -> dict:
        """
        Returns the limitations and usages related to your project. If you need more power, feel free to reach out, and we will make it happen.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/limits", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_limits(**local_vars))
        
    def get_project_scopes(self) -> dict:
        """
        Returns a list of scopes and the display name of each fang cloud services scope. These scopes are to be used with Project API Access.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/project_scopes", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_project_scopes(**local_vars))
        
    def get_redirect_uris(self, app) -> dict:
        """
        Retrieves a list of URLs the specified application can redirect to during authentication
        
        Note that the `redirect_uri` parameter must match one of these URLs exactly or authentication will not occur
        :param app: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/redirect_uri?app={}".format(self._url_encode(app)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_redirect_uris(**local_vars))
        
    def create_redirect_uri(self, app, uri) -> dict:
        """
        Adds a new URL to the list of locations the specified application can redirect to during authentication
        :param app: 
        :param uri:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/redirect_uri?app={}".format(self._url_encode(app)), 
            headers=headers,
            json={
                "uri": uri
            }
        )
        
        return self._check_status(r, lambda: self.create_redirect_uri(**local_vars))
        
    def update_redirect_uri(self, app, id, uri) -> dict:
        """
        Updates an existing new URL in the list of locations the specified application can redirect to during authentication
        :param app: 
        :param id: 
        :param uri:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/redirect_uri?app={}&id={}".format(self._url_encode(app), self._url_encode(id)), 
            headers=headers,
            json={
                "uri": uri
            }
        )
        
        return self._check_status(r, lambda: self.update_redirect_uri(**local_vars))
        
    def remove_redirect__uri(self, app, id) -> dict:
        """
        Removes an existing new URL in the list of locations the specified application can redirect to during authentication
        :param app: 
        :param id: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/redirect_uri?app={}&id={}".format(self._url_encode(app), self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_redirect__uri(**local_vars))
        
    def get_recipients(self) -> dict:
        """
        Retrieves a list of recipients attached to the project.
        
        Recipients can be used to have notifications sent to them through the notification services. Any service can queue a message to be sent to a recipient.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/recipient", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_recipients(**local_vars))
        
    def create_recipient(self, type, name, contact) -> dict:
        """
        Creates a new recipient for the selected project
        
        Recipients can be used to have notifications sent to them through the notification services. Any service can queue a message to be sent to a recipient.
        :param type:
        :param name:
        :param contact:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/recipient", 
            headers=headers,
            json={
                "contact": contact,
                "name": name,
                "type": type
            }
        )
        
        return self._check_status(r, lambda: self.create_recipient(**local_vars))
        
    def update_recipient(self, id, type, name, contact) -> dict:
        """
        Updates an existing recipient for the selected project
        
        Recipients can be used to have notifications sent to them through the notification services. Any service can queue a message to be sent to a recipient.
        :param id: 
        :param type:
        :param name:
        :param contact:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/recipient?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "contact": contact,
                "name": name,
                "type": type
            }
        )
        
        return self._check_status(r, lambda: self.update_recipient(**local_vars))
        
    def delete_recipient(self, id) -> dict:
        """
        Deletes the specified recipient for the selected project
        
        Recipients can be used to have notifications sent to them through the notification services. Any service can queue a message to be sent to a recipient.
        :param id: The ID of the recipient to delete
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/project/recipient?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.delete_recipient(**local_vars))
        