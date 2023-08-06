"""
WARNING: THIS MODULE IS GENERATED! ALL CHANGES WILL BE DISCARDED
"""

import requests
import urllib.parse


class FangTranslationServices:
    """
    Welcome to the FangTranslationServices API!
    
    This API is for translating files for automated application localization
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
    
    def poll_translation(self, id) -> dict:
        """
        Polls the status of an ongoing translation job.
        
        When a translation is complete, the value of `completed` will change from `null` to the datetime of completion.
        
        See the *Download Translation* section to download the processed file
        
        Translations are removed 24 hours after creation.
        :param id: The ID of the translation job
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/translation?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.poll_translation(**local_vars))
        
    def enqueue_translation(self) -> dict:
        """
        Adds a file to the translation queue to be translated.
        
        Files can only be translated from English at this time.
        
        NOTE: Translations may not be 100% accurate.
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        raise NotImplementedError('The requested endpoint is not ready for use')

    def download_translation(self, id) -> dict:
        """
        Allows the specified translation job to be downloaded after completion.
        
        If this endpoint is called and the job is not yet complete, you will receive an HTTP: 425 response code.
        :param id: The ID of the translation job
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/translation/download?id={}".format(self._url_encode(id)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.download_translation(**local_vars))
        
    def get_languages(self) -> dict:
        """
        Retrieves the list of supported languages
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/translation/languages", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_languages(**local_vars))
        
    def get_formats(self) -> dict:
        """
        Retrieves the list of supported file formats
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "GET", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/translation/formats", 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.get_formats(**local_vars))
        
    def extract_text(self, format) -> dict:
        """
        Converts the provided document to a JSON translation file which is compatable with the translator. The contents of the document are sent as the body of the request.
        
        **Note**: While we do our best to create descriptive keys, to reference the translations, the system is by no means perfect. Key names may be very bulky/bloated and some text may be missed. We strongly advise a manual review of the file before using it anywhere else.
        
        Supported input file formats:
        
        - HTML
            
        
        _More coming soon_
        :param format: The format of the input document
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        headers = self.headers.copy()
        r = requests.request(
            "POST", 
            "https://fangcloudservices.pythonanywhere.com/api/v1/translation/extract?format={}".format(self._url_encode(format)), 
            headers=headers
        )
        
        return self._check_status(r, lambda: self.extract_text(**local_vars))
        
    def generate_library(self, language) -> dict:
        """
        Generates a new file from the provided JSON translation file which can be imported into your project to make translation management easier.
        
        Please refer to the _Library Generator_ page under _Translations_ when logged into your account for information on each library.
        
        Supported languages:
        
        - JavaScript
            
        
        _More coming soon_
        :param language: The language to generate the library for
        """
        local_vars = locals()
        if 'self' in local_vars: del local_vars['self']

        raise NotImplementedError('The requested endpoint is not ready for use')
