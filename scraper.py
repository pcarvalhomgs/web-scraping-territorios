import os
import time
import re
import requests
import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# Remove acentos e espaços de nomes para criar pastas
def normalizar_nome(txt):
    return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII').lower().replace(" ", "_")

# Inicializa o navegador Chrome em modo oculto (headless)
def criar_driver():
    options = Options()
    if os.path.exists("/usr/sbin/chromium-browser"):
        options.binary_location = "/usr/sbin/chromium-browser"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

# Captura o link do PDF dentro da string JavaScript
def extrair_url_javascript(texto):
    if not texto: return ""
    match = re.search(r"'(http[s]?://[^']+?\.pdf)\s*'", texto)
    return match.group(1).strip() if match else ""

# Baixa o arquivo PDF e salva no disco
def baixar_pdf(url, destino):
    try:
        r = requests.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(destino, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return True
    except: pass
    return False

# Localiza e entra no iframe que contém os resultados
def switch_to_grid_iframe(driver):
    driver.switch_to.default_content()
    time.sleep(2)
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for f in iframes:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(f)
            if "scGridTabela" in driver.page_source:
                return True
        except: continue
    return False

# Executa a busca e coleta dados de uma prefeitura ou câmara
def coletar_entidade(municipio, entidade, ids_processados, BASE_DADOS, URL_SITE,dataInicio, dataFim):
    dados_entidade = []
    driver = criar_driver()
    dir_output = os.path.join(BASE_DADOS, "pdfs", normalizar_nome(municipio), entidade)
    os.makedirs(dir_output, exist_ok=True)
    
    try:
        print(f"\n[*] BUSCANDO: {municipio} -> {entidade}...")
        driver.get(URL_SITE)
        time.sleep(4)

        # Seleciona filtros no site
        try:
            Select(driver.find_element(By.ID, "SC_nomeentidade")).select_by_visible_text(entidade)
            Select(driver.find_element(By.ID, "SC_nomemunicipio")).select_by_visible_text(municipio)
        except:
            # Tenta sem acento se o nome original falhar
            try:
                municipio_sem_acento = unicodedata.normalize('NFKD', municipio).encode('ASCII', 'ignore').decode('ASCII')
                Select(driver.find_element(By.ID, "SC_nomemunicipio")).select_by_visible_text(municipio_sem_acento)
            except:
                print(f"  [!] Município {municipio} não encontrado.")
                return []

        # Define o período de busca
        campo_ini = driver.find_element(By.ID, "SC_data_dia_de")
        campo_fim = driver.find_element(By.ID, "SC_data_dia_ate")
        campo_ini.click(); campo_ini.clear(); campo_ini.send_keys(f"{dataInicio}"); campo_ini.send_keys(Keys.TAB)
        campo_fim.click(); campo_fim.clear(); campo_fim.send_keys(f"{dataFim}"); campo_fim.send_keys(Keys.TAB)
        
        # Clica em Pesquisar
        driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "sc_b_pesq_bot"))
        time.sleep(15)

        # Acessa o iframe de resultados
        if not switch_to_grid_iframe(driver):
            print(f"  [?] Sem registros para {entidade}.")
            return []

        # Aumenta para 100 resultados por página
        try:
            input_qtd = driver.find_element(By.ID, "quant_linhas_f0_bot")
            input_qtd.clear(); input_qtd.send_keys("100")
            driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "qtlin_bot"))
            time.sleep(10); switch_to_grid_iframe(driver)
        except: pass

        # Percorre as páginas de resultados
        pagina_atual = 1
        while True:
            rows = driver.find_elements(By.CSS_SELECTOR, "tr[id^='SC_ancor']")
            if not rows: break
            
            try:
                info_pag = driver.find_element(By.CLASS_NAME, "scGridToolbarPadding").text
                print(f"  [Pág {pagina_atual}] {info_pag}")
            except: pass

            for row in rows:
                try:
                    # Extrai dados da linha
                    id_cod = row.find_element(By.CLASS_NAME, "css_codigo_grid_line").text.strip()
                    if id_cod in ids_processados: continue
                    ids_processados.add(id_cod)

                    link_raw = row.find_element(By.CLASS_NAME, "css_nomearq_grid_line").find_element(By.TAG_NAME, "a").get_attribute("href")
                    url_pdf = extrair_url_javascript(link_raw)
                    
                    item = {
                        "N° Edição": row.find_element(By.CLASS_NAME, "css_numedicao_grid_line").text.strip(),
                        "Ano": row.find_element(By.CLASS_NAME, "css_ano_grid_line").text.strip(),
                        "Data": row.find_element(By.CLASS_NAME, "css_data_grid_line").text.strip(),
                        "Município": municipio,
                        "Entidade": entidade,
                        "Categoria": row.find_element(By.CLASS_NAME, "css_nomecategoria_grid_line").text.strip(),
                        "Documento": row.find_element(By.CLASS_NAME, "css_nomedoc_grid_line").text.strip(),
                        "Identificador": id_cod,
                        "URL": url_pdf,
                        "Arquivo": os.path.basename(url_pdf)
                    }
                    
                    # Baixa o PDF se houver link e se o arquivo não existir
                    if item["URL"]:
                        caminho_local = os.path.join(dir_output, item["Arquivo"])
                        if not os.path.exists(caminho_local):
                            baixar_pdf(item["URL"], caminho_local)
                    
                    dados_entidade.append(item)
                except: continue

            # Tenta ir para a próxima página
            try:
                btn_proximo = driver.find_element(By.ID, "forward_bot")
                if "_off.gif" in btn_proximo.find_element(By.TAG_NAME, "img").get_attribute("src"): break
                driver.execute_script("arguments[0].click();", btn_proximo)
                pagina_atual += 1; time.sleep(8); switch_to_grid_iframe(driver)
            except: break

    except Exception as e:
        print(f"  [!] Erro na coleta: {e}")
    finally:
        driver.quit()
    
    return dados_entidade
