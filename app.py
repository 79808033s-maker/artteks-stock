import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="Учет Остатков — Art-Teksgroup", layout="centered")

# Кастомный CSS для подсветки поля поиска и яркой красной кнопки со стрелкой
st.markdown("""
    <style>
    input[aria-label="🔍 Поиск товара:"] {
        background-color: #fff9db !important;
        border: 2px solid #fcc419 !important;
        color: #212529 !important;
        font-weight: 500;
    }
    /* Стили для жирной красной кнопки поиска */
    div.stButton > button {
        background-color: #e03131;
        color: white;
        border: none;
        font-weight: bold;
        font-size: 20px;
        border-radius: 6px;
        width: 100%;
        margin-top: 27px;
        height: 42px;
    }
    div.stButton > button:hover {
        background-color: #c92a2a;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

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
            if index < 12:
                continue
            
            name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            if not name or name == 'nan' or name.lower().startswith('всего'):
                continue
            
            raw_total = row.iloc[8]
            try:
                total_val = float(raw_total) if pd.notna(raw_total) else 0.0
            except:
                total_val = 0.0

            raw_transit = row.iloc[10]
            transit_status = ""
            try:
                if pd.notna(raw_transit) and float(raw_transit) > 0:
                    transit_status = "В пути"
            except:
                pass

            products.append({
                'name': name,
                'total': total_val,
                'transit': transit_status
            })

        # Создаем строку поиска и рядом красную кнопку с жирной стрелкой
        col_search, col_btn = st.columns([4, 1])
        with col_search:
            raw_query = st.text_input("🔍 Поиск товара:", "").strip()
        with col_btn:
            search_clicked = st.button("➔")

        # Сохраняем запрос в сессии по нажатию кнопки со стрелкой
        if "applied_query" not in st.session_state:
            st.session_state["applied_query"] = ""

        if search_clicked:
            st.session_state["applied_query"] = raw_query

        # Если строка поиска полностью пустая, сбрасываем фильтр
        if not raw_query:
            st.session_state["applied_query"] = ""

        query = st.session_state["applied_query"].lower()

        filtered_data = []
        for p in products:
            if query in p['name'].lower():
                val = p['total']
                
                # Форматирование остатка строго до 1 знака (без лишних нулей)
                if val > 50:
                    display_total = ">50"
                elif val % 1 == 0:
                    display_total = int(val)
                else:
                    display_total = f"{val:.1f}"

                display_status = f"**{p['transit']}**" if p['transit'] else ""

                filtered_data.append({
                    "Остаток (метр/шт)": display_total,
                    "Наименование товара": p['name'],
                    "Статус": display_status,
                    "_raw_val": val
                })

        result_df = pd.DataFrame(filtered_data)

        st.write(f"Найдено позиций: {len(result_df)}")

        display_df = result_df[["Остаток (метр/шт)", "Наименование товара", "Статус"]].copy()
        raw_vals = result_df["_raw_val"].tolist()

        def color_rows(row):
            idx = row.name
            try:
                val = float(raw_vals[idx])
                if val > 50:
                    return ['background-color: #d4edda; color: #155724'] * len(row)  # Зеленый (>50)
                elif val < 10:
                    return ['background-color: #f8d7da; color: #721c24'] * len(row)  # Красный (<10)
                else:
                    return ['background-color: #fff3cd; color: #856404'] * len(row)  # Желтый (10-50)
            except:
                pass
            return [''] * len(row)

        styled_df = display_df.style.apply(color_rows, axis=1)

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
