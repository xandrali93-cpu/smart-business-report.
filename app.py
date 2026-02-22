import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    # 1. ШРИФТ (Убедись, что файл DejaVuSans.ttf лежит в корне на GitHub!)
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')
    pdf.set_font('DejaVu', '', 16)
    
    # Заголовок
    pdf.cell(0, 10, "Умный бизнес-отчет / Smart Business Report", ln=True, align="C")
    pdf.ln(10)

    # 2. МЕТРИКИ
    pdf.set_font("DejaVu", "", 12)
    total_records = len(data)
    total_amount = data['Amount'].sum() if 'Amount' in data.columns else 0
    pdf.cell(0, 10, f"Всего транзакций (Total Transactions): {total_records}", ln=True)
    pdf.cell(0, 10, f"Общая выручка (Total Revenue): {total_amount:,.2f} T", ln=True)
    pdf.ln(10)

    # 3. ГРАФИК 1 (ТРЕНДЫ)
    if 'Date' in data.columns and 'Amount' in data.columns:
        trend_data = data.groupby('Date')['Amount'].sum().reset_index()
        plt.figure(figsize=(10, 5))
        plt.plot(trend_data['Date'], trend_data['Amount'], marker='o', color='tab:blue')
        plt.title("Revenue Trend")
        plt.grid(True)
        plt.savefig("temp_line.png", format='png', bbox_inches='tight')
        plt.close() # ЗАКРЫВАЕМ график сразу после сохранения
        
        pdf.image("temp_line.png", x=10, y=pdf.get_y(), w=180)
        pdf.ln(10)

    # 4. ГРАФИК 2 (КАТЕГОРИИ)
    if 'Category' in data.columns and 'Amount' in data.columns:
        pie_data = data.groupby('Category')['Amount'].sum()
        plt.figure(figsize=(8, 8))
        plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
        plt.title("Revenue by Category")
        plt.savefig("temp_pie.png", format='png', bbox_inches='tight')
        plt.close() # ОЧИЩАЕМ холст
        
        # Если места мало, переходим на новую страницу
        if pdf.get_y() > 180:
            pdf.add_page()
        pdf.image("temp_pie.png", x=10, y=pdf.get_y(), w=150)

    return pdf.output()

# --- ОСНОВНОЙ ИНТЕРФЕЙС STREAMLIT ---
st.title("📊 Smart-Analytic-v1")

# Здесь должен быть твой код загрузки данных или создания df
# Для примера создадим тестовые данные, чтобы кнопка сразу работала:
if 'df' not in locals():
    df = pd.DataFrame({
        'Date': ['21-02', '22-02'],
        'Amount': [160000, 336500],
        'Category': ['Смартфон Samsung', 'Наушники']
    })

# Кнопка скачивания
try:
    pdf_bytes = generate_pdf(df)
    st.download_button(
        label="🚀 Сгенерировать и скачать PDF Отчет",
        data=bytes(pdf_bytes),
        file_name="Business_Report.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Ошибка при создании отчета: {e}")












