import requests
from urllib.parse import urlencode

class Financials:
    def __init__(self, rate_limiter, api_key, company_id, return_raw=False):
        self.rate_limiter = rate_limiter
        self.api_key = api_key
        self.company_id = company_id
        self.return_raw = return_raw
        self.timeout = 15
    
    def _get_timeout(self):
        return self.timeout
    
    def _get_headers(self):
        return {
            'Authorization': 'Bearer ' + self.api_key,
            'Company': self.company_id,
            'Content-Type': 'application/json'
        }

    def ListSummaries(self, equity_id='', query={}):
        with self.rate_limiter:
            query_str = urlencode(query)
            url = 'https://api.withgraham.io/v1/equities/' + str(equity_id) + '/financials'
            if query_str != '':
                url += '?' + query_str
            
            r = requests.get(url, headers=self._get_headers(), json=None, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to get financials for equity'
                }
            
            if self.return_raw:
                return r.json(), None
            return r.json()['financials'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }
    
    def ListSECForms(self, equity_id='', query={}):
        with self.rate_limiter:
            query_str = urlencode(query)
            url = 'https://api.withgraham.io/v1/equities/' + str(equity_id) + '/financials/sec-forms'
            if query_str != '':
                url += '?' + query_str
            
            r = requests.get(url, headers=self._get_headers(), json=None, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to get SEC forms for equity'
                }
            
            if self.return_raw:
                return r.json(), None
            return r.json()['forms'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }
    

class Equities:
    def __init__(self, rate_limiter, api_key, company_id, return_raw=False):
        self.rate_limiter = rate_limiter
        self.api_key = api_key
        self.company_id = company_id
        self.return_raw = return_raw
        self.timeout = 15
    
    def _get_timeout(self):
        return self.timeout
    
    def _get_headers(self):
        return {
            'Authorization': 'Bearer ' + self.api_key,
            'Company': self.company_id,
            'Content-Type': 'application/json'
        }
    
    def List(self, query={}):
        with self.rate_limiter:
            query_str = urlencode(query)
            url = 'https://api.withgraham.io/v1/equities'
            if query_str != '':
                url += '?' + query_str
            
            r = requests.get(url, headers=self._get_headers(), json=None, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to list equities'
                }
            
            if self.return_raw:
                return r.json(), None
            return r.json()['equities'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }
    
    def Get(self, equity_id='', query={}):
        with self.rate_limiter:
            query_str = urlencode(query)
            url = 'https://api.withgraham.io/v1/equities/' + str(equity_id)
            if query_str != '':
                url += '?' + query_str
            
            r = requests.get(url, headers=self._get_headers(), json=None, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to get equity'
                }
            
            if self.return_raw:
                return r.json(), None
            return r.json()['equity'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }
    
    def Daily(self, equity_id='', query={}):
        with self.rate_limiter:
            query_str = urlencode(query)
            url = 'https://api.withgraham.io/v1/equities/' + str(equity_id) + '/daily'
            if query_str != '':
                url += '?' + query_str
            
            r = requests.get(url, headers=self._get_headers(), json=None, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to get daily snapshot for equity'
                }
            
            if self.return_raw:
                return r.json(), None
            return r.json()['dailySnapshots'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }
    
    def Financials(self, equity_id='', query={}):
        return Financials(self.rate_limiter, self.api_key, self.company_id, self.return_raw)
    
    def Dividends(self, equity_id='', query={}):
        with self.rate_limiter:
            query_str = urlencode(query)
            url = 'https://api.withgraham.io/v1/equities/' + str(equity_id) + '/dividends'
            if query_str != '':
                url += '?' + query_str
            
            r = requests.get(url, headers=self._get_headers(), json=None, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to get equity'
                }
            
            if self.return_raw:
                return r.json(), None
            return r.json()['dividends'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }
    