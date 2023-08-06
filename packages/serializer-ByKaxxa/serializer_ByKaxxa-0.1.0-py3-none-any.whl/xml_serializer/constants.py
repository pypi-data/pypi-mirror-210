BASE_TYPES = r"str|int|float|bool|NoneType|list|dict"

KEY = fr"key"
VALUE = fr"value"

ELEMENT_P = fr"\s*(\<(?P<{KEY}>{BASE_TYPES})\>(?P<{VALUE}>([^<>]*)|(?R)+)\</({BASE_TYPES})\>)\s*"