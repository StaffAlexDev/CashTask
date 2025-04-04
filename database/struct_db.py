from database.db_settings import get_db_connection


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица с сотрудников
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID пользователя
            telegram_id INTEGER UNIQUE NOT NULL,        -- ID пользователя в Telegram
            first_name TEXT,                            -- Имя пользователя
            last_name TEXT,                             -- Фамилия пользователя
            language TEXT,                              -- Выбранный язык
            phone_number TEXT,                          -- Номер телефона
            role TEXT,                                  -- Роль
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата регистрации
        );
    """)
    # Таблица кто кого подтвердил в сотрудниках
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_approvals (
            approval_id INTEGER PRIMARY KEY AUTOINCREMENT,  
            approver_id INTEGER NOT NULL,  -- Кто подтвердил (telegram_id)
            approved_id INTEGER NOT NULL,  -- Кого подтвердили (telegram_id)
            approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Время подтверждения
            FOREIGN KEY (approver_id) REFERENCES employees(telegram_id) ON DELETE CASCADE,
            FOREIGN KEY (approved_id) REFERENCES employees(telegram_id) ON DELETE CASCADE
        );
        """)

    # Таблица с клиентов
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                clients_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID пользователя
                telegram_id INTEGER UNIQUE,                 -- ID пользователя в Telegram
                first_name TEXT,                            -- Имя пользователя
                last_name TEXT,                             -- Фамилия пользователя
                phone_number TEXT NOT NULL,                          -- Номер телефона
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата регистрации
            );
        """)

    # Таблица автомобилей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            car_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID машины
            clients_id INTEGER,                           -- ID владельца машины (клиента)
            car_brand TEXT,                            -- Марка машины
            car_model TEXT,                            -- Модель машины
            car_year INTEGER,                          -- Год выпуска
            license_plate TEXT UNIQUE,                 -- Номерной знак
            vin_code TEXT UNIQUE,                      -- VIN
            FOREIGN KEY (clients_id) REFERENCES clients(clients_id) ON DELETE CASCADE
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
            FOREIGN KEY (worker_id) REFERENCES employees(telegram_id) ON DELETE SET NULL
        );
    """)

    # Таблица задач
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID задачи
            assigned_to INTEGER,                        -- ID сотрудника, которому назначена задача
            assigned_by INTEGER,                        -- ID админа или staff, который создал задачу
            description TEXT,                           -- Описание задачи
            status TEXT DEFAULT 'in_progress',          -- Статус задачи: in_progress, done
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата создания задачи
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата обновления задачи
            FOREIGN KEY (assigned_to) REFERENCES employees(telegram_id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_by) REFERENCES employees(telegram_id) ON DELETE SET NULL
        );
    """)

    # Таблица финансов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS finances_by_car (
            finance_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный ID записи
            amount REAL NOT NULL,                          -- Сумма (доход или расход)
            type TEXT NOT NULL,                            -- Тип: income (доход), expense (расход)
            description TEXT,                              -- Описание (например, "Покупка фильтров")
            photo TEXT,                                    -- ссылка на фото чека или товара
            admin_id INTEGER,                              -- ID админа, который внес запись
            order_id INTEGER,                                -- ID автомобиля, к которому относится запись
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата записи
            FOREIGN KEY (admin_id) REFERENCES employees(telegram_id) ON DELETE SET NULL,  -- Привязка к админу
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL       -- Привязка к order
        );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS finances_general (
        finance_id INTEGER PRIMARY KEY AUTOINCREMENT,      -- Уникальный ID записи
            amount REAL NOT NULL,                          -- Сумма (доход или расход)
            type TEXT NOT NULL,                            -- Тип: income (доход), expense (расход)
            description TEXT,                              -- Описание (например, "Покупка фильтров")
            photo TEXT,                                    -- ссылка на фото чека или товара
            admin_id INTEGER NOT NULL,                     -- ID админа, который внес запись
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата записи
            FOREIGN KEY (admin_id) REFERENCES employees(telegram_id) ON DELETE SET NULL  -- Привязка к админу
        );
    """)

    # Индексы
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_employees_telegram_id ON employees(telegram_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_telegram_id ON clients(telegram_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cars_clients_id ON cars(clients_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_car_id ON orders(car_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_worker_id ON orders(worker_id);")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    pass
