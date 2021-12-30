import strawberry


class LimitedString(str):
    pass


class StringLimitExceeded(Exception):
    pass


LimitedStringScalar = strawberry.scalar(
    LimitedString,
    serialize=lambda v: v,
)
