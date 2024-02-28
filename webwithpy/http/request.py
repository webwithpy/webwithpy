from urllib.parse import unquote


class Request:
    """
    given request from asyncio socket -> http/https
    currently only tested under https
    """

    def __init__(self, req_header: str):
        req_header_as_dict = self._headers_to_dict(req_header)
        self.path, self.vars = self._parse_path(
            req_header_as_dict.get("path", "GET / HTTP/1.1")
        )
        # ALL FORM DATA IS ONLY ACCEPTED VIA <form method="POST">!!
        self.form_data: dict = req_header_as_dict.get("form_data", {})

        # Type of the connection send to the user
        self.connection_type = req_header_as_dict.get("Connection", "?!")

        # how much content is send
        self.content_length = req_header_as_dict.get("Content-Length", "/")

        # where the content came from
        self.origin = req_header_as_dict.get("Origin", None)

        # cookies and path
        self.method = self._parse_method(req_header_as_dict.get("path", "ANY"))
        self.cookies = self._parse_cookies(req_header_as_dict.get("Cookie", ""))

    @classmethod
    def _headers_to_dict(cls, full_header: str) -> dict:
        """
        makes so that a given header is turned into a dictionary
        """
        split_full_header = full_header.split("\n")
        header_dict = {}
        for header in split_full_header:
            split_header = header.split(": ", 2)

            # if the len of the split_header is 1(aka it is not split it must be the path or form_data
            if len(split_header) == 1:
                if "GET" in split_header[0] or "POST" in split_header[0]:
                    header_dict["path"] = split_header[0]
                elif "=" in split_header[0]:
                    header_dict["form_data"] = cls._extract_vars_from_path(
                        split_header[0]
                    )
                continue

            # this is an empty line
            elif len(split_header) < 1:
                continue

            # turn this into a dict
            header_dict[split_header[0]] = split_header[1]

        return header_dict

    @classmethod
    def _parse_method(cls, path_header: str):
        """
        I know PUT also exists however it is not supported(at least not before 1.0)
        :param path_header: example 'GET / HTTP/1.1'
        :return: 'GET' or 'POST'
        """
        return "GET" if "GET" in path_header else "POST"

    @classmethod
    def _extract_vars_from_path(cls, variable_side_path: str) -> dict:
        """
        variable side path is everything after the ? in 127.0.0.1:8000/test?var1=1
        aka variable side path is in this case 'var1=1'
        """
        # separates all variables from variable side path
        # result: var1=1,var2=1 -> ['var1=1', 'var2=2']
        split_vars = variable_side_path.strip().split("&")
        # return the variables as a dictionary
        return {
            k: unquote(v) for k, v in [split_var.split("=") for split_var in split_vars]
        }

    @classmethod
    def _parse_path(cls, path_header: str):
        """
        :param path_header: example 'GET / HTTP/1.1'
        :return: url true path
        """
        path_split = path_header.split(" ")[1].split("?")

        if len(path_split) == 1:
            return path_split[0], {}

        return [path_split[0], cls._vars_to_dict(path_split[1])]

    @classmethod
    def _parse_host(cls, host_header: str):
        """
        get where url of the client
        """
        return host_header.split(" ")[1]

    @classmethod
    def _HTTP_type(cls, path_header: str) -> str:
        # type of the http used
        return path_header.split(" ")[1]

    @classmethod
    def _parse_cookies(cls, cookies_as_str: str) -> dict:
        if len(cookies_as_str) == 0:
            return {}

        cookies_dict = {}

        for cookie in cookies_as_str.split(";"):
            k, v = cookie.split("=")
            cookies_dict[k] = v.replace("\r", "")

        return cookies_dict

    @classmethod
    def _vars_to_dict(cls, kwargs: str) -> dict:
        """
        turns http variables to dict
        """
        if len(kwargs) == 0:
            return {}

        # vars dict
        var_dict = {}
        items = kwargs.split("&")
        for item in items:
            # key, value
            k, v = item.split("=")
            var_dict[k] = v

        return var_dict
