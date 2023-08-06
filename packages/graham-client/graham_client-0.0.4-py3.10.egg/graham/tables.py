import requests

class Tables:
    def __init__(self, rate_limiter, api_key, company_id, table_id):
        if table_id == None or table_id == '':
            return None, {
                'status_code': 400,
                'error_message': 'Table ID is required'
            }
        self.rate_limiter = rate_limiter
        self.table_id = table_id
        self.api_key = api_key
        self.company_id = company_id
        self.timeout = 15
    
    def _get_timeout(self):
        return self.timeout
    
    def _get_headers(self):
        return {
            'Authorization': 'Bearer ' + self.api_key,
            'Company': self.company_id,
            'Content-Type': 'application/json'
        }

    def Read(self, query={}, limit = None, selectedColumns = None):
        with self.rate_limiter:
            url = 'https://api.withgraham.io/v1/tables/' + str(self.table_id) + '/data/read'
            payload = {
                "query": query,
            }
            if limit != None:
                payload['limit'] = limit
            if selectedColumns != None:
                payload['selectedColumns'] = selectedColumns
            
            r = requests.post(url, headers=self._get_headers(), json=payload, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to read from table'
                }
            return r.json()['results'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }
    
    def Write(self, data = {}):
        with self.rate_limiter:
            url = 'https://api.withgraham.io/v1/tables/' + str(self.table_id) + '/data'
            payload = {
                "data": data,
            }
            
            r = requests.post(url, headers=self._get_headers(), json=payload, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to write to table'
                }
            return r.json()['results'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }

    def Delete(self, query = {}):
        with self.rate_limiter:
            url = 'https://api.withgraham.io/v1/tables/' + str(self.table_id) + '/data'
            payload = {
                "query": query,
            }
            
            r = requests.delete(url, headers=self._get_headers(), json=payload, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to delete from table'
                }
            return r.json()['results'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }
    
    def DeleteAll(self):
        with self.rate_limiter:
            url = 'https://api.withgraham.io/v1/tables/' + str(self.table_id) + '/data/all'

            r = requests.delete(url, headers=self._get_headers(), json={}, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to delete from table'
                }
            return r.json()['results'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }

    def Update(self, query = {}, data = {}):
        with self.rate_limiter:
            url = 'https://api.withgraham.io/v1/tables/' + str(self.table_id) + '/data'
            payload = {
                "data": data,
                "query": query,
            }
            
            r = requests.patch(url, headers=self._get_headers(), json=payload, timeout=self._get_timeout())
            if r.status_code != 200:
                return None, {
                    'status_code': r.status_code,
                    'text': r.text,
                    'error_message': 'failed to update table'
                }
            return r.json()['results'], None
        return None, {
            'status_code': 429,
            'error_message': 'rate limit exceeded'
        }

