import asyncio

from database.settings_pg import get_db_connection


async def create_tables():
    conn = await get_db_connection()
    try:
        # Таблица сотрудников
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                user_id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100) DEFAULT '',
                language VARCHAR(10),
                phone_number VARCHAR(20),
                role VARCHAR(20),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # Таблица подтверждений сотрудников
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS employee_approvals (
                approval_id SERIAL PRIMARY KEY,
                approver_id BIGINT NOT NULL,
                approved_id BIGINT NOT NULL,
                approved_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (approver_id) REFERENCES employees(telegram_id) ON DELETE CASCADE,
                FOREIGN KEY (approved_id) REFERENCES employees(telegram_id) ON DELETE CASCADE
            );
        """)

        # Таблица автомобилей сотрудников
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS employer_cars (
                car_id SERIAL PRIMARY KEY,
                employer_id BIGINT,
                car_brand VARCHAR(50),
                car_model VARCHAR(50),
                license_plate VARCHAR(20) UNIQUE,
                technical_inspection DATE,
                insurance DATE,
                FOREIGN KEY (employer_id) REFERENCES employees(telegram_id) ON DELETE CASCADE
            );
        """)

        # Таблица клиентов
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                client_id SERIAL PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100) DEFAULT '',
                phone_number VARCHAR(20) UNIQUE,
                social_network VARCHAR(100),
                is_deleted BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # Таблица автомобилей клиентов
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                car_id SERIAL PRIMARY KEY,
                client_id INTEGER,
                car_brand VARCHAR(50),
                car_model VARCHAR(50),
                license_plate VARCHAR(20) UNIQUE,
                vin_code VARCHAR(30) UNIQUE,
                is_deleted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
            );
        """)

        # Таблица заказов
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                car_id INTEGER,
                worker_id BIGINT,
                description TEXT,
                status VARCHAR(20) DEFAULT 'new',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (car_id) REFERENCES cars(car_id) ON DELETE CASCADE,
                FOREIGN KEY (worker_id) REFERENCES employees(telegram_id) ON DELETE SET NULL
            );
        """)

        # Таблица задач
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id SERIAL PRIMARY KEY,
                assigned_to BIGINT,
                assigned_by BIGINT,
                description TEXT,
                status VARCHAR(20) DEFAULT 'in_progress',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (assigned_to) REFERENCES employees(telegram_id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_by) REFERENCES employees(telegram_id) ON DELETE SET NULL
            );
        """)

        # Таблица финансов по автомобилям
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS finances_by_car (
                finance_id SERIAL PRIMARY KEY,
                amount NUMERIC(12, 2) NOT NULL,
                type VARCHAR(20) NOT NULL,
                description TEXT,
                photo TEXT,
                admin_id BIGINT,
                order_id INTEGER,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (admin_id) REFERENCES employees(telegram_id) ON DELETE SET NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
            );
        """)

        # Таблица общих финансов
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS finances_general (
                finance_id SERIAL PRIMARY KEY,
                amount NUMERIC(12, 2) NOT NULL,
                type VARCHAR(20) NOT NULL,
                description TEXT,
                photo TEXT,
                admin_id BIGINT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (admin_id) REFERENCES employees(telegram_id) ON DELETE SET NULL
            );
        """)

        # Временная таблица для данных (например, подтверждений)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS temporary_data (
                id SERIAL PRIMARY KEY,
                key VARCHAR(34) UNIQUE,
                data JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # TODO Протестировать таблицу
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS deletion_logs (
                log_id   SERIAL PRIMARY KEY,
                item_type VARCHAR(20) NOT NULL,
                item_id   INTEGER    NOT NULL,
                deleted_by BIGINT    NOT NULL,
                deleted_at TIMESTAMPTZ DEFAULT NOW()
            );    
        """)

        await conn.execute("""
            INSERT INTO employees (telegram_id, first_name, role)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO NOTHING;
            """, 202126961, 'Алексей', 'superadmin')

        print("Таблицы успешно созданы!")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(create_tables())
