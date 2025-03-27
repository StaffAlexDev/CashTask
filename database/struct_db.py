from database.db_settings import get_db_connection


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица с сотрудников
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID пользователя
            telegram_id INTEGER UNIQUE NOT NULL,        -- ID пользователя в Telegram
            first_name TEXT,                            -- Имя пользователя
            last_name TEXT,                             -- Фамилия пользователя
            language TEXT,                              -- Выбранный язык
            phone_number TEXT,                          -- Номер телефона
            role TEXT,                                  -- Роль (ссылка на таблицу roles)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата регистрации
        );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS approvals (
        approval_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        approver_id INTEGER NOT NULL,  -- Кто подтвердил (telegram_id)
        approved_id INTEGER NOT NULL,  -- Кого подтвердили (telegram_id)
        approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Время подтверждения
        FOREIGN KEY (approver_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
        FOREIGN KEY (approved_id) REFERENCES users(telegram_id) ON DELETE CASCADE
    );
    """)

    # Таблица автомобилей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            car_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID машины
            user_id INTEGER,                           -- ID владельца машины (клиента)
            car_brand TEXT,                            -- Марка машины
            car_model TEXT,                            -- Модель машины
            car_year INTEGER,                          -- Год выпуска
            license_plate TEXT UNIQUE,                 -- Номерной знак
            vin_code TEXT UNIQUE,                      -- VIN
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """)

    # Таблица заказов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID заказа
            car_id INTEGER,                              -- ID машины
            worker_id INTEGER,                           -- ID сотрудника, который выполняет заказ
            description TEXT,                            -- Описание работ
            status TEXT DEFAULT 'new',                   -- Статус заказа: new, in_progress, done
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата создания заказа
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата обновления заказа
            FOREIGN KEY (car_id) REFERENCES cars(car_id) ON DELETE CASCADE,
            FOREIGN KEY (worker_id) REFERENCES users(user_id) ON DELETE SET NULL
        );
    """)

    # Таблица задач
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID задачи
            assigned_to INTEGER,                        -- ID сотрудника, которому назначена задача
            assigned_by INTEGER,                        -- ID админа или staff, который создал задачу
            description TEXT,                           -- Описание задачи
            status TEXT DEFAULT 'new',                  -- Статус задачи: new, in_progress, done
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата создания задачи
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата обновления задачи
            FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_by) REFERENCES users(user_id) ON DELETE SET NULL
        );
    """)

    # Таблица финансов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS finances (
            finance_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID записи
            amount REAL NOT NULL,                          -- Сумма (доход или расход)
            description TEXT,                              -- Описание (например, "Покупка фильтров")
            type TEXT NOT NULL,                            -- Тип: income (доход), expense (расход)
            admin_id INTEGER NOT NULL,                     -- ID админа, который внес запись
            order_id INTEGER,                                -- ID автомобиля, к которому относится запись
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата записи
            FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE SET NULL,  -- Привязка к админу
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL       -- Привязка к order
        );
    """)

    conn.commit()
    conn.close()


# if __name__ == "__main__":
#     create_tables()
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO user_settings (user_id, languages) VALUES (?, ?) ", ("202126961", "ru"))
#     cursor.execute("SELECT * FROM user_settings WHERE user_id=?", ("202126961",))
#     data = cursor.fetchone()
#     print(data["user_id"])
#     print(data["languages"])
