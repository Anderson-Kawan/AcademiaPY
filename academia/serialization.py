import phpserialize
import logging

def desserializar_equipamentos(equipamentos_serializados):
    """
    Desserializa uma string de equipamentos serializada em PHP.

    Parâmetros:
        equipamentos_serializados (str): String serializada em PHP.

    Retorna:
        str: String formatada com os equipamentos.
    """
    if isinstance(equipamentos_serializados, str) and equipamentos_serializados.startswith('a:'):
        try:
            equipamentos_desserializados = phpserialize.loads(equipamentos_serializados.encode('utf-8'), decode_strings=True)
            if isinstance(equipamentos_desserializados, dict):
                return ", ".join(map(str, equipamentos_desserializados.values()))
        except Exception as e:
            logging.error(f"Erro ao desserializar equipamentos: {e}")
            return "Erro na desserialização"
    return equipamentos_serializados

def desserializar_e_formatar_exercicios(dados_serializados):
    """
    Desserializa e formata os exercícios serializados em PHP.

    Parâmetros:
        dados_serializados (str, bytes, list ou dict): Dados serializados em PHP ou já desserializados.

    Retorna:
        list: Lista de exercícios formatados.
    """
    try:
        if not dados_serializados:
            logging.warning("Nenhum dado serializado fornecido.")
            return []

        # Se os dados já estiverem desserializados (lista ou dicionário), retorne diretamente
        if isinstance(dados_serializados, (list, dict)):
            logging.info("Dados já desserializados.")
            return dados_serializados

        # Se for bytes, decodifique para string
        if isinstance(dados_serializados, bytes):
            dados_serializados = dados_serializados.decode('utf-8')

        # Verifique se os dados são uma string serializada em PHP
        if isinstance(dados_serializados, str) and dados_serializados.startswith('a:'):
            try:
                dados_desserializados = phpserialize.loads(dados_serializados.encode('utf-8'), decode_strings=True)
            except Exception as e:
                logging.error(f"Erro ao desserializar os dados: {e}")
                return []
        else:
            logging.error(f"Dados serializados inválidos: {dados_serializados}")
            return []

        exercicios_formatados = []

        # Processar os dados desserializados
        if isinstance(dados_desserializados, dict):
            for _, grupo in dados_desserializados.items():
                if not isinstance(grupo, dict):
                    continue

                grupo_nome = grupo.get("grupo", "Grupo não identificado")
                exercicios = grupo.get("exercicios", {})

                if not isinstance(exercicios, dict):
                    continue

                for _, exercicio in exercicios.items():
                    if not isinstance(exercicio, dict):
                        continue

                    # Extrair os equipamentos corretamente
                    equipamentos_serializados = exercicio.get("equipamentos", "")
                    equipamentos = "Não especificado"

                    if isinstance(equipamentos_serializados, str) and equipamentos_serializados.startswith('a:'):
                        try:
                            equipamentos_desserializados = phpserialize.loads(equipamentos_serializados.encode('utf-8'), decode_strings=True)
                            if isinstance(equipamentos_desserializados, dict):
                                equipamentos = ", ".join(map(str, equipamentos_desserializados.values()))
                        except Exception as e:
                            logging.error(f"Erro ao desserializar equipamentos: {e}")
                            equipamentos = "Erro na desserialização"

                    elif isinstance(equipamentos_serializados, list):
                        equipamentos = ", ".join(map(str, equipamentos_serializados))
                    elif isinstance(equipamentos_serializados, str):
                        equipamentos = equipamentos_serializados

                    exercicio_formatado = {
                        "Grupo": grupo_nome,
                        "nome_exercicio": exercicio.get("exercicios", "Não especificado"),
                        "ID": exercicio.get("id", "Não especificado"),
                        "Séries": exercicio.get("series", "Não especificado"),
                        "Quantidade": exercicio.get("qtd", "Não especificado"),
                        "Carga": exercicio.get("carga", "Não especificado"),
                        "Observação": exercicio.get("obs", "Não especificado"),
                        "Método": exercicio.get("metodo", "Não especificado"),
                        "equipamentos": equipamentos,  # Usar equipamentos extraídos
                    }

                    # Verifica se os campos obrigatórios estão presentes
                    if not exercicio_formatado["ID"] or not exercicio_formatado["nome_exercicio"]:
                        logging.warning(f"Exercício incompleto: {exercicio_formatado}")
                        continue  # Ignora exercícios incompletos

                    exercicios_formatados.append(exercicio_formatado)
        else:
            logging.error(f"Formato de dados desserializados inválido: {type(dados_desserializados)}")
            return []

        return exercicios_formatados
    except Exception as e:
        logging.error(f"Erro ao desserializar os exercícios: {e}")
        return []
