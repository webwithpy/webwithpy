from requests_toolbelt.multipart import decoder


class BaseHTTPRequestParser:
    def __init__(self, raw_request: str):
        self.method, self.path, self.query_params, self.form_data = self._parse_request(
            raw_request
        )

        raw_request = raw_request.replace("\r", "")

        self.raw_headers = self._get_raw_headers(raw_request)
        self.cookies = self._parse_cookies(self.raw_headers["Cookie"])

    def _parse_request(self, raw_request):
        header, body = self._extract_header_and_body(raw_request)
        method, path, query_params = self._parse_header(header)
        form_data = self._parse_body(header, body)
        form_data = self._remove_quotes_from_keys(form_data)

        return method, path, query_params, form_data

    @staticmethod
    def _remove_quotes_from_keys(input_dict):
        return {key.replace('"', ''): value for key, value in input_dict.items()}

    @staticmethod
    def _extract_header_and_body(raw_request):
        return raw_request.split("\r\n\r\n", 1)

    @staticmethod
    def _parse_header(header):
        method, path, header = header.split(" ", 2)
        path_parts = path.split("?")
        path = path_parts[0]
        query_params = {}

        if len(path_parts) > 1:
            query_params = dict(param.split("=") for param in path_parts[1].split("&"))

        return method, path, query_params

    @staticmethod
    def _get_raw_headers(request: str):
        # we use [:1] here to remove http type from the header as it is not needed
        header = request.split("\n")[1:]
        headers = {}
        for line in header:
            if not line:
                break

            key, val = line.split(":", 1)
            headers[key] = val.strip()

        return headers

    @staticmethod
    def _parse_body(header, body):
        raise NotImplementedError("Subclasses must implement parse_body method")

    @classmethod
    def _parse_cookies(cls, cookies_as_str: str) -> dict:
        if len(cookies_as_str) == 0:
            return {}

        cookies_dict = {}

        for cookie in cookies_as_str.split(";"):
            k, v = cookie.split("=")
            cookies_dict[k] = v.replace("\r", "")

        return cookies_dict


class MultipartHTTPRequestParser(BaseHTTPRequestParser):
    @staticmethod
    def _parse_body(header, body):
        content_type = None
        for line in header.split("\n"):
            if line.startswith("Content-Type:"):
                content_type = line.split(": ")[1]

        if content_type and "multipart/form-data" in content_type:
            multipart_decoder = decoder.MultipartDecoder(body.encode(), content_type)
            form_data = {}
            for part in multipart_decoder.parts:
                if part.headers.get(b"Content-Disposition"):
                    content_disposition = part.headers[b"Content-Disposition"].decode()
                    disposition_params = {}
                    for kv in content_disposition.split("; "):
                        kv_split = kv.split("=")
                        if len(kv_split) == 1:
                            disposition_params[kv_split[0]] = None
                        else:
                            disposition_params[kv_split[0]] = kv_split[1].strip()

                    if "name" in disposition_params:
                        form_data[disposition_params["name"]] = part.content.decode()
            return form_data
        else:
            return {}


class FormURLEncodedHTTPRequestParser(BaseHTTPRequestParser):
    @staticmethod
    def _parse_body(header, body):
        content_type = None
        for line in header.split("\n"):
            if line.startswith("Content-Type:"):
                content_type = line.split(": ")[1]

        if content_type and "application/x-www-form-urlencoded" in content_type:
            form_data = {}
            for param in body.split("&"):
                key, value = param.split("=")
                form_data[key] = value
            return form_data
        else:
            return {}
