import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from fpdf import FPDF

# Отключаем интерактивный режим Matplotlib (графики рисуются только в фоне)
matplotlib.use('Agg')

# === 1. НАСТРОЙКА ИНТЕРФЕЙСА ===
st.set_page_config(page_title="Smart Business Report", layout="wide")
st.title("📊 Умный отчет для бизнеса / Smart Business Report")

# === 2. БОКОВАЯ ПАНЕЛЬ И ЗАГРУЗКА ФАЙЛА ===
with st.sidebar:
    st.header("📁 Загрузка данных")
    uploaded_file = st.file_uploader("Загрузи Excel или CSV", type=['csv', 'xlsx'])

if not uploaded_file:
    st.info("👋 Привет! Загрузи свой отчет по продажам (Excel или CSV), и я мгновенно сделаю PDF-аналитику.")
    st.stop()

# === 3. ЧТЕНИЕ ФАЙЛА ===
try:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Ошибка при чтении файла: {e}")
    st.stop()

# === 4. УМНЫЙ ПОИСК КОЛОНОК (SUPERSTORE READY) ===
mapping = {}
for col in df.columns:
    col_lower = str(col).lower().strip()
    
    # Ищем деньги (берем первую подходящую колонку)
    if 'Amount' not in mapping.values() and any(kw in col_lower for kw in ['sales', 'profit', 'сумма', 'цена', 'итого', 'total', 'выручка', 'amount', 'оплате', 'продажи', 'прибыль']):
        mapping[col] = 'Amount'
        
    # Ищем даты
    elif 'Date' not in mapping.values() and any(kw in col_lower for kw in ['order date', 'дата', 'date', 'время', 'период']):
        mapping[col] = 'Date'
        
    # Ищем категории/товары
    elif 'Category' not in mapping.values() and any(kw in col_lower for kw in ['category', 'sub-category', 'product', 'категория', 'подкатегория', 'товар', 'item', 'название', 'сегмент', 'номенклатура']):
        mapping[col] = 'Category'

df = df.rename(columns=mapping)

# Приводим дату к нужному формату, если она найдена
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# === 5. ОТОБРАЖЕНИЕ ДАННЫХ (ПРЕВЬЮ) ===
st.success("✅ Данные успешно загружены и распознаны!")
st.write("Вот как программа увидела твой файл (первые 5 строк):")
st.dataframe(df.head())

# === 6. ГЕНЕРАТОР PDF ===
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Подключаем кириллицу (убедись, что DejaVuSans.ttf на месте)
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')
    
    # Заголовок
    pdf.set_font("DejaVu", "", 16)
    pdf.cell(0, 10, "Умный бизнес-отчет / Smart Business Report", ln=True, align="C")
    pdf.ln(5)

    # Базовые метрики
    pdf.set_font("DejaVu", "", 12)
    total_records = len(data)
    total_amount = data['Amount'].sum() if 'Amount' in data.columns else 0
    pdf.cell(0, 10, f"Всего транзакций (Total Transactions): {total_records}", ln=True)
    pdf.cell(0, 10, f"Общая выручка (Total Revenue): {total_amount:,.2f} ₸", ln=True)
    pdf.ln(10)

    # --- УМНЫЙ ТЕКСТОВЫЙ АНАЛИЗ ---
    if 'Category' in data.columns and 'Amount' in data.columns:
        pdf.set_font("DejaVu", "", 12)
        pdf.cell(0, 10, "AI Инсайт по продажам (Sales Insight):", ln=True)
        
        category_sales = data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        top_category = str(category_sales.index[0])
        top_amount = category_sales.iloc[0]
        top_percentage = (top_amount / total_amount) * 100 if total_amount > 0 else 0

        insight_ru = (
            f"🇷🇺 Анализ показывает, что «{top_category}» — главный драйвер продаж. "
            f"Этот товар принес {top_amount:,.2f} ₸ ({top_percentage:.1f}% от всей выручки). "
        )
        if top_percentage > 50:
            insight_ru += "Внимание: Бизнес сильно зависит от одного товара. Рекомендуется расширить ассортимент."
        else:
            insight_ru += "Отличная работа: Продажи хорошо сбалансированы. Продолжай в том же духе."

        insight_en = (
            f"🇬🇧 Analysis shows that '{top_category}' is your main sales driver, "
            f"generating {top_amount:,.2f} ₸ ({top_percentage:.1f}% of total revenue). "
        )
        if top_percentage > 50:
            insight_en += "Warning: High reliance on a single product. Consider diversifying your inventory."
        else:
            insight_en += "Great job: Your sales are well-balanced. Keep up the good work."

        final_insight = insight_ru + "\n\n" + insight_en
        pdf.multi_cell(0, 7, final_insight)
        pdf.ln(10)

    # --- ГРАФИК 1: ТРЕНДЫ ---
    if 'Date' in data.columns and 'Amount' in data.columns:
        trend_data = data.groupby('Date')['Amount'].sum().reset_index()
        
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(trend_data['Date'], trend_data['Amount'], marker='o', color='tab:blue')
        ax1.set_title("Revenue Trend")
        ax1.grid(True)
        fig1.savefig("temp_line.png", format='png', bbox_inches='tight')
        plt.close(fig1) 
        
        # Вставка картинки + жесткий отступ вниз, чтобы избежать наложения
        start_y = pdf.get_y()
        pdf.image("temp_line.png", x=15, y=start_y, w=180)
        pdf.set_y(start_y + 90) # Проматываем страницу вниз под график
        pdf.ln(10)

    # --- ГРАФИК 2: КАТЕГОРИИ ---
    if 'Category' in data.columns and 'Amount' in data.columns:
        pie_data = data.groupby('Category')['Amount'].sum()
        
        fig2, ax2 = plt.subplots(figsize=(8, 8))
        ax2.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
        ax2.set_title("Revenue by Category")
        fig2.savefig("temp_pie.png", format='png', bbox_inches='tight')
        plt.close(fig2) 
        
        # Проверяем, хватит ли места на странице для круга
        if pdf.get_y() > 170: 
            pdf.add_page()
            
        start_y2 = pdf.get_y()
        pdf.image("temp_pie.png", x=35, y=start_y2, w=140)

    return pdf.output()

# === 7. КНОПКА СКАЧИВАНИЯ ===
st.markdown("---")
if 'Amount' in df.columns:
    try:
        pdf_bytes = generate_pdf(df)
        st.download_button(
            label="🚀 Сгенерировать и скачать PDF Отчет",
            data=bytes(pdf_bytes),
            file_name="Smart_Business_Report.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Произошла ошибка при генерации PDF: {e}")
else:
    st.warning("⚠️ Для создания отчета программа должна найти колонку с суммой (Amount). Проверь свой файл!")









