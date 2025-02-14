BEGIN;

SET CLIENT_ENCODING TO 'UTF8';

DROP VIEW IF EXISTS alunos_por_classe;

DROP TABLE IF EXISTS escolas;
DROP TABLE IF EXISTS unidades;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS alunos;
DROP TABLE IF EXISTS matrículas;

CREATE TABLE escolas (
	id SERIAL PRIMARY KEY,
	sed_id INTEGER UNIQUE,
	nome TEXT
);

CREATE TABLE unidades (
	id SERIAL PRIMARY KEY,
	escola_sed_id INTEGER,
	sed_id INTEGER UNIQUE,
	nome TEXT
);

CREATE TABLE classes (
	id SERIAL PRIMARY KEY,
	escola_sed_id INTEGER,
	unidade_sed_id INTEGER,
	sed_id TEXT UNIQUE,
	sed_id_b TEXT UNIQUE,
	descrição TEXT
);

CREATE TABLE alunos (
	id SERIAL PRIMARY KEY,
	sed_id INTEGER UNIQUE,
	nome TEXT,
	ra TEXT,
	ra_dígito TEXT,
	nascimento_data DATE,
	sexo TEXT,
	raça_cor TEXT,
	nome_mãe TEXT,
	nome_pai TEXT,
	bolsa_família BOOLEAN,
	nascimento_cidade TEXT,
	nascimento_uf TEXT,
	certidão_data DATE,
	certidão_número TEXT,
	endereço_cep TEXT,
	endereço TEXT,
	endereço_número TEXT,
	endereço_complemento TEXT,
	endereço_bairro TEXT,
	endereço_cidade TEXT,
	endereço_uf TEXT,
	endereço_latitude TEXT,
	endereço_longitude TEXT
);

CREATE TABLE matrículas (
	id SERIAL PRIMARY KEY,
	sed_id TEXT UNIQUE,
	diretoria TEXT,
	rede TEXT,
	município TEXT,
	escola_id INTEGER,
	escola_nome TEXT,
	classe_id TEXT,
	tipo TEXT,
	habilidade TEXT,
	turma TEXT,
	série TEXT,
	turno TEXT,
	aluno_id INTEGER,
	número TEXT,
	data_início DATE,
	data_fim DATE,
	situação TEXT
);

CREATE VIEW alunos_por_classe AS (
	SELECT
		matrículas.sed_id,
		matrículas.diretoria,
		matrículas.rede,
		matrículas.município,
		matrículas.escola_id,
		matrículas.escola_nome,
		matrículas.tipo,
		matrículas.habilidade,
		matrículas.classe_id,
		classes.sed_id as classe_id_a,
		matrículas.turma,
		matrículas.turno,
		matrículas.série,
		matrículas.número,
		matrículas.data_início,
		matrículas.data_fim,
		matrículas.situação,
		matrículas.aluno_id,
		alunos.nome,
		alunos.ra,
		alunos.ra_dígito,
		alunos.nascimento_data,
		alunos.sexo,
		alunos.raça_cor,
		alunos.nome_mãe,
		alunos.nome_pai,
		alunos.bolsa_família,
		alunos.nascimento_cidade,
		alunos.nascimento_uf,
		alunos.certidão_data,
		alunos.certidão_número,
		alunos.endereço_cep,
		alunos.endereço,
		alunos.endereço_número,
		alunos.endereço_complemento,
		alunos.endereço_bairro,
		alunos.endereço_cidade,
		alunos.endereço_uf,
		alunos.endereço_latitude,
		alunos.endereço_longitude
	FROM matrículas
	LEFT JOIN alunos ON matrículas.aluno_id = alunos.sed_id
	LEFT JOIN classes ON matrículas.classe_id = classes.sed_id_b
	WHERE
		(matrículas.data_início > date_trunc('year', now()))
		AND
		(matrículas.data_início < (date_trunc('year', now()) + interval '1 year'))
		AND
		(matrículas.escola_id IN (SELECT escolas.sed_id FROM escolas))
  ORDER BY matrículas.escola_id, matrículas.classe_id, cast(matrículas.número AS integer)
);

COMMIT;