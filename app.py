import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="Учет Остатков — Art-Teksgroup", layout="centered")

st.title("📦 Остатки Art-Teksgroup SRL Moldova")
st.markdown("📞 **Телефон для справок:** `079202099`")
st.markdown("---")

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
            if index < 12:  # Шапка отчета
                continue
            
            name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            if not name or name == 'nan' or name.lower().startswith('всего'):
                continue
            
            # Остаток товара (колонка 8)
            raw_total = row.iloc[8]
            try:
                total_val = float(raw_total) if pd.notna(raw_total) else 0.0
            except:
                total_val = 0.0

            # В пути (колонка 10)
            raw_transit = row.iloc[10]
            has_transit = False
            try:
                if pd.notna(raw_transit) and float(raw_transit) > 0:
                    has_transit = True
            except:
                pass

            products.append({
                'name': name,
                'total': total_val,
                'has_transit': has_transit
            })

        query = st.text_input("🔍 Поиск товара:", "").strip().lower()

        filtered_data = []
        for p in products:
            if query in p['name'].lower():
                val = p['total']
                
                # Форматирование остатка
                if val > 50:
                    display_total = ">50"
                else:
                    display_total = round(val, 2) if val % 1 != 0 else int(val)

                # Добавляем примечание "в пути" без цифр
                display_name = p['name']
                if p['has_transit']:
                    display_name = f"{p['name']} (в пути)"

                filtered_data.append({
                    "Остаток (метр/шт)": display_total,
                    "Наименование товара": display_name,
                    "_raw_val": val
                })

        result_df = pd.DataFrame(filtered_data)

        st.write(f"Найдено позиций: {len(result_df)}")

        # Убираем техническую колонку ДО применения стилей
        display_df = result_df[["Остаток (метр/шт)", "Наименование товара"]].copy()
        raw_vals = result_df["_raw_val"].tolist()

        # Функция для подсветки строк по индексам
        def color_rows(row):
            idx = row.name
            try:
                val = float(raw_vals[idx])
                if val > 50:
                    return ['background-color: #d4edda'] * len(row)  # Зеленый (>50)
                elif val < 10:
                    return ['background-color: #f8d7da'] * len(row)  # Красный (<10)
                else:
                    return ['background-color: #fff3cd'] * len(row)  # Желтый (от 10 до 50)
            except:
                pass
            return [''] * len(row)

        styled_df = display_df.style.apply(color_rows, axis=1)

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
