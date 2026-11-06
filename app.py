import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Учет Остатков — Артекс", layout="centered")

st.title("📦 Общие остатки товаров")

# Ищем файл отчета прямо в репозитории (поддерживает и .xlsx, и .xls)
file_path = None
for filename in os.listdir("."):
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        # Исключаем служебные файлы, если есть
        if not filename.startswith("~$"):
            file_path = filename
            break

if file_path is None:
    st.warning("⚠️ Файл с остатками пока не загружен в систему.")
else:
    try:
        # Читаем файл в зависимости от его формата
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, sheet_name=0, header=None, engine='openpyxl')
        else:
            df = pd.read_excel(file_path, sheet_name=0, header=None, engine='xlrd')

        # Обработка данных вашей таблицы 1С
        products = []
        for index, row in df.iterrows():
            if index < 11:
                continue
            name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else str(row.iloc[1]).strip()
            if name == 'nan' or not name:
                continue
            products.append({
                'name': name,
                'total': row.iloc[2] if pd.notna(row.iloc[2]) else 0
            })

        # Строка поиска для сотрудников
        query = st.text_input("🔍 Поиск товара:", "").strip().lower()

        filtered_data = []
        for p in products:
            if query in p['name'].lower():
                filtered_data.append({
                    "Остаток": p['total'],
                    "Наименование товара": p['name']
                })

        result_df = pd.DataFrame(filtered_data)

        # Выводим таблицу только для просмотра (без каких-либо кнопок скачивания)
        st.write(f"Найдено позиций: {len(result_df)}")
        st.dataframe(result_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
