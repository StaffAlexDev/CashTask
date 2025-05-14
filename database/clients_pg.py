from database.settings_pg import get_db_connection


async def add_client(company_id: int, first_name: str, phone_number: str,
                     last_name: str = None, social_network: str = None):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO clients (company_id, first_name, last_name, phone_number, social_network)
            VALUES ($1, $2, $3, $4, $5)
            ''',
            company_id, first_name, last_name, phone_number, social_network
        )
    finally:
        await conn.close()


async def get_all_clients(company_id: int):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT * FROM clients WHERE company_id = $1 AND is_deleted = FALSE',
            company_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_client_id_by_name(company_id: int, client_name: str):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT client_id FROM clients WHERE company_id = $1 AND first_name = $2 AND is_deleted = FALSE',
            company_id, client_name
        )
        return [r['client_id'] for r in rows]
    finally:
        await conn.close()


async def get_client_id_by_phone_number(company_id: int, phone_number: str):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            'SELECT client_id FROM clients WHERE company_id = $1 AND phone_number = $2',
            company_id, phone_number
        )
        return row['client_id'] if row else None
    finally:
        await conn.close()


async def get_client_by_id(company_id: int, client_id: int):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            'SELECT * FROM clients WHERE company_id = $1 AND client_id = $2 AND is_deleted = FALSE',
            company_id, client_id
        )
        return dict(row) if row else None
    finally:
        await conn.close()


async def delete_client_by_id(company_id: int, client_id: int, deleted_by: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            'UPDATE clients SET is_deleted = TRUE WHERE company_id = $1 AND client_id = $2 AND is_deleted = FALSE',
            company_id, client_id
        )
        count = int(result.split()[1])
        if count > 0:
            await conn.execute(
                'INSERT INTO deletion_logs (company_id, item_type, item_id, deleted_by) VALUES ($1, $2, $3, $4)',
                company_id, 'client', client_id, deleted_by
            )
            return True
        return False
    finally:
        await conn.close()


async def restore_client_by_id(company_id: int, client_id: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            'UPDATE clients SET is_deleted = FALSE WHERE company_id = $1 AND client_id = $2 AND is_deleted = TRUE',
            company_id, client_id
        )
        return int(result.split()[1]) > 0
    finally:
        await conn.close()


# ======================================= Clients and their Cars =============================================
async def add_car(company_id: int, client_id: int, car_brand: str, car_model: str,
                  license_plate: str, vin_code: str = None):
    conn = await get_db_connection()
    try:
        existing = await conn.fetchrow(
            'SELECT 1 FROM cars WHERE company_id = $1 AND (license_plate = $2 OR vin_code = $3)',
            company_id, license_plate, vin_code
        )
        if existing:
            return False, "Автомобиль с таким номером или VIN уже существует"

        await conn.execute(
            '''
            INSERT INTO cars (company_id, client_id, car_brand, car_model, license_plate, vin_code)
            VALUES ($1, $2, $3, $4, $5, $6)
            ''',
            company_id, client_id, car_brand, car_model, license_plate, vin_code
        )
        return True, ""
    except Exception as e:
        return False, f"Ошибка базы данных: {str(e)}"
    finally:
        await conn.close()


async def get_client_cars(company_id: int, client_id: int):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT * FROM cars WHERE company_id = $1 AND client_id = $2 AND is_deleted = FALSE',
            company_id, client_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_car_by_id(company_id: int, car_id: int):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            'SELECT * FROM cars WHERE company_id = $1 AND car_id = $2 AND is_deleted = FALSE',
            company_id, car_id
        )
        return dict(row) if row else None
    finally:
        await conn.close()


async def get_all_cars(company_id: int):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT * FROM cars WHERE company_id = $1 AND is_deleted = FALSE',
            company_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_car_id_by_license_plate(company_id: int, license_plate: str):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            'SELECT car_id FROM cars WHERE company_id = $1 AND license_plate = $2',
            company_id, license_plate
        )
        return row['car_id'] if row else None
    finally:
        await conn.close()


async def get_cars_and_owner_by_model(company_id: int, model: str):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            '''
            SELECT c.car_id, cl.first_name, cl.last_name, cl.phone_number,
                   c.car_model, c.license_plate
            FROM cars c
            JOIN clients cl ON c.client_id = cl.client_id AND c.company_id = cl.company_id
            WHERE c.company_id = $1 AND c.car_model = $2 AND c.is_deleted = FALSE
            ''',
            company_id, model
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def restore_car_by_id(company_id: int, car_id: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            'UPDATE cars SET is_deleted = FALSE WHERE company_id = $1 AND car_id = $2 AND is_deleted = TRUE',
            company_id, car_id
        )
        return int(result.split()[1]) > 0
    finally:
        await conn.close()