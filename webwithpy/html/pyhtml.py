from typing import Type


class HtmlTag:
    @classmethod
    def set_dict_attrs(cls, kwargs):
        return " ".join([f'{k.replace("_", "")}="{v}"' for k, v in kwargs.items()])

    @classmethod
    def set_tag(cls, text, field):
        return text if field else ""

    def __repr__(self):
        return self.__str__()


class Form(HtmlTag):
    def __init__(
        self,
        _accept_charset: str = "",
        _action: str = "",
        _autocomplete: str = "",
        _enctype: str = "",
        _method: str = "",
        _name: str = "",
        _novalidate: str = "",
        _rel: str = "",
        _target: str = "",
        *tags: str | HtmlTag,
    ):
        self.attributes = {
            "accept_charset": _accept_charset,
            "action": _action,
            "autocomplete": _autocomplete,
            "enctype": _enctype,
            "method": _method,
            "name": _name,
            "novalidate": _novalidate,
            "rel": _rel,
            "target": _target,
        }

        for attribute, value in self.attributes.items():
            self.attributes[attribute] = self.set_tag(f"{attribute}={value}", value)

        self.tags = tags

    def __str__(self):
        return f"<form {' '.join([attr for attr in self.attributes])}>{''.join(self.tags.__str__())}</form>"


class Label(HtmlTag):
    def __init__(self, _for: str = "", _form: str = "", *tags: str | HtmlTag):
        self._for = self.set_tag(f"for='{_for}'", _for)
        self._form = self.set_tag(f"form={_form}", _form)
        self.tags = tags

    def __str__(self):
        return (
            f"<label {self._for} {self._form}> {''.join(self.tags.__str__())} </label>"
        )


class Input(HtmlTag):
    def __init__(
        self,
        _name: str = "",
        _type: str = "",
        _class: str = "",
        **attrs: str,
    ):
        self._name = self.set_tag(f"name='{_name}'", _name)
        self._type = self.set_tag(f"type='{_type}'", _type)
        self._class = self.set_tag(f"class='{_class}'", _class)
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<input {self._name} {self._type} {self._class} {self.attrs}/>"


class Span(HtmlTag):
    def __init__(self, *tags: str | HtmlTag, **attrs: str):
        self.tags = tags
        self.attrs = attrs

    def __str__(self):
        return f"<span {self.set_dict_attrs(self.attrs)}>{''.join([tag for tag in self.tags])}</span>"


class Div(HtmlTag):
    def __init__(self, *tags: str | HtmlTag, **attrs: str):
        self.tags = tags
        self.attrs = attrs

    def __str__(self):
        return f"<div {self.set_dict_attrs(self.attrs)}>{''.join(self.tags)}</div>"


class H3(HtmlTag):
    def __init__(self, text: str = "", **attrs):
        self.text = text
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<h3 {self.attrs}>{''.join(self.text)}</h3>"


class H4(HtmlTag):
    def __init__(self, text: str = "", **attrs):
        self.text = text
        self.attrs = self.set_dict_attrs(attrs)

    def __str__(self):
        return f"<h4 {self.attrs}>{''.join(self.text)}</h4>"


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
