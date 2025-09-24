import os
import time
import re
import requests

import flet
from flet import (
    Page,
    Text,
    Switch,
    TextField,
    ElevatedButton,
    Column,
    Container,
    Row,
    Divider,
    ProgressRing,
    ProgressBar,
    SnackBar,
    Colors,
    padding,
    ThemeMode,
)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURAÇÕES API ReceitaWS ---
API_URL     = "https://www.receitaws.com.br/v1/cnpj/{}"
RATE_LIMIT  = 3      # segundos entre chamadas
BACKOFF_429 = 60     # espera extra se der HTTP 429

# --- CONFIGURAÇÕES Selenium/Chrome ---
CHROMEDRIVER_PATH = r"C:\Drivers\chromedriver-win64\chromedriver.exe"
GOOGLE_URL        = "https://www.google.com/"

# ─── Inicializa o ChromeDriver (Selenium 4.x) ───────────────────────────────
chrome_opts = Options()
chrome_opts.add_argument("--start-maximized")
chrome_opts.add_argument("--log-level=3")
chrome_opts.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(
    executable_path=CHROMEDRIVER_PATH,
    log_path=os.devnull
)
driver = webdriver.Chrome(service=service, options=chrome_opts)

# já carrega o Google assim que o Chrome abre
driver.get(GOOGLE_URL)


# ─── FUNÇÕES AUXILIARES ─────────────────────────────────────────────────────

def consulta_cnpj_data(cnpj: str) -> str:
    cnpj_num = "".join(filter(str.isdigit, cnpj))
    if len(cnpj_num) != 14:
        return f"{cnpj_num};;FORMATO_INVÁLIDO"
    for attempt in (1, 2):
        resp = requests.get(API_URL.format(cnpj_num), timeout=10)
        if resp.status_code == 429 and attempt == 1:
            time.sleep(BACKOFF_429)
            continue
        if resp.status_code != 200:
            return f"{cnpj_num};;ERRO:HTTP_{resp.status_code}"
        data = resp.json()
        if data.get("status") == "ERROR":
            return f"{cnpj_num};;ERRO:{data.get('message')}"
        nome  = data.get("nome","").strip()
        email = data.get("email","").strip()
        tel   = data.get("telefone","").strip()
        cnae  = data.get("cnae_fiscal","").strip()
        desc  = data.get("cnae_fiscal_descricao","").strip()
        if not cnae:
            ap = data.get("atividade_principal",[])
            if ap:
                cnae = ap[0].get("code","").strip()
                desc = ap[0].get("text","").strip()
        quadro = "|".join(
            f"{s.get('nome','')}({s.get('qual','')})"
            for s in data.get("qsa",[])
        )
        return ";".join([cnpj_num,nome,email,tel,cnae,desc,quadro])
    return f"{cnpj_num};;ERRO:HTTP_429_PERSISTENTE"


def formatar_telefone(raw: str) -> str:
    digits = re.sub(r"\D","", raw or "")
    if len(digits) == 10:
        return f"{digits[:2]} {digits[2:6]}-{digits[6:]}"
    if len(digits) == 11:
        return f"{digits[:2]} {digits[2:7]}-{digits[7:]}"
    raise ValueError("Telefone inválido: use 10 ou 11 dígitos")


def buscar_cnpj_por_telefone(telefone_fmt: str) -> str:
    driver.get(GOOGLE_URL)
    wait = WebDriverWait(driver, timeout=10, poll_frequency=0.5)
    q = wait.until(EC.presence_of_element_located((By.NAME, "q")))
    q.clear()
    q.send_keys(telefone_fmt, Keys.ENTER)
    h3s = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3.LC20lb"))
    )
    for h in h3s:
        m = re.search(r"\b(\d{14})\b", h.text)
        if m:
            return m.group(1)
    return ""


# ─── INTERFACE FLET ─────────────────────────────────────────────────────────

def main(page: Page):
    # modo escuro e cores iniciais
    page.theme_mode = ThemeMode.DARK
    page.window_width         = 580
    page.window_height        = 400
    page.window_resizable     = False
    page.padding              = padding.all(10)
    page.bgcolor              = Colors.BLACK
    page.vertical_alignment   = "start"
    page.horizontal_alignment = "center"

    # componentes da coluna esquerda (API CNPJ)
    modo_lote      = Switch(label="Modo Lote", value=False)
    tf_cnpj        = TextField(label="CNPJ (14 dígitos)", width=300, text_align="center")
    btn_consulta   = ElevatedButton("Consultar", width=150)
    spinner_ind    = ProgressRing(visible=False, width=40, height=40)
    btn_copy_left  = ElevatedButton("Copiar", width=100, disabled=True)
    result_ind     = Column(spacing=8, width=350)
    tf_path        = TextField(label="Caminho do TXT", width=300, hint_text="Ex: C:\\arquivo.txt")
    btn_batch      = ElevatedButton("Processar lote", width=150)
    spinner_bt     = ProgressRing(visible=False, width=40, height=40)
    progress       = ProgressBar(visible=False, width=300)
    log_bt         = Text("", size=14, visible=False)
    result_bt      = Column(spacing=4, width=350)
    last_line_left = [""]

    def alternar_modo(e=None):
        lot = modo_lote.value
        tf_cnpj.visible        = not lot
        btn_consulta.visible   = not lot
        spinner_ind.visible    = False
        btn_copy_left.visible  = not lot
        btn_copy_left.disabled = True
        result_ind.visible     = not lot
        tf_path.visible        = lot
        btn_batch.visible      = lot
        spinner_bt.visible     = False
        progress.visible       = False
        log_bt.visible         = False
        result_bt.visible      = lot
        page.update()

    modo_lote.on_change = alternar_modo
    alternar_modo()

    def on_consulta_left(e):
        line = consulta_cnpj_data(tf_cnpj.value or "")
        last_line_left[0] = line
        parts = line.split(";")
        if "ERRO:" in line:
            page.snack_bar = SnackBar(Text(parts[-1]))
            page.snack_bar.open = True
            page.update()
            return
        spinner_ind.visible    = True
        btn_consulta.disabled  = True
        result_ind.controls.clear()
        page.update()
        _, nome, email, tel, cnae, desc, quadro = parts
        result_ind.controls.extend([
            Text(f"Razão Social: {nome}", size=14),
            Text(f"E-mail: {email}", size=14),
            Text(f"Telefone: {tel}", size=14),
            Text(f"CNAE: {cnae} – {desc}", size=14),
        ])
        if quadro:
            result_ind.controls.append(Divider())
            result_ind.controls.append(Text("Quadro Social:", size=14, weight="bold"))
            for s in quadro.split("|"):
                result_ind.controls.append(Text(f"– {s}", size=12))
        spinner_ind.visible    = False
        btn_consulta.disabled  = False
        btn_copy_left.disabled = False
        page.update()

    btn_consulta.on_click = on_consulta_left

    def on_copy_left(e):
        page.set_clipboard(last_line_left[0])
        page.snack_bar = SnackBar(Text("Copiado!"))
        page.snack_bar.open = True
        page.update()

    btn_copy_left.on_click = on_copy_left

    def on_batch(e):
        path = tf_path.value or ""
        if not os.path.isfile(path):
            page.snack_bar = SnackBar(Text("Arquivo não encontrado"))
            page.snack_bar.open = True
            page.update()
            return
        with open(path, "r", encoding="utf-8") as f:
            lista = [l.strip() for l in f if l.strip()]
        total = len(lista)
        spinner_bt.visible   = True
        btn_batch.disabled   = True
        progress.visible     = True
        progress.value       = 0
        log_bt.visible       = True
        log_bt.value         = f"0/{total}"
        result_bt.controls.clear()
        page.update()
        lines = []
        for i, raw in enumerate(lista, start=1):
            log_bt.value   = f"{i}/{total}"
            progress.value = i/total
            page.update()
            lines.append(consulta_cnpj_data(raw))
            time.sleep(RATE_LIMIT)
        with open("resultado_consulta.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        spinner_bt.visible = False
        btn_batch.disabled = False
        result_bt.controls.append(Text("Batch concluído!", size=14))
        page.snack_bar = SnackBar(Text("Arquivo gerado"))
        page.snack_bar.open = True
        page.update()

    btn_batch.on_click = on_batch

    left_panel = Container(
        content=Column([
            Text("Consulta por CNPJ (API)", size=18, weight="bold"),
            modo_lote, Divider(),
            tf_cnpj,
            Row([btn_consulta, spinner_ind, btn_copy_left], alignment="center"),
            result_ind,
            Divider(),
            tf_path,
            Row([btn_batch, spinner_bt], alignment="center"),
            progress, log_bt, result_bt,
        ], spacing=12),
        padding=padding.all(16),
        bgcolor=Colors.GREY_900,
        border_radius=8,
        width=360, height=580
    )

    # componentes à direita (Pesquisa por Telefone)
    tf_tel        = TextField(label="Telefone (10 ou 11 dígitos)", width=300, text_align="center")
    btn_tel       = ElevatedButton("Consultar Tel.", width=150)
    spinner_tel   = ProgressRing(visible=False, width=36, height=36)
    resultado_tel = Text("", size=16, weight="bold")
    btn_copy_tel  = ElevatedButton("Copiar", disabled=True)
    last_tel      = {"cnpj": ""}

    def on_consulta_tel(e):
        spinner_tel.visible     = True
        btn_tel.disabled        = True
        btn_copy_tel.disabled   = True
        resultado_tel.value     = ""
        page.update()
        try:
            fmt  = formatar_telefone(tf_tel.value)
            cnpj = buscar_cnpj_por_telefone(fmt)
            if not cnpj:
                raise ValueError("Nenhum CNPJ encontrado")
            resultado_tel.value   = f"CNPJ: {cnpj}"
            last_tel["cnpj"]      = cnpj
            btn_copy_tel.disabled = False
        except Exception as ex:
            page.snack_bar = SnackBar(Text(f"Erro: {ex}"))
            page.snack_bar.open = True
        finally:
            spinner_tel.visible = False
            btn_tel.disabled    = False
            page.update()

    btn_tel.on_click = on_consulta_tel

    def on_copy_tel(e):
        page.set_clipboard(last_tel["cnpj"])
        page.snack_bar = SnackBar(Text("Copiado!"))
        page.snack_bar.open = True
        page.update()

    btn_copy_tel.on_click = on_copy_tel

    right_panel = Container(
        content=Column([
            Text("Consulta por Telefone", size=18, weight="bold"),
            Divider(),
            Text("Insira um telefone para pesquisa automática do CNPJ.", size=12),
            tf_tel,
            Row([btn_tel, btn_copy_tel, spinner_tel], alignment="center", spacing=10),
            resultado_tel,
        ], spacing=12),
        padding=padding.all(16),
        bgcolor=Colors.GREY_900,
        border_radius=8,
        width=360, height=580
    )

    page.add(Row([left_panel, right_panel], alignment="spaceEvenly", spacing=20))


if __name__ == "__main__":
    # view=flet.FLET_APP abre em janela nativa desktop
    flet.app(target=main, view=flet.FLET_APP)
