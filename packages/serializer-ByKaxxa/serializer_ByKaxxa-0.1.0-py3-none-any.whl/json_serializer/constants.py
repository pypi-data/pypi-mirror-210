JSON_INT = r"[+-]?\d+"
JSON_FLOAT = fr"({JSON_INT}(?:\.\d+)?(?:e{JSON_INT})?)"
JSON_BOOL = r"((True)|(False))\b"
JSON_STR = r"\"((\\\")|[^\"])*\""
JSON_NONE = r"\b(Null)\b"
JSON_COMPLEX = fr"{JSON_FLOAT}{JSON_FLOAT}j"

JSON_LIST_RECURSION = r"\[(?R)?(,(?R))*\]"
JSON_DICT_RECURSION = r"\{((?R):(?R))?(?:,(?R):(?R))*\}"

JSON_VALUE = fr"\s*({JSON_LIST_RECURSION}|{JSON_DICT_RECURSION}|{JSON_STR}|{JSON_FLOAT}|" \
             fr"{JSON_BOOL}|{JSON_INT}|{JSON_NONE}|{JSON_COMPLEX}\s*)"

