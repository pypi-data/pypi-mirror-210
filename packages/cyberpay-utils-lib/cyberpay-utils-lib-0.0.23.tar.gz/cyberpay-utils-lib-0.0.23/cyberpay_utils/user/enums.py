from enum import Enum


class GetCompanyUsersJsonType(Enum):
    DEFAULT = "DEFAULT"
    ONLY_EMAILS = "ONLY_EMAILS"
    WITH_PROFILE = "WITH_PROFILE"
