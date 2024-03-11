class Uri:
    """
    Example of an uri can be sqlite:/test.db
    """

    @classmethod
    def get_db_name(cls, uri: str) -> str:
        """
        Return the name of the database before the ':' in an uri.
        """
        return uri.split(":")[0]

    @classmethod
    def get_db_path(cls, uri: str):
        return uri.split(":")[1]
