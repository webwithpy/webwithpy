from requests_toolbelt.multipart import decoder


class BaseHTTPRequestParser:
    def __init__(self, raw_request: bytes):
        self.method, self.path, self.query_params, self.form_data = self._parse_request(
            raw_request
        )
        headers, _ = self._extract_header_and_body(raw_request)
        headers: str = headers.decode("utf-8")
        headers = headers.replace("\r", "")

        self.raw_headers: dict[str, str] = self._get_raw_headers(headers)
        self.cookies = self._parse_cookies(self.raw_headers.get("Cookie", ""))

    def _parse_request(self, raw_request: bytes):
        header, body = self._extract_header_and_body(raw_request)
        method, path, query_params = self._parse_header(header)
        form_data = self._parse_body(header, body)
        form_data = self._remove_quotes_from_keys(form_data)

        return method.decode(), path.decode(), query_params, form_data

    @staticmethod
    def _remove_quotes_from_keys(input_dict: str):
        return {key.replace('"', ""): value for key, value in input_dict.items()}

    @staticmethod
    def _extract_header_and_body(raw_request: bytes) -> list[bytes]:
        return raw_request.split(b"\r\n\r\n", 1)

    @staticmethod
    def _parse_header(header: bytes):
        method, path, header = header.split(b" ", 2)
        path_parts: list[bytes] = path.split(b"?")
        path = path_parts[0]
        query_params = {}

        if len(path_parts) > 1:
            for part in path_parts[1].split(b"&"):
                key, value = part.split(b"=")
                query_params[key.decode()] = value.decode()

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
    def _parse_body(header: bytes, body: bytes):
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
    def _parse_body(header: bytes, body: bytes) -> dict[str, str]:
        content_type = None
        for line in header.split(b"\n"):
            if line.startswith(b"Content-Type:"):
                content_type = line.split(b": ")[1]

        if content_type and b"multipart/form-data" in content_type:
            multipart_decoder = decoder.MultipartDecoder(
                body, content_type.decode("utf-8")
            )

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
                        try:
                            form_data[
                                disposition_params["name"]
                            ] = part.content.decode()
                        except UnicodeDecodeError:
                            form_data[disposition_params["name"]] = part.content

            return form_data
        else:
            return {}


class FormURLEncodedHTTPRequestParser(BaseHTTPRequestParser):
    @staticmethod
    def _parse_body(header: bytearray, body: bytearray) -> dict[str, str]:
        content_type = None
        for line in header.split(b"\n"):
            if line.startswith(b"Content-Type:"):
                content_type = line.split(b": ")[1]

        if content_type and b"application/x-www-form-urlencoded" in content_type:
            form_data = {}
            for param in body.split(b"&"):
                key, value = param.split(b"=")
                form_data[key] = value
            return form_data
        else:
            return {}
