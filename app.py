import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from fpdf import FPDF
import matplotlib

# Отключаем интерактивный режим Matplotlib, чтобы Streamlit не ругался
matplotlib.use('Agg') 

# === 1. НАСТРОЙКА ИНТЕРФЕЙСА ===
st.set_page_config(page_title="Smart Business Report", layout="wide")
st.title("📊 Умный отчет для бизнеса / Smart Business Report")

# === 2. БОКОВАЯ ПАНЕЛЬ И ЗАГРУЗКА ФАЙЛА ===
with st.sidebar:
    st.header("📁 Загрузка данных")
    uploaded_file = st.file_uploader("Загрузи Excel или CSV", type=['csv', 'xlsx'])

# Если файла нет - ждем
if not uploaded_file:
    st.info("👋 Привет! Загрузи свой отчет по продажам (Excel или CSV), и я мгновенно сделаю PDF-аналитику твоего бизнеса.")
    st.stop()

# === 3. ЧТЕНИЕ ФАЙЛА И УМНЫЙ ПОИСК КОЛОНОК ===
try:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Ошибка при чтении файла: {e}")
    st.stop()

# Smart Column Mapping (Тот самый искусственный интеллект для колонок)
mapping = {}
for col in df.columns:
    col_lower = str(col).lower()
    if any(kw in col_lower for kw in ['сумма', 'цена', 'итого', 'total', 'выручка', 'amount']):
        mapping[col] = 'Amount'
    elif any(kw in col_lower for kw in ['дата', 'date', 'время', 'период']):
        mapping[col] = 'Date'
    elif any(kw in col_lower for kw in ['категория', 'товар', 'item', 'название', 'category']):
        mapping[col] = 'Category'

df = df.rename(columns=mapping)

# Приводим дату к формату времени
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# === 4. ОТОБРАЖЕНИЕ ДАННЫХ В БРАУЗЕРЕ ===
st.success("✅ Данные успешно загружены и распознаны!")
st.write("Вот как программа увидела твой файл (первые 5 строк):")
st.dataframe(df.head())

# === 5. ГЕНЕРАТОР PDF (НАШ ВЧЕРАШНИЙ ШЕДЕВР) ===
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Подключаем кириллицу (шрифт должен лежать в папке src)
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    
    # Заголовок
    # Заголовок
    pdf.set_font("DejaVu", "", 16)
    pdf.cell(0, 10, "Умный бизнес-отчет / Smart Business Report", ln=True, align="C")

    # Базовые метрики
    pdf.set_font("DejaVu", "", 12)
    total_records = len(data)
    total_amount = data['Amount'].sum() if 'Amount' in data.columns else 0
    pdf.cell(0, 10, f"Всего транзакций (Total Transactions): {total_records}", ln=True)
    pdf.cell(0, 10, f"Общая выручка (Total Revenue): {total_amount:,.2f} ₸", ln=True)
    pdf.ln(10)

    # --- УМНЫЙ ТЕКСТОВЫЙ АНАЛИЗ (Двуязычный) ---
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, "AI Инсайт по продажам (Sales Insight):", ln=True)
    pdf.set_font("DejaVu", "", 12)

    if 'Category' in data.columns and 'Amount' in data.columns:
        # Находим топ-товар и его долю
        category_sales = data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        top_category = str(category_sales.index[0])
        top_amount = category_sales.iloc[0]
        top_percentage = (top_amount / total_amount) * 100 if total_amount > 0 else 0

        # 1. Формируем русский текст
        insight_ru = (
            f"🇷🇺 Анализ показывает, что «{top_category}» — главный драйвер продаж. "
            f"Этот товар принес {top_amount:,.2f} ₸ ({top_percentage:.1f}% от всей выручки). "
        )
        if top_percentage > 50:
            insight_ru += "Внимание: Бизнес сильно зависит от одного товара. Рекомендуется расширить ассортимент."
        else:
            insight_ru += "Отличная работа: Продажи хорошо сбалансированы. Продолжай в том же духе."

        # 2. Формируем английский текст
        insight_en = (
            f"🇬🇧 Analysis shows that '{top_category}' is your main sales driver, "
            f"generating {top_amount:,.2f} ₸ ({top_percentage:.1f}% of total revenue). "
        )
        if top_percentage > 50:
            insight_en += "Warning: High reliance on a single product. Consider diversifying your inventory."
        else:
            insight_en += "Great job: Your sales are well-balanced. Keep up the good work."

        # 3. Склеиваем оба текста
        final_insight = insight_ru + "\n\n" + insight_en

        # Вставляем двуязычный текст в PDF
        pdf.multi_cell(0, 7, final_insight)
        pdf.ln(10)
    # ---------------------------------------------------

    # График 1: Тренды
    if 'Date' in data.columns and 'Amount' in data.columns:
        trend_data = data.groupby('Date')['Amount'].sum().reset_index()
        fig_line, ax_line = plt.subplots(figsize=(8, 4))
        ax_line.plot(trend_data['Date'], trend_data['Amount'], color='tab:blue')
        ax_line.set_title("Revenue Trend")
        
        plt.figure(figsize=(10, 5))
        # ... твой код рисования графиков (plt.plot) ...
        plt.savefig("temp_line.png", format='png', bbox_inches='tight')
        plt.close() # Важно закрыть график
        pdf.image("temp_line.png", x=10, y=pdf.get_y(), w=190)

    # График 2: Категории
    if 'Category' in data.columns and 'Amount' in data.columns:
        pie_data = data.groupby('Category')['Amount'].sum()
        fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
        ax_pie.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%')
        ax_pie.set_title("Revenue by Category")
        
        # --- Круговая диаграмма ---
        plt.figure(figsize=(10, 5))
        # ... твой код рисования (plt.pie) ...
        plt.savefig("temp_pie.png", format='png', bbox_inches='tight')
        plt.close()
        pdf.image("temp_pie.png", x=10, y=pdf.get_y(), w=190)
        
        if pdf.get_y() > 200:
            pdf.add_page()
        plt.close('all')

    return pdf.output()
# === 6. КНОПКА СКАЧИВАНИЯ ===
st.markdown("---")
if 'Date' in df.columns and 'Amount' in df.columns and 'Category' in df.columns:
    pdf_bytes = generate_pdf(df)
    st.download_button(
        label="🚀 Сгенерировать и скачать PDF Отчет",
        data=pdf_bytes,
        file_name="AI_Business_Report.pdf",
        mime="application/pdf"
    )
else:
    st.warning("⚠️ Для создания отчета в файле должны быть колонки с датой, суммой и названием товаров.")













