import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

st.set_page_config(layout="wide")
st.title("📊 Sabit Konumlu Word Cloud Uygulaması")

RENK_DOSYASI = "renkler.json"
RENKLER = [
    "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
    "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
    "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000",
]

def renk_haritasini_yukle_veya_olustur(kelimeler):
    if os.path.exists(RENK_DOSYASI):
        with open(RENK_DOSYASI, "r", encoding="utf-8") as f:
            renk_haritasi = json.load(f)
    else:
        renk_haritasi = {}

    renk_index = 0
    for kelime in kelimeler:
        if kelime not in renk_haritasi:
            renk_haritasi[kelime] = RENKLER[renk_index % len(RENKLER)]
            renk_index += 1

    with open(RENK_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(renk_haritasi, f, ensure_ascii=False, indent=2)

    return renk_haritasi

uploaded_file = st.file_uploader("Excel dosyanızı yükleyin (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if not {"Kelime", "Frekans", "X Koordinat", "Y Koordinat"}.issubset(df.columns):
        st.error("❌ Excel dosyası 'Kelime', 'Frekans', 'X Koordinat', 'Y Koordinat' sütunlarını içermelidir.")
    else:
        kelimeler = df["Kelime"].tolist()
        frekanslar = df["Frekans"].tolist()
        x_koordinatlar = df["X Koordinat"].tolist()
        y_koordinatlar = df["Y Koordinat"].tolist()

        renk_haritasi = renk_haritasini_yukle_veya_olustur(kelimeler)

        max_freq = max(frekanslar)
        min_freq = min(frekanslar)
        max_size = 70
        min_size = 10

        def normalize(freq):
            if max_freq == min_freq:
                return (max_size + min_size) / 2
            return min_size + (freq - min_freq) / (max_freq - min_freq) * (max_size - min_size)

        fig, ax = plt.subplots(figsize=(12, 7))
        ax.axis("off")

        for kelime, freq, x, y in zip(kelimeler, frekanslar, x_koordinatlar, y_koordinatlar):
            boyut = normalize(freq)
            renk = renk_haritasi.get(kelime, "#000000")
            ax.text(x, y, kelime, fontsize=boyut, color=renk, ha='center', va='center', transform=ax.transAxes)

        st.pyplot(fig)
        plt.savefig("output.png", bbox_inches='tight', dpi=300)
        st.success("✅ Görsel başarıyla oluşturuldu ve output.png olarak kaydedildi.")

        with open("output.png", "rb") as f:
            st.download_button("📥 PNG Görselini İndir", f, file_name="wordcloud.png", mime="image/png")
