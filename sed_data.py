import argparse
from datetime import datetime
import csv
import json
import os
import sys
from collections.abc import Iterator

import sed_api

data_choices = ["escolas", "unidades", "classes", "alunos", "aluno", "matriculas", "all-matriculas"]

parser = argparse.ArgumentParser(description="Extrai dados do SED.")

parser.add_argument("--data", "-d", choices=data_choices, required=True, help="Tipo de dado a ser extraído")
parser.add_argument("--output", "-o", required=True, help="Arquivo de saída de dados.")

parser.add_argument("--cookie-sed", help="Cookie 'SED' para o domínio 'sed.educacao.sp.gov.br' autenticado em sua conta do SED. Alternativamente, utilize a variável de ambiente 'SED_DATA_COOKIE_SED'")
parser.add_argument("--format", "-f", choices=["csv", "json"], default="csv", help="Formato dos dados extraídos (padrão: csv)")

parser.add_argument("--escola-id", help="Usado para unidades, classes, alunos")
parser.add_argument("--ano-letivo", default=str(datetime.now().year), help=f"Usado para classes, alunos (padrão: ano atual)")
parser.add_argument("--unidade-id", help="Usado para classes")
parser.add_argument("--classe-id", help="Usado para alunos")
parser.add_argument("--aluno-id", help="Usado para aluno, matriculas")

parser.add_argument("--verbose", "-v", action="store_true", help="Mostra mais informações durante a execução")

args = parser.parse_args()

if args.verbose:
	print("sed_data")

auth = {
	"cookie_SED": args.cookie_sed if args.cookie_sed != None
		else os.environ["SED_DATA_COOKIE_SED"] if "SED_DATA_COOKIE_SED" in os.environ
		else None
}

if auth["cookie_SED"] == None:
	print("Error: Needs --cookie-sed or SED_DATA_COOKIE_SED env var")
	exit(1)

result = None

match args.data:
	case "escolas":
		result = sed_api.get_escolas(auth)
	case "unidades":
		if args.escola_id == None:
			parser.error("Error: --data unidades needs --escola-id")
		result = sed_api.get_unidades(auth, args.escola_id)
	case "classes":
		if args.escola_id == None or args.unidade_id == None:
			parser.error("Error: --data classes needs --escola-id and --unidade-id")
		result = sed_api.get_classes(auth, args.ano_letivo, args.escola_id, args.unidade_id)
	case "alunos":
		if args.escola_id == None or args.classe_id == None:
			parser.error("Error: --data alunos needs --escola-id and --classe-id")
		result = sed_api.get_alunos(auth, args.ano_letivo, args.escola_id, args.classe_id)
	case "aluno":
		if args.aluno_id == None:
			parser.error("Error: --data aluno needs --aluno-id")
		result = sed_api.get_aluno(auth, args.aluno_id)
	case "matriculas":
		if args.aluno_id == None:
			parser.error("Error: --data matriculas needs --aluno-id")
		result = sed_api.get_matriculas(auth, args.aluno_id)
	case "all-matriculas":
		result = sed_api.get_all_matriculas(auth, args.ano_letivo)

match args.format:
	case "json":
		class IteratorAsList(list):
			def __init__(self, iterator):
				self.iterator = iterator
				self._len = 1

			def __iter__(self):
				self._len = 0
				for item in self.iterator:
					yield item
					self._len += 1

			def __len__(self):
				return self._len
		
		def json_encode(obj):
			if isinstance(obj, datetime):
				return obj.isoformat()
			if isinstance(obj, Iterator):
				return IteratorAsList(obj)
			raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

		with open(args.output, "w", encoding="utf-8") as f:
			for chunk in json.JSONEncoder(indent="\t", default=json_encode).iterencode(result):
				f.write(chunk)
				f.flush()

	case "csv":
		if not isinstance(result, list) and not isinstance(result, Iterator):
			result = [result]
		if not isinstance(result, Iterator):
			result = iter(result)
			
		first_row = next(result)

		with open(args.output, "w", encoding="utf-8-sig", newline="") as f:
			writer = csv.DictWriter(f, fieldnames=first_row.keys(), delimiter=";")
			writer.writeheader()
			f.flush()

			writer.writerow(first_row)
			f.flush()

			for row in result:
				writer.writerow(row)
				f.flush()