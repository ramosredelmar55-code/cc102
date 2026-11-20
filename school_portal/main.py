"""School Portal - student and teacher login (PyQt5 + Qt Designer).

Run:
    pip install PyQt5
    python main.py

Edit the layouts visually with Qt Designer, for example:
    designer ui/login.ui
Colors and fonts live in style.qss (loaded when the app starts).
"""

import sys
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

import auth
from pages import ASSETS, LoginPage, RolePage, SignupPage

BASE_DIR = Path(__file__).resolve().parent


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("School Portal")
        self.resize(960, 740)
        self.setMinimumSize(720, 700)

        self.role = None
        self.role_page = RolePage()
        self.login_page = LoginPage()
        self.signup_page = SignupPage()

        self.stack = QtWidgets.QStackedWidget()
        for page in (self.role_page, self.login_page, self.signup_page):
            self.stack.addWidget(page)
        self.setCentralWidget(self.stack)

        self.role_page.role_chosen.connect(self.show_login)
        self.login_page.back_requested.connect(lambda: self.stack.setCurrentWidget(self.role_page))
        self.login_page.signup_requested.connect(self.show_signup)
        self.login_page.authenticated.connect(self.on_authenticated)
        self.signup_page.back_requested.connect(self.show_login_again)
        self.signup_page.registered.connect(self.on_registered)

    # ---------- navigation ----------
    def show_login(self, role: str) -> None:
        self.role = role
        self.login_page.set_role(role)
        self.stack.setCurrentWidget(self.login_page)
        self.login_page.focus_first()

    def show_login_again(self) -> None:
        self.stack.setCurrentWidget(self.login_page)
        self.login_page.focus_first()

    def show_signup(self) -> None:
        self.signup_page.set_role(self.role)
        self.stack.setCurrentWidget(self.signup_page)
        self.signup_page.focus_first()

    # ---------- results ----------
    def on_registered(self, email: str) -> None:
        self.login_page.prefill(email, "Account created. Sign in to continue.")
        self.stack.setCurrentWidget(self.login_page)

    def on_authenticated(self, role: str, user: dict) -> None:
        """Open your dashboard here. For now, confirm the sign in."""
        QtWidgets.QMessageBox.information(
            self,
            "School Portal",
            f"Signed in as {user['full_name']} ({role}).\n\nConnect your {role} dashboard here.",
        )


def load_stylesheet(app: QtWidgets.QApplication) -> None:
    qss = (BASE_DIR / "style.qss").read_text(encoding="utf-8")
    app.setStyleSheet(qss.replace("@ASSETS@", ASSETS.as_posix()))


def main() -> int:
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    auth.init_db()
    app = QtWidgets.QApplication(sys.argv)
    load_stylesheet(app)

    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
