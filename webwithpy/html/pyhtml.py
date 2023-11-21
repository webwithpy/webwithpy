class HtmlTag:
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
        *tags,
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
        return f"<form {' '.join([attr for attr in self.attributes])}>{''.join(self.tags)}</form>"


class Label(HtmlTag):
    def __init__(self, _for: str = "", _form: str = "", *tags):
        self._for = self.set_tag(f"for='{_for}'", _for)
        self._form = self.set_tag(f"form={_form}", _form)
        self.tags = tags

    def __str__(self):
        return f"<label {self._for} {self._form}> {''.join(self.tags)} </label>"


class Input(HtmlTag):
    def __init__(self, _name: str = "", _type: str = "", _required: bool = False):
        self._name = self.set_tag(f"name='{_name}'", _name)
        self._type = self.set_tag(f"type='{_type}'", _type)
        self._required = self.set_tag("required", _required)

    def __str__(self):
        return f"<input name='{self._name}' type='{self._type}' {self._required}/>"
