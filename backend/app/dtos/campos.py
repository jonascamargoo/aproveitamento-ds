from typing import Annotated

from pydantic import StringConstraints

# Texto obrigatório: remove espaços das pontas e não aceita vazio ("   " é recusado)
TextoObrigatorio = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
