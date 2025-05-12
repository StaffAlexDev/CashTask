from database.settings_pg import get_db_connection


async def add_client(first_name: str, phone_number: str, last_name: str = None, social_network: str = None):
    conn = await get_db_connection()
    try:
        await conn.execute(
            '''
            INSERT INTO clients (first_name, last_name, phone_number, social_network)
            VALUES ($1, $2, $3, $4)
            ''',
            first_name, last_name, phone_number, social_network
        )
    finally:
        await conn.close()


async def get_all_clients():
    conn = await get_db_connection()
    try:
        rows = await conn.fetch('SELECT * FROM clients WHERE is_deleted = FALSE')
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_client_id_by_name(client_name: str):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            'SELECT * FROM clients WHERE first_name = $1', client_name
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_client_id_by_phone_number(phone_number: str):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow('SELECT client_id FROM clients WHERE phone_number = $1', phone_number)
        return row['client_id'] if row else None
    finally:
        await conn.close()


async def get_client_by_id(client_id: int):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow('SELECT * FROM clients WHERE client_id = $1', client_id)
        return dict(row) if row else None
    finally:
        await conn.close()


async def delete_client_by_id(client_id: int, deleted_by: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            'UPDATE clients SET is_deleted = TRUE WHERE client_id = $1', client_id
        )
        count = int(result.split()[1])
        if count > 0:
            await conn.execute(
                'INSERT INTO deletion_logs (item_type, item_id, deleted_by) VALUES ($1, $2, $3)',
                'client', client_id, deleted_by
            )
            return True
        return False
    finally:
        await conn.close()


async def restore_client_by_id(client_id: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            'UPDATE clients SET is_deleted = FALSE WHERE client_id = $1 AND is_deleted = TRUE',
            client_id
        )
        return result[-1] != '0'
    finally:
        await conn.close()


# ======================================= Clients car =============================================
async def add_car(client_id: int, car_brand: str, car_model: str, license_plate: str, vin_code: str = None):
    conn = await get_db_connection()
    try:
        existing = await conn.fetchrow(
            '''SELECT * FROM cars WHERE license_plate = $1 OR vin_code = $2''', license_plate, vin_code
        )
        if existing:
            return False, "Автомобиль с таким номером или VIN уже существует"

        await conn.execute(
            '''INSERT INTO cars (client_id, car_brand, car_model, license_plate, vin_code)
               VALUES ($1, $2, $3, $4, $5)''',
            client_id, car_brand, car_model, license_plate, vin_code
        )
        return True, ""
    except Exception as e:
        return False, f"Ошибка базы данных: {str(e)}"
    finally:
        await conn.close()


async def get_client_cars(client_id: int):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch('SELECT * FROM cars WHERE client_id = $1', client_id)
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_car_by_id(car_id: int):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow('SELECT * FROM cars WHERE car_id = $1', car_id)
        return dict(row) if row else None
    finally:
        await conn.close()


async def get_all_cars():
    conn = await get_db_connection()
    try:
        rows = await conn.fetch('SELECT * FROM cars WHERE is_deleted = FALSE')
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_car_id_by_license_plate(license_plate: str):
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            'SELECT car_id FROM cars WHERE license_plate = $1', license_plate
        )
        return row['car_id'] if row else None
    finally:
        await conn.close()


async def get_cars_and_owner_by_model(model: str):
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            '''
            SELECT cars.car_id, clients.first_name, clients.last_name, clients.phone_number,
                   cars.car_model, cars.license_plate
            FROM cars
            JOIN clients ON cars.client_id = clients.client_id
            WHERE cars.car_model = $1
            ''',
            model
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def restore_car_by_id(car_id: int) -> bool:
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            'UPDATE cars SET is_deleted = FALSE WHERE car_id = $1 AND is_deleted = TRUE',
            car_id
        )
        return result[-1] != '0'
    finally:
        await conn.close()
