class SQLDialect:
    equals = '='
    and_ = 'AND'
    or_ = 'OR'
    neq = '!='
    lt = '<'
    le = '<='
    gt = '>'
    ge = '>='

    @classmethod
    def sql_str(cls, value):
        return f"'{value}'"
