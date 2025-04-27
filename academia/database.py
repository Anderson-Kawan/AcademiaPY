import pymysql
from dotenv import load_dotenv
import os
from serialization import desserializar_e_formatar_exercicios
import traceback
import logging
from datetime import datetime, date

DB_CONFIG = {
    "host": "host",
    "database": "database",
    "user": "user",
    "password": "senha",
    "cursorclass": pymysql.cursors.DictCursor
}

def buscar_aluno_nome_ou_matricula(busca):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Normalizar a busca - remover espaços extras e padronizar case
        busca = ' '.join(busca.strip().split()).lower()
        
        # Busca por matrícula
        if busca.isdigit():
            query = """
            SELECT id, nome, sobrenome, status 
            FROM alunos 
            WHERE id LIKE %s AND status = 0
            ORDER BY nome
            """
            cursor.execute(query, (f"%{busca}%",))
        else:
            # Primeiro tenta busca exata (case insensitive e ignorando espaços extras)
            query = """
            SELECT id, nome, sobrenome, status 
            FROM alunos 
            WHERE LOWER(CONCAT(TRIM(nome), ' ', TRIM(sobrenome))) = %s 
            AND status = 0
            ORDER BY nome
            """
            cursor.execute(query, (busca,))
            resultados = cursor.fetchall()
            
            # Se não encontrou exato, faz busca aproximada
            if not resultados:
                partes = busca.split()
                
                # Construir condições para cada parte do nome
                conditions = []
                params = []
                for parte in partes:
                    conditions.append("(LOWER(nome) LIKE %s OR LOWER(sobrenome) LIKE %s)")
                    params.extend([f"%{parte}%", f"%{parte}%"])
                
                # Query que exige TODAS as partes estejam presentes
                query = f"""
                SELECT id, nome, sobrenome, status 
                FROM alunos 
                WHERE status = 0 AND {' AND '.join(conditions)}
                ORDER BY 
                    CASE 
                        WHEN LOWER(CONCAT(nome, ' ', sobrenome)) LIKE %s THEN 0
                        ELSE 1
                    END,
                    nome
                """
                params.append(f"%{busca}%")
                cursor.execute(query, params)

        resultados = cursor.fetchall()

        if not resultados:
            return "Nenhum aluno encontrado ou o aluno está inativo."

        return resultados
    except Exception as e:
        logging.error(f"Erro ao buscar alunos: {e}")
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
                a.sobrenome AS aluno_sobrenome,
                a.id AS aluno_matricula,
                a.dataUltimaAvaliacaoFisica AS ultima_avaliacao,
                at.dataValidade AS data_validade,
                i.nome AS professor_nome,
                i.sobrenome AS professor_sobrenome,
                at.status AS status,
                at.nome AS treino_nome,
                ati.nome AS tipo_treino,
                at.instrucoes AS instrucoes,
                ati.exercicios AS exercicios,  -- Dados serializados dos exercícios
                ati.qtdExecutada AS qtd_executada,
                ati.qtd AS qtd_total
            FROM alunos AS a
            INNER JOIN alunos_treinos at ON a.id = at.idAluno
            INNER JOIN alunos_treinos_itens ati ON at.id = ati.idTreino
            LEFT JOIN instrutores i ON a.idProfessor = i.id
            WHERE a.id = %s AND at.dataValidade > NOW()
            ORDER BY a.id, at.nome;
        """
        cursor.execute(query, (codigo,))
        resultados = cursor.fetchall()

        if not resultados:
            return "Nenhuma ficha ativa encontrada para o aluno."

        # Desserializar os exercícios e buscar detalhes na tabela `exercicios`
        for resultado in resultados:
            if resultado.get('exercicios'):
                exercicios_desserializados = desserializar_e_formatar_exercicios(resultado['exercicios'])
                exercicios_detalhados = []

                for exercicio in exercicios_desserializados:
                    if isinstance(exercicio, dict) and 'ID' in exercicio:
                        id_exercicio = exercicio['ID']
                        # Buscar detalhes do exercício na tabela `exercicios`
                        cursor.execute("SELECT * FROM exercicios WHERE id = %s", (id_exercicio,))
                        detalhes_exercicio = cursor.fetchone()

                        if detalhes_exercicio:
                            exercicio['nome_exercicio'] = detalhes_exercicio['nome']
                            exercicio['equipamentos'] = detalhes_exercicio['equipamentos']
                            exercicios_detalhados.append(exercicio)

                resultado['exercicios'] = exercicios_detalhados
        return resultados  # Retorna a primeira ficha encontrada
    except Exception as e:
        erro_detalhado = traceback.format_exc()
        logging.error(f"Erro ao buscar ficha: {e}\n{erro_detalhado}")
        return f"Erro ao buscar ficha: {e}\n{erro_detalhado}"
    finally:
        if conn:
            conn.close()