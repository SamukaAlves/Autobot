import os
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QFileDialog,
    QCheckBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from dotenv import load_dotenv

from selenium_handler import SEIAutomation


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automação SEI Funpresp-Jud")
        self.setGeometry(100, 100, 400, 270)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setStyleSheet("background-color: #dfdfdf;")

        load_dotenv()

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Entradas de usuário e senha
        self.usuario_input = self._create_input_field("Usuário")
        self.senha_input = self._create_input_field("Senha", is_password=True)
        self.diretorio_input, diretorio_layout = self._create_directory_input()

        # Preencher com valores salvos
        self.usuario_input.setText(os.getenv("SEI_USUARIO", ""))
        self.senha_input.setText(os.getenv("SEI_SENHA", ""))

        # Checkbox salvar login
        self.salvar_login_checkbox = QCheckBox("Salvar informações de login")
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.senha_input)
        layout.addLayout(diretorio_layout)
        layout.addWidget(self.salvar_login_checkbox)

        # Botão Executar
        self.btn_executar = QPushButton("Executar")
        self.btn_executar.setStyleSheet(
            "background-color: #0e509a; color: white; border-radius: 5px; padding: 4px;"
        )
        self.btn_executar.setFixedSize(150, 30)
        self.btn_executar.clicked.connect(self.executar_automacao)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_executar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _create_input_field(self, placeholder, is_password=False):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)

        input_field.setStyleSheet(
            """
            background-color: #ffffff;
            color: black;
            border-radius: 5px;
            padding: 6px;
            QLineEdit::placeholderText { color: #555555; }
        """
        )
        return input_field

    def _create_directory_input(self):
        hbox = QHBoxLayout()
        diretorio_input = QLineEdit()
        diretorio_input.setPlaceholderText("Diretório dos arquivos")
        diretorio_input.setStyleSheet(
            """
            background-color: #ffffff;
            color: black;
            border-radius: 5px;
            padding: 6px;
            QLineEdit::placeholderText { color: #555555; }
        """
        )
        btn_select = QPushButton("Selecionar")
        btn_select.setStyleSheet(
            "background-color: #f7a833; color: black; border-radius: 5px; padding: 6px;"
        )
        btn_select.clicked.connect(lambda: self.select_directory(diretorio_input))

        hbox.addWidget(diretorio_input)
        hbox.addWidget(btn_select)
        return diretorio_input, hbox

    def select_directory(self, input_field):
        directory = QFileDialog.getExistingDirectory(self, "Selecionar Diretório")
        if directory:
            input_field.setText(directory)

    def executar_automacao(self):
        usuario = self.usuario_input.text()
        senha = self.senha_input.text()
        diretorio = os.path.normpath(self.diretorio_input.text().strip())

        if not all([usuario, senha, diretorio]):
            QMessageBox.warning(self, "Erro", "Todos os campos são obrigatórios!")
            return

        # Salvar no .env se checkbox estiver marcado
        if self.salvar_login_checkbox.isChecked():
            with open(".env", "w") as f:
                f.write(f"SEI_USUARIO={usuario}\n")
                f.write(f"SEI_SENHA={senha}\n")

        try:
            automacao = SEIAutomation()
            automacao.executar(usuario, senha, diretorio)
            QMessageBox.information(self, "Sucesso", "Automação concluída com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro durante a execução: {str(e)}")
        finally:
            self.usuario_input.clear()
            self.senha_input.clear()
            self.diretorio_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
