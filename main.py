import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QComboBox, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QHBoxLayout, QTextEdit, QSpinBox, QGridLayout, QFormLayout
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import sqlite3


# Класс для работы с базой данных
class Database:
    def __init__(self, db_name="dating_bureau.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Таблица пользователей
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            password TEXT,
            age INTEGER,
            gender TEXT,
            interests TEXT,
            photo TEXT
        )
        ''')

        # Таблица сообщений
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            message TEXT,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
        ''')

        # Таблица лайков
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            liked_user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (liked_user_id) REFERENCES users(id)
        )
        ''')

        self.connection.commit()

    def add_user(self, name, password, age, gender, interests, photo):
        try:
            self.cursor.execute('''
            INSERT INTO users (name, password, age, gender, interests, photo) 
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, password, age, gender, interests, photo))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def check_user(self, name, password):
        self.cursor.execute('''
        SELECT * FROM users WHERE name = ? AND password = ?
        ''', (name, password))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.cursor.execute('''
        SELECT id, name, age, gender, interests, photo FROM users
        ''')
        return self.cursor.fetchall()

    def get_user_by_id(self, user_id):
        self.cursor.execute('''
        SELECT id, name, age, gender, interests, photo FROM users WHERE id = ?
        ''', (user_id,))
        return self.cursor.fetchone()

    def update_user(self, user_id, name, password, age, gender, interests, photo):
        self.cursor.execute('''
        UPDATE users SET name = ?, password = ?, age = ?, gender = ?, interests = ?, photo = ? WHERE id = ?
        ''', (name, password, age, gender, interests, photo, user_id))
        self.connection.commit()

    def add_like(self, user_id, liked_user_id):
        self.cursor.execute('''
        INSERT INTO likes (user_id, liked_user_id) VALUES (?, ?)
        ''', (user_id, liked_user_id))
        self.connection.commit()

    def add_message(self, sender_id, receiver_id, message):
        self.cursor.execute('''
        INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)
        ''', (sender_id, receiver_id, message))
        self.connection.commit()

    def get_messages(self, user_id):
        self.cursor.execute('''
        SELECT sender_id, receiver_id, message FROM messages WHERE sender_id = ? OR receiver_id = ?
        ''', (user_id, user_id))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()


# Основное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Бюро знакомств")
        self.setGeometry(100, 100, 400, 300)

        # Центральный виджет и компоновка
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Логотип
        self.add_logo()

        # Кнопка "Регистрация"
        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.setIcon(QIcon("templates/register_icon.png"))
        self.register_button.clicked.connect(self.open_registration_window)
        self.layout.addWidget(self.register_button)

        # Кнопка "Войти"
        self.login_button = QPushButton("Войти")
        self.login_button.setIcon(QIcon("templates/login_icon.png"))
        self.login_button.clicked.connect(self.open_login_window)
        self.layout.addWidget(self.login_button)

        # Применение стилей
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)

    def add_logo(self):
        logo = QLabel(self)
        pixmap = QPixmap("templates/logo.png")  # Замените на путь к вашему логотипу
        logo.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        self.layout.addWidget(logo)

    def open_registration_window(self):
        self.registration_window = RegistrationWindow()
        self.registration_window.show()

    def open_login_window(self):
        self.login_window = LoginWindow(self)
        self.login_window.show()


# Окно регистрации
class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setGeometry(100, 100, 400, 350)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Имя пользователя")
        self.layout.addWidget(self.name_input)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Пароль")
        self.layout.addWidget(self.password_input)

        self.age_input = QLineEdit(self)
        self.age_input.setPlaceholderText("Возраст")
        self.layout.addWidget(self.age_input)

        self.gender_input = QComboBox(self)
        self.gender_input.addItems(["Мужской", "Женский"])
        self.layout.addWidget(self.gender_input)

        self.interests_input = QLineEdit(self)
        self.interests_input.setPlaceholderText("Интересы")
        self.layout.addWidget(self.interests_input)

        self.photo_button = QPushButton("Загрузить фотографию", self)
        self.photo_button.clicked.connect(self.load_photo)
        self.layout.addWidget(self.photo_button)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.clicked.connect(self.register_user)
        self.layout.addWidget(self.register_button)

        self.photo_path = ""

    def load_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фото", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.photo_path = file_path

    def register_user(self):
        name = self.name_input.text()
        password = self.password_input.text()
        age = self.age_input.text()
        gender = self.gender_input.currentText()
        interests = self.interests_input.text()

        if not name or not password or not age or not gender or not interests or not self.photo_path:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения!")
            return

        try:
            age = int(age)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Возраст должен быть числом!")
            return

        db = Database()
        if db.add_user(name, password, age, gender, interests, self.photo_path):
            QMessageBox.information(self, "Успех", "Пользователь зарегистрирован!")
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует!")


# Окно входа
class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Вход")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Имя пользователя")
        self.layout.addWidget(self.name_input)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Пароль")
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти", self)
        self.login_button.clicked.connect(self.login_user)
        self.layout.addWidget(self.login_button)

    def login_user(self):
        username = self.name_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите имя пользователя и пароль.")
            return

        db = Database()
        user = db.check_user(username, password)
        if user:
            QMessageBox.information(self, "Успех", "Вход выполнен успешно!")
            self.close()
            self.main_window.close()  # Закрываем окно входа
            self.profile_window = ProfileWindow(user)
            self.profile_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль.")


# Окно просмотра профилей
class ProfileWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Просмотр профилей")
        self.setGeometry(100, 100, 600, 400)

        self.user = user
        self.db = Database()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.profile_list = QListWidget(self)
        self.layout.addWidget(self.profile_list)

        self.load_profiles()

        # Кнопка для просмотра своего профиля
        self.view_profile_button = QPushButton("Посмотреть свой профиль")
        self.view_profile_button.clicked.connect(self.view_own_profile)
        self.layout.addWidget(self.view_profile_button)

    def load_profiles(self):
        users = self.db.get_all_users()
        for user in users:
            if user[0] == self.user[0]:  # Пропускаем текущего пользователя
                continue
            item = QListWidgetItem(self.profile_list)
            profile_widget = ProfileWidget(user, self.user[0])
            item.setSizeHint(profile_widget.sizeHint())
            self.profile_list.addItem(item)
            self.profile_list.setItemWidget(item, profile_widget)

    def view_own_profile(self):
        self.own_profile_window = OwnProfileWindow(self.user)
        self.own_profile_window.show()


# Виджет профиля
class ProfileWidget(QWidget):
    def __init__(self, user, current_user_id):
        super().__init__()
        self.user = user
        self.current_user_id = current_user_id
        self.db = Database()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Фото
        photo_label = QLabel(self)
        pixmap = QPixmap(user[5]) if user[5] else QPixmap("templates/default.png")
        photo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        self.layout.addWidget(photo_label)

        # Информация о пользователе
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"Имя: {user[1]}"))
        info_layout.addWidget(QLabel(f"Возраст: {user[2]}"))
        info_layout.addWidget(QLabel(f"Интересы: {user[4]}"))
        self.layout.addLayout(info_layout)

        # Кнопки взаимодействия
        buttons_layout = QVBoxLayout()
        self.like_button = QPushButton("Мне нравится")
        self.like_button.clicked.connect(self.like_user)
        buttons_layout.addWidget(self.like_button)

        self.message_button = QPushButton("Отправить сообщение")
        self.message_button.clicked.connect(self.send_message)
        buttons_layout.addWidget(self.message_button)

        self.layout.addLayout(buttons_layout)

    def like_user(self):
        self.db.add_like(self.current_user_id, self.user[0])
        QMessageBox.information(self, "Успех", f"Вы поставили лайк пользователю {self.user[1]}!")

    def send_message(self):
        message_window = MessageWindow(self.current_user_id, self.user[0])
        message_window.show()


# Окно отправки сообщения
class MessageWindow(QWidget):
    def __init__(self, sender_id, receiver_id):
        super().__init__()
        self.setWindowTitle("Отправить сообщение")
        self.setGeometry(100, 100, 400, 300)

        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.db = Database()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.message_input = QTextEdit(self)
        self.layout.addWidget(self.message_input)

        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

    def send_message(self):
        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "Ошибка", "Сообщение не может быть пустым!")
            return

        self.db.add_message(self.sender_id, self.receiver_id, message)
        QMessageBox.information(self, "Успех", "Сообщение отправлено!")
        self.close()


# Окно просмотра своего профиля
class OwnProfileWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Мой профиль")
        self.setGeometry(100, 100, 400, 300)

        self.user = user
        self.db = Database()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Фото
        self.photo_label = QLabel(self)
        pixmap = QPixmap(user[5]) if user[5] else QPixmap("templates/default.png")
        self.photo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        self.layout.addWidget(self.photo_label)

        # Информация о пользователе
        self.name_input = QLineEdit(user[1], self)
        self.layout.addWidget(QLabel("Имя:"))
        self.layout.addWidget(self.name_input)

        self.password_input = QLineEdit(user[2], self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(QLabel("Пароль:"))
        self.layout.addWidget(self.password_input)

        self.age_input = QLineEdit(str(user[3]), self)
        self.layout.addWidget(QLabel("Возраст:"))
        self.layout.addWidget(self.age_input)

        self.gender_input = QComboBox(self)
        self.gender_input.addItems(["Мужской", "Женский"])
        self.gender_input.setCurrentText(user[4])
        self.layout.addWidget(QLabel("Пол:"))
        self.layout.addWidget(self.gender_input)

        self.interests_input = QLineEdit(user[5], self)
        self.layout.addWidget(QLabel("Интересы:"))
        self.layout.addWidget(self.interests_input)

        self.photo_button = QPushButton("Изменить фото", self)
        self.photo_button.clicked.connect(self.load_photo)
        self.layout.addWidget(self.photo_button)

        self.save_button = QPushButton("Сохранить изменения", self)
        self.save_button.clicked.connect(self.save_profile)
        self.layout.addWidget(self.save_button)

    def load_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фото", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.photo_path = file_path
            pixmap = QPixmap(file_path)
            self.photo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))

    def save_profile(self):
        name = self.name_input.text()
        password = self.password_input.text()
        age = self.age_input.text()
        gender = self.gender_input.currentText()
        interests = self.interests_input.text()

        if not name or not password or not age or not gender or not interests:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения!")
            return

        try:
            age = int(age)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Возраст должен быть числом!")
            return

        self.db.update_user(self.user[0], name, password, age, gender, interests, self.photo_path)
        QMessageBox.information(self, "Успех", "Профиль обновлен!")
        self.close()


# Окно поиска пользователей
class SearchWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Поиск пользователей")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Фильтры
        self.age_min = QSpinBox(self)
        self.age_min.setRange(18, 100)
        self.age_min.setValue(18)
        self.layout.addWidget(QLabel("Минимальный возраст:"))
        self.layout.addWidget(self.age_min)

        self.age_max = QSpinBox(self)
        self.age_max.setRange(18, 100)
        self.age_max.setValue(100)
        self.layout.addWidget(QLabel("Максимальный возраст:"))
        self.layout.addWidget(self.age_max)

        self.gender_filter = QComboBox(self)
        self.gender_filter.addItems(["Любой", "Мужской", "Женский"])
        self.layout.addWidget(QLabel("Пол:"))
        self.layout.addWidget(self.gender_filter)

        self.interests_filter = QLineEdit(self)
        self.interests_filter.setPlaceholderText("Интересы")
        self.layout.addWidget(QLabel("Интересы:"))
        self.layout.addWidget(self.interests_filter)

        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.search_users)
        self.layout.addWidget(self.search_button)

        self.results_list = QListWidget(self)
        self.layout.addWidget(self.results_list)

    def search_users(self):
        self.results_list.clear()
        db = Database()
        users = db.get_all_users()

        for user in users:
            age = user[2]
            gender = user[3]
            interests = user[4]

            if (self.age_min.value() <= age <= self.age_max.value()) and (
                self.gender_filter.currentText() == "Любой" or self.gender_filter.currentText() == gender
            ) and (
                not self.interests_filter.text() or self.interests_filter.text().lower() in interests.lower()
            ):
                item = QListWidgetItem(self.results_list)
                profile_widget = ProfileWidget(user, None)
                item.setSizeHint(profile_widget.sizeHint())
                self.results_list.addItem(item)
                self.results_list.setItemWidget(item, profile_widget)


# Главная функция
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())