import re
from typing import Union

from jusbrasil_challenge.constants import (
    CNJ_UF_IDENTIFIER,
    CNJ_REGEX_PATTERN,
)


def get_uf_by_cnj(cnj: str) -> Union[str, None]:
    """Get federative unit passing the CNJ as a parameter using\
    CNJ_REGEX_PATTERN and CNJ_UF_IDENTIFIER to identify it."""
    cnj = re.match(CNJ_REGEX_PATTERN, cnj)
    return CNJ_UF_IDENTIFIER(cnj[1]).name if cnj else None
