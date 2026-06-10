from playwright.sync_api import sync_playwright
import os

# Garante que a pasta data existe
os.makedirs("data", exist_ok=True)

def login_manual():
    with sync_playwright() as p:
        # Abrimos com headless=False para tu veres o browser
        browser = p.chromium.launch(
            headless=False
        )
        
        context = browser.new_context()
        page = context.new_page()

        print("Por favor, faz login no Lavbella.com e resolve qualquer Captcha/2FA...")
        page.goto("https://xxxx")

        # O script fica à espera que tu feches o browser manualmente após o login
        # Ou podes aumentar o timeout para te dar tempo
        page.wait_for_timeout(90000) # Tens 90 segundos para logar

        # Guarda o estado (cookies, local storage) na pasta que será o Volume
        context.storage_state(path="data/auth.json")
        print("Sessão guardada com sucesso em data/auth.json!")
        browser.close()

if __name__ == "__main__":
    login_manual()