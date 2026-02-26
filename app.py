import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from fpdf import FPDF
import matplotlib

# Отключаем интерактивный режим Matplotlib
matplotlib.use('Agg') 

# === 1. НАСТРОЙКА ИНТЕРФЕЙСА ===
st.set_page_config(page_title="Smart Business Report", layout="wide")
st.title("📊 Умный отчет для бизнеса / Smart Business Report")

# === 2. БОКОВАЯ ПАНЕЛЬ И ЗАГРУЗКА ФАЙЛА ===
with st.sidebar:
    st.header("📁 Загрузка данных")
    uploaded_file = st.file_uploader("Загрузи Excel или CSV", type=['csv', 'xlsx'])

if not uploaded_file:
    st.info("👋 Привет! Загрузи свой отчет по продажам, и я сделаю PDF-аналитику.")
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


# Обновленный Smart Column Mapping
mapping = {}
for col in df.columns:
    col_lower = str(col).lower().strip() # Убираем лишние пробелы
    
    # Ищем деньги (Amount)
    if any(kw in col_lower for kw in ['сумма', 'цена', 'итого', 'total', 'amount', 'выручка', 'оплате']):
        mapping[col] = 'Amount'
        
    # Ищем даты (Date)
    elif any(kw in col_lower for kw in ['дата', 'date', 'время', 'период', 'день']):
        mapping[col] = 'Date'
        
    # Ищем категории/товары (Category)
    elif any(kw in col_lower for kw in ['категория', 'товар', 'item', 'название', 'номенклатура']):
        mapping[col] = 'Category'

df = df.rename(columns=mapping)

# === 4. ГЕНЕРАТОР PDF ===
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Подключаем кириллицу
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')
    pdf.set_font('DejaVu', '', 16)
    
    pdf.cell(0, 10, "Умный бизнес-отчет / Smart Business Report", ln=True, align="C")
    pdf.ln(10)

    # Метрики
    pdf.set_font("DejaVu", "", 12)
    total_records = len(data)
    total_amount = data['Amount'].sum() if 'Amount' in data.columns else 0
    pdf.cell(0, 10, f"Всего транзакций: {total_records}", ln=True)
    pdf.cell(0, 10, f"Общая выручка: {total_amount:,.2f} ₸", ln=True)
    pdf.ln(10)

    # График 1: Тренды
    if 'Date' in data.columns and 'Amount' in data.columns:
        trend_data = data.groupby('Date')['Amount'].sum().reset_index()
        plt.figure(figsize=(10, 5))
        plt.plot(trend_data['Date'], trend_data['Amount'], marker='o', color='tab:blue')
        plt.title("Revenue Trend")
        plt.savefig("temp_line.png", format='png', bbox_inches='tight')
        plt.close()
        pdf.image("temp_line.png", x=10, y=pdf.get_y(), w=180)
        pdf.ln(10)

    # График 2: Категории
    if 'Category' in data.columns and 'Amount' in data.columns:
        pie_data = data.groupby('Category')['Amount'].sum()
        plt.figure(figsize=(8, 8))
        plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
        plt.title("Revenue by Category")
        plt.savefig("temp_pie.png", format='png', bbox_inches='tight')
        plt.close()
        
        if pdf.get_y() > 180:
            pdf.add_page()
        pdf.image("temp_pie.png", x=10, y=pdf.get_y(), w=150)

    plt.close('all')
    return pdf.output()

# === 5. КНОПКА СКАЧИВАНИЯ ===
st.markdown("---")
if 'Amount' in df.columns:
    # Генерируем один раз
    report_data = generate_pdf(df)
    st.download_button(
       label="🚀 Сгенерировать и скачать PDF Отчет",
       data=bytes(report_data),
       file_name="Business_Report.pdf",
       mime="application/pdf"
    )
else:
    st.warning("⚠️ В файле должна быть колонка с суммой (Amount).")











