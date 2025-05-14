import asyncio

from database.settings_pg import get_db_connection


async def create_tables():
    conn = await get_db_connection()
    try:

        await conn.execute("""
            DO
            $$
            DECLARE
                r RECORD;
            BEGIN
              FOR r IN (
                SELECT tablename
                  FROM pg_tables
                 WHERE schemaname = 'public'
              ) LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
              END LOOP;
            END
            $$;
        """)

        # Таблица фирмы
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                company_id   SERIAL PRIMARY KEY,
                name         TEXT    NOT NULL,
                invite_code  TEXT    UNIQUE NOT NULL,  -- случайная строка-токен
                created_at   TIMESTAMP DEFAULT NOW()
            );
        """)

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
                created_at TIMESTAMPTZ DEFAULT NOW(),
                company_id INTEGER NOT NULL REFERENCES companies(company_id)
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
                FOREIGN KEY (approved_id) REFERENCES employees(telegram_id) ON DELETE CASCADE,
                company_id INTEGER NOT NULL REFERENCES companies(company_id)
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
                FOREIGN KEY (employer_id) REFERENCES employees(telegram_id) ON DELETE CASCADE,
                company_id INTEGER NOT NULL REFERENCES companies(company_id)
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
                created_at TIMESTAMPTZ DEFAULT NOW(),
                company_id INTEGER NOT NULL REFERENCES companies(company_id)
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
                FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
                company_id INTEGER NOT NULL REFERENCES companies(company_id)
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
                FOREIGN KEY (worker_id) REFERENCES employees(telegram_id) ON DELETE SET NULL,
                company_id INTEGER NOT NULL REFERENCES companies(company_id)
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
                FOREIGN KEY (assigned_by) REFERENCES employees(telegram_id) ON DELETE SET NULL,
                company_id INTEGER NOT NULL REFERENCES companies(company_id)
            );
        """)

        # Таблица финансов
        await conn.execute("""
            CREATE TABLE finances (
                finance_id    SERIAL      PRIMARY KEY,
                amount        NUMERIC(12,2) NOT NULL,      -- всегда положительное число
                direction     VARCHAR(3)    NOT NULL,      -- 'in' или 'out'
                category      VARCHAR(30)   NOT NULL,      -- например, 'director_fund','client_advance','part_purchase'
                company_id    INTEGER       NOT NULL REFERENCES companies(company_id),
                admin_id      INTEGER       NOT NULL REFERENCES employees(user_id),
                client_id     INTEGER       NULL    REFERENCES clients(client_id),
                car_id        INTEGER       NULL    REFERENCES cars(car_id),
                advance_src   INTEGER       NULL    REFERENCES finances(finance_id),  
                -- если эта расходная операция профинансирована авансом клиента,
                -- тут хранится ID записи-аванса (direction='in', category='client_advance')
                description   TEXT,
                photo         TEXT,
                created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW()
            );
        """)

        # Временная таблица для данных (например, подтверждений)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS temporary_data (
                id SERIAL PRIMARY KEY,
                key VARCHAR(34) UNIQUE,
                data JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                company_id INTEGER NOT NULL REFERENCES companies(company_id)
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

        # Индексы для ускоренного запросов по таблицам
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_employees_company
                ON employees(company_id);

            CREATE INDEX IF NOT EXISTS idx_clients_company
                ON clients(company_id);
            
            CREATE INDEX IF NOT EXISTS idx_cars_company
                ON cars(company_id);
            
            CREATE INDEX IF NOT EXISTS idx_employer_cars_company
                ON employer_cars(company_id);
            
            CREATE INDEX IF NOT EXISTS idx_finances_company
                ON finances(company_id);

            CREATE INDEX IF NOT EXISTS idx_finances_client
                ON finances(client_id);
            
            CREATE INDEX IF NOT EXISTS idx_finances_car
                ON finances(car_id);
            
            CREATE INDEX IF NOT EXISTS idx_finances_category_direction
                ON finances(company_id, category, direction, created_at DESC);
            
            CREATE INDEX IF NOT EXISTS idx_employer_cars_employer
                ON employer_cars(employer_id);
            
            CREATE INDEX IF NOT EXISTS idx_cars_client
                ON cars(client_id);
            
            CREATE INDEX IF NOT EXISTS idx_orders_car
                ON orders(car_id);
            
            CREATE INDEX IF NOT EXISTS idx_orders_company_status_created
                ON orders(company_id, status, created_at DESC);
            
            CREATE INDEX IF NOT EXISTS idx_tasks_company_assigned_status
                ON tasks(company_id, assigned_to, status);
        """)

        # await conn.execute("""
        #     INSERT INTO employees (telegram_id, first_name, role)
        #     VALUES ($1, $2, $3)
        #     ON CONFLICT (telegram_id) DO NOTHING;
        #     """, 202126961, 'Алексей', 'superadmin')

        print("Таблицы успешно созданы!")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(create_tables())
