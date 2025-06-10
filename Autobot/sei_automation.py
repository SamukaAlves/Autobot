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
)
from selenium_handler import SEIAutomation
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automação SEI Funpresp-Jud")
        self.setGeometry(100, 100, 400, 250)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setStyleSheet("background-color: #dfdfdf;")

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Campos de entrada com placeholders mais escuros
        self.usuario_input = self._create_input_field("Usuário")
        self.senha_input = self._create_input_field("Senha", is_password=True)
        self.diretorio_input, diretorio_layout = self._create_directory_input()

        layout.addWidget(self.usuario_input)
        layout.addWidget(self.senha_input)
        layout.addLayout(diretorio_layout)

        # Botão de execução menor e centralizado
        self.btn_executar = QPushButton("Executar")
        self.btn_executar.setStyleSheet(
            "background-color: #0e509a; color: white; border-radius: 5px; padding: 4px;"
        )
        self.btn_executar.setFixedSize(150, 30)  # Tamanho reduzido
        self.btn_executar.clicked.connect(self.executar_automacao)

        # Layout para centralizar o botão
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
        """Cria o campo de entrada para diretório com um botão de seleção."""
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
            "background-color: #f7a833; color: white; border-radius: 5px; padding: 6px;"
        )
        btn_select.clicked.connect(lambda: self.select_directory(diretorio_input))

        hbox.addWidget(diretorio_input)
        hbox.addWidget(btn_select)

        return diretorio_input, hbox  # Retorna ambos separadamente

    def select_directory(self, input_field):
        directory = QFileDialog.getExistingDirectory(self, "Selecionar Diretório")
        if directory:
            input_field.setText(directory)

    def executar_automacao(self):
        usuario = self.usuario_input.text()
        senha = self.senha_input.text()
        diretorio = self.diretorio_input.text().strip()  # Remove espaços extras

        # Normaliza o caminho para garantir compatibilidade
        diretorio = os.path.normpath(diretorio)

        if not all([usuario, senha, diretorio]):
            QMessageBox.warning(self, "Erro", "Todos os campos são obrigatórios!")
            return

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
