class Request:
    def __init__(self, req_header: str):
        req_header_as_dict = self.headers_to_dict(req_header)
        self.path = self.parse_path(req_header_as_dict.get("path", '/'))
        self.connection_type = req_header_as_dict.get("Connection", "?!")
        self.content_length = req_header_as_dict.get("Content-Length", '/')
        self.origin = req_header_as_dict.get("Origin", None)
        self.vars = req_header_as_dict.get("vars", {})
        self.method = self.parse_method(req_header_as_dict.get("path", 'ANY'))

    @classmethod
    def headers_to_dict(cls, full_header: str) -> dict:
        split_full_header = full_header.split("\n")
        header_dict = {}
        for header in split_full_header:
            split_header = header.split(': ', 2)
            if len(split_header) == 1:
                if "GET" in split_header[0] or "POST" in split_header[0]:
                    header_dict["path"] = split_header[0]
                elif '=' in split_header[0]:
                    header_dict["vars"] = cls.extract_vars_from_path(split_header[0])
                continue
            elif len(split_header) < 1:
                continue

            header_dict[split_header[0]] = split_header[1]

        return header_dict

    @classmethod
    def parse_method(cls, path_header: str):
        """
        I know PUT also exists however it is not supported(atleast not before 1.0)
        :param path_header: example 'GET / HTTP/1.1'
        :return: 'GET' or 'POST'
        """
        return "GET" if "GET" in path_header else "POST"

    @classmethod
    def extract_vars_from_path(cls, variable_side_path: str) -> dict:
        """
        variable side path is everything after the ? in 127.0.0.1:8000/test?var1=1
        aka variable side path is in this case 'var1=1'
        """
        # separates all variables from variable side path
        # result: var1=1,var2=1 -> ['var1=1', 'var2=2']
        split_vars = variable_side_path.strip().split('&')

        # return the variables as an dictionary
        return {k: v for k, v in [split_var.split('=') for split_var in split_vars]}

    @classmethod
    def parse_path(cls, path_header: str):
        """
        :param path_header: example 'GET / HTTP/1.1'
        :return: url true path
        """
        return path_header.split(" ")[1]

    @classmethod
    def parse_host(cls, host_header: str):
        return host_header.split(" ")[1]

    @classmethod
    def HTTP_type(cls, path_header):
        return path_header.split(" ")[1]