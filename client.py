import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="Rejestracja Czasu Pracy", layout="centered")

st.markdown("<h2 style='text-align: center;'>🕒 Indywidualny Raport Czasu</h2>", unsafe_allow_html=True)
st.write("Wypełnij dane. Informacje zostaną przesłane bezpośrednio do serwera в мережі.")

emp_id = st.text_input("🔑 Twój numer służbowy (ID)")
password = st.text_input("🔒 Hasło", type="password")

st.markdown("---")

log_date = st.date_input("📅 Data", date.today())
status = st.selectbox("💼 Status dnia", ["Przepracowane", "Chorobowe (L4)", "Urlop"])

if status == "Przepracowane":
    hours = st.number_input("⏱ Przepracowane godziny", min_value=0.0, max_value=24.0, value=8.0, step=0.5)
else:
    hours = 0.0

st.markdown("###")

if st.button("🚀 Wyślij do biura", use_container_width=True):
    if not emp_id or not password:
        st.error("Wprowadź ID oraz Hasło!")
    else:
        payload = {
            "emp_id": emp_id,
            "password": password,
            "date": str(log_date),
            "status": status,
            "hours": hours
        }
        
        try:
            SERVER_URL = "https://onrender.com"
            response = requests.post(SERVER_URL, json=payload)
            
            # Безпечно обробляємо відповідь від сервера, щоб додаток не падав
            try:
                res_data = response.json()
                if response.status_code == 200:
                    st.success(res_data.get("message", "Dane zostały zapisane!"))
                else:
                    st.error(res_data.get("detail", "Błąd serwera."))
            except Exception:
                st.error(f"❌ Serwer zwrócił błąd (Kod {response.status_code}): {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Brak połączenia z biurem. Sprawdź internet lub adres serwera.")
