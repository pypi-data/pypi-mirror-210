class AllbaroError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class UnauthenticatedError(AllbaroError):
    def __init__(self):
        self.msg = "올바로 시스템 로그인이 필요합니다."


class AlreadyAuthenticationError(AllbaroError):
    def __init__(self):
        self.msg = "올바로 시스템에 이미 로그인 되었습니다."


class AllbaroResponseError(AllbaroError):
    def __init__(self):
        self.msg = "올바로 시스템이 응답하지 않습니다."


class LoginFailedError(AllbaroError):
    def __init__(self):
        self.msg = "올바로 시스템 로그인에 실패했습니다. 아이디와 비밀번호를 확인하세요."


class ParsingError(AllbaroError):
    def __init__(self, target_list):
        self.msg = f"올바로 응답에서 [{', '.join(target_list)}] 정보를 찾을 수 없습니다."
