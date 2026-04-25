import os
import csv
from scraper import coletar_entidade

# Configurações
URL_SITE = "https://www.diarioficialdosmunicipios.org/consulta/ConPublicacaoGeral/ConPublicacaoGeral.php"

# Teste com apenas 2 municípios e periodo menor.
MUNICIPIOS = [
    "Alvorada do Gurgueia", "Avelino Lopes"
]

# MUNICIPIOS = [
#     "Alvorada do Gurgueia", "Avelino Lopes", "Barreiras do Piauí", "Bom Jesus", "Colônia do Gurgueia", "Corrente",
#       "Cristalândia do Piauí", "Cristino Castro", "Curimatá", "Currais", "Eliseu Martins", "Gilbués",
#         "Júlio Borges", "Manoel Emídio", "Monte Alegre do Piauí", "Morro Cabeça no Tempo", "Palmeira do Piauí",
#           "Parnaguá", "Redenção do Gurgueia", "Riacho Frio", "Santa Filomena", "Santa Luz", "São Gonçalo do Gurgueia", "Sebastião Barros"
# ]

ENTIDADES = ["Prefeitura", "Camara"] 

# Define o período de 01/10/2025 a 31/12/2025.
dataInicio = "01102025"
dataFim = "31122025"

BASE_DADOS = "dados_coletados"
DIR_CSV = os.path.join(BASE_DADOS, "csv")
PATH_CSV = os.path.join(DIR_CSV, "dados.csv")


# Cria pastas para o CSV
def configurar_ambiente():
    os.makedirs(DIR_CSV, exist_ok=True)
    print(f"[*] arquivos serão salvos em: {BASE_DADOS}/")

# Adiciona os dados coletados ao arquivo CSV
def salvar_csv(dados, modo='a'):
    campos = ["N° Edição", "Ano", "Data", "Município", "Entidade", "Categoria", "Documento", "Arquivo", "URL", "Identificador"]
    file_exists = os.path.isfile(PATH_CSV)
    
    with open(PATH_CSV, modo, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction='ignore', delimiter="|")
        if not file_exists or modo == 'w':
            writer.writeheader()
        writer.writerows(dados)

# Função principal
def main():
    configurar_ambiente()
    ids_processados = set()
    
    # Verifica o arquivo CSV existente para evitar o download de duplicatas.
    if os.path.exists(PATH_CSV):
        with open(PATH_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter="|")
            for row in reader:
                ids_processados.add(row['Identificador'])
        print(f"[*] {len(ids_processados)} registros já existentes carregados.")

    # Loop por municípios e entidades
    for m in MUNICIPIOS:
        print(f"\n{'=='*60}\n= CIDADE: {m.upper()}\n{'=='*60}")
        for e in ENTIDADES:
            resultados = coletar_entidade(m, e, ids_processados, BASE_DADOS, URL_SITE, dataInicio, dataFim)
            if resultados:
                salvar_csv(resultados, modo='a')
                print(f"  {len(resultados)} novos registros salvos.")

    print(f"\n[*] FINALIZADO. CSV: {PATH_CSV}")

if __name__ == "__main__":
    main()