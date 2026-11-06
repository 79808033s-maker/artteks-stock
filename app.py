import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="Учет Остатков — Art-Teksgroup", layout="centered")

st.title("📦 Остатки Art-Teksgroup SRL Moldova")

file_path = None
for filename in os.listdir("."):
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        if not filename.startswith("~$"):
            file_path = filename
            break

if file_path is None:
    st.warning("⚠️ Файл с остатками пока не загружен в систему.")
else:
    try:
        timestamp = os.path.getmtime(file_path)
        update_date = datetime.datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y в %H:%M')
        
        st.info(f"📅 **Дата обновления отчета:** {update_date}")

        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, sheet_name=0, header=None, engine='openpyxl')
        else:
            df = pd.read_excel(file_path, sheet_name=0, header=None, engine='xlrd')

        products = []
        for index, row in df.iterrows():
            if index < 11:
                continue
            name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else str(row.iloc[1]).strip()
            if name == 'nan' or not name:
                continue
            
            raw_total = row.iloc[2]
            try:
                total_val = float(raw_total) if pd.notna(raw_total) else 0.0
            except:
                total_val = 0.0

            products.append({
                'name': name,
                'total': total_val
            })

        query = st.text_input("🔍 Поиск товара:", "").strip().lower()

        filtered_data = []
        for p in products:
            if query in p['name'].lower():
                val = p['total']
                
                # Форматирование отображения остатка
                if val > 50:
                    display_total = ">50"
                else:
                    display_total = round(val, 2) if val % 1 != 0 else int(val)

                filtered_data.append({
                    "Остаток": display_total,
                    "Наименование товара": p['name'],
                    "_raw_val": val  # тех. поле для точной цветовой логики
                })

        result_df = pd.DataFrame(filtered_data)

        st.write(f"Найдено позиций: {len(result_df)}")

        # Функция для раскраски строк в зависимости от остатка
        def color_rows(row):
            try:
                val = float(row['_raw_val'])
                if val > 50:
                    return ['background-color: #d4edda'] * len(row)  # Зеленый (пастельный)
                elif val < 10:
                    return ['background-color: #f8d7da'] * len(row)  # Красный (пастельный)
                else:
                    return ['background-color: #fff3cd'] * len(row)  # Желтый (пастельный)
            except:
                pass
            return [''] * len(row)

        # Применяем стили и скрываем техническую колонку
        styled_df = result_df.style.apply(color_rows, axis=1).hide(subset=["_raw_val"], axis="columns")

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
