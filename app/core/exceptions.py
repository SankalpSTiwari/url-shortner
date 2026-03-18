class URLNotFoundError(Exception):
    def __init__(self, short_code: str):
        self.short_code = short_code
        super().__init__(f"Short URL not found: {short_code}")


class URLExpiredError(Exception):
    def __init__(self, short_code: str):
        self.short_code = short_code
        super().__init__(f"Short URL has expired: {short_code}")


class AliasConflictError(Exception):
    def __init__(self, alias: str):
        self.alias = alias
        super().__init__(f"Custom alias already in use: {alias}")
