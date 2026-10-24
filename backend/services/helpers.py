from datetime import date


def obrigatorios(dados, campos):
    ausentes = [campo for campo in campos if dados.get(campo) in (None, "")]
    if ausentes:
        raise ValueError("Campos obrigatórios: " + ", ".join(ausentes))


def inteiro_positivo(valor, nome):
    try:
        convertido = int(valor)
    except (TypeError, ValueError) as erro:
        raise ValueError(f"{nome} deve ser um número inteiro.") from erro
    if convertido <= 0:
        raise ValueError(f"{nome} deve ser maior que zero.")
    return convertido


def data_iso(valor, nome):
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError) as erro:
        raise ValueError(f"{nome} deve usar o formato AAAA-MM-DD.") from erro
