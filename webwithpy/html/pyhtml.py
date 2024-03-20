import base64
from typing import Any


class HtmlTag:
    @classmethod
    def set_dict_attrs(cls, kwargs):
        return " ".join([f'{k.replace("_", "")}="{v}"' for k, v in kwargs.items()])

    @classmethod
    def set_tag(cls, text, field):
        return text if field else ""

    def __repr__(self):
        return self.__str__()


class TextField(HtmlTag):
    def __init__(self, **attrs: Any):
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<textarea {self.attrs}> </textarea>"


class Form(HtmlTag):
    def __init__(self, *tags: str | HtmlTag, **attrs):
        self.attrs = self.set_dict_attrs(attrs)
        self.tags = tags

    def __str__(self):
        return (
            f"<form enctype=multipart/form-data {self.attrs}>{''.join([tag.__str__() for tag in self.tags])}</form>"
        )


class Label(HtmlTag):
    def __init__(self, *tags: str | HtmlTag, **attrs):
        self.attrs = self.set_dict_attrs(attrs)
        self.tags = tags

    def __str__(self):
        return f"<label {self.attrs}> {''.join(self.tags.__str__())} </label>"


class Input(HtmlTag):
    def __init__(
            self,
            **attrs: Any,
    ):
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<input {self.attrs}/>"


class Span(HtmlTag):
    def __init__(self, *tags: str | HtmlTag, **attrs: str):
        self.tags = tags
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<span {self.attrs}>{''.join([tag for tag in self.tags])}</span>"


class Div(HtmlTag):
    def __init__(self, *tags: str | HtmlTag, _class: str = "", **attrs: str):
        self._class = _class
        self.tags = tags
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return (
            f"<div class={self._class} {self.attrs}>"
            f" {''.join([tag.__str__() for tag in self.tags])}</div>"
        )


class Img(HtmlTag):
    def __init__(self, image_bytes: bytes, image_type: str, **attrs: str):
        encoded_image_data = base64.b64encode(image_bytes)
        str_encoded_image_data = encoded_image_data.decode('utf-8')
        src = f'data:image/{image_type};base64,{str_encoded_image_data}'
        attrs.update({'src': src})
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<img {self.attrs} />"


class H1(HtmlTag):
    def __init__(self, text: str = "", **attrs):
        self.text = text
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<h1 {self.attrs}>{''.join(self.text)}</h1>"


class H2(HtmlTag):
    def __init__(self, text: str = "", **attrs):
        self.text = text
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<h2 {self.attrs}>{''.join(self.text)}</h2>"


class H3(HtmlTag):
    def __init__(self, text: str = "", **attrs):
        self.text = text
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<h3 {self.attrs}>{''.join(self.text)}</h3>"


class H4(HtmlTag):
    def __init__(self, _class: str = "", text: str = "", **attrs):
        self._class = _class
        self.text = text
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<h4 class={self._class} {self.attrs}>{''.join(self.text)}</h4>"


class A(HtmlTag):
    """
    Html <a> </a> tag in python
    """

    def __init__(
            self,
            *tags: str | HtmlTag,
            _class: str = "",
            _href: str = "",
            **attrs: str,
    ):
        self._class = self.set_tag(f"class='{_class}'", _class)
        self._href = self.set_tag(f'href="{_href}"', _href)
        self.tags = tags
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<a {self._class} {self._href} {self.attrs}> {''.join([tag.__str__() for tag in self.tags])} </a>"


class P(HtmlTag):
    """
    Html <p> </p> tag in python
    """

    def __init__(
            self,
            text: str = "",
            _class: str = "",
            _href: str = "",
            **attrs: str,
    ):
        self.text = text
        self._class = self.set_tag(f"class='{_class}'", _class)
        self._href = self.set_tag(f'href="{_href}"', _href)
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<a {self._class} {self._href} {self.attrs}> {self.text} </a>"
