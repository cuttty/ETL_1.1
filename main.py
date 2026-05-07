import psycopg2
import pandas as pd
from datetime import datetime
import time
import os

# Настройки подключения
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'dbname': 'demo',
    'user': 'postgres',
    'password': '3289'
}

# Папка с нормализованными CSV-файлами (даты уже в YYYY-MM-DD)
CSV_DIR = './data_normalized'

# Сопоставление таблицы и имени файла
FILES_CONFIG = {
    'ds.ft_balance_f': 'ft_balance_f.csv',
    'ds.ft_posting_f': 'ft_posting_f.csv',
    'ds.md_account_d': 'md_account_d.csv',
    'ds.md_currency_d': 'md_currency_d.csv',
    'ds.md_exchange_rate_d': 'md_exchange_rate_d.csv',
    'ds.md_ledger_account_s': 'md_ledger_account_s.csv'
}

# Первичные ключи
TABLE_PKS = {
    'ds.ft_balance_f': ['on_date', 'account_rk'],
    'ds.md_account_d': ['data_actual_date', 'account_rk'],
    'ds.md_currency_d': ['currency_rk', 'data_actual_date'],
    'ds.md_exchange_rate_d': ['data_actual_date', 'currency_rk'],
    'ds.md_ledger_account_s': ['ledger_account', 'start_date']
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# Запись в таблицу логов
def log_event(conn, process_name, start, end, status, rows, message=''):
    sql = """
        INSERT INTO logs.etl_log (process_name, start_time, end_time, status, rows_processed, message)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        cur.execute(sql, (process_name, start, end, status, rows, message))
    conn.commit()

# Преобразует дату из типа стринг в тип дата
def safe_date_parser(val):
    if pd.isna(val) or str(val).strip() == '':
        return None
    try:
        return pd.to_datetime(val).date()
    except:
        return None
# Тип в столбцах в тип дата
def parse_dates_in_df(df, column_list):
    for col in column_list:
        if col in df.columns:
            df[col] = df[col].apply(safe_date_parser)
    return df

# Вставка всех строк
def insert_data(df, table_name, conn):
    columns = list(df.columns)
    placeholders = ','.join(['%s'] * len(columns))
    col_str = ','.join(columns)
    sql = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            values = [row[c] if pd.notna(row[c]) else None for c in columns]
            cur.execute(sql, values)
    conn.commit()

# Вставка строк с обновлением для таблци с первичным ключом
def upsert_data(df, table_name, conn):
    pks = TABLE_PKS[table_name]
    all_columns = list(df.columns)
    value_columns = [c for c in all_columns if c not in pks]

    insert_cols = ','.join(all_columns)
    values_ph = ','.join(['%s'] * len(all_columns))
    conflict_target = ','.join(pks)
    update_set = ','.join([f"{c}=EXCLUDED.{c}" for c in value_columns])

    sql = f"""
        INSERT INTO {table_name} ({insert_cols})
        VALUES ({values_ph})
        ON CONFLICT ({conflict_target}) DO UPDATE SET {update_set}
    """
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            values = [row[c] if pd.notna(row[c]) else None for c in all_columns]
            cur.execute(sql, values)
    conn.commit()

# Главная функция загрузки
def run_etl():
    conn = get_connection()
    process_name = 'DS_CSV_LOAD'
    start_time = datetime.now()

    # Записываем старт в лог
    log_event(conn, process_name, start_time, None, 'STARTED', 0)
    print(f"[{datetime.now()}] ETL стартовал ")
    time.sleep(5)

    total_rows = 0
    status = 'SUCCESS'
    message = ''

    try:
        for table_name, file_name in FILES_CONFIG.items():
            file_path = os.path.join(CSV_DIR, file_name)
            if not os.path.exists(file_path):
                message += f'Файл {file_path} не найден; '
                continue

            print(f"Загружаю {file_name} в {table_name}...")
            # Читаем CSV (разделитель ;)
            df = pd.read_csv(file_path, sep=';', dtype=str, keep_default_na=False)

            # Обрабатываем даты (ищем столбцы с датами)
            date_columns = [c for c in df.columns if 'date' in c.lower()]
            df = parse_dates_in_df(df, date_columns)

            if table_name == 'ds.ft_posting_f':
                # Очистка таблицы и простая вставка
                with conn.cursor() as cur:
                    cur.execute("TRUNCATE TABLE ds.ft_posting_f")
                conn.commit()
                insert_data(df, table_name, conn)
            else:
                upsert_data(df, table_name, conn)

            total_rows += len(df)
            print(f" -> {len(df)} строк загружено в {table_name}")

    except Exception as e:
        status = 'FAILED'
        message += str(e)
        print(f"ОШИБКА: {e}")
    finally:
        end_time = datetime.now()
        log_event(conn, process_name, start_time, end_time, status, total_rows, message)
        conn.close()
        print(f"[{end_time}] ETL завершён. Статус: {status}")


if __name__ == '__main__':
    run_etl()