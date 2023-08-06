import re
from typing import Union

def walk(target: Union[dict, list, str], path: str):
    path = re.sub('\[(?:"([^"]+)"|\'([^\']+)\'|([^\]]+))\]', '.\\1\\2\\3', path)
    segments = path.split('.')

    current_target = target

    for segment in segments:
        if segment.isnumeric():
            index = int(segment)
            if isinstance(current_target, list) or isinstance(current_target, str):
                if len(current_target) > index:
                    current_target = current_target[index]
                    continue
                else:
                    return None
            else:
                return None

        if isinstance(current_target, dict):
            if segment in current_target:
                current_target = current_target[segment]
                continue
            else:
                return None

        if isinstance(current_target, object):
            if hasattr(current_target, segment):
                current_target = getattr(current_target, segment)
                continue
            else:
                return None

        return None

    return current_target
