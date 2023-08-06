import re


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def mask(text):
    if text is None:
        return None
    text = str(text)
    if len(text) < 4:
        return '*' * len(text)
    return text[:2] + '*' * (len(text) - 4) + text[-2:]
