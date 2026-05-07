import pandas as pd
import os
from dateutil.parser import parse as dateparse
import chardet

INPUT_DIR = './data'
OUTPUT_DIR = './data_normalized'

DATE_COLUMNS = ['on_date', 'oper_date', 'data_actual_date', 'data_actual_end_date', 'start_date', 'end_date']

def normalize_date(val):
    if pd.isna(val) or str(val).strip() == '':
        return ''
    try:
        dt = dateparse(str(val))
        return dt.strftime('%Y-%m-%d')
    except:
        return val

# возвращает название кодировки
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        return chardet.detect(f.read())['encoding']

def process_file(file_name):
    input_path = os.path.join(INPUT_DIR, file_name)
    output_path = os.path.join(OUTPUT_DIR, file_name)
    encoding = detect_encoding(input_path)
    df = pd.read_csv(input_path, sep=';', dtype=str, keep_default_na=False, encoding=encoding)
    for col in df.columns:
        if col in DATE_COLUMNS:
            df[col] = df[col].apply(normalize_date)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(output_path, sep=';', index=False, encoding='utf-8')
    print(f" сохранён в {output_path}")

def main():
    for fn in os.listdir(INPUT_DIR):
        if fn.endswith('.csv'):
            process_file(fn)
    print("Готово")

if __name__ == '__main__':
    main()