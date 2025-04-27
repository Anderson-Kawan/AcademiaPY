import pymysql
from dotenv import load_dotenv
import os
from serialization import desserializar_e_formatar_exercicios  # Importação adicionada
import traceback
import logging
from datetime import datetime, date


DB_CONFIG = {
    "host": "187.84.232.163",
    "database": "academia_plataforma_producao",
    "user": "academia_root",
    "password": "a@pp3965",
    "cursorclass": pymysql.cursors.DictCursor
}

def buscar_aluno_nome_ou_matricula(busca):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
        SELECT id, nome, sobrenome, status 
        FROM alunos 
        WHERE (nome LIKE %s OR id LIKE %s) AND status = 0
        ORDER BY nome
        """
        cursor.execute(query, (f"%{busca}%", f"%{busca}%"))
        resultados = cursor.fetchall()

        if not resultados:
            return "Nenhum aluno encontrado ou o aluno está inativo."

        return resultados
    except Exception as e:
        logging.error(f"Erro ao buscar alunos: {e}")  # Registrar o erro no arquivo de log
        return f"Erro ao buscar alunos: {e}"
    finally:
        if conn:
            conn.close()
import pymysql
from dotenv import load_dotenv
import os
from serialization import desserializar_e_formatar_exercicios  # Importação adicionada
import traceback
import logging
from datetime import datetime, date  # Importação correta


DB_CONFIG = {
    "host": "187.84.232.163",
    "database": "academia_plataforma_producao",
    "user": "academia_root",
    "password": "a@pp3965",
    "cursorclass": pymysql.cursors.DictCursor
}

def buscar_aluno_nome_ou_matricula(busca):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
        SELECT id, nome, sobrenome, status 
        FROM alunos 
        WHERE (nome LIKE %s OR id LIKE %s) AND status = 0
        ORDER BY nome
        """
        cursor.execute(query, (f"%{busca}%", f"%{busca}%"))
        resultados = cursor.fetchall()

        if not resultados:
            return "Nenhum aluno encontrado ou o aluno está inativo."

        return resultados
    except Exception as e:
        logging.error(f"Erro ao buscar alunos: {e}")  # Registrar o erro no arquivo de log
        return f"Erro ao buscar alunos: {e}"
    finally:
        if conn:
            conn.close()
def buscar_ficha(codigo):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Verifica se o aluno está ativo
        cursor.execute("SELECT status FROM alunos WHERE id = %s", (codigo,))
        aluno_status = cursor.fetchone()

        if not aluno_status:
            return "Aluno não encontrado."
        if aluno_status['status'] == 1:
            return "Aluno inativo."
        
        query = """
            SELECT 
                a.nome AS aluno_nome,
                a.id AS aluno_matricula,
                u.nome AS professor_nome,
                u.id AS professor_matricula,
                at.status AS status,
                at.nome AS treino_nome,
                at.instrucoes AS instrucoes,
                at.ultimoRealizadoData AS ultima_avaliacao,
                ati.exercicios AS exercicios_serializados
            FROM alunos AS a
            INNER JOIN alunos_treinos at ON a.id = at.idAluno
            LEFT JOIN usuarios u ON at.idProfessor = u.id
            INNER JOIN alunos_treinos_itens ati ON at.id = ati.idTreino
            WHERE a.id = %s AND at.status = 1
            ORDER BY a.id, at.nome;
        """
        cursor.execute(query, (codigo,))
        resultados = cursor.fetchall()

        if not resultados:
            return "Nenhuma ficha ativa encontrada para o aluno."

        fichas = []
        for resultado in resultados:
            status = resultado["status"]
            aluno_nome = resultado["aluno_nome"]
            aluno_matricula = resultado["aluno_matricula"]
            professor_nome = resultado.get("professor_nome", "Nao informado")
            professor_matricula = resultado.get("professor_matricula", "Nao informado")
            treino_nome = resultado["treino_nome"]
            ultima_avaliacao = resultado["ultima_avaliacao"] if resultado["ultima_avaliacao"] else "Nao Realizada"
            instrucoes = resultado["instrucoes"]
            exercicios_serializados = resultado["exercicios_serializados"]

            # Desserializar os exercícios
            if not exercicios_serializados or not exercicios_serializados.startswith('a:'):
                return f"Erro: Dados de exercícios ausentes ou inválidos para o aluno {aluno_nome}."

            exercicios = desserializar_e_formatar_exercicios(exercicios_serializados)

            if isinstance(exercicios, str) and exercicios.startswith("Erro"):
                return exercicios

            ficha = (
                f"------------------------------------------\n"
                f"ACADEMIA BE HAPPY\n"
                f"------------------------------------------\n\n"
                f"\n"
                f"ALUNO:        {aluno_nome.title()}\n"
                f"CÓDIGO:       {aluno_matricula}\n"
                f"PROFESSOR:    {(professor_nome or '').title()}\n"
                f"TREINO:       {treino_nome}\n"
                f"DATA:         {datetime.now().strftime("%d/%m/%Y")}\n"
                f"\n"
            )

            for exercicio in exercicios:
                exercicio_id = exercicio['ID']
                if exercicio_id != 'Não especificado':
                    detalhes = get_exercicio_details(cursor, int(exercicio_id))
                    if detalhes:
                        exercicio['detalhes'] = {
                            'nome': detalhes['nome'],
                            'instrucoes': detalhes['instrucoes']
                        }
                    else:
                        exercicio['detalhes'] = {'nome': 'Não encontrado', 'instrucoes': 'N/A'}

                if exercicio.get('detalhes', {}).get('nome') != 'Não encontrado':
                    ficha += (
                        f"------------------------------------------\n"
                        f"EXERCÍCIOS:\n"
                        f"------------------------------------------\n"
                        f"{exercicio.get('detalhes', {}).get('nome', 'N/A')}\n"
                        f"------------------------------------------\n"
                        f"{exercicio.get('detalhes', {}).get('nome', 'N/A')} - {exercicio.get('detalhes', {}).get('instrucoes', 'N/A')}\n"
                        f"{exercicio['Séries']}\n"
                        f"{exercicio['Quantidade']}\n"
                        f"{exercicio['Carga']}\n"
                        f"{exercicio['Observação']}\n"
                        f"------------------------------------------\n"
                    )

            fichas.append({"nome_treino": treino_nome, "conteudo": ficha})

        return fichas
    except Exception as e:
        erro_detalhado = traceback.format_exc()
        logging.error(f"Erro ao buscar ficha: {e}\n{erro_detalhado}")
        return f"Erro ao buscar ficha: {e}\n{erro_detalhado}"
    finally:
        if conn:
            conn.close()

def get_exercicio_details(cursor, exercicio_id):
    query_exercicio = """
        SELECT
            id, nome, instrucoes
        FROM exercicios
        WHERE id = %s
    """
    cursor.execute(query_exercicio, (exercicio_id,))
    return cursor.fetchone()