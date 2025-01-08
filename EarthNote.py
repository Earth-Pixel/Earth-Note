import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QTextEdit, QLabel, QSizePolicy,
    QCheckBox, QDialog
)
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap
import re


NOTES_DIR = os.path.expanduser("~/.notes_app")
os.makedirs(NOTES_DIR, exist_ok=True)
ICON_PATH = "D:/проекты/EarthNote/icon.png"
BUTTON_COLOR = "#7cb34d"
RESIZE_MARGIN = 6

class FramelessResizeMixin:
    def __init__(self):
        self._resizing = False
        self._resizing_right = False
        self._resizing_left = False
        self._resizing_bottom = False
        self._mouse_pressed_pos = QPoint()
        self._start_geom = QRect()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton and not self.isMaximized():
            pos = event.pos()
            rect = self.rect()
            if abs(pos.x() - rect.right()) <= RESIZE_MARGIN:
                self._resizing = True
                self._resizing_right = True
                self._start_geom = self.geometry()
                self._mouse_pressed_pos = event.globalPos()
                event.accept()
            elif abs(pos.x() - rect.left()) <= RESIZE_MARGIN:
                self._resizing = True
                self._resizing_left = True
                self._start_geom = self.geometry()
                self._mouse_pressed_pos = event.globalPos()
                event.accept()
            elif abs(pos.y() - rect.bottom()) <= RESIZE_MARGIN:
                self._resizing = True
                self._resizing_bottom = True
                self._start_geom = self.geometry()
                self._mouse_pressed_pos = event.globalPos()
                event.accept()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if not self.isMaximized():
            pos = event.pos()
            rect = self.rect()
            if abs(pos.x() - rect.right()) <= RESIZE_MARGIN:
                self.setCursor(Qt.SizeHorCursor)
            elif abs(pos.x() - rect.left()) <= RESIZE_MARGIN:
                self.setCursor(Qt.SizeHorCursor)
            elif abs(pos.y() - rect.bottom()) <= RESIZE_MARGIN:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

        if self._resizing:
            diff = event.globalPos() - self._mouse_pressed_pos
            geom = self._start_geom
            new_left = geom.left()
            new_top = geom.top()
            new_width = geom.width()
            new_height = geom.height()
            if self._resizing_right:
                new_width = geom.width() + diff.x()
            if self._resizing_left:
                new_left = geom.left() + diff.x()
                new_width = geom.width() - diff.x()
            if self._resizing_bottom:
                new_height = geom.height() + diff.y()
            if new_width < 300:
                new_width = 300
            if new_height < 200:
                new_height = 200
            if self._resizing_left:
                right_edge = geom.right()
                new_left = right_edge - new_width
                if new_left > right_edge - 300:
                    new_left = right_edge - 300
            self.setGeometry(new_left, new_top, new_width, new_height)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self._resizing = False
        self._resizing_right = False
        self._resizing_left = False
        self._resizing_bottom = False
        self.setCursor(Qt.ArrowCursor)

class CustomTitleBar(QWidget):
    def __init__(self, parent_window, title="Earth Note", icon_path=ICON_PATH):
        super().__init__()
        self.parent_window = parent_window
        self.title = title
        self.icon_path = icon_path
        self._mouse_pressed = False
        self._mouse_pos = QPoint()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(6)
        pix = QPixmap(self.icon_path).scaled(43, 43, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        from PyQt5.QtWidgets import QLabel, QWidget, QSizePolicy
        lbl_icon = QLabel()
        lbl_icon.setPixmap(pix)
        layout.addWidget(lbl_icon)
        lbl_title = QLabel(self.title)
        lbl_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: black;")
        layout.addWidget(lbl_title)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(spacer)
        self.btn_min = QPushButton("-")
        self.btn_min.setFixedSize(33, 33)
        self.btn_min.setStyleSheet(self.button_style())
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.btn_min)
        self.btn_max = QPushButton("□")
        self.btn_max.setFixedSize(33, 33)
        self.btn_max.setStyleSheet(self.button_style())
        self.btn_max.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.btn_max)
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedSize(33, 33)
        self.btn_close.setStyleSheet(self.button_style(close=True))
        self.btn_close.clicked.connect(self.parent_window.close)
        layout.addWidget(self.btn_close)

    def button_style(self, close=False):
        if close:
            return """
                QPushButton {
                    background-color: #ff5c5c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ff4040;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #cccccc;
                    color: black;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b3b3b3;
                }
            """

    def toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.btn_max.setText("□")
        else:
            self.parent_window.showMaximized()
            self.btn_max.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.parent_window.isMaximized():
            self._mouse_pressed = True
            self._mouse_pos = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._mouse_pressed and (event.buttons() & Qt.LeftButton) and not self.parent_window.isMaximized():
            self.parent_window.move(event.globalPos() - self._mouse_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._mouse_pressed = False

class CustomTitleBarDialog(QWidget):
    def __init__(self, parent_window, title="Note", icon_path=ICON_PATH):
        super().__init__()
        self.parent_window = parent_window
        self.title = title
        self.icon_path = icon_path
        self._mouse_pressed = False
        self._mouse_pos = QPoint()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(6)
        pix = QPixmap(self.icon_path).scaled(43, 43, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        from PyQt5.QtWidgets import QLabel, QWidget, QSizePolicy
        lbl_icon = QLabel()
        lbl_icon.setPixmap(pix)
        layout.addWidget(lbl_icon)
        lbl_title = QLabel(self.title)
        lbl_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: black;")
        layout.addWidget(lbl_title)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(spacer)
        self.btn_min = QPushButton("-")
        self.btn_min.setFixedSize(33, 33)
        self.btn_min.setStyleSheet(self.button_style())
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.btn_min)
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedSize(33, 33)
        self.btn_close.setStyleSheet(self.button_style(close=True))
        self.btn_close.clicked.connect(self.parent_window.close)
        layout.addWidget(self.btn_close)

    def button_style(self, close=False):
        if close:
            return """
                QPushButton {
                    background-color: #ff5c5c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ff4040;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #cccccc;
                    color: black;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b3b3b3;
                }
            """

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.parent_window.isMaximized():
            self._mouse_pressed = True
            self._mouse_pos = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._mouse_pressed and (event.buttons() & Qt.LeftButton) and not self.parent_window.isMaximized():
            self.parent_window.move(event.globalPos() - self._mouse_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._mouse_pressed = False

class PasswordDialog(QDialog):
    def __init__(self, correct_password="", parent=None):
        super().__init__(parent)
        self.correct_password = correct_password
        self._accepted = False
        self.user_password = ""
        self._was_accepted = False
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(300, 150)
        self.rounded_container = QWidget(self)
        self.rounded_container.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px; 
        """)
        self.rounded_container.setGeometry(0, 0, 300, 150)
        self.title_bar = QWidget(self.rounded_container)
        self.title_bar.setGeometry(0, 0, 300, 30)
        self.title_bar.setStyleSheet("background-color: #cccccc; border-top-left-radius: 10px; border-top-right-radius: 10px;")
        self.close_button = QPushButton("X", self.title_bar)
        self.close_button.setGeometry(270, 0, 30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5c5c;
                color: white;
                border: none;
                border-top-right-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ff4040;
            }
        """)
        self.close_button.clicked.connect(self.reject)
        self._dragging = False
        self._drag_pos = QPoint()
        self.title_bar.mousePressEvent = self._titlebar_mousePressEvent
        self.title_bar.mouseMoveEvent = self._titlebar_mouseMoveEvent
        self.title_bar.mouseReleaseEvent = self._titlebar_mouseReleaseEvent
        self.label_info = QLabel("Enter your password:", self.rounded_container)
        self.label_info.move(20, 40)
        self.label_info.resize(260, 20)
        self.label_info.setStyleSheet("font-size: 10pt;")
        self.edit_pass = QLineEdit(self.rounded_container)
        self.edit_pass.setGeometry(20, 65, 260, 25)
        self.edit_pass.setEchoMode(QLineEdit.Password)
        self.edit_pass.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 3px;
            }
        """)
        self.ok_button = QPushButton("OK", self.rounded_container)
        self.ok_button.setGeometry(50, 110, 80, 30)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #7cb34d;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6ca145;
            }
        """)
        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button = QPushButton("Cancel", self.rounded_container)
        self.cancel_button.setGeometry(170, 110, 80, 30)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #7cb34d;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6ca145;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)

    def _titlebar_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def _titlebar_mouseMoveEvent(self, event):
        if self._dragging and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def _titlebar_mouseReleaseEvent(self, event):
        self._dragging = False

    def on_ok(self):
        self.user_password = self.edit_pass.text().strip()
        self._was_accepted = True
        self.accept()

    def get_password(self):
        return self.user_password

    def is_accepted(self):
        return self._was_accepted

class NotesApp(FramelessResizeMixin, QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        FramelessResizeMixin.__init__(self)
        self.current_note_window = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(100, 100, 650, 450)
        self.rounded_container = QWidget()
        self.rounded_container.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
        """)
        container_layout = QVBoxLayout(self.rounded_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        self.title_bar = CustomTitleBar(self, title="Earth Note", icon_path=ICON_PATH)
        container_layout.addWidget(self.title_bar)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        self.notes_list = QListWidget()
        self.notes_list.setDragEnabled(True)
        self.notes_list.setAcceptDrops(True)
        self.notes_list.setDropIndicatorShown(True)
        self.notes_list.setDragDropMode(self.notes_list.InternalMove)
        self.notes_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                font-size: 12pt;
                border-radius: 6px;
            }}
            QListWidget::item {{
                padding: 5px;
            }}
            QListWidget::item:selected {{
                background-color: {BUTTON_COLOR};
                color: white;
            }}
        """)
        self.notes_list.itemDoubleClicked.connect(self.open_note)
        content_layout.addWidget(self.notes_list)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        self.new_button = QPushButton("Create note")
        self.new_button.setStyleSheet(self.green_button_style())
        self.new_button.clicked.connect(self.new_note)
        btn_layout.addWidget(self.new_button)
        self.open_button = QPushButton("Open note")
        self.open_button.setStyleSheet(self.green_button_style())
        self.open_button.clicked.connect(self.open_selected_note)
        btn_layout.addWidget(self.open_button)
        self.delete_button = QPushButton("Delete note")
        self.delete_button.setStyleSheet(self.green_button_style())
        self.delete_button.clicked.connect(self.delete_note)
        btn_layout.addWidget(self.delete_button)
        content_layout.addLayout(btn_layout)
        container_layout.addWidget(content_widget)
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self.rounded_container)
        self.setCentralWidget(central)
        os.makedirs(NOTES_DIR, exist_ok=True)
        self.load_notes_list()

    def green_button_style(self):
        return f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #6ca145;
            }}
            QPushButton:pressed {{
                background-color: #5d8f3b;
            }}
        """

    def load_notes_list(self):
        self.notes_list.clear()
        for filename in os.listdir(NOTES_DIR):
            if filename.endswith(".txt"):
                note_name = filename[:-4]
                self.notes_list.addItem(note_name)

    def new_note(self):
        if self.current_note_window is not None:
            return
        note_win = NoteWindow(parent_app=self, note_name="", note_path="")
        note_win.show()
        self.current_note_window = note_win

    def open_selected_note(self):
        current_item = self.notes_list.currentItem()
        if current_item:
            self.open_note(current_item)

    def open_note(self, item):
        if self.current_note_window is not None:
            return
        note_name = item.text()
        note_path = os.path.join(NOTES_DIR, f"{note_name}.txt")
        note_win = NoteWindow(parent_app=self, note_name=note_name, note_path=note_path)
        note_win.show()
        self.current_note_window = note_win

    def delete_note(self):
        current_item = self.notes_list.currentItem()
        if current_item:
            note_name = current_item.text()
            file_path = os.path.join(NOTES_DIR, f"{note_name}.txt")
            if os.path.exists(file_path):
                os.remove(file_path)
            self.load_notes_list()

class NoteWindow(FramelessResizeMixin, QMainWindow):
    def __init__(self, parent_app=None, note_name="", note_path=""):
        QMainWindow.__init__(self)
        FramelessResizeMixin.__init__(self)
        self.parent_app = parent_app
        self.note_name = note_name
        self.note_path = note_path
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(150, 150, 450, 350)
        self.rounded_container = QWidget()
        self.rounded_container.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
        """)
        container_layout = QVBoxLayout(self.rounded_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        self.title_bar = CustomTitleBarDialog(self, title="Note", icon_path=ICON_PATH)
        container_layout.addWidget(self.title_bar)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Name")
        self.title_edit.setText(note_name)
        self.title_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {BUTTON_COLOR};
                border-radius: 6px;
                padding: 5px;
                font-size: 10pt;
            }}
        """)
        self.content_layout.addWidget(self.title_edit)
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Note text")
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                font-size: 10pt;
                padding: 5px;
            }
        """)
        self.content_layout.addWidget(self.text_edit)
        switch_layout = QHBoxLayout()
        switch_layout.setSpacing(10)
        self.password_checkbox = QCheckBox()
        self.password_checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 50px; 
                height: 25px;
            }
            QCheckBox::indicator:unchecked {
                image: url();
                border: 2px solid #cccccc;
                border-radius: 12px;
                background-color: #cccccc;
            }
            QCheckBox::indicator:unchecked::hover {
                background-color: #b3b3b3;
            }
            QCheckBox::indicator:checked {
                image: url();
                border: 2px solid #7cb34d;
                border-radius: 12px;
                background-color: #7cb34d;
            }
        """)
        self.password_checkbox.stateChanged.connect(self.on_password_switch)
        switch_layout.addWidget(self.password_checkbox)
        self.label_password = QLabel("Password")
        self.label_password.setStyleSheet("font-size: 10pt;")
        switch_layout.addWidget(self.label_password)
        self.edit_password = QLineEdit()
        self.edit_password.setPlaceholderText("Enter your password")
        self.edit_password.setEchoMode(QLineEdit.Password)
        self.edit_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 6px;
                padding: 5px;
                font-size: 10pt;
            }
        """)
        self.edit_password.hide()
        switch_layout.addWidget(self.edit_password)
        self.content_layout.addLayout(switch_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet(self.green_button_style())
        self.save_button.clicked.connect(self.save_note)
        btn_layout.addWidget(self.save_button)
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet(self.green_button_style())
        self.close_button.clicked.connect(self.close)
        btn_layout.addWidget(self.close_button)
        self.content_layout.addLayout(btn_layout)
        container_layout.addWidget(self.content_widget)
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self.rounded_container)
        self.setCentralWidget(central)
        self.load_with_password_check(note_path)

    def on_password_switch(self, state):
        if state == Qt.Checked:
            self.edit_password.show()
        else:
            self.edit_password.hide()

    def green_button_style(self):
        return f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #6ca145;
            }}
            QPushButton:pressed {{
                background-color: #5d8f3b;
            }}
        """

    def load_with_password_check(self, note_path):
        if not note_path or not os.path.exists(note_path):
            return
        with open(note_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            return
        first_line = lines[0].rstrip("\n")
        if first_line.startswith("!!PASS="):
            correct_pass = first_line[7:]
            dlg = PasswordDialog(correct_password=correct_pass)
            dlg.show()
            dlg.exec_()
            if dlg.is_accepted():
                user_pass = dlg.get_password()
                if user_pass == correct_pass:
                    content = "".join(lines[1:])
                    self.text_edit.setText(content)
                else:
                    pass
            else:
                pass
        else:
            content = "".join(lines)
            self.text_edit.setText(content)

    def save_note(self):
        name = self.title_edit.text().strip()
        if not name:
            return
        file_path = os.path.join(NOTES_DIR, f"{name}.txt")
        main_text = self.text_edit.toPlainText()
        lines_to_save = []
        if self.password_checkbox.isChecked():
            pass_str = self.edit_password.text().strip()
            if pass_str:
                lines_to_save.append(f"!!PASS={pass_str}")
        if main_text:
            if lines_to_save:
                lines_to_save.append(main_text)
            else:
                lines_to_save.append(main_text)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines_to_save))
        if self.parent_app:
            self.parent_app.load_notes_list()

    def closeEvent(self, event):
        if self.parent_app and self.parent_app.current_note_window == self:
            self.parent_app.current_note_window = None
        super().closeEvent(event)

    def sanitize_note_name(name):
        return re.sub(r'[<>:"/\\|?*]', "_", name)

    note_name = sanitize_note_name(note_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    os.makedirs(NOTES_DIR, exist_ok=True)
    main_window = NotesApp()
    main_window.show()
    sys.exit(app.exec_())
