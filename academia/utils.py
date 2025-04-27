import re

def limpar_texto(texto):
    # Mantém letras, números, espaços, quebras de linha, acentos e símbolos comuns
    # Adicionamos todos os caracteres especiais necessários para fichas de treino
    padrao = r'[^\w\sáéíóúâêîôûãõçÁÉÍÓÚÂÊÎÔÛÃÕÇñÑäëïöüÄËÏÖÜàèìòùÀÈÌÒÙýÝ\-\_\/\.,:;!?@#\$%&\*\(\)\[\]\{\}\+=\|\'"\n]'
    texto_limpo = re.sub(padrao, '', texto)
    
    # Corrige problemas comuns de formatação
    texto_limpo = re.sub(r'\r\n', '\n', texto_limpo)  # Padroniza quebras de linha
    texto_limpo = re.sub(r' +', ' ', texto_limpo)     # Remove múltiplos espaços
    texto_limpo = re.sub(r'\n ', '\n', texto_limpo)   # Remove espaços no início de linhas
    
    return texto_limpo.strip()