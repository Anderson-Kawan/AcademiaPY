import phpserialize

#Módulo serialization.py

#Responsável por desserializar dados de exercícios no formato PHP serializado.

def desserializar_e_formatar_exercicios(dados_serializados):
    try:
        if isinstance(dados_serializados, bytes):
            dados_serializados = dados_serializados.decode('utf-8')

        if not dados_serializados.startswith('a:'):
            raise ValueError("Dados serializados não têm o formato esperado.")

        dados_desserializados = phpserialize.loads(dados_serializados.encode('utf-8'), decode_strings=True)
        #Desserializa e formata os dados de exercícios.

        exercicios_formatados = []

        for _, grupo in dados_desserializados.items():
            grupo_nome = grupo.get("grupo", "Grupo não identificado")
            exercicios = grupo.get("exercicios", {})

            for _, exercicio in exercicios.items():
                exercicios_formatados.append({
                    "Grupo": grupo_nome,
                    "Exercicios": exercicio.get("exercicios", "Não especificado"),
                    "ID": exercicio.get("id", "Não especificado"),
                    "Séries": exercicio.get("series", "Não especificado"),
                    "Quantidade": exercicio.get("qtd", "Não especificado"),
                    "Carga": exercicio.get("carga", "Não especificado"),
                    "Observação": exercicio.get("obs", "Não especificado"),
                })
            #Parâmetros:
                #dados_serializados (bytes ou str): Dados serializados no formato PHP.
        return exercicios_formatados
        #Retorna:
            #list: Lista de exercícios formatados ou uma mensagem de erro.
    except Exception as e:
        return f"Erro ao desserializar os exercícios: {e}"