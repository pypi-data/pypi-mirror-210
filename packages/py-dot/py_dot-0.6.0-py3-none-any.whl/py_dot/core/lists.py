from typing import List


def safe_insert(target: List, index, value, fill=None):
    size = len(target)

    if size > index:
        target[index] = value
    else:
        while size != index:
            target.append(fill)
            size += 1

        target.insert(index, value)

    return target


def to_wrap_string(
        items: list | tuple,
        starts: str = '',
        ends: str = '',
        separator: str = '',
        first_starts: str = '',
        last_ends: str = ''
) -> str:
    """ Array join with wrapping characters

    :param items       : target array
    :param starts      : item starts with this character
    :param ends        : item ends with this character, using starts when empty
    :param separator   : items join with this character
    :param first_starts: most-left additional character
    :param last_ends   : most-right additional character
    """
    if first_starts + starts + separator + ends + last_ends == '':
        raise ValueError('Required one argument at least')

    if ends == '':
        ends = starts

    return first_starts + starts + (ends + separator + starts).join(items) + ends + last_ends


def from_wrap_string(
        wrapped_string: str,
        starts: str = '',
        ends: str = '',
        separator: str = '',
        first_starts: str = '',
        last_ends: str = ''
) -> list:
    """ String Split with wrapping characters

    :param wrapped_string: target string
    :param starts        : item starts with this character
    :param ends          : item ends with this character, using starts when empty
    :param separator     : items join with this character
    :param first_starts  : most-left additional character
    :param last_ends     : most-right additional character
    """
    if first_starts + starts + separator + ends + last_ends == '':
        raise ValueError('Required one argument at least')

    if not wrapped_string:
        return []

    if ends == '':
        ends = starts

    start_strings = first_starts + starts

    if not wrapped_string.startswith(start_strings):
        pass

    end_strings = ends + last_ends
    if not wrapped_string.endswith(end_strings):
        pass

    return wrapped_string[len(start_strings):-len(end_strings)].split(ends + separator + starts)
