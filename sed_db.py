import psycopg
from psycopg import sql
from psycopg.rows import dict_row
import os
from datetime import datetime

import sed_api

auth = {
	"cookie_SED": os.environ["SED_DATA_COOKIE_SED"] if "SED_DATA_COOKIE_SED" in os.environ
		else None
}

postgres_url = os.environ["SED_DATA_POSTGRES_URL"]

ano_atual = datetime.now().year

def db_set_escolas(cur, escolas):
	cur.executemany("""
		INSERT INTO escolas (
			sed_id,
			nome
		) VALUES (
			%(id)s,
			%(nome)s
		)
			ON CONFLICT (sed_id) DO UPDATE SET
			sed_id = EXCLUDED.sed_id,
			nome = EXCLUDED.nome
	""", escolas)

def db_set_unidades(cur, escola_id, unidades):
	cur.executemany(sql.SQL("""
		INSERT INTO unidades (
			escola_sed_id,
			sed_id,
			nome
		) VALUES (
			{},
			%(id)s,
			%(nome)s
		)
		ON CONFLICT (sed_id) DO UPDATE SET
			escola_sed_id = EXCLUDED.escola_sed_id,
			sed_id = EXCLUDED.sed_id,
			nome = EXCLUDED.nome
	""").format(escola_id), unidades)

def db_set_classes(cur, escola_id, unidade_id, classes):
	cur.executemany(sql.SQL("""
		INSERT INTO classes (
			escola_sed_id,
			unidade_sed_id,
			sed_id,
			sed_id_b,
			descrição
		) VALUES (
			{},
			{},
			%(id)s,
			%(id_b)s,
			%(descrição)s
		) ON CONFLICT (sed_id) DO UPDATE SET
			escola_sed_id = EXCLUDED.escola_sed_id,
			unidade_sed_id = EXCLUDED.unidade_sed_id,
			sed_id = EXCLUDED.sed_id,
			sed_id_b = EXCLUDED.sed_id_b,
			descrição = EXCLUDED.descrição
	""").format(escola_id, unidade_id), classes)

def db_set_alunos(cur, alunos):
	cur.executemany("""
		INSERT INTO alunos (
			sed_id,
			nome,
			ra,
			ra_dígito,
			nascimento_data
		) VALUES (
			%(id)s,
			%(nome)s,
			%(ra)s,
			%(ra_dígito)s,
			%(nascimento_data)s
		) ON CONFLICT (sed_id) DO UPDATE SET
			sed_id = EXCLUDED.sed_id,
			nome = EXCLUDED.nome,
			ra = EXCLUDED.ra,
			ra_dígito = EXCLUDED.ra_dígito,
			nascimento_data = EXCLUDED.nascimento_data
	""", alunos)

def db_set_aluno(cur, aluno_id, aluno):
	cur.execute(sql.SQL("""
		INSERT INTO alunos (
			sed_id,
			nome,
			ra,
			ra_dígito,
			nascimento_data,
			sexo,
			raça_cor,
			nome_mãe,
			nome_pai,
			bolsa_família,
			nascimento_cidade,
			nascimento_uf,
			certidão_data,
			certidão_número,
			endereço_cep,
			endereço,
			endereço_número,
			endereço_complemento,
			endereço_bairro,
			endereço_cidade,
			endereço_uf,
			endereço_latitude,
			endereço_longitude
		) VALUES (
			{},
			%(nome)s,
			%(ra)s,
			%(ra_dígito)s,
			%(nascimento_data)s,
			%(sexo)s,
			%(raça_cor)s,
			%(nome_mãe)s,
			%(nome_pai)s,
			%(bolsa_família)s,
			%(nascimento_cidade)s,
			%(nascimento_uf)s,
			%(certidão_data)s,
			%(certidão_número)s,
			%(endereço_cep)s,
			%(endereço)s,
			%(endereço_número)s,
			%(endereço_complemento)s,
			%(endereço_bairro)s,
			%(endereço_cidade)s,
			%(endereço_uf)s,
			%(endereço_latitude)s,
			%(endereço_longitude)s
		) ON CONFLICT (sed_id) DO UPDATE SET
			sed_id = EXCLUDED.sed_id,
			nome = EXCLUDED.nome,
			ra = EXCLUDED.ra,
			ra_dígito = EXCLUDED.ra_dígito,
			nascimento_data = EXCLUDED.nascimento_data,
			sexo = EXCLUDED.sexo,
			raça_cor = EXCLUDED.raça_cor,
			nome_mãe = EXCLUDED.nome_mãe,
			nome_pai = EXCLUDED.nome_pai,
			bolsa_família = EXCLUDED.bolsa_família,
			nascimento_cidade = EXCLUDED.nascimento_cidade,
			nascimento_uf = EXCLUDED.nascimento_uf,
			certidão_data = EXCLUDED.certidão_data,
			certidão_número = EXCLUDED.certidão_número,
			endereço_cep = EXCLUDED.endereço_cep,
			endereço = EXCLUDED.endereço,
			endereço_número = EXCLUDED.endereço_número,
			endereço_complemento = EXCLUDED.endereço_complemento,
			endereço_bairro = EXCLUDED.endereço_bairro,
			endereço_cidade = EXCLUDED.endereço_cidade,
			endereço_uf = EXCLUDED.endereço_uf,
			endereço_latitude = EXCLUDED.endereço_latitude,
			endereço_longitude = EXCLUDED.endereço_longitude
	""").format(aluno_id), aluno)

def db_set_matrículas(cur, aluno_id, matrículas):
	cur.executemany(sql.SQL("""
		INSERT INTO matrículas (
			sed_id,
			diretoria,
			rede,
			município,
			escola_id,
			escola_nome,
			classe_id,
			tipo,
			habilidade,
			turma,
			série,
			turno,
			aluno_id,
			número,
			data_início,
			data_fim,
			situação
		) VALUES (
			%(id)s,
			%(diretoria)s,
			%(rede)s,
			%(município)s,
			%(escola_id)s,
			%(escola_nome)s,
			%(classe_id)s,
			%(tipo)s,
			%(habilidade)s,
			%(turma)s,
			%(série)s,
			%(turno)s,
			{},
			%(número)s,
			%(data_início)s,
			%(data_fim)s,
			%(situação)s
		) ON CONFLICT (sed_id) DO UPDATE SET
			sed_id = EXCLUDED.sed_id,
			diretoria = EXCLUDED.diretoria,
			rede = EXCLUDED.rede,
			município = EXCLUDED.município,
			escola_id = EXCLUDED.escola_id,
			escola_nome = EXCLUDED.escola_nome,
			classe_id = EXCLUDED.classe_id,
			tipo = EXCLUDED.tipo,
			habilidade = EXCLUDED.habilidade,
			turma = EXCLUDED.turma,
			série = EXCLUDED.série,
			turno = EXCLUDED.turno,
			aluno_id = EXCLUDED.aluno_id,
			número = EXCLUDED.número,
			data_início = EXCLUDED.data_início,
			data_fim = EXCLUDED.data_fim,
			situação = EXCLUDED.situação
	""").format(aluno_id), matrículas)

def db_set_escolas_from_matrículas():
	pass

def db_set_classes_from_matrículas():
	pass

def db_get_alunos_por_classe(cur):
	cur.execute("""
		SELECT * FROM alunos_por_classe
	""")
	return cur.fetchall()

def update_classes_only(escola_id, unidade_id, ano_letivo=ano_atual):
	with psycopg.connect(postgres_url, autocommit=True) as conn:
		with conn.cursor() as cur:
			print("sed_api.get_classes", escola_id, unidade_id)
			classes = sed_api.get_classes(auth, ano_letivo, escola_id, unidade_id)
			print("db_set_classes", escola_id, unidade_id, classes)
			db_set_classes(cur, escola_id, unidade_id, classes)

def update_alunos_only(escola_id, classe_id, ano_letivo=ano_atual):
	with psycopg.connect(postgres_url, autocommit=True) as conn:
		with conn.cursor() as cur:
			print("sed_api.get_alunos", escola_id, classe_id)
			alunos_classe = sed_api.get_alunos(auth, ano_letivo, escola_id, classe_id)
			print("db_set_alunos", alunos_classe)
			db_set_alunos(cur, alunos_classe)

def get_alunos_por_classe():
	with psycopg.connect(postgres_url, autocommit=True, row_factory=dict_row) as conn:
		with conn.cursor() as cur:
			return db_get_alunos_por_classe(cur)

def update_all(ano_letivo=ano_atual):
	print("update_all")
	
	with psycopg.connect(postgres_url, autocommit=True) as conn:
		with conn.cursor() as cur:
			print("sed_api.get_escolas")
			escolas = sed_api.get_escolas(auth)
			print("db_set_escolas", escolas)
			db_set_escolas(cur, escolas)

			for escola in escolas:
				print("sed_api.get_unidades", escola['id'])
				unidades = sed_api.get_unidades(auth, escola['id'])
				print("db_set_unidades", escola['id'], unidades)
				db_set_unidades(cur, escola['id'], unidades)

				for unidade in unidades:
					print("sed_api.get_classes", escola['id'], unidade['id'])
					classes = sed_api.get_classes(auth, ano_letivo, escola['id'], unidade['id'])
					print("db_set_classes", escola['id'], unidade['id'], classes)
					db_set_classes(cur, escola['id'], unidade['id'], classes)

					for classe in classes:
						print("sed_api.get_alunos", escola['id'], classe['id'])
						alunos_classe = sed_api.get_alunos(auth, ano_letivo, escola['id'], classe['id'])
						print("db_set_alunos", alunos_classe)
						db_set_alunos(cur, alunos_classe)

						for aluno_classe in alunos_classe:
							print(repr(aluno_classe['id']))

							print("sed_api.get_aluno", aluno_classe['id'])
							aluno = sed_api.get_aluno(auth, aluno_classe['id'])
							print("db_set_aluno", aluno_classe['id'], aluno)
							db_set_aluno(cur, aluno_classe['id'], aluno)

							print("sed_api.get_matriculas", aluno_classe['id'])
							matrículas = sed_api.get_matriculas(auth, aluno_classe['id'])
							print("db_set_matrículas", aluno_classe['id'], matrículas)
							db_set_matrículas(cur, aluno_classe['id'], matrículas)

if __name__ == "__main__":
	update_all()