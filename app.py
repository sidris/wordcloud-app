import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import random
from matplotlib import transforms

st.set_page_config(layout="wide")
st.title("📊 Akıllı Word Cloud: Sabit Renk, Frekans, Çakışmasız Yerleşim")

RENK_DOSYASI = "renkler.json"
RENKLER = [
    "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
    "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
    "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000",
]

def renk_haritasini_yukle_veya_olustur(kelimeler):
    renk_haritasi = {}
    
    if os.path.exists(RENK_DOSYASI):
        try:
            with open(RENK_DOSYASI, "r", encoding="utf-8") as f:
                renk_haritasi = json.load(f)
        except json.JSONDecodeError:
            st.warning("⚠️ 'renkler.json' bozuk olduğu için sıfırdan oluşturuluyor.")
            renk_haritasi = {}
            os.remove(RENK_DOSYASI)

    renk_index = 0
    for kelime in kelimeler:
        if kelime not in renk_haritasi:
            renk_haritasi[kelime] = RENKLER[renk_index % len(RENKLER)]
            renk_index += 1

    with open(RENK_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(renk_haritasi, f, ensure_ascii=False, indent=2)

    return renk_haritasi

# Çakışmasız yerleştirme
def kelime_koy(ax, kelime, fontsize, renk, kutular, fig):
    for deneme in range(100):
        x, y = random.uniform(0.05, 0.95), random.uniform(0.05, 0.95)
        text = ax.text(x, y, kelime, fontsize=fontsize, color=renk,
                       ha='center', va='center', transform=ax.transAxes)

        renderer = fig.canvas.get_renderer()
        bbox = text.get_window_extent(renderer=renderer)
        inv = ax.transAxes.inverted()
        bbox_axes = transforms.Bbox(inv.transform(bbox))

        if not any(bbox_axes.overlaps(k) for k in kutular):
            kutular.append(bbox_axes)
            return x, y
        else:
            text.remove()
    return None, None  # Başarısız

uploaded_file = st.file_uploader("📂 Excel dosyanızı yükleyin (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    required_columns = {"Kelime", "Frekans", "X Koordinat", "Y Koordinat"}
    if not required_columns.issubset(df.columns):
        st.error("❌ Excel dosyasında 'Kelime', 'Frekans', 'X Koordinat', 'Y Koordinat' sütunları olmalı.")
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
        kutular = []

        final_positions = []
        for kelime, freq, x, y in zip(kelimeler, frekanslar, x_koordinatlar, y_koordinatlar):
            boyut = normalize(freq)
            renk = renk_haritasi.get(kelime, "#000000")

            if pd.notnull(x) and pd.notnull(y):
                t = ax.text(x, y, kelime, fontsize=boyut, color=renk,
                            ha='center', va='center', transform=ax.transAxes)
                renderer = fig.canvas.get_renderer()
                bbox = t.get_window_extent(renderer=renderer)
                inv = ax.transAxes.inverted()
                bbox_axes = transforms.Bbox(inv.transform(bbox))
                kutular.append(bbox_axes)
                final_positions.append((kelime, x, y))
            else:
                x_auto, y_auto = kelime_koy(ax, kelime, boyut, renk, kutular, fig)
                if x_auto is not None:
                    final_positions.append((kelime, x_auto, y_auto))
                else:
                    st.warning(f"⚠️ '{kelime}' kelimesi yerleştirilemedi, fazla doluluk olabilir.")

        st.pyplot(fig)

        plt.savefig("output.png", bbox_inches='tight', dpi=300)
        st.success("✅ Görsel başarıyla oluşturuldu ve 'output.png' olarak kaydedildi.")

        with open("output.png", "rb") as f:
            st.download_button("📥 PNG Görselini İndi_
