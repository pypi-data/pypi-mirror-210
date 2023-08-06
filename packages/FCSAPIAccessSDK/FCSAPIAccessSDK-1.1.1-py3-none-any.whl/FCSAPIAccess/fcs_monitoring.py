"""
WARNING: THIS MODULE IS GENERATED! ALL CHANGES WILL BE DISCARDED
"""

import requests
import urllib.parse


class FangMonitoringServices:
    """
    Welcome to the FangCloudServices API!
    
    This API is for information relating to FangMonitoringServices, the URL monitoring and uptime tracker.
    
    **NOTE**: Changes can take up to 10 minutes to take affect
    
    **NOTE**: History is only kept for 30 days, but if the last state change was more than 30 days ago, it is kept until the next state change
    
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
    
    def get_urls(self) -> dict:
        """
        This endpoint retrieves the URLs you are monitoring
        
        **Requires Scope**: `monitor:view:url`
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/url_monitor/url", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_urls(**local_vars))
        
    def create_url(self, name, url, interval, notification_channel) -> dict:
        """
        Adds a new URL to your list of URLs being monitored
        
        `notification_channel` is the ID of the channel where change notifications will automatically be sent. This is part of Notification services.
        
        **Requires Scope**: `monitor:update:url`
        :param name:
        :param url:
        :param interval:
        :param notification_channel:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/url_monitor/url", 
            headers=headers,
            json={
                "interval": interval,
                "name": name,
                "notification_channel": notification_channel,
                "url": url
            }
        )
        
        return self._check_status(r, lambda: self.create_url(**local_vars))
        
    def update_url(self, id, name, url, interval, notification_channel) -> dict:
        """
        Updates the data related to the specified URL
        
        `notification_channel` is the ID of the channel where change notifications will automatically be sent. This is part of Notification services.
        
        **Requires Scope**: `monitor:update:url`
        :param id: 
        :param name:
        :param url:
        :param interval:
        :param notification_channel:
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        r = requests.request(
            "PUT", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/url_monitor/url?id={}".format(self._url_encode(id)), 
            headers=headers,
            json={
                "interval": interval,
                "name": name,
                "notification_channel": notification_channel,
                "url": url
            }
        )
        
        return self._check_status(r, lambda: self.update_url(**local_vars))
        
    def delete_url(self, id) -> dict:
        """
        Deletes the specified URL and wipes all of its history.
        
        **WARNING**: This **CAN NOT** be undone!
        
        **Requires Scope**: `monitor:update:url`
        :param id: 
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "DELETE", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/url_monitor/url?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.delete_url(**local_vars))
        
    def get_url_history(self, id) -> dict:
        """
        Pulls all the history of either all or one of the monitored endpoints.
        
        Note that the response only contains state changes in chronological order.
        
        It is assumed that each state carries over to the next record. For example, if a state starts at `00:25:26` and the next state begins at `10:25:26`, it is assumed that the URL was in that state for the full 10 hour interval.
        
        **Requires Scope**: `monitor:view:state`
        :param id: Optional URL ID to pull the history of a single tracked URL
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/url_monitor/history?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_url_history(**local_vars))
        