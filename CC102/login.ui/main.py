import sys
import hashlib

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QFrame, QMessageBox,
    QGraphicsDropShadowEffect,
)

# --- Demo credential store -------------------------------------------------
# Replace this dict with a real database / API lookup in production.
def _h(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


USERS = {
    "student": {
        "alice": _h("student123"),
        "bob":   _h("bobpass456"),
    },
    "teacher": {
        "msreyes": _h("teach789"),
    },
}

ROLE_LABELS = {"Student": "student", "Teacher": "teacher"}

# --- Theme tokens ----------------------------------------------------------
BLUE_700 = "#1d4ed8"
BLUE_600 = "#2563eb"
BLUE_500 = "#3b82f6"
BLUE_100 = "#dbeafe"
BLUE_50  = "#eff6ff"
WHITE    = "#ffffff"
GREY_900 = "#0f172a"
GREY_500 = "#64748b"
GREY_300 = "#cbd5e1"
RED_600  = "#dc2626"


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("School Portal — Sign In")
        self.setFixedSize(880, 560)
        self._build_ui()
        self._apply_styles()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_brand_panel())

        right = QWidget()
        right.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(60, 40, 60, 40)
        right_layout.addStretch()
        right_layout.addWidget(self._build_card())
        right_layout.addStretch()
        outer.addWidget(right, 1)

    def _build_brand_panel(self):
        """Left-hand blue panel with the product mark and a bit of copy."""
        panel = QWidget()
        panel.setObjectName("brandPanel")
        panel.setFixedWidth(340)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 50, 40, 50)

        badge = QLabel("SP")
        badge.setObjectName("badge")
        badge.setFixedSize(58, 58)
        badge.setAlignment(Qt.AlignCenter)

        name = QLabel("School Portal")
        name.setObjectName("brandName")

        tagline = QLabel("One place for lessons,\ngrades and announcements.")
        tagline.setObjectName("brandTagline")
        tagline.setWordWrap(True)

        layout.addWidget(badge)
        layout.addSpacing(18)
        layout.addWidget(name)
        layout.addWidget(tagline)
        layout.addStretch()
        layout.addWidget(self._QLabel_muted("© 2026 School Portal"))
        return panel

    @staticmethod
    def _QLabel_muted(text):
        lbl = QLabel(text)
        lbl.setObjectName("brandFooter")
        return lbl

    def _build_card(self):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(400)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(38)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(37, 99, 235, 45))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(34, 32, 34, 32)
        layout.setSpacing(6)

        title = QLabel("Sign in")
        title.setObjectName("title")

        subtitle = QLabel("Choose your role to continue")
        subtitle.setObjectName("subtitle")

        # Role toggle made of two pill buttons
        self.role_row = QHBoxLayout()
        self.role_row.setSpacing(8)
        self.role_buttons = {}
        for label in ROLE_LABELS:
            btn = QPushButton(label)
            btn.setObjectName("rolePill")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, l=label: self._set_role(l))
            self.role_buttons[label] = btn
            self.role_row.addWidget(btn)
        self.role_buttons["Student"].setChecked(True)

        # Credentials
        self.username = QLineEdit()
        self.username.setPlaceholderText("Student ID or username")
        self.username.setObjectName("input")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setObjectName("input")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self._attempt_login)

        self.show_pw = QPushButton("Show")
        self.show_pw.setObjectName("ghost")
        self.show_pw.setCheckable(True)
        self.show_pw.setCursor(Qt.PointingHandCursor)
        self.show_pw.setFixedWidth(58)
        self.show_pw.toggled.connect(self._toggle_password)

        pw_row = QHBoxLayout()
        pw_row.setSpacing(8)
        pw_row.addWidget(self.password, 1)
        pw_row.addWidget(self.show_pw)

        self.login_btn = QPushButton("Log in")
        self.login_btn.setObjectName("primary")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setMinimumHeight(44)
        self.login_btn.clicked.connect(self._attempt_login)

        self.status = QLabel("")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(18)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(14)
        layout.addLayout(self.role_row)
        layout.addSpacing(12)
        layout.addWidget(self.username)
        layout.addSpacing(4)
        layout.addLayout(pw_row)
        layout.addSpacing(4)
        layout.addWidget(self.status)
        layout.addSpacing(6)
        layout.addWidget(self.login_btn)
        layout.addSpacing(12)
        layout.addWidget(
            self._centered("Forgot your password? Contact the registrar."),
        )

        self.username.setFocus()
        return card

    @staticmethod
    def _centered(text):
        lbl = QLabel(text)
        lbl.setObjectName("hint")
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    # --------------------------------------------------------------- styling
    def _apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {WHITE};
                color: {GREY_900};
                font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
                font-size: 14px;
            }}

            /* ---- left brand panel ---- */
            QWidget#brandPanel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 {BLUE_700}, stop:1 {BLUE_500});
            }}
            QLabel#badge {{
                background: rgba(255,255,255,0.18);
                color: {WHITE};
                border: 1px solid rgba(255,255,255,0.45);
                border-radius: 14px;
                font-size: 21px;
                font-weight: 700;
            }}
            QLabel#brandName {{
                color: {WHITE};
                font-size: 24px;
                font-weight: 700;
                background: transparent;
            }}
            QLabel#brandTagline {{
                color: {BLUE_100};
                font-size: 14px;
                line-height: 20px;
                background: transparent;
            }}
            QLabel#brandFooter {{
                color: rgba(255,255,255,0.65);
                font-size: 12px;
                background: transparent;
            }}

            /* ---- right panel + card ---- */
            QWidget#rightPanel {{ background: {BLUE_50}; }}
            QFrame#card {{
                background: {WHITE};
                border: 1px solid {BLUE_100};
                border-radius: 16px;
            }}

            QLabel#title {{ font-size: 26px; font-weight: 700; color: {GREY_900}; }}
            QLabel#subtitle {{ font-size: 13px; color: {GREY_500}; }}
            QLabel#hint {{ font-size: 12px; color: {GREY_500}; }}
            QLabel#status {{ font-size: 12.5px; color: {RED_600}; }}

            /* ---- role pills ---- */
            QPushButton#rolePill {{
                background: {BLUE_50};
                color: {BLUE_700};
                border: 1px solid {BLUE_100};
                border-radius: 10px;
                padding: 9px 14px;
                font-weight: 600;
            }}
            QPushButton#rolePill:hover {{ background: {BLUE_100}; }}
            QPushButton#rolePill:checked {{
                background: {BLUE_600};
                color: {WHITE};
                border: 1px solid {BLUE_600};
            }}

            /* ---- inputs ---- */
            QLineEdit#input {{
                background: {WHITE};
                border: 1px solid {GREY_300};
                border-radius: 10px;
                padding: 11px 13px;
                selection-background-color: {BLUE_500};
            }}
            QLineEdit#input:hover {{ border: 1px solid {BLUE_500}; }}
            QLineEdit#input:focus {{
                border: 2px solid {BLUE_600};
                padding: 10px 12px;   /* keeps size stable with thicker border */
            }}

            /* ---- buttons ---- */
            QPushButton#primary {{
                background: {BLUE_600};
                color: {WHITE};
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton#primary:hover   {{ background: {BLUE_700}; }}
            QPushButton#primary:pressed {{ background: #1e40af; }}
            QPushButton#primary:disabled {{ background: {GREY_300}; color: {WHITE}; }}

            QPushButton#ghost {{
                background: {BLUE_50};
                color: {BLUE_700};
                border: 1px solid {BLUE_100};
                border-radius: 10px;
                padding: 11px 8px;
                font-size: 12.5px;
                font-weight: 600;
            }}
            QPushButton#ghost:hover {{ background: {BLUE_100}; }}
            QPushButton#ghost:checked {{ background: {BLUE_600}; color: {WHITE};
                                         border: 1px solid {BLUE_600}; }}
        """)

    # ------------------------------------------------------------- behaviour
    def _set_role(self, label: str):
        for name, btn in self.role_buttons.items():
            btn.setChecked(name == label)
        self.status.clear()
        self.password.clear()
        role = ROLE_LABELS[label]
        self.username.setPlaceholderText(
            "Student ID or username" if role == "student" else "Teacher username"
        )
        self.username.setFocus()

    def _toggle_password(self, checked: bool):
        self.password.setEchoMode(
            QLineEdit.Normal if checked else QLineEdit.Password
        )
        self.show_pw.setText("Hide" if checked else "Show")

    def _attempt_login(self):
        role = next(
            (ROLE_LABELS[l] for l, b in self.role_buttons.items() if b.isChecked()),
            "student",
        )
        user = self.username.text().strip().lower()
        pw = self.password.text()

        if not user or not pw:
            self.status.setText("Please enter both a username and a password.")
            return

        expected = USERS.get(role, {}).get(user)
        if expected is None or expected != _h(pw):
            self.status.setText("Incorrect username or password for this role.")
            self.password.clear()
            self.password.setFocus()
            return

        self.status.clear()
        self._open_dashboard(role, user)

    def _open_dashboard(self, role: str, user: str):
        QMessageBox.information(
            self,
            "Login successful",
            f"Welcome, {user}!\n\nYou are signed in as a {role}.",
        )
        # Real app: show StudentDashboard(user) or TeacherDashboard(user) here.


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
