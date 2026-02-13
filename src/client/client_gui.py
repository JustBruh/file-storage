import sys
import logging
from PyQt5 import QtWidgets

from src.client.lib.client_lib import *


class FSSClientGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File Storage Client")

        layout = QtWidgets.QFormLayout()

        self.server_input = QtWidgets.QLineEdit()
        self.command_input = QtWidgets.QLineEdit()
        self.file_name_input = QtWidgets.QLineEdit()
        self.new_file_name_input = QtWidgets.QLineEdit()
        self.login_input = QtWidgets.QLineEdit()
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.new_username_input = QtWidgets.QLineEdit()

        self.run_button = QtWidgets.QPushButton("Run Command")
        self.run_button.clicked.connect(self.run_command)

        self.output_box = QtWidgets.QTextEdit()
        self.output_box.setReadOnly(True)

        layout.addRow("Server:", self.server_input)
        layout.addRow("Command:", self.command_input)
        layout.addRow("File Name:", self.file_name_input)
        layout.addRow("New File Name:", self.new_file_name_input)
        layout.addRow("Login:", self.login_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("New Username:", self.new_username_input)
        layout.addRow(self.run_button)
        layout.addRow("Output:", self.output_box)

        self.setLayout(layout)
        self.resize(500, 400)

    def run_command(self):
        logging.basicConfig(filename='client-gui.log', level=logging.ERROR)
        logger = logging.getLogger(__name__)

        server = self.server_input.text()
        command = self.command_input.text()
        file_name = self.file_name_input.text()
        new_file_name = self.new_file_name_input.text()
        login = self.login_input.text() or "anonymous"
        password = self.password_input.text() or "anonymous"
        new_username = self.new_username_input.text()

        client = FileStorageClient()

        class Args:
            pass

        args = Args()
        args.server = server
        args.command = command
        args.file_name = file_name
        args.new_file_name = new_file_name
        args.login = login
        args.password = password
        args.new_username = new_username

        try:
            client.connect_and_authenticate(server, args, logger)
            result = client.handle_command(command, args)
            self.output_box.setText(str(result))
            client.connection.close()

        except Exception as ex:
            self.output_box.setText(str(ex))
            logger.error(f"Exception raised: {ex}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = FSSClientGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()