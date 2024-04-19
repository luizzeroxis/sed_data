import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_cookies(auth):
	return {
		'SED': auth['cookie_SED'],
	}

def get_escolas(auth):
	response = requests.get('https://sed.educacao.sp.gov.br/nca/Matricula/ConsultaMatricula/DropDownEscolasCIEJson',
		cookies=get_cookies(auth),
	)

	json = response.json()

	escolas = []
	for item in json:
		escolas.append({
			'id': item['Value'],
			'nome': item['Text'],
		})

	return escolas

def get_unidades(auth, escola_id):
	response = requests.get('https://sed.educacao.sp.gov.br/nca/Matricula/ConsultaMatricula/DropDownUnidadesJson',
		cookies=get_cookies(auth),
		params=(
			('escola', escola_id),
		))

	json = response.json()

	unidades = []
	for item in json:
		unidades.append({
			'id': item['Value'],
			'nome': item['Text'],
		})

	return unidades

def get_classes(auth, ano_letivo, escola_id, unidade_id):
	response = requests.post('https://sed.educacao.sp.gov.br/NCA/matricula/ConsultaMatricula/Pesquisar',
		cookies=get_cookies(auth),
		data={
			'anoLetivo': ano_letivo,
			'codigoEscola': escola_id,
			'codigoUnidade': unidade_id,
		})

	soup = BeautifulSoup(response.text, 'html.parser')
	trs = soup.tbody.findAll('tr')

	classes = []
	for tr in trs:
		onclick = tr.find('a')['onclick']

		classes.append({
			# VisualizarClasse(<ano_letivo>, <escola_id>, <classe_id>)
			'id': onclick.split('(')[1].split(')')[0].split(', ')[2],
			'id_b': str(tr.find(class_='colnrClasse').string),
			'descrição': str(tr.find(class_='colTurmaDes').string),
		})

	return classes

def get_alunos(auth, ano_letivo, escola_id, classe_id):
	response = requests.post('https://sed.educacao.sp.gov.br/NCA/Matricula/ConsultaMatricula/Visualizar',
		cookies=get_cookies(auth),
		data={
			'anoLetivo': ano_letivo,
			'codigoEscola': escola_id,
			'codigoTurma': classe_id,
			'matricula': 'true',
			'visualizar': 'false',
		})

	soup = BeautifulSoup(response.text, 'html.parser')
	trs = soup.tbody.findAll('tr')

	alunos = []
	for tr in trs:
		onclick = tr.findAll('td')[-3].a['onclick']

		alunos.append({
			# movimentacaoMatricula(aluno_id, ano_letivo, classe_id, matricula_id)
			'id': str(onclick.split('(')[1].split(',')[0]),
			'nome': str(tr.findAll('td')[3].string.strip()),
			'ra': str(tr.findAll('td')[4].string),
			'ra_dígito': str(tr.findAll('td')[5].string),
			'nascimento_data': datetime.strptime(str(tr.findAll('td')[7].string), "%d/%m/%Y"),
		})

	return alunos

def get_aluno(auth, aluno_id):
	response = requests.post('https://sed.educacao.sp.gov.br/NCA/FichaAluno/FichaAluno',
		cookies=get_cookies(auth),
		data={
			'codigoAluno': aluno_id,
		})

	soup = BeautifulSoup(response.text, 'html.parser')

	aluno = {
		'nome': str(soup.find(id="NomeAluno")['value']),
		'ra': str(soup.find(id="nrRA")['value']),
		'ra_dígito': str(soup.find(id="nrDigRa")['value']),
		'nascimento_data': datetime.strptime(str(soup.find(id="DtNascimento")['value'][:10]), "%d/%m/%Y"),
		'sexo': str(soup.find(id="Sexo")['value']),
		'nome_mãe': str(soup.find(id="NomeMae")['value']),
		'nome_pai': str(soup.find(id="NomePai")['value']),
		'bolsa_família': True if soup.find(id="BolsaFamilia", checked=True) else False,
		'nascimento_cidade': str(soup.find(id="CidadeNascimento")['value']),
		'nascimento_uf': str(soup.find(id="UFNascimento")['value']),
		'certidão_data': datetime.strptime(str(soup.find(id="dtEmisRegNasc")['value'][:10]), "%d/%m/%Y") if soup.find(id="dtEmisRegNasc")['value'] != '' else None,
		'certidão_número': str(soup.find(id="NumeroCertidaoNova")['value'] if soup.find(id="NumeroCertidaoNova") else None),
		'endereço_cep': str(soup.find(id="EnderecoCEP")['value']),
		'endereço': str(soup.find(id="Endereco")['value']),
		'endereço_número': str(soup.find(id="EnderecoNR")['value']),
		'endereço_complemento': str(soup.find(id="EnderecoComplemento")['value']),
		'endereço_bairro': str(soup.find(id="EnderecoBairro")['value']),
		'endereço_cidade': str(soup.find(id="EnderecoCidade")['value']),
		'endereço_uf': str(soup.find(id="EnderecoUF")['value']),
		'endereço_latitude': str(soup.find(id="Latitude")['value']),
		'endereço_longitude': str(soup.find(id="Longitude")['value']),
	}

	return aluno

def get_matriculas(auth, aluno_id):
	response = requests.post('https://sed.educacao.sp.gov.br/NCA/FichaAluno/ConsultarMatriculaFichaAluno',
		cookies=get_cookies(auth),
		data={
			'codigoAluno': aluno_id,
			# consultaProgramas: "False",
			# Editar: "false",
		})

	soup = BeautifulSoup(response.text, 'html.parser')

	trs = soup.find(id="tabelaDadosMatricula").tbody.findAll('tr')

	matriculas = []
	for tr in trs:
		tds = tr.findAll('td')

		matriculas.append({
			'id': str(tds[4].string),
			# 'ano': str(tds[0].string),
			'diretoria': str(tds[1].string),
			'município': str(tds[2].string),
			'rede': str(tds[3].string),
			'escola_id': str(tds[5].string),
			'escola_nome': str(tds[6].string),
			'turno': str(tds[7].string),
			'tipo': str(tds[8].string),
			'habilidade': str(tds[9].string),
			'série': str(tds[10].string),
			'turma': str(tds[11].string),
			'data_início': datetime.strptime(str(tds[12].string.strip()[:10]), "%d/%m/%Y"),
			'data_fim': datetime.strptime(str(tds[13].string.strip()[:10]), "%d/%m/%Y"),
			'classe_id': str(tds[14].text.strip()),
			'número': str(tds[15].string) if tds[15].string.isnumeric() else "0",
			'situação': str(tds[16].string),
		})

	return matriculas

def get_all_matriculas(auth, ano_letivo, callback=None):
	result_escolas = get_escolas(auth)
	for escola in result_escolas:
		result_unidades = get_unidades(auth, escola['id'])
		for unidade in result_unidades:
			result_classes = get_classes(auth, ano_letivo, escola['id'], unidade['id'])
			for classe in result_classes:
				result_alunos = get_alunos(auth, ano_letivo, escola['id'], classe['id'])
				for aluno in result_alunos:
					result_aluno = get_aluno(auth, aluno['id'])
					result_matriculas = get_matriculas(auth, aluno['id'])

					for matricula in result_matriculas:
						final_escola = dict(escola)
						final_escola['escola_id'] = final_escola.pop('id')
						final_escola['escola_nome'] = final_escola.pop('nome')

						final_unidade = dict(unidade)
						final_unidade['unidade_id'] = final_unidade.pop('id')
						final_unidade['unidade_nome'] = final_unidade.pop('nome')

						final_classe = dict(classe)
						final_classe['classe_id'] = final_classe.pop('id')
						final_classe['classe_id_b'] = final_classe.pop('id_b')
						final_classe['classe_descrição'] = final_classe.pop('descrição')

						final_aluno = dict(aluno)
						final_aluno['aluno_id'] = final_aluno.pop('id')

						final_matricula = dict(matricula)
						final_matricula['matricula_id'] = final_matricula.pop('id')

						yield {
							**final_escola,
							**final_unidade,
							**final_classe,
							**final_aluno,
							**result_aluno,
							**final_matricula,
						}