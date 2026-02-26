import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
from fpdf import FPDF

# Отключаем интерактивный режим Matplotlib (чтобы графики не наслаивались в фоне)
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

# === 3. ЧТЕНИЕ ФАЙЛА И УМНЫЙ ПОИСК КОЛОНОК ===
try:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Ошибка при чтении файла: {e}")
    st.stop()

# Умный поиск (теперь точно найдет "итого к оплате")
mapping = {}
for col in df.columns:
    col_lower = str(col).lower().strip()
    if any(kw in col_lower for kw in ['сумма', 'цена', 'итого', 'total', 'выручка', 'amount', 'оплате']):
        mapping[col] = 'Amount'
    elif any(kw in col_lower for kw in ['дата', 'date', 'время', 'период']):
        mapping[col] = 'Date'
    elif any(kw in col_lower for kw in ['категория', 'товар', 'item', 'название', 'category']):
        mapping[col] = 'Category'

df = df.rename(columns=mapping)

if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# === 4. ОТОБРАЖЕНИЕ ДАННЫХ (ПРЕВЬЮ ВЕРНУЛОСЬ!) ===
st.success("✅ Данные успешно загружены и распознаны!")
st.write("Вот как программа увидела твой файл (первые 5 строк):")
st.dataframe(df.head())

# === 5. ГЕНЕРАТОР PDF (С ТВОИМ ТЕКСТОМ И РАЗДЕЛЕННЫМИ ГРАФИКАМИ) ===
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Подключаем кириллицу
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

    # --- УМНЫЙ ТЕКСТОВЫЙ АНАЛИЗ (ТВОЙ БЛОК ВЕРНУЛСЯ) ---
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
        
        plt.figure(figsize=(10, 5))
        plt.plot(trend_data['Date'], trend_data['Amount'], marker='o', color='tab:blue')
        plt.title("Revenue Trend")
        plt.grid(True)
        plt.savefig("temp_line.png", format='png', bbox_inches='tight')
        plt.close('all') # ЖЕСТКАЯ ОЧИСТКА ПАМЯТИ
        
        pdf.image("temp_line.png", x=10, y=pdf.get_y(), w=180)
        pdf.ln(10)

    # --- ГРАФИК 2: КАТЕГОРИИ ---
    if 'Category' in data.columns and 'Amount' in data.columns:
        pie_data = data.groupby('Category')['Amount'].sum()
        
        plt.figure(figsize=(8, 8))
        plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
        plt.title("Revenue by Category")
        plt.savefig("temp_pie.png", format='png', bbox_inches='tight')
        plt.close('all') # ЖЕСТКАЯ ОЧИСТКА ПАМЯТИ
        
        if pdf.get_y() > 180:
            pdf.add_page()
            
        pdf.image("temp_pie.png", x=10, y=pdf.get_y(), w=150)

    return pdf.output()

# === 6. КНОПКА СКАЧИВАНИЯ ===
st.markdown("---")
if 'Amount' in df.columns:
    st.download_button(
        label="🚀 Сгенерировать и скачать PDF Отчет",
        data=bytes(generate_pdf(df)),
        file_name="Business_Report.pdf",
        mime="application/pdf"
    )
else:
    st.warning("⚠️ Для создания отчета программа должна найти колонку с суммой. Проверь свой файл!")









