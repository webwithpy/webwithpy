class HtmlData:
    # list of requests with their function
    # for example if some loads their function with @GET(path='/') then we will store it here.
    req_paths: [] = []

    @classmethod
    def search_req_paths(cls, url, method):
        for rp in cls.req_paths:
            if rp["url"] == url and rp["request_type"] == method:
                return rp

        return False
