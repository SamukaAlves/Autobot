from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import re
from datetime import datetime
import logging
import traceback
import pyautogui
import time


class SEIAutomation:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def executar(self, usuario, senha, diretorio):
        try:
            self.logger.info("Iniciando processo de automação")
            self.login(usuario, senha)
            self.processar_arquivos(diretorio)
        except Exception as e:
            self.logger.error(f"Erro durante a execução: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
        finally:
            self.logger.info("Finalizando automação")
            try:
                self.driver.quit()
            except:
                pass

    def login(self, usuario, senha):
        self.driver.get("https://sei.funprespjud.com.br/")

        # Login
        self.wait.until(
            EC.presence_of_element_located((By.ID, "txtUsuario"))
        ).send_keys(usuario)
        self.driver.find_element(By.ID, "pwdSenha").send_keys(senha)
        self.driver.find_element(By.ID, "sbmAcessar").click()
        # Buscar processo

    def buscar_processo(self, processo):
        campo_pesquisa = self.wait.until(
            EC.presence_of_element_located((By.ID, "txtPesquisaRapida"))
        )
        campo_pesquisa.clear()
        campo_pesquisa.send_keys(processo)
        campo_pesquisa.send_keys(Keys.RETURN)

    def processar_arquivos(self, diretorio):
        self.logger.info(f"Iniciando processamento de arquivos em {diretorio}")
        arquivos = [f for f in os.listdir(diretorio) if f.endswith(".pdf")]

        for arquivo in arquivos:
            try:
                self.logger.info(f"Processando arquivo: {arquivo}")
                processo_base = arquivo.replace(".pdf", "")
                processo = processo_base.replace(".", "/")

                self.buscar_processo(processo)
                self.incluir_documento(processo, diretorio)

                self.logger.info(f"Arquivo {arquivo} processado com sucesso")

            except Exception as e:
                self.logger.error(f"Erro ao processar {arquivo}: {str(e)}")
                self.logger.error(traceback.format_exc())
                continue

    def escrever_texto_robusto(self, texto, intervalo=0.1, tentativas=3):
        """
        Método para digitar o texto com pyautogui.write de forma robusta,
        incluindo tentativas e intervalo entre as teclas.
        """
        for tentativa in range(tentativas):
            pyautogui.write(texto, interval=intervalo)
            time.sleep(0.5)  # Aguarda processamento
            # Aqui poderia ter validação de sucesso, se possível
            self.logger.info(f"Tentativa {tentativa + 1}: Texto digitado.")
            break  # Remove esta linha para permitir múltiplas tentativas

    def incluir_documento(self, processo, diretorio):
        try:
            self.logger.info(f"Tentando incluir documento para processo {processo}")

            # Esperar a página carregar completamente
            self.driver.implicitly_wait(5)

            # Tentar clicar no botão várias vezes se necessário
            max_tentativas = 3
            for tentativa in range(max_tentativas):
                try:
                    self.logger.info(f"Tentativa {tentativa + 1} de clicar no botão")

                    # Esperar explicitamente pela presença do frame principal (se existir)
                    try:
                        frame_principal = self.wait.until(
                            EC.presence_of_element_located((By.NAME, "ifrVisualizacao"))
                        )
                        self.driver.switch_to.frame(frame_principal)
                        self.logger.info("Mudou para o frame principal")
                    except:
                        self.logger.info("Não foi necessário mudar de frame")

                    # Script mais robusto para encontrar e clicar no botão
                    script_click = """
                        function encontrarEClicar() {
                            var links = document.getElementsByTagName('a');
                            for(var i = 0; i < links.length; i++) {
                                var link = links[i];
                                if(link.href.includes('acao=documento_escolher_tipo') &&
                                   link.querySelector('img[src*="documento_incluir.svg"]')) {
                                    link.click();
                                    return true;
                                }
                            }
                            return false;
                        }
                        return encontrarEClicar();
                    """

                    clicked = self.driver.execute_script(script_click)

                    if clicked:
                        self.logger.info("Botão encontrado e clicado com sucesso")
                        break
                    else:
                        self.logger.warning("Botão não encontrado nesta tentativa")

                except Exception as e:
                    self.logger.error(f"Erro na tentativa {tentativa + 1}: {str(e)}")
                    if tentativa == max_tentativas - 1:
                        raise

                # Voltar ao contexto padrão antes da próxima tentativa
                try:
                    self.driver.switch_to.default_content()
                except:
                    pass

                # Pequena pausa entre tentativas
                time.sleep(2)

            # Após clicar no botão "Incluir Documento", vamos selecionar o documento externo
            try:
                self.logger.info("Tentando selecionar documento externo")

                # Esperar a página carregar
                self.driver.implicitly_wait(5)

                # Tentar clicar no link "Externo" várias vezes se necessário
                max_tentativas = 3
                for tentativa in range(max_tentativas):
                    try:
                        self.logger.info(
                            f"Tentativa {tentativa + 1} de clicar em 'Externo'"
                        )

                        # Script para encontrar e clicar no link "Externo"
                        script_click = """
                            function encontrarEClicarExterno() {
                                var links = document.getElementsByTagName('a');
                                for(var i = 0; i < links.length; i++) {
                                    var link = links[i];
                                    if(link.href.includes('acao=documento_receber') && 
                                       link.textContent.trim() === 'Externo' &&
                                       link.className === 'ancoraOpcao') {
                                        link.click();
                                        return true;
                                    }
                                }
                                return false;
                            }
                            return encontrarEClicarExterno();
                        """

                        clicked = self.driver.execute_script(script_click)

                        if clicked:
                            self.logger.info(
                                "Link 'Externo' encontrado e clicado com sucesso"
                            )
                            break
                        else:
                            self.logger.warning(
                                "Link 'Externo' não encontrado nesta tentativa"
                            )

                    except Exception as e:
                        self.logger.error(
                            f"Erro na tentativa {tentativa + 1}: {str(e)}"
                        )
                        if tentativa == max_tentativas - 1:
                            raise

                    # Pequena pausa entre tentativas
                    time.sleep(2)

                self.logger.info("Continuando com o preenchimento do formulário")

                # Continuar com o resto do processo
                self.driver.switch_to.default_content()

                # Mudar para o iframe antes de procurar elementos do formulário
                self.wait.until(
                    EC.frame_to_be_available_and_switch_to_it(
                        (By.ID, "ifrVisualizacao")
                    )
                )
                self.logger.info("Mudou para o iframe 'ifrVisualizacao'")

                # Aguardar e clicar no 'Tipo de Documento'
                select_element = self.wait.until(
                    EC.presence_of_element_located((By.ID, "selSerie"))
                )
                select_element.click()

                # Aguardar e clicar na opção "Comprovante"
                self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//select[@id='selSerie']/option[text()='Comprovante']",
                        )
                    )
                ).click()

                # Aguardar um momento para a seleção ser processada
                time.sleep(1)

                # Preencher a data
                data_atual = datetime.now().strftime("%d/%m/%Y")
                self.driver.execute_script(
                    f"document.getElementById('txtDataElaboracao').value = '{data_atual}';"
                )
                time.sleep(2)
                # Preencher formulário

                # Formato nato-digital
                self.driver.find_element(By.ID, "divOptNato").click()

                # Garantir que o fieldset de nível de acesso esteja visível
                self.wait.until(
                    EC.presence_of_element_located((By.ID, "fldNivelAcesso"))
                )

                # Nível de acesso público
                self.driver.find_element(By.ID, "divOptPublico").click()

                # Anexar arquivo
                self.logger.info("Anexando arquivo")

                # Aguardar a presença da aba de anexos
                self.wait.until(EC.presence_of_element_located((By.ID, "frmAnexos")))

                # Garantir que o label 'Anexar Arquivo' esteja acessível antes de interagir
                lbl_arquivo = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "lblArquivo"))
                )

                # Clicar no label para abrir o explorador de arquivos
                lbl_arquivo.click()
                self.logger.info("Explorador de arquivos acionado")

                # Aguardar um pequeno intervalo para garantir que o explorador abriu
                time.sleep(2)

                # Garantir que o explorador de arquivos está aberto
                tentativas = 3
                for tentativa in range(tentativas):
                    if pyautogui.getActiveWindow() is None:
                        self.logger.warning(
                            f"Tentativa {tentativa + 1}: Explorador não detectado, tentando novamente..."
                        )
                        lbl_arquivo.click()
                        time.sleep(2)
                    else:
                        break

                # Definir o nome do arquivo e caminho
                nome_arquivo = processo.replace("/", ".") + ".pdf"
                caminho_arquivo = os.path.join(diretorio, nome_arquivo)
                time.sleep(
                    2
                )  # Aguardar um momento para garantir que o explorador está ativo

                # Usar método robusto para digitar o caminho do arquivo
                self.escrever_texto_robusto(
                    caminho_arquivo, intervalo=0.025, tentativas=3
                )
                time.sleep(2)  # Pequeno intervalo antes de pressionar Enter
                pyautogui.press("enter")
                self.logger.info(f"Arquivo {nome_arquivo} selecionado")

                # Aguarde um breve momento para garantir que a janela está ativa
                time.sleep(2)

                # Pressiona 'Tab' para mover o foco para o botão de salvar
                pyautogui.press("tab")

                # Aguarda um pequeno intervalo para garantir a mudança de foco
                time.sleep(0.5)

                # Pressiona 'Enter' para confirmar o salvamento
                pyautogui.press("enter")
                time.sleep(3)  # Aguardar o arquivo ser carregado
                self.logger.info("Documento salvo com sucesso")

                # Voltar ao contexto principal
                self.driver.switch_to.default_content()

            except Exception as e:
                self.logger.error(f"Erro ao incluir documento: {str(e)}")
                self.logger.error(traceback.format_exc())
                raise

        except Exception as e:
            self.logger.error(f"Erro ao incluir documento: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
