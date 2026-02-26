import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from fpdf import FPDF

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
    st.info("👋 Привет! Загрузи свой отчет по продажам (Excel или CSV), и я мгновенно сделаю PDF-аналитику.")
    st.stop()

# === 3. ЧТЕНИЕ ФАЙЛА (С ЗАЩИТОЙ ОТ ГРЯЗНЫХ ДАННЫХ) ===
try:
    if uploaded_file.name.endswith('.csv'):
        try:
            # Пытаемся прочитать как обычный CSV
            df = pd.read_csv(uploaded_file)
        except Exception:
            # Если файл "грязный" (как Superstore), читаем с пропуском битых строк
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=',', on_bad_lines='skip', engine='python')
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Ошибка при чтении файла: {e}")
    st.stop()











