"""Pages for the School Portal: role selection, login and sign up."""

from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets, uic

import auth

BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR / "ui"
ASSETS = BASE_DIR / "assets"

ROLES = ("student", "teacher")

# Everything that differs between the two roles lives here.
ROLE_COPY = {
    "student": {
        "signin_title": "Student sign in",
        "signup_title": "Create a student account",
        "id_label": "Student ID",
        "id_hint": "e.g. 2026-00123",
        "group_label": "Grade level",
        "groups": ["Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12", "College"],
    },
    "teacher": {
        "signin_title": "Teacher sign in",
        "signup_title": "Create a teacher account",
        "id_label": "Employee ID",
        "id_hint": "e.g. T-0456",
        "group_label": "Department",
        "groups": ["Mathematics", "Science", "English", "Social Studies",
                   "Arts and PE", "Technology", "Other"],
    },
}


# ---------------------------------------------------------------- helpers
def set_icon(label: QtWidgets.QLabel, filename: str, size: int) -> None:
    label.setPixmap(QtGui.QIcon(str(ASSETS / filename)).pixmap(size, size))


def repolish(widget: QtWidgets.QWidget) -> None:
    """Re-apply the stylesheet after a dynamic property changed."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def show_message(label: QtWidgets.QLabel, text: str = "", state: str = "error") -> None:
    label.setProperty("state", state)
    repolish(label)
    label.setText(text)
    label.setVisible(bool(text))


def toggle_echo(edits, visible: bool) -> None:
    mode = QtWidgets.QLineEdit.Normal if visible else QtWidgets.QLineEdit.Password
    for edit in edits:
        edit.setEchoMode(mode)


class BasePage(QtWidgets.QWidget):
    """Loads a .ui file into this widget and adds the panel shadow."""

    UI_FILE = ""

    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        uic.loadUi(str(UI_DIR / self.UI_FILE), self)

        shadow = QtWidgets.QGraphicsDropShadowEffect(self.panel)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QtGui.QColor(15, 58, 138, 40))
        self.panel.setGraphicsEffect(shadow)


# ---------------------------------------------------------- role selection
class RolePage(BasePage):
    UI_FILE = "role_select.ui"

    role_chosen = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.role = None
        self.cards = {
            "student": (self.studentCard, self.studentRadio),
            "teacher": (self.teacherCard, self.teacherRadio),
        }

        set_icon(self.logoMark, "logo.svg", 24)
        set_icon(self.studentIcon, "student.svg", 30)
        set_icon(self.teacherIcon, "teacher.svg", 30)

        for role, (card, _radio) in self.cards.items():
            card.setProperty("roleId", role)
            card.setFocusPolicy(QtCore.Qt.StrongFocus)
            card.installEventFilter(self)
            for lbl in card.findChildren(QtWidgets.QLabel):
                lbl.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        self.continueButton.clicked.connect(self._confirm)

    def eventFilter(self, obj, event):
        role = obj.property("roleId") if isinstance(obj, QtWidgets.QFrame) else None
        if role in ROLES:
            if (event.type() == QtCore.QEvent.MouseButtonPress
                    and event.button() == QtCore.Qt.LeftButton):
                self._select(role)
                return True
            if event.type() == QtCore.QEvent.KeyPress and event.key() in (
                    QtCore.Qt.Key_Space, QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                self._select(role)
                return True
        return super().eventFilter(obj, event)

    def _select(self, role: str) -> None:
        self.role = role
        for name, (card, radio) in self.cards.items():
            active = name == role
            card.setProperty("selected", active)
            radio.setProperty("selected", active)
            radio.setText("\u2713" if active else "")
            repolish(card)
            repolish(radio)
        self.continueButton.setEnabled(True)
        self.continueButton.setText(f"Continue as {role.capitalize()}")

    def _confirm(self) -> None:
        if self.role:
            self.role_chosen.emit(self.role)


# ------------------------------------------------------------------- login
class LoginPage(BasePage):
    UI_FILE = "login.ui"

    back_requested = QtCore.pyqtSignal()
    signup_requested = QtCore.pyqtSignal()
    authenticated = QtCore.pyqtSignal(str, dict)  # role, user

    def __init__(self):
        super().__init__()
        self.role = None
        set_icon(self.miniLogo, "logo.svg", 18)
        show_message(self.messageLabel)

        self.backButton.clicked.connect(self.back_requested)
        self.signUpLink.clicked.connect(self.signup_requested)
        self.signInButton.clicked.connect(self._submit)
        self.emailEdit.returnPressed.connect(self.passwordEdit.setFocus)
        self.passwordEdit.returnPressed.connect(self._submit)
        self.showPasswordCheck.toggled.connect(
            lambda on: toggle_echo([self.passwordEdit], on))

    def set_role(self, role: str) -> None:
        self.role = role
        self.headingLabel.setText(ROLE_COPY[role]["signin_title"])
        self.passwordEdit.clear()
        self.showPasswordCheck.setChecked(False)
        show_message(self.messageLabel)

    def prefill(self, email: str, message: str = "") -> None:
        self.emailEdit.setText(email)
        self.passwordEdit.clear()
        show_message(self.messageLabel, message, "success")
        self.passwordEdit.setFocus()

    def focus_first(self) -> None:
        self.emailEdit.setFocus()

    def _submit(self) -> None:
        email = self.emailEdit.text().strip()
        password = self.passwordEdit.text()
        if not email or not password:
            show_message(self.messageLabel, "Enter your email and password.")
            return
        try:
            user = auth.authenticate(self.role, email, password)
        except auth.AuthError as exc:
            show_message(self.messageLabel, str(exc))
            self.passwordEdit.selectAll()
            self.passwordEdit.setFocus()
            return
        show_message(self.messageLabel)
        self.passwordEdit.clear()
        self.authenticated.emit(self.role, user)


# ----------------------------------------------------------------- sign up
class SignupPage(BasePage):
    UI_FILE = "signup.ui"

    back_requested = QtCore.pyqtSignal()   # go back to login
    registered = QtCore.pyqtSignal(str)    # email of the new account

    def __init__(self):
        super().__init__()
        self.role = None
        set_icon(self.miniLogo, "logo.svg", 18)
        show_message(self.messageLabel)

        self.backButton.clicked.connect(self.back_requested)
        self.loginLink.clicked.connect(self.back_requested)
        self.createButton.clicked.connect(self._submit)
        for edit in (self.fullNameEdit, self.idEdit, self.emailEdit, self.passwordEdit):
            edit.returnPressed.connect(self.focusNextChild)
        self.confirmEdit.returnPressed.connect(self._submit)
        self.showPasswordCheck.toggled.connect(
            lambda on: toggle_echo([self.passwordEdit, self.confirmEdit], on))

    def set_role(self, role: str) -> None:
        self.role = role
        copy = ROLE_COPY[role]
        self.headingLabel.setText(copy["signup_title"])
        self.idLabel.setText(copy["id_label"])
        self.idEdit.setPlaceholderText(copy["id_hint"])
        self.groupLabel.setText(copy["group_label"])
        self.groupCombo.clear()
        self.groupCombo.addItems(copy["groups"])
        self._clear()

    def focus_first(self) -> None:
        self.fullNameEdit.setFocus()

    def _clear(self) -> None:
        for edit in (self.fullNameEdit, self.idEdit, self.emailEdit,
                     self.passwordEdit, self.confirmEdit):
            edit.clear()
        self.showPasswordCheck.setChecked(False)
        show_message(self.messageLabel)

    def _submit(self) -> None:
        name = self.fullNameEdit.text().strip()
        school_id = self.idEdit.text().strip()
        email = self.emailEdit.text().strip()
        password = self.passwordEdit.text()
        confirm = self.confirmEdit.text()

        if not all((name, school_id, email, password, confirm)):
            error = "Fill in all fields to continue."
        elif not auth.is_valid_email(email):
            error = "Enter a valid email address."
        elif len(password) < auth.MIN_PASSWORD_LENGTH:
            error = f"Password must be at least {auth.MIN_PASSWORD_LENGTH} characters."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            error = ""

        if error:
            show_message(self.messageLabel, error)
            return

        try:
            auth.register(self.role, name, school_id,
                          self.groupCombo.currentText(), email, password)
        except auth.AuthError as exc:
            show_message(self.messageLabel, str(exc))
            return

        self._clear()
        self.registered.emit(email.lower())
