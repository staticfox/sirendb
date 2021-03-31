import strawberry


@strawberry.type(
    name='Siren',
    description=(
        'Describes the attributes of an outdoor warning siren.'
    )
)
class Siren:
    '''
    Siren description here
    '''
    name: str = strawberry.field(
        description='The name of the siren'
    )
