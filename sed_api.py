import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import dataclass
import re

@dataclass
class SEDContext:
	session: requests.Session
	request_verification_token: str = ''
	authorization: str = ''

def start_context(auth):
	session = requests.Session()
	session.cookies.set('SED', auth['cookie_SED'])

	# request_verification_token
	response = session.get('https://sed.educacao.sp.gov.br/NCA/Matricula/ConsultaMatricula/Index')

	soup = BeautifulSoup(response.text, 'html.parser')
	request_verification_token = soup.find('input', attrs={'name': '__RequestVerificationToken'})['value']

	# authorization
	response = session.get("https://sed.educacao.sp.gov.br/NCA/FichaAluno/Consulta")

	match = re.search(r'Execute\.Init\("(.*?)"', response.text)
	authorization = match.group(1)

	return SEDContext(session=session, request_verification_token=request_verification_token, authorization=authorization)

def get_cookies(auth):
	return {
		'SED': auth['cookie_SED'],
	}

def get_escolas(context):
	response = context.session.get('https://sed.educacao.sp.gov.br/nca/Matricula/ConsultaMatricula/DropDownEscolasCIEJson')

	json = response.json()

	escolas = []
	for item in json:
		escolas.append({
			'id': item['Value'],
			'nome': item['Text'],
		})

	return escolas

def get_unidades(context, escola_id):
	response = context.session.get('https://sed.educacao.sp.gov.br/nca/Matricula/ConsultaMatricula/DropDownUnidadesJson',
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

def get_classes(context, ano_letivo, escola_id, unidade_id):
	response = context.session.post('https://sed.educacao.sp.gov.br/NCA/matricula/ConsultaMatricula/Pesquisar',
		data={
			'__RequestVerificationToken': context.request_verification_token,
			'anoLetivo': ano_letivo,
			'codigoEscolaCIE': escola_id,
			'codigoUnidadeCIE': unidade_id,
			'tipoConsulta': 2,
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

def get_alunos(context, ano_letivo, escola_id, classe_id):
	response = context.session.post('https://sed.educacao.sp.gov.br/NCA/Matricula/ConsultaMatricula/Visualizar',
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
		a = tr.select('td > a[onclick^="movimentacaoMatricula"]')[0] # ^= is starts with
		onclick = a['onclick']

		alunos.append({
			# movimentacaoMatricula(aluno_id, ano_letivo, classe_id, matricula_id)
			'id': str(onclick.split('(')[1].split(',')[0]),
			'nome': str(tr.findAll('td')[3].string.strip()),
			'ra': str(tr.findAll('td')[4].string),
			'ra_dígito': str(tr.findAll('td')[5].string),
			'nascimento_data': datetime.strptime(str(tr.findAll('td')[7].string), "%d/%m/%Y"),
		})

	return alunos

def get_aluno(context, aluno_id):
	response = context.session.post('https://sed.educacao.sp.gov.br/NCA/FichaAluno/FichaAluno',
		data={
			'codigoAluno': aluno_id,
		})

	soup = BeautifulSoup(response.text, 'html.parser')

	def achar_value(id):
		e = soup.find(id=id)
		return str(e['value']) if e else None

	def achar_checkbox(id):
		return True if soup.find(id=id, checked=True) else False

	def achar_data(id):
		v = soup.find(id=id)['value']
		return datetime.strptime(str(v[:10]), "%d/%m/%Y") if v != '' else None

	aluno = {
		'nome': achar_value("NomeAluno"),
		'nome_social': achar_value("NomeSocial"),
		'nome_afetivo': achar_value("NomeAfetivo"),
		'ra': achar_value("nrRA"),
		'ra_dígito': achar_value("nrDigRa"),
		'nascimento_data': achar_data("DtNascimento"),
		'sexo': achar_value("Sexo"),
		'raça_cor': achar_value("DescricaoRacaCor"),
		'tipo_sanguíneo': achar_value("TipoSanguineo"),
		'falecimento': achar_checkbox("Falecimento"),
		'email': achar_value("Email"),
		'email_google': achar_value("EmailGoogle"),
		'email_microsoft': achar_value("EmailMicrosoft"),
		'nome_mãe': achar_value("NomeMae"),
		'nome_pai': achar_value("NomePai"),
		'bolsa_família': achar_checkbox("BolsaFamilia"),
		'identificação_única_educacenso': achar_value("idAlunoMec"),
		'nacionalidade': achar_value("CodigoNacionalidade"),
		'nascimento_cidade': achar_value("CidadeNascimento"),
		'nascimento_uf': achar_value("UFNascimento"),
		'nascimento_país': achar_value("CodigoPaisNascimento"),
		'quilombola': achar_checkbox("Quilombo"),
		'possui_internet': achar_checkbox("INTERNETSIM"),
		'possui_computador': achar_checkbox("SmartPessoalSIM"),
		'cpf': achar_value("CpfAluno"),
		'rg': achar_value("RgAluno"),
		'rg_dígito': achar_value("DigRgAluno"),
		'rg_uf': achar_value("sgUfRg"),
		'rg_data': achar_data("dtEmisRg"),
		'cin_data': achar_data("DataEmissaoCarteiraIdentidadeNacional"),
		'rg_militar': achar_value("RgMilitarAluno"),
		'rg_militar_dígito': achar_value("DigRgMilitarAluno"),
		'nis': achar_value("NIS"),
		'sus': achar_value("NumeroCNS"),
		'entrada_no_brasil_data': achar_data("dtEntradaBrasil"),
		'certidão_data': achar_data("dtEmisRegNasc"),
		'certidão_número': achar_value("NumeroCertidaoNova"),
		'deficiente': achar_checkbox("Deficiente"),
		'endereço_cep': achar_value("EnderecoCEP"),
		'endereço_tipo': achar_value("TipoLogradouro"),
		'endereço_diferenciado': achar_value("LocalizacaoDiferenciada"),
		'endereço': achar_value("Endereco"),
		'endereço_número': achar_value("EnderecoNR"),
		'endereço_complemento': achar_value("EnderecoComplemento"),
		'endereço_bairro': achar_value("EnderecoBairro"),
		'endereço_cidade': achar_value("EnderecoCidade"),
		'endereço_uf': achar_value("EnderecoUF"),
		'endereço_latitude': achar_value("Latitude"),
		'endereço_longitude': achar_value("Longitude"),
	}

	return aluno

def get_matriculas(context, aluno_id):
	response = context.session.post('https://sed.educacao.sp.gov.br/NCA/FichaAluno/ConsultarMatriculaFichaAluno',
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

def get_transporte_indicação(context, aluno_id):
	response = context.session.post('https://sed.educacao.sp.gov.br/geo/fichaaluno/indicacao/listar',
		headers = {
			'Authorization': context.authorization,
		},
		data={
			'codigo': aluno_id,
			'editar': 'true',
			'__RequestVerificationToken': context.request_verification_token,
		})

	with open('debug.html', 'w') as f: f.write(response.text)

	json = response.json()

	return json['data'][0]['StatusTransporte'] if len(json['data']) != 0 else None

def get_all_matriculas(context, ano_letivo, callback=None):
	result_escolas = get_escolas(context)
	for escola in result_escolas:
		result_unidades = get_unidades(context, escola['id'])
		for unidade in result_unidades:
			result_classes = get_classes(context, ano_letivo, escola['id'], unidade['id'])
			for classe in result_classes:
				result_alunos = get_alunos(context, ano_letivo, escola['id'], classe['id'])
				for aluno in result_alunos:
					result_aluno = get_aluno(context, aluno['id'])
					result_matriculas = get_matriculas(context, aluno['id'])
					result_transporte_indicação = get_transporte_indicação(context, aluno['id'])

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
							'transporte_indicação': result_transporte_indicação,
						}