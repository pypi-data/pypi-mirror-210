import requests


class apiip:
    url = 'http://apiip.net/api/check'
    ssl_url = 'https://apiip.net/api/check'
    api_key = ''
    options = {}

    def __init__(self, api_key, options={}):
        self.api_key = api_key
        self.options = options
        if ('ssl' in options and options['ssl']):
            self.api_url = self.ssl_url
        else:
            self.api_url = self.url

    def get_location(self, query={}):
        query['accessKey'] = self.api_key

        response = requests.get(self.api_url, params=query)

        if response.status_code == 200:
            if ('output' in query and query['output'] == 'xml'):
                data = response.text
            else:
                data = response.json()
        else:
            data = response.json()

        return data
