from wwp_data.html_data import HtmlData


def generate_req_data_from_input(func, req_type: str, **kwargs) -> dict:
    combined_dict = {"func": func, "request_type": req_type}
    combined_dict.update(kwargs)

    return combined_dict


def GET(url='/'):
    def wrapper(func):
        HtmlData.req_paths.append(generate_req_data_from_input(func, "GET", url=url))

    return wrapper


def POST(url='/'):
    def wrapper(func):
        HtmlData.req_paths.append(generate_req_data_from_input(func, "POST", url=url))

    return wrapper


def ANY(url='/'):
    def wrapper(func):
        HtmlData.req_paths.append(generate_req_data_from_input(func, "GET", url=url))
        HtmlData.req_paths.append(generate_req_data_from_input(func, "POST", url=url))

    return wrapper