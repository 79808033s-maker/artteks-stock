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
        # Автоматически получаем дату и время изменения файла в репозитории
        timestamp = os.path.getmtime(file_path)
        update_date = datetime.datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y в %H:%M')
        
        # Выводим дату обновления на экран
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
            products.append({
                'name': name,
                'total': row.iloc[2] if pd.notna(row.iloc[2]) else 0
            })

        query = st.text_input("🔍 Поиск товара:", "").strip().lower()

        filtered_data = []
        for p in products:
            if query in p['name'].lower():
                filtered_data.append({
                    "Остаток": p['total'],
                    "Наименование товара": p['name']
                })

        result_df = pd.DataFrame(filtered_data)

        st.write(f"Найдено позиций: {len(result_df)}")

        def highlight_gt_50(row):
            try:
                if float(row['Остаток']) > 50:
                    return ['background-color: #fff3cd'] * len(row)
            except:
                pass
            return [''] * len(row)

        styled_df = result_df.style.apply(highlight_gt_50, axis=1)

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
