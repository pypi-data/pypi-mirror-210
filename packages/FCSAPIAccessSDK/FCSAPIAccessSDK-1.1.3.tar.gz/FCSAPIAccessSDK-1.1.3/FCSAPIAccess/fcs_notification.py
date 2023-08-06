"""
WARNING: THIS MODULE IS GENERATED! ALL CHANGES WILL BE DISCARDED
"""

import requests
import urllib.parse


class FangNotificationServices:
    """
    Welcome to the FangCloudServices API!
    
    This API is for information relating to FangNotificationServices, the messaging and notification manager
    
    **NOTE**: messages are cleared 24 hours after being sent. If an application does not pull the message within the 24 hours, then it will never read the message.
    
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
    
    def get_channels(self) -> dict:
        """
        Retrieves a list of existing channels
        
        **Requires Scope**: `notification:view:channel`
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/channel", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_channels(**local_vars))
        
    def create_channel(self, name) -> dict:
        """
        Creates a new channel
        
        **Requires Scope**: `notification:update:channel`
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/channel", 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.create_channel(**local_vars))
        
    def update_channel(self, id, name) -> dict:
        """
        Updates the channel information
        
        **Requires Scope**: `notification:update:channel`
        :param id: 
        :param name:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/channel?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.update_channel(**local_vars))
        
    def remove_channel(self, id) -> dict:
        """
        Deletes a channel and all of its history
        
        **Requires Scope**: `notification:update:channel`
        :param id: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/channel?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_channel(**local_vars))
        
    def get_recipients(self, channel) -> dict:
        """
        Returns all of the recipients which have been added to a channel
        
        **Requires Scope**: `notification:view:channel_recipient`
        :param channel: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/channel_recipient?channel={}".format(self._url_encode(channel)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_recipients(**local_vars))
        
    def add_recipient(self, channel, recipient) -> dict:
        """
        Adds the specified recipient to the specified channel
        
        **Requires Scope**: `notification:update:channel_recipient`
        :param channel: 
        :param recipient:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/channel_recipient?channel={}".format(self._url_encode(channel)), 
            headers=headers,
            json={
                "recipient": recipient
            }
        )
        
        return self._check_status(r, lambda: self.add_recipient(**local_vars))
        
    def remove_recipient(self, channel, recipient) -> dict:
        """
        Removes the specified recipient from the specified channel
        
        **Requires Scope**: `notification:update:channel_recipient`
        :param channel: 
        :param recipient: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/channel_recipient?channel={}&recipient={}".format(self._url_encode(channel), self._url_encode(recipient)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.remove_recipient(**local_vars))
        
    def pull_message(self, channel) -> dict:
        """
        Pulls the queued messages. Note that once a message is pulled, you will not be able to pull it again from this endpoint.
        
        Services authenticated using the same `client_id` and `client_secret` are considered the same application, and so pulling a message from one instance of an app will prevent other apps authenticated with the same credentials from being able to pull that message.
        
        **Requires Scope**: `notification:pull:message`
        :param channel: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/message?channel={}".format(self._url_encode(channel)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.pull_message(**local_vars))
        
    def push_message(self, channel, name, body) -> dict:
        """
        Pushes a new message to the queue. In the JSON you may specify `name`, `body` or `code`. All 3 are optional. This does, however, mean that you can push empty messages.
        
        **Requires Scope**: `notification:push:message`
        :param channel: 
        :param name:
        :param body:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/message?channel={}".format(self._url_encode(channel)), 
            headers=headers,
            json={
                "body": body,
                "name": name
            }
        )
        
        return self._check_status(r, lambda: self.push_message(**local_vars))
        
    def get_history(self, channel) -> dict:
        """
        Pulls the message history of the specified channel.
        
        Messages can only be seen for up to 24 hours.
        
        Note that if the `sender` is `null`, the message was either system generated, or sent through the message sender.
        
        **Requires Scope**: `notification:view:history`
        :param channel: The ID of the channel to pull message history from
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/notification/history?channel={}".format(self._url_encode(channel)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_history(**local_vars))
        