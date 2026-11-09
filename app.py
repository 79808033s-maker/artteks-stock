import streamlit as st
import pandas as pd
import os
import datetime

# Настройка вкладки браузера
st.set_page_config(
    page_title="Остатки Art-Teksgroup SRL",
    page_icon="📦",
    layout="centered"
)

# Красивое оформление мета-тегов для превью в WhatsApp, Viber и Telegram
st.markdown("""
    <head>
        <meta property="og:title" content="Остатки Art-Teksgroup SRL Moldova">
        <meta property="og:description" content="Актуальный складской учет тканей и дат прибытия в пути. Телефон: 079202099">
        <meta property="og:type" content="website">
        <meta property="og:site_name" content="Art-Teksgroup">
    </head>
    <style>
    /* Яркий красный фон для заголовка */
    .custom-header {
        background-color: #e03131;
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
    }
    .header-title-1 {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .header-title-2 {
        font-size: 26px;
        font-weight: bold;
    }
    /* Подсветка поля поиска желтоватым цветом */
    input[aria-label="🔍 Поиск товара:"] {
        background-color: #fff9db !important;
        border: 2px solid #fcc419 !important;
        color: #212529 !important;
        font-weight: 500;
    }
    /* Стили для компактной красной кнопки поиска в конце строки */
    div.stButton > button {
        background-color: #e03131;
        color: white;
        border: none;
        font-weight: bold;
        font-size: 18px;
        border-radius: 6px;
        width: 100%;
        margin-top: 27px;
        height: 38px;
    }
    div.stButton > button:hover {
        background-color: #c92a2a;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Красный блок заголовка в две строки
st.markdown("""
    <div class="custom-header">
        <div class="header-title-1">📦 Остатки</div>
        <div class="header-title-2">Art-Teksgroup SRL Moldova</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-size: 16px; font-weight: bold;'>📞 Телефон для справок: <code>079202099</code></p>", unsafe_allow_html=True)
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

        # Динамически определяем колонки в пути из строки 0
        transit_columns = []
        if len(df) > 0:
            row_0 = df.iloc[0]
            for col_idx in range(3, len(row_0)):
                header_text = str(row_0.iloc[col_idx])
                if "пути" in header_text.lower() or "приб" in header_text.lower():
                    label = header_text.replace('\n', ' ')
                    if "Приб." in label:
                        label = label.split("Приб.")[-1].strip()
                    elif "приб" in label.lower():
                        label = label.split("приб")[-1].strip()
                    else:
                        label = "В пути"
                    
                    transit_columns.append({
                        'col_idx': col_idx,
                        'label': f"Приб. {label}" if not label.startswith("Приб") else label
                    })

        raw_products = []
        for index, row in df.iterrows():
            if index < 2: # Пропускаем заголовки
                continue
            
            name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            if not name or name == 'nan' or name.lower().startswith('всего'):
                continue
            
            col0_val = row.iloc[0]
            raw_total = row.iloc[2] # Свободный остаток
            try:
                total_val = float(raw_total) if pd.notna(raw_total) else 0.0
            except:
                total_val = 0.0

            # Проверяем наличие в пути
            transit_notes = []
            for t_col in transit_columns:
                try:
                    val_transit = row.iloc[t_col['col_idx']]
                    if pd.notna(val_transit) and float(val_transit) > 0:
                        transit_notes.append(t_col['label'])
                except:
                    pass

            transit_status = ", ".join(transit_notes) if transit_notes else ""

            raw_products.append({
                'name': name,
                'col0': col0_val,
                'total': total_val,
                'transit': transit_status
            })

        # Точное определение шапок коллекций:
        # Шапка коллекции — это строка, за которой сразу идет элемент с номером 1 в первой колонке (col0 == 1)
        processed_products = []
        for i, p in enumerate(raw_products):
            is_header = False
            
            if i + 1 < len(raw_products):
                next_col0 = raw_products[i+1]['col0']
                try:
                    if float(next_col0) == 1.0:
                        is_header = True
                except:
                    pass

            processed_products.append({
                'name': p['name'],
                'total': p['total'] if not is_header else None,
                'transit': "" if is_header else p['transit'],
                'is_header': is_header
            })

        # Поле поиска и кнопка со стрелкой вплотную друг к другу
        col_search, col_btn = st.columns([5, 1])
        with col_search:
            raw_query = st.text_input("🔍 Поиск товара:", "").strip()
        with col_btn:
            search_clicked = st.button("➔")

        if "applied_query" not in st.session_state:
            st.session_state["applied_query"] = ""

        if search_clicked:
            st.session_state["applied_query"] = raw_query

        if not raw_query:
            st.session_state["applied_query"] = ""

        query = st.session_state["applied_query"].lower()

        filtered_data = []
        for p in processed_products:
            if query in p['name'].lower():
                val = p['total']
                
                if p['is_header']:
                    display_total = ""
                    full_name_display = f"🔹 **{p['name']}**"
                else:
                    if val is None or pd.isna(val) or val == 0:
                        display_total = "0"
                    elif val > 50:
                        display_total = ">50"
                    elif val % 1 == 0:
                        display_total = int(val)
                    else:
                        display_total = f"{val:.1f}"

                    full_name_display = p['name']
                    if p['transit']:
                        full_name_display = f"{p['name']} (🚚 {p['transit']})"

                filtered_data.append({
                    "Остаток": display_total,
                    "Наименование товара": full_name_display,
                    "_raw_val": val if not p['is_header'] else -1
                })

        result_df = pd.DataFrame(filtered_data)

        st.write(f"Найдено позиций: {len(result_df)}")

        display_df = result_df[["Остаток", "Наименование товара"]].copy()
        raw_vals = result_df["_raw_val"].tolist()

        def color_rows(row):
            idx = row.name
            try:
                val = float(raw_vals[idx])
                if val == -1:
                    return ['background-color: #e9ecef; color: #495057; font-weight: bold;'] * len(row)
                elif val > 50:
                    return ['background-color: #d4edda; color: #155724'] * len(row)
                elif val < 10:
                    return ['background-color: #f8d7da; color: #721c24'] * len(row)
                else:
                    return ['background-color: #fff3cd; color: #856404'] * len(row)
            except:
                pass
            return [''] * len(row)

        styled_df = display_df.style.apply(color_rows, axis=1)

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
