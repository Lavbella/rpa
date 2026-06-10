
import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright
import io
import pytesseract
from PIL import Image, ImageFilter, ImageOps

# Caminhos dentro do contentor (mapeados pelo volume Docker)
DATA_DIR = "data"
AUTH_FILE = f"{DATA_DIR}/auth.json"
OUTPUT_EXCEL = f"{DATA_DIR}/posts_extraidos.xlsx"
ACTIVITY_POST_SELECTOR = 'div[data-urn][role="article"]'

# URL da tua atividade ou de um post específico
TARGET_URL = "https://xxxx"


def atualizar_excel_com_tabela(page, filename=OUTPUT_EXCEL, coluna="", nlinha=-1):

    # 1. Extrair os Nomes das Colunas (Cabeçalho)
    # Procura os <th> ou os <td> da primeira linha da tabela
    header_elementos = page.locator("tr").first.locator("th, td").all_text_contents()
    colunas_nomes = [texto.strip() for texto in header_elementos]

    # 1. Extração dos dados da página (como fizeste antes)
    linhas = page.locator("tr[id^='idtr']").all()
    novos_dados = []

    for linha in linhas:
        colunas = linha.locator("td").all_text_contents()
        novos_dados.append([texto.strip() for texto in colunas])

    if not novos_dados:
        print("⚠️ Nada para extrair.")
        log_rpa("Nada para extrair.")
        return ""

    # 2. Criar DataFrame com os novos registos
    df_novo = pd.DataFrame(novos_dados, columns=colunas_nomes)

    # 3. Lógica de Update
    if os.path.exists(filename):
        # Carrega o existente
        df_antigo = pd.read_excel(filename)
        # Junta o antigo com o novo (append)
        # ignore_index=True garante que a numeração das linhas continua correta
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
        # Opcional: Remover duplicados se o robô ler a mesma linha duas vezes
        df_final = df_final.drop_duplicates()
    else:
        # Se não existe, o final é apenas o novo
        df_final = df_novo

    # 4. Grava de volta no Excel
    df_final.to_excel(filename, index=False)
    print(f"✅ Excel atualizado: {len(df_final)} linhas totais.")
    log_rpa(f"Excel atualizado: {len(df_final)} linhas totais.")

    # Após o df_final ser criado na tua função de update
    
    if len(df_final) >= nlinha:
        codigo_linha_5 = df_final.loc[nlinha - 1, coluna]
        log_rpa(f"O código capturado da linha 5 foi: {codigo_linha_5}")

    return codigo_linha_5


def snapshot(page, acao):
    print(f"📸 Foto: {acao}")
    page.screenshot(path="data/live.png")

def extrair_texto_captcha(page):
    """
    Captura a imagem do captcha e transforma em texto.
    Funciona diretamente no Docker.
    """

    try:
        # 1. Localiza a imagem (ajusta o seletor 'img' conforme o site)
        # Exemplo: page.locator("img#captcha_img")
        captcha_element = page.locator("img#captchaimglogin")
        captcha_element.wait_for(state="visible", timeout=5000)
        log_rpa("Localiza a imagem CAPTCHA")
        snapshot(captcha_element, "captcha_original")

        # 2. Tira o screenshot do elemento em memória (bytes)
        captcha_bytes = captcha_element.screenshot()
        log_rpa("Tira o screenshot do elemento em memória (bytes)")

        # 3. Abre com o Pillow e otimiza para o OCR
        img = Image.open(io.BytesIO(captcha_bytes))
        log_rpa("otimiza a imagem para o OCR")

        img = img.convert('L')  # Escala de cinza para melhor leitura
        log_rpa("Escala de cinza para melhor leitura")

        img = img.resize((img.width * 4, img.height * 4), Image.Resampling.LANCZOS)
        log_rpa("Resize da imagem")

        # 2. Filtro de Nitidez para definir as bordas e não "fechar" o 'c'
        img = img.filter(ImageFilter.SHARPEN)
        log_rpa("Aplicar filtro para aumentar a nitidez e o contraste")

        # 4. O Tesseract no Docker será chamado aqui automaticamente
        custom_config = r'--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789'

        log_rpa("Aplica o OCR")
        texto = pytesseract.image_to_string(img, config=custom_config).strip()
        log_rpa(f"Captcha lido: {texto}")

        # Limpa caracteres não alfanuméricos comuns em erros de leitura
        texto_limpo = ''.join(e for e in texto if e.isalnum())
        log_rpa("Limpa caracteres não alfanuméricos comuns em erros de leitura")
        log_rpa(f"Captcha lido: {texto_limpo}")

        return texto_limpo

    except Exception as e:
        print(f"❌ Erro ao processar CAPTCHA no Docker: {e}")
        log_rpa(f"Erro ao processar CAPTCHA no Docker: {e}")
        return None

def realizar_login_ciclico(page, utilizador, senha, num1, num6, captcha_visto_agora):
    """
    Executa o login direto. Como a sessão morre em 30 min, 
    este bloco será chamado sempre que fores expulso para o 'indexadm'.
    """
    try:
        # 1. Preenchimento rápido para evitar que o captcha expire
        log_rpa("Preenchimento dos dados de Login")
        page.locator("#utilizador_login").fill(utilizador)    
        page.locator("#codigoacesso_login").fill(senha)        
        page.locator("#numero_1").fill(str(num1))
        page.locator("#numero_6").fill(str(num6))
        page.locator("#captcha_login").fill(str(captcha_visto_agora))
        snapshot(page, "dados_login_inseridos")
        # 2. Submeter
        log_rpa("Efetuar o Login")
        page.locator("#submit_login").click()
        page.locator("#controla-icon-menu").wait_for(state="visible", timeout=10000)

        # 4. Validar se entramos mesmo
        if page.locator("#controla-icon-menu").is_visible(timeout=5000):
            print("✅ Login efetuado com sucesso!")
            log_rpa("Login efetuado com sucesso!...")
            snapshot(page, "Login_Confirmado")
            return True
        else:
            print("❌ Falha: Os dados do CAPTCHA estão errados.")
            log_rpa("Falha: Os dados do CAPTCHA estão errados.")
            return False
            
    except Exception as e:
        print(f"⚠️ Erro durante a tentativa de login: {e}")
        log_rpa(f"Erro durante a tentativa de login: {e}")
        return False

def clean_state():

    # --- LIMPEZA DE ESTADO ANTERIOR ---
    ficheiros_para_limpar = [
        f"{DATA_DIR}/erro_debug.png",
        f"{DATA_DIR}/live.png",
        f"{DATA_DIR}/status.txt",
        f"{DATA_DIR}/processo.log",
        f"{DATA_DIR}/posts_extraidos.xlsx"
    ]
    
    for f in ficheiros_para_limpar:
        if os.path.exists(f):
            os.remove(f)
            print(f"🧹 Limpo: {f}")
    # ----------------------------------

def log_rpa(mensagem):
    # 1. Escreve no ficheiro de logs para o Streamlit ler (acumulativo)
    with open(f"{DATA_DIR}/processo.log", "a", encoding="utf-8") as f:
        f.write(f"🕒[{datetime.now().strftime('%H:%M:%S')}] {mensagem}\n")


def run_rpa():

    clean_state()

    max_tentativas = 10
    tentativas = 0
    retorno_ciclo_sucesso = False
    erro_leitura_captcha = False

    codigo_musica_ouvir = ""

    with sync_playwright() as p:
        print("🚀 A iniciar browser...")
        log_rpa("A iniciar browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 2. Aceder à página
            print(f"📡 Acedendo a: {TARGET_URL}")
            log_rpa(f"Acedendo a: {TARGET_URL}")
            page.goto(TARGET_URL, wait_until="domcontentloaded")
            page.screenshot(path=f"{DATA_DIR}/live.png", full_page=True)

            while not retorno_ciclo_sucesso and tentativas < max_tentativas:

                print(f"🔄 Tentativa {tentativas}/{max_tentativas}...")
                log_rpa(f"Tentativa {tentativas}/{max_tentativas} para ler o CAPTCHA")
                # 3. Chamar a função do CAPTCHA
                print("📸 A capturar e a ler o CAPTCHA...")
                log_rpa("A capturar e a ler o CAPTCHA...")
                codigo_captcha = extrair_texto_captcha(page) 

                if not codigo_captcha:
                    print(f"⚠️ Não foi possível extrair o texto do CAPTCHA. A recarregar...")
                    log_rpa("Não foi possível extrair o texto do CAPTCHA. A recarregar...")
                    erro_leitura_captcha = True
                else:
                    print(f"🤖 CAPTCHA lido: {codigo_captcha}")
                    log_rpa("CAPTCHA lido")

                # Validação 1: Tamanho
                if len(codigo_captcha) != 6 and not erro_leitura_captcha:
                    print(f"⚠️ Tamanho errado ({len(codigo_captcha)}). A recarregar...")
                    log_rpa(f"Tamanho errado ({len(codigo_captcha)}). Refrescar e ler novamente...")
                    erro_leitura_captcha = True

                # 4. Executar o Login
                if not erro_leitura_captcha:
                    sucesso = realizar_login_ciclico(
                        page, 
                        utilizador="xxxxxx", 
                        senha="######", 
                        num1 = 999,
                        num6 = 999,
                        captcha_visto_agora=codigo_captcha
                    )

                    if not sucesso:
                        print(f"Falha no login: os dados ou o CAPTCHA foram rejeitados.")
                        log_rpa(f"Falha no login: os dados ou o CAPTCHA foram rejeitados.")
                        
                    else:
                        retorno_ciclo_sucesso = True

                if not retorno_ciclo_sucesso:
                    page.reload(wait_until="domcontentloaded")
                    erro_leitura_captcha = False
                    tentativas += 1

            if retorno_ciclo_sucesso:

                page.locator("#controla-icon-menu").click()
                page.locator("#menu_p").wait_for(state="visible", timeout=10000)

                if page.locator("#menu_p").is_visible():
                    print("✅ Menu visível!")
                    log_rpa("Menu visível!")
                    snapshot(page, "Menu expandido")
                else:
                    log_rpa("Falha a expandir o menu.")
                    raise Exception("Falha a expandir o menu.")

                page.locator("#limenu5").click()
                page.locator("#gestaotimeless").wait_for(state="visible", timeout=5000)
                if page.locator("#gestaotimeless").is_visible():
                    print("✅ Gestão Timeless visível")
                    log_rpa("Gestão Timeless visível!")
                    snapshot(page, "Gestão Timeless")
                else:
                    log_rpa("Falha a abrir Gestão Timeless.")
                    raise Exception("Falha a abrir Gestão Timeless.")                

                page.locator("#autorvideo_id_gtp").fill("Fingertips")
                snapshot(page, "Insere autor para pesquisa")
                log_rpa("Insere autor para pesquisa")

                page.locator("#gestaotimeless_pesquisa_b").click()
                page.locator("#idtr0").wait_for(state="visible", timeout=10000)

                if page.locator("#idtr0").is_visible():
                    print("Pesquisou com sucesso!")
                    log_rpa("Pesquisou com sucesso!...")
                    snapshot(page, "Pesquisa efetuada")
                    codigo_musica_ouvir = atualizar_excel_com_tabela(page, filename=OUTPUT_EXCEL, coluna="Código", nlinha=5)

                    if codigo_musica_ouvir != "":
                        page.locator("#video-id").fill(codigo_musica_ouvir)
                        snapshot(page, "Insere o código do video")
                        log_rpa("Insere o código do video!...")
                        print("Insere o código do video!...")

                        page.locator("#add-song").click()
                        page.wait_for_timeout(4000)   
                        log_rpa("Video obtido e visualizado.")
                        print("Video obtido e visualizado.")
                        snapshot(page, "Video obtido e visualizado.")

                        
                else:
                    print("❌ Não conseguiu pesquisar ou oesquisa sem resultados.")
                    log_rpa("Não conseguiu pesquisar ou oesquisa sem resultados.")
                    snapshot(page, "Não conseguiu pesquisar ou pesquisa sem resultados.")
    
                


                # Finalizar com sucesso
                with open(f"{DATA_DIR}/status.txt", "w") as f:
                    f.write(
                        f"Sucesso ✅\n"
                        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                    )

                page.screenshot(path=f"{DATA_DIR}/ultimo_sucesso.png", full_page=True)
                log_rpa("Objetivo atingido com sucesso.")
                print("✅ Objetivo atingido com sucesso.")

            else:
                log_rpa("Falha a obter o capcha após 10 tentativas.")
                raise Exception("Falha a obter o capcha após 10 tentativas.")

        except Exception as e:
            print(f"⚠️ Erro no RPA: {e}")
            # Tira print do erro
            try:
                page.screenshot(path=f"{DATA_DIR}/erro_debug.png", full_page=True)
            except:
                pass
        
        finally:
            browser.close()
            print("🔒 Browser fechado.")

if __name__ == "__main__":
    run_rpa()