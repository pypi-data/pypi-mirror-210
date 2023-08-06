class ViewError(Exception):
    code: int
    status: int = 500
    reason_format: str = ''

    @classmethod
    def name(cls) -> str:
        return cls.__name__[:-5]

    def __repr__(self):
        return '<{} code={} reason={!r}>'.format(
            self.__class__.__name__, self.code, self.reason()
        )

    def reason(self):
        return self.reason_format.format(*self.args)

    def error_msg(self):
        return '{:d}: {}'.format(self.code, self.reason())


class ClientError(ViewError):
    code = 4000
    status = 400
    reason_format = 'Unknown client error'


class ClientBadRequestError(ClientError):
    code = 4000
    status = 400
    reason_format = 'Bad request error'


class ClientUnauthorizedError(ViewError):
    code = 4001
    status = 401
    reason_format = 'Unauthorized error'


class ClientForbiddenError(ViewError):
    code = 4003
    status = 403
    reason_format = 'Forbidden error'


class ClientMethodNotAllowedError(ViewError):
    code = 4005
    status = 405
    reason_format = 'Method not allowed error'


class ClientConflictError(ViewError):
    code = 4009
    status = 409
    reason_format = 'Conflict error'


class ServerError(ViewError):
    code = 5000
    status = 500
    reason_format = 'Unknown server error'
