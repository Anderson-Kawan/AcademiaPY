from datetime import datetime
from serialization import desserializar_e_formatar_exercicios, desserializar_equipamentos
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG)

def formatar_ficha(ficha):
    try:
        # Extrair informações do aluno e do treino
        aluno_nome = ficha.get('aluno_nome', 'N/A')
        aluno_sobrenome = ficha.get('aluno_sobrenome', 'N/A')
        aluno_matricula = ficha.get('aluno_matricula', 'N/A')
        professor_nome = ficha.get('professor_nome', 'N/C')
        professor_sobrenome = ficha.get('professor_sobrenome', '')
        treino_nome = ficha.get('treino_nome', 'Treino não identificado')
        tipo_treino = ficha.get('tipo_treino', 'Treino não identificado')
        treino_vezes = ficha.get('qtd_executada', 0) + 1
        treino_vezes_total = ficha.get('qtd_total', 1)
        treino_validade = ficha.get('data_validade', datetime.now().date()).strftime('%d/%m/%Y')
        treino_instrucoes = ficha.get('instrucoes', '')
        ultima_avaliacao = ficha.get('ultima_avaliacao', '0000-00-00')
        if ultima_avaliacao == '0000-00-00':
            ultima_avaliacao = 'Não realizou, fale com seu professor.'

        # Desserializar os exercícios
        exercicios_serializados = ficha.get('exercicios', '')
        exercicios = desserializar_e_formatar_exercicios(exercicios_serializados)

        # Log para depuração
        logging.debug(f"Exercícios desserializados: {exercicios}")

        # Formatar a ficha
        ficha_formatada = (
            f"--------------------------------------------------\n"
            f"ACADEMIA BE HAPPY\n"
            f"--------------------------------------------------\n\n"
            f"ALUNO:        {aluno_nome.title()} {aluno_sobrenome.title()}\n"
            f"CÓDIGO:       {aluno_matricula}\n"
            f"PROFESSOR:    {professor_nome.title()} {professor_sobrenome.title()}\n"
            f"TREINO:       {tipo_treino.title()} ({treino_vezes}/{treino_vezes_total})\n"
            f"DATA:         {datetime.now().strftime('%d/%m/%Y')}\n"
            f"VALIDADE:     {treino_validade}\n"
            f"ÚLT. AVALIAÇÃO:    {ultima_avaliacao}\n\n"
            f"--------------------------------------------------\n"
            f"EXERCÍCIOS:\n"
            f"--------------------------------------------------\n"
        )

        # Adicionar exercícios
        if isinstance(exercicios, list) and len(exercicios) > 0:
            for exercicio in exercicios:
                grupo_nome = exercicio.get("Grupo", "")
                if grupo_nome:
                    ficha_formatada += f"\n{grupo_nome.upper()}\n"
                    ficha_formatada += f"--------------------------------------------------\n"

                exercicio_nome = exercicio.get("nome_exercicio", "Exercício não especificado")
                exercicio_series = exercicio.get("Séries", "Não especificado")
                exercicio_qtd = exercicio.get("Quantidade", "Não especificado")
                exercicio_carga = exercicio.get("Carga", "0").strip()  # Remove espaços em branco
                exercicio_obs = exercicio.get("Observação", "")
                exercicio_equipamentos = exercicio.get("equipamentos", "").strip()  # Remove espaços em branco

                # Desserializar os equipamentos, se necessário
                exercicio_equipamentos = desserializar_equipamentos(exercicio_equipamentos)

                # Formatar a carga - adicionar 'kg' apenas se for um número válido e maior que 0
                try:
                    carga_num = float(exercicio_carga) if exercicio_carga else 0
                    carga_formatada = f"- {int(carga_num)}kg" if carga_num > 0 else ""
                except ValueError:
                    carga_formatada = ""

                # Formatar equipamentos - adicionar parênteses apenas se houver conteúdo
                equipamentos_formatado = f"({exercicio_equipamentos})" if exercicio_equipamentos else ""

                # Formatar a linha do exercício
                ficha_formatada += f"{exercicio_nome.upper()} {equipamentos_formatado}\n"
                
                # Construir a linha de séries/repetições
                linha = ""
                if exercicio_series == '1':
                    linha = f"{exercicio_qtd} reps {carga_formatada}"
                else:
                    linha = f"{exercicio_series} x {exercicio_qtd}{carga_formatada}"
                
                ficha_formatada += linha + "\n"

                if exercicio_obs and exercicio_obs.strip() and exercicio_obs.strip() != "0":
                    ficha_formatada += f"> {exercicio_obs.strip().upper()}\n"
        else:
            ficha_formatada += "Nenhum exercício cadastrado para este treino.\n"

        # Adicionar observações gerais
        ficha_formatada += (
            f"\n--------------------------------------------------\n"
            f"OBSERVAÇÕES GERAIS:\n"
            f"--------------------------------------------------\n"
            f"{treino_instrucoes if treino_instrucoes else ''}\n\n"
            f"        Powered by Tamanduá Fit\n"
        )

        return ficha_formatada

    except Exception as e:
        logging.error(f"Erro ao formatar ficha: {e}")
        return f"Erro ao formatar ficha: {e}"