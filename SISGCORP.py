# -*- coding: utf-8 -*-
import os
import requests
import time
import threading
import subprocess
import json
import ctypes
from ctypes import wintypes
import customtkinter as ctk
from tkinter import messagebox, scrolledtext
from tkinter import Tk, END

from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By

# URLs da API
BASE_EXISTE_HISTORICO = "https://sisgcorp.eb.mil.br/sisgcorpregistro/api/solicitacao-servico/autorizacoes-pce/existe-historico/"
BASE_LISTAR_HISTORICO = "https://sisgcorp.eb.mil.br/sisgcorpregistro/api/solicitacao-servico/autorizacoes-pce/listar-historico/"
BASE_BAIXAR_RELATORIO = "https://sisgcorp.eb.mil.br/sisgcorpregistro/api/solicitacao-servico/autorizacoes-pce/baixar-relatorio/"
BASE_URL_SOLICITACAO = "https://sisgcorp.eb.mil.br/sisgcorpregistro/api/solicitacao-servico"
delay = 2
debug_port = "9222"

cookies = None
is_running = False
thread = None
btn_abrir_navegador = None
btn_capturar_cookies = None
btn_iniciar_busca = None
label_usuario_logado = None
log_textbox = None

def log_message(message, level="info"):
    # Adiciona uma mensagem ao log com base no nível especificado. Níveis disponíveis: 'info', 'success', 'warning', 'error', 'debug'
    if log_textbox:
        log_textbox.configure(state='normal')
        
        # Definir emojis e tags de cores com base no nível
        emojis = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "debug": "🐞",
        }
        tag_colors = {
            "info": "cyan",
            "success": "green",
            "warning": "orange",
            "error": "red",
            "debug": "purple",
        }
        emoji = emojis.get(level, "ℹ️")
        color = tag_colors.get(level, "white")
        
        # Configurar tags se ainda não estiverem configuradas
        if not log_textbox.tag_names():
            for tag, col in tag_colors.items():
                log_textbox.tag_configure(tag, foreground=col, font=("Segoe UI Emoji", 10))
        
        # Inserir a mensagem com o emoji e a tag de cor
        log_textbox.insert(END, f"{emoji} {message}\n", level)
        log_textbox.see(END)
        log_textbox.configure(state='disabled')
    else:
        print(message)

def print_separator():
    log_message("-" * 60, "debug")

def abrir_navegador():
    comando = (
        r'"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" '
        f'--remote-debugging-port={debug_port} '
        r'--user-data-dir="C:\Selenium\EdgeProfile" '
        "https://sisgcorp.eb.mil.br/"
    )
    subprocess.Popen(comando, shell=True)
    messagebox.showinfo(
        "Aguarde",
        "O navegador foi aberto em modo debug. Faça login manualmente no SISGCORP antes de capturar os cookies."
    )
    log_message("Navegador aberto em modo debug.", "info")

def capturar_cookies():
    global cookies, label_usuario_logado
    try:
        print_separator()
        log_message("Capturando cookies...", "info")

        options = webdriver.EdgeOptions()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=options
        )
        if len(driver.window_handles) > 0:
            log_message("Navegador detectado. Tentando capturar cookies...", "success")
        else:
            log_message("Nenhuma aba detectada, abra o site manualmente.", "warning")

        nome_usuario = obter_nome_usuario(driver)
        log_message(f"Nome do usuário no momento do login: {nome_usuario}", "debug")

        selenium_cookies = driver.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}

        if label_usuario_logado is not None and nome_usuario != "Usuario_Desconhecido":
            label_usuario_logado.configure(text=f"Logado como: {nome_usuario}")

        driver.quit()

        log_message("Cookies capturados com sucesso.", "success")
        messagebox.showinfo(
            "Configuração de Cookies",
            "Cookies capturados com sucesso. Abra todas as páginas do SisGCorp, depois você pode iniciar a busca."
        )
    except Exception as e:
        log_message(f"Falha ao configurar cookies: {e}", "error")
        messagebox.showerror("Erro", f"Falha ao configurar cookies: {e}")

def obter_nome_usuario(driver):
    try:
        user_span = driver.find_element(By.CSS_SELECTOR, "span.profile-name")
        return user_span.text.strip()
    except:
        return "Usuario_Desconhecido"

def obter_caminho_area_de_trabalho():
    # Obtém o caminho da área de trabalho no Windows, independentemente do idioma.
    csidl_personal = 0  # CSIDL_DESKTOP
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, csidl_personal, 0, 0, buf)
    return buf.value

def salvar_arquivo_em_pasta(response, nome_usuario, final_id):
    try:
        # Obtém o caminho da área de trabalho
        desktop_path = obter_caminho_area_de_trabalho()
        dir_path = os.path.join(desktop_path, "Documentos Sisgcorp", nome_usuario)
        
        # Cria o diretório, se não existir
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            log_message(f"Criada a pasta: {dir_path}", "info")
        
        # Define o caminho do arquivo
        caminho_arquivo = os.path.join(dir_path, f"documento_{final_id}.pdf")
        
        # Salva o conteúdo do arquivo
        with open(caminho_arquivo, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        
        log_message(f"Documento {final_id} salvo em: {caminho_arquivo}", "success")
    except Exception as e:
        log_message(f"Erro ao salvar arquivo: {str(e)}", "error")

def baixar_todos_docs_api(solicitacao_id, nome_usuario):
    print_separator()
    log_message(f"Buscando possíveis documentos em /solicitacao-servico/{solicitacao_id} ...", "info")
    url_info = f"{BASE_URL_SOLICITACAO}/{solicitacao_id}"
    try:
        resp_info = requests.get(url_info, cookies=cookies)
        if resp_info.status_code != 200:
            log_message(f"Erro {resp_info.status_code} ao acessar {url_info}", "error")
            return
        possiveis_docs = [
            "carteira-cr",
            "certificado-arma-craf",
            "listagem/emitir-guia",
            "emitir-guia",
        ]
        for doc_name in possiveis_docs:
            download_url = f"{BASE_URL_SOLICITACAO}/{solicitacao_id}/{doc_name}"
            log_message(f"Tentando baixar: {download_url}", "info")
            doc_resp = requests.get(download_url, cookies=cookies, stream=True)
            if doc_resp.status_code == 200:
                salvar_arquivo_em_pasta(doc_resp, nome_usuario, f"{solicitacao_id}_{doc_name}")
            else:
                log_message(f"Documento '{doc_name}' não encontrado (Status {doc_resp.status_code}).", "warning")
    except Exception as e:
        log_message(f"Exceção ao obter documentos extras da solicitação {solicitacao_id}: {e}", "error")
    print_separator()

def buscar_documentos():
    global is_running
    processos = obter_processos()
    driver = configurar_driver_com_devtools()
    print_separator()
    log_message("=== INICIANDO BUSCA DE DOCUMENTOS ===", "info")
    print_separator()
    nome_usuario = obter_nome_usuario(driver)
    log_message(f"Nome do usuário identificado como: {nome_usuario}", "debug")
    if label_usuario_logado is not None and nome_usuario != "Usuario_Desconhecido":
        label_usuario_logado.configure(text=f"Logado como: {nome_usuario}")
    for processo in processos:
        if not is_running:
            log_message("Busca interrompida pelo usuário.", "error")
            break
        print_separator()
        id_processo = processo["id"]
        log_message(f"Processando processo ID: {id_processo}", "info")
        documento_id = capturar_id_via_xhr(driver, id_processo)
        if documento_id is None:
            log_message(f"Não foi possível prosseguir sem ID para {id_processo}.", "error")
            continue
        existe_url = f"{BASE_EXISTE_HISTORICO}{documento_id}"
        try:
            resp_existe = requests.get(existe_url, cookies=cookies)
            if resp_existe.status_code == 200:
                existe_valor = resp_existe.json()
                if not existe_valor:
                    log_message(f"O ID {documento_id} não possui histórico. Pulando...", "warning")
                    continue
            else:
                log_message(f"Erro ao checar histórico. Status: {resp_existe.status_code}", "error")
                continue
        except Exception as e:
            log_message(f"Erro ao checar histórico: {e}", "error")
            continue
        listar_url = f"{BASE_LISTAR_HISTORICO}{documento_id}"
        try:
            resp_listar = requests.get(listar_url, cookies=cookies)
            if resp_listar.status_code == 200:
                data_listar = resp_listar.json()
                content = data_listar.get("content", [])
                if not content:
                    log_message(f"'listar-historico/{documento_id}' veio vazio. Pulando...", "warning")
                    continue
                id_final = content[0]["id"]
                log_message(f"ID FINAL capturado: {id_final}", "success")
            else:
                log_message(f"Falha ao listar histórico. Status: {resp_listar.status_code}", "error")
                continue
        except Exception as e:
            log_message(f"Erro ao listar histórico: {e}", "error")
            continue
        baixar_url = f"{BASE_BAIXAR_RELATORIO}{id_final}"
        try:
            resp_baixar = requests.get(baixar_url, cookies=cookies, stream=True)
            if resp_baixar.status_code == 200:
                salvar_arquivo_em_pasta(resp_baixar, nome_usuario, id_final)
            else:
                log_message(f"Falha ao baixar documento {id_final}. Status: {resp_baixar.status_code}", "warning")
        except Exception as e:
            log_message(f"Erro ao baixar documento {id_final}: {e}", "error")
        baixar_todos_docs_api(documento_id, nome_usuario)
        time.sleep(delay)
    driver.quit()
    if is_running:
        print_separator()
        log_message("Busca de documentos concluída!", "success")
        print_separator()
        messagebox.showinfo("Concluído", "Verifique a pasta no seu desktop para encontrar os documentos baixados.")
    else:
        print_separator()
        log_message("A busca foi interrompida antes de concluir todos os processos.", "error")
        print_separator()

def configurar_driver_com_devtools():
    service = EdgeService(EdgeChromiumDriverManager().install())
    options = webdriver.EdgeOptions()
    options.set_capability("ms:loggingPrefs", {"performance": "ALL"})
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
    driver = webdriver.Edge(service=service, options=options)
    return driver

def capturar_id_via_xhr(driver, id_processo):
    log_message(f"Capturando ID do processo '{id_processo}' via XHR...", "debug")
    try:
        driver.get_log("performance")
        linhas = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for linha in linhas:
            if id_processo in linha.text:
                log_message(f"Clicando no processo '{id_processo}' na tabela...", "debug")
                linha.click()
                time.sleep(3)
                break
        else:
            log_message(f"Processo '{id_processo}' não encontrado na tabela.", "error")
            return None
        performance_logs = driver.get_log("performance")
        for entry in performance_logs:
            msg = entry.get("message", "")
            if "existe-historico" in msg:
                try:
                    network_event = json.loads(msg)["message"]
                    method = network_event["method"]
                    if method == "Network.requestWillBeSent":
                        url = network_event["params"]["request"]["url"]
                        if "existe-historico" in url:
                            id_capturado = url.split("/")[-1]
                            log_message(f"ID capturado para o processo '{id_processo}': {id_capturado}", "success")
                            return id_capturado
                except Exception as e:
                    log_message(f"Erro ao processar log de performance: {e}", "error")
        log_message(f"Não foi possível capturar o ID para o processo '{id_processo}'.", "error")
        return None
    except Exception as e:
        log_message(f"Erro ao capturar o ID via XHR: {e}", "error")
        return None

def obter_processos():
    print_separator()
    log_message("Acessando página de processos...", "info")
    try:
        driver = configurar_driver_com_devtools()
        driver.get("https://sisgcorp.eb.mil.br/#/listar-processos")
        time.sleep(10)
        try:
            processos = driver.execute_script(
                """
                const rows = document.querySelectorAll('table tbody tr');
                return Array.from(rows).map(row => {
                    const cols = row.querySelectorAll('td');
                    const id = cols[0]?.innerText || '';
                    const status = cols[3]?.innerText || '';
                    return { id, status };
                }).filter(p => ['Pronto para Análise', 'Em análise', 'Deferido'].includes(p.status));
                """
            )
        except Exception as js_error:
            log_message(f"Erro ao executar script JavaScript: {js_error}", "error")
            processos = []
        driver.quit()
        if processos:
            log_message(f"Processos encontrados: {processos}", "success")
            return processos
        else:
            log_message("Nenhum processo encontrado. Verifique se há processos com os status desejados.", "error")
            return []
    except Exception as e:
        log_message(f"Erro ao obter processos: {e}", "error")
        return []

def iniciar_busca_por_usuario():
    global is_running, thread
    if not cookies:
        messagebox.showerror("Erro", "Por favor, configure os cookies antes de iniciar a busca.")
        return
    is_running = True
    thread = threading.Thread(target=buscar_documentos)
    thread.start()
    log_message("Iniciando a busca de documentos...", "info")

def parar_busca():
    global is_running
    is_running = False
    log_message("Interrompendo busca...", "error")

def consultar_processo_especifico():
    # Consulta um processo específico com base no número fornecido pelo usuário.
    global cookies
    process_number = process_number_entry.get()
    if not process_number.strip():
        log_message("Por favor, insira um número de processo válido.", "warning")
        return

    if not cookies:
        messagebox.showerror("Erro", "Por favor, configure os cookies antes de realizar a consulta.")
        return

    log_message(f"Iniciando consulta para o processo: {process_number}...", "info")
    try:
        driver = configurar_driver_com_devtools()
        driver.get("https://sisgcorp.eb.mil.br/#/listar-processos")
        time.sleep(10)  # Aguarda o carregamento da página
        
        # Verifica se o processo específico existe na tabela
        linhas = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for linha in linhas:
            if process_number in linha.text:
                log_message(f"Processo encontrado: {process_number}. Capturando dados...", "success")
                linha.click()
                time.sleep(3)

                # Reutiliza a lógica de captura de ID e download de documentos
                documento_id = capturar_id_via_xhr(driver, process_number)
                if documento_id is None:
                    log_message(f"Não foi possível capturar o ID para o processo {process_number}.", "error")
                    return
                
                baixar_todos_docs_api(documento_id, "Usuario")
                log_message(f"Documentos baixados para o processo: {process_number}.", "success")
                messagebox.showinfo("Concluído", f"Consulta para o processo {process_number} foi concluída com sucesso.")
                break
        else:
            log_message(f"Processo {process_number} não encontrado.", "warning")
            messagebox.showwarning("Aviso", f"Processo {process_number} não encontrado.")
    except Exception as e:
        log_message(f"Erro ao consultar o processo {process_number}: {e}", "error")
    finally:
        if 'driver' in locals():
            driver.quit()

def criar_interface():
    global btn_abrir_navegador, btn_capturar_cookies, btn_iniciar_busca, label_usuario_logado, log_textbox, process_number_entry
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.title("Buscador de Arquivos SisGCorp")
    root.geometry("800x720")  # Tamanho ajustado
    root.resizable(False, False)

    # Ajustando a cor de fundo para cinza claro
    bg_color = "#2E2E2E"  # Cinza mais claro

    # Container principal
    main_frame = ctk.CTkFrame(root, corner_radius=10, fg_color=bg_color)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Título
    title = ctk.CTkLabel(
        main_frame,
        text="Buscador de Arquivos SisGCorp - V1.2",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#C9AA79",
        fg_color=bg_color
    )
    title.pack(pady=10)

    # Botões
    frame_buttons = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=bg_color)
    frame_buttons.pack(pady=10)

    btn_abrir_navegador = ctk.CTkButton(
        frame_buttons,
        text="Abrir Navegador",
        command=abrir_navegador,
        width=120,
        height=35,
        corner_radius=20,
        fg_color="#C9AA79",
        text_color="black",
        hover_color="#A8835F"
    )
    btn_abrir_navegador.grid(row=0, column=0, padx=10)

    btn_capturar_cookies = ctk.CTkButton(
        frame_buttons,
        text="Capturar Cookies",
        command=capturar_cookies,
        width=120,
        height=35,
        corner_radius=20,
        fg_color="#C9AA79",
        text_color="black",
        hover_color="#A8835F"
    )
    btn_capturar_cookies.grid(row=0, column=1, padx=10)

    btn_iniciar_busca = ctk.CTkButton(
        frame_buttons,
        text="Iniciar Busca",
        command=iniciar_busca_por_usuario,
        width=120,
        height=35,
        corner_radius=20,
        fg_color="#C9AA79",
        text_color="black",
        hover_color="#A8835F"
    )
    btn_iniciar_busca.grid(row=0, column=2, padx=10)

    btn_parar = ctk.CTkButton(
        frame_buttons,
        text="Parar Busca",
        command=parar_busca,
        width=120,
        height=35,
        corner_radius=20,
        fg_color="#C9AA79",
        text_color="black",
        hover_color="#A8835F"
    )
    btn_parar.grid(row=0, column=3, padx=10)

    # Campo para Número do Processo
    frame_process_number = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=bg_color)
    frame_process_number.pack(pady=10)

    process_number_label = ctk.CTkLabel(
        frame_process_number,
        text="Número do Processo:",
        font=ctk.CTkFont(size=14),
        text_color="#C9AA79",
        fg_color=bg_color
    )
    process_number_label.grid(row=0, column=0, padx=5)

    process_number_entry = ctk.CTkEntry(
        frame_process_number,
        width=300,
        font=ctk.CTkFont(size=14),
        fg_color="#FFFFFF",
        text_color="black"
    )
    process_number_entry.grid(row=0, column=1, padx=5)

    btn_consultar_processo = ctk.CTkButton(
        frame_process_number,
        text="Consultar Processo",
        command=consultar_processo_especifico,
        width=150,
        height=35,
        corner_radius=20,
        fg_color="#C9AA79",
        text_color="black",
        hover_color="#A8835F"
    )
    btn_consultar_processo.grid(row=0, column=2, padx=10)

    # Informações do usuário
    label_usuario_logado = ctk.CTkLabel(
        main_frame,
        text="",
        font=ctk.CTkFont(size=16),
        text_color="#C9AA79",
        fg_color=bg_color
    )
    label_usuario_logado.pack(pady=5)

    # Texto de contribuição (parte em negrito)
    contribuicao_label_bold = ctk.CTkLabel(
        main_frame,
        text="Sua contribuição faz a diferença!",
        font=ctk.CTkFont(size=14, weight="bold"),  # Fonte em bold
        text_color="#C9AA79",
        fg_color=bg_color,
        justify="center",
        wraplength=700
    )
    contribuicao_label_bold.pack(pady=(10, 0))

    # Texto de contribuição (parte normal)
    contribuicao_label_normal = ctk.CTkLabel(
        main_frame,
        text=(
            "Apoie este projeto seguindo o Canal Portal do Mundo e baixando o aplicativo CAC Companion.\n"
            "Com sua ajuda, podemos continuar criando soluções incríveis para você!"
        ),
        font=ctk.CTkFont(size=14),  # Fonte normal
        text_color="#C9AA79",
        fg_color=bg_color,
        justify="center",
        wraplength=700
    )
    contribuicao_label_normal.pack(pady=(0, 5))


    # Botões de contribuição
    frame_contribuicao = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=bg_color)
    frame_contribuicao.pack(pady=10)

    btn_seguir_portal = ctk.CTkButton(
        frame_contribuicao,
        text="Seguir Canal Portal do Mundo",
        command=lambda: subprocess.Popen(['start', 'https://www.youtube.com/@PortaldoMundo'], shell=True),
        width=200,
        height=35,
        corner_radius=20,
        fg_color="#4A521F",
        text_color="white",
        hover_color="#218838"
    )
    btn_seguir_portal.grid(row=0, column=0, padx=10)

    btn_baixar_app = ctk.CTkButton(
        frame_contribuicao,
        text="Baixar CAC Companion",
        command=lambda: subprocess.Popen(['start', 'https://play.google.com/store/apps/details?id=com.catleapstudios.caccompanion&hl=pt_BR'], shell=True),
        width=200,
        height=35,
        corner_radius=20,
        fg_color="#4A521F",
        text_color="white",
        hover_color="#218838"
    )
    btn_baixar_app.grid(row=0, column=1, padx=10)


    # Log Frame
    log_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=bg_color)
    log_frame.pack(pady=10, fill="both", expand=True)

    log_label = ctk.CTkLabel(
        log_frame,
        text="Log de Atividades:",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="#C9AA79",
        fg_color=bg_color
    )
    log_label.pack(pady=(10, 0))

    log_textbox = scrolledtext.ScrolledText(
        log_frame,
        width=90,
        height=15,  # Diminuído para liberar espaço para o footer
        state='disabled',
        wrap='word',
        bg="#3E3E3E",  # Cinza para contraste com o texto
        fg="#FFFFFF",
        font=("Segoe UI Emoji", 10)  # Fonte que suporta emojis
    )
    log_textbox.pack(pady=10, padx=10, fill="both", expand=True)

    # Footer separado
    footer_frame = ctk.CTkFrame(root, corner_radius=0, fg_color=bg_color)
    footer_frame.pack(side="bottom", fill="x")

    footer = ctk.CTkLabel(
        footer_frame,
        text="Powered by Canal Portal do Mundo & CAC Companion - Versão 1.2",
        font=ctk.CTkFont(size=13),
        text_color="#C9AA79",
        fg_color=bg_color
    )
    footer.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    criar_interface()
