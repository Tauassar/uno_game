import typing


async def async_iterable_to_list(iterable: typing.AsyncIterable) -> typing.List:
    return [entry async for entry in iterable]
