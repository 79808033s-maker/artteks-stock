import streamlit as st
import pandas as pd

st.set_page_config(page_title="Учет Остатков — Артекс", layout="centered")

st.title("📦 Общие остатки товаров")

uploaded_file = st.file_uploader("📂 Выберите или перетащите файл отчета 1С (.xlsx или .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        try:
            df = pd.read_excel(uploaded_file, sheet_name=0, header=None, engine='openpyxl')
        except Exception:
            df = pd.read_excel(uploaded_file, sheet_name=0, header=None, engine='xlrd')
            
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
                val = p['total']
                try:
                    num_val = float(str(val).replace(',', '.'))
                except ValueError:
                    num_val = 0

                if num_val > 50:
                    display_val = ">50"
                else:
                    if isinstance(val, float) and val.is_integer():
                        display_val = int(val)
                    else:
                        display_val = val
                    
                # Сохраняем только видимые колонки и число для подсветки
                filtered_data.append({
                    "Остаток": str(display_val), 
                    "Наименование товара": str(p['name']), 
                    "_num": num_val
                })
                
        st.write(f"Найдено позиций: {len(filtered_data)}")
        
        if filtered_data:
            df_show = pd.DataFrame(filtered_data)
            
            # Функция подсветки строки по значению _num
            def highlight_row(row):
                n = row["_num"]
                if n > 50:
                    return ['background-color: #ffffff; color: #0f172a'] * len(row)
                elif n <= 0:
                    return ['background-color: #fee2e2; color: #991b1b; font-weight: bold'] * len(row)
                elif n <= 10:
                    return ['background-color: #fef9c3; color: #854d0e; font-weight: bold'] * len(row)
                else:
                    return ['background-color: #e0f2fe; color: #075985; font-weight: bold'] * len(row)

            # Применяем стили ко всей таблице (включая _num), а затем выводим без технической колонки
            df_styled = df_show.style.apply(highlight_row, axis=1)

            st.dataframe(
                df_styled,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "_num": None  # Полностью скрываем техническую колонку средствами Streamlit
                }
            )
            
    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
else:
    st.info("👆 Загрузите свежий файл выгрузки из 1С, чтобы посмотреть остатки с подсветкой.")