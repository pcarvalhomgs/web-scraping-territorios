# Web Scraping — Diário Oficial dod Municipios (Território: Chapada das Mangabeiras)

Automação e coleta de publicações do Diário Oficial dos Municípios do Piauí, focando no território **Chapada das Mangabeiras**.

## Escopo da Coleta
- **Ano:** 2025
- **Entidades:** Prefeitura e Câmara Municipal

## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem principal.
- **Selenium**: Automação da navegação e interação com filtros.
- **Requests**: Para download de arquivos.

## ⚙️ Descrição da Implementação

A solução foi desenvolvida para lidar com a estrutura dinâmica do site da APPM (Scriptcase):
- **Navegação Dinâmica**: Gerenciamento de iframes e seleção automatizada de filtros.
- **Extração via Regex**: Captura de URLs de download embutidas em funções JavaScript.
- **Prevenção de Duplicidade**: O script verifica o histórico no CSV para evitar downloads repetidos.
- **Headless Mode**: Execução em segundo plano para otimização de recursos.

## 📂 Armazenamento de Dados

Os dados são salvos na pasta `dados_coletados/`:
- **CSV**: Contém metadados (edição, data, município, entidade, link e identificador único).
- **PDFs**: Organizados automaticamente em subpastas por `município/entidade`.

## Guia de Execução

### Pré-requisitos
- Navegador baseado em Chromium instalado (Chrome, Edge, outros).

### Comandos para Iniciar
```bash
# Faça o clone do diretório do projeto
# Instale as bibliotecas selenium e requests (usar ambiente virtual (.venv) opcional).
pip install requests selenium

# Execute o scraper
python3 main_scraper.py
```

