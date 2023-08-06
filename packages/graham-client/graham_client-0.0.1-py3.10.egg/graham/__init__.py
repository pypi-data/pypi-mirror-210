from ratelimiter import RateLimiter

from . import tables, equities

class GrahamClient:
    def __init__(self, api_key, company_id):
        self.rate_limiter = RateLimiter(max_calls=5, period=1)
        self.api_key = api_key
        self.company_id = company_id
    
    def Tables(self, table_id):
        return tables.Tables(self.rate_limiter, self.api_key, self.company_id, table_id)

    def Equities(self):
        return equities.Equities(self.rate_limiter, self.api_key, self.company_id)