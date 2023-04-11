import typing


async def dummy_list(
    quantity: int,
    with_name: bool = False,
    name: typing.Optional[str] = None,
):
    placeholder = name if with_name else 'sample_dummy'
    return {
        'dummies': [
            {'id': i, 'name': f'{placeholder}_{i}'} for i in range(quantity)
        ],
    }
