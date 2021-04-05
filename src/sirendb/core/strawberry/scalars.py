import strawberry


class LimitedString(str):
    pass


LimitedStringScalar = strawberry.scalar(
    LimitedString,
    serialize=lambda v: v,
)
