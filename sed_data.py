import argparse
import os
import sys
import json
import csv
from datetime import datetime

import sed_api

data_choices = ['escolas', 'unidades', 'classes', 'alunos', 'aluno', 'matriculas']

parser = argparse.ArgumentParser(description='Extrai dados do SED.')

parser.add_argument("--data", "-d", choices=data_choices, required=True, help="Tipo de dado a ser extraído")

parser.add_argument("--cookie-sed", help="Cookie 'SED' para o domínio 'sed.educacao.sp.gov.br' autenticado em sua conta do SED. Alternativamente, utilize a variável de ambiente 'SED_DATA_COOKIE_SED'")
parser.add_argument("--format", "-f", choices=["json", "csv"], default="json", help="Formato dos dados extraídos")

parser.add_argument('--escola-id', help="Usado para unidades, classes, alunos")
parser.add_argument('--ano-letivo', default=str(datetime.now().year), help=f"Usado para classes, alunos (padrão: ano atual)")
parser.add_argument('--unidade-id', help="Usado para classes")
parser.add_argument('--classe-id', help="Usado para alunos")
parser.add_argument('--aluno-id', help="Usado para aluno, matriculas")

args = parser.parse_args()

auth = {
	'cookie_SED': args.cookie_sed if args.cookie_sed != None
		else os.environ['SED_DATA_COOKIE_SED'] if 'SED_DATA_COOKIE_SED' in os.environ
		else None
}

if auth['cookie_SED'] == None:
	print('Error: Needs --cookie-sed or SED_DATA_COOKIE_SED env var')
	exit(1)

result = None

match args.data:
	case 'escolas':
		result = sed_api.get_escolas(auth)
	case 'unidades':
		if args.escola_id == None:
			parser.error("Error: --data unidades needs --escola-id")
		result = sed_api.get_unidades(auth, args.escola_id)
	case 'classes':
		if args.escola_id == None or args.unidade_id == None:
			parser.error("Error: --data classes needs --escola-id and --unidade-id")
		result = sed_api.get_classes(auth, args.ano_letivo, args.escola_id, args.unidade_id)
	case 'alunos':
		if args.escola_id == None or args.classe_id == None:
			parser.error("Error: --data alunos needs --escola-id and --classe-id")
		result = sed_api.get_alunos(auth, args.ano_letivo, args.escola_id, args.classe_id)
	case 'aluno':
		if args.aluno_id == None:
			parser.error("Error: --data aluno needs --aluno-id")
		result = sed_api.get_aluno(auth, args.aluno_id)
	case 'matriculas':
		if args.aluno_id == None:
			parser.error("Error: --data matriculas needs --aluno-id")
		result = sed_api.get_matriculas(auth, args.aluno_id)

match args.format:
	case 'json':
		def json_encode(obj):
			if isinstance(obj, datetime):
				return obj.isoformat()
			raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')

		print(json.dumps(result, indent='\t', default=json_encode))
	case 'csv':
		if not isinstance(result, list):
			result = [result]

		writer = csv.DictWriter(sys.stdout, fieldnames=result[0].keys(), delimiter=";")
		writer.writeheader()
		writer.writerows(result)