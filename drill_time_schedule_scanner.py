import streamlit as st
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from sya import coordinates, tambah_waktu

st.set_page_config(layout="centered")
st.title("🖼️ Analisis Gambar Time Sheet Drilling")

# uploaded_file = r"/mount/src/drill-time-schedule-scanner/image_fix.png"
# uploaded_file = r"image_test.png"
uploaded_file = st.file_uploader("📤 Unggah gambar timesheet (format: JPG, PNG, dsb)", type=["jpg", "jpeg", "png"])


if uploaded_file is not None:
    # Baca dan konversi gambar ke OpenCV format
    image = Image.open(uploaded_file).convert("RGB")
    image = np.array(image)
    # img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    BLACK_THRESHOLD = 105
    BLACK_PIXEL_PERCENTAGE = 0.4

    t = 7.10

    data = []

    # Loop tiap area koordinat
    for row in coordinates.values():
        for activity, (x1, y1, x2, y2) in row.items():
            roi = gray_image[y1:y2, x1:x2]  # Region of Interest (area yang dicek)

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            print(activity, (x1, y1, x2, y2))
            # Hitung jumlah pixel hitam di area tersebut
            total_pixels = roi.size
            black_pixels = np.sum(roi < BLACK_THRESHOLD)
            # cv2.circle(image, (center_x, center_y), 3, (255, 0, 0), -1)


            # Hitung persentase pixel hitam
            black_ratio = black_pixels / total_pixels

            if black_ratio > BLACK_PIXEL_PERCENTAGE:
                # Gambar titik merah di tengah area
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                cv2.circle(image, (center_x, center_y), 3, (0, 0, 255), -1)
                # Simpan ke hasil
                data.append({
                    "Waktu": t,
                    "Aktivitas": activity
                })
            

                # Tampilkan label
                cv2.putText(image, activity, (x1, y1 - 5), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 255, 0), 1)
                cv2.circle(image, (center_x, center_y), 3, (255, 0, 0), -1)
                print(t, activity)    

        t = tambah_waktu(t,10)

    df_results = pd.DataFrame(data)

    st.subheader("🧪 Gambar Hasil Proses (Threshold + Titik)")
    st.image(image, caption="Gambar setelah diproses", use_column_width=True)

    # Hitung jumlah kemunculan per aktivitas
    activity_counts = df_results["Aktivitas"].value_counts()

    st.subheader("📊 Aktivitas Paling Sering Muncul")
    fig, ax = plt.subplots()
    activity_counts.plot(kind="bar", ax=ax, color='skyblue')
    ax.set_ylabel("Jumlah Kemunculan")
    ax.set_xlabel("Aktivitas")
    st.pyplot(fig)

    st.subheader("📋 Daftar Aktivitas per Waktu")
    st.dataframe(df_results)


else:
    st.info("Silakan upload gambar terlebih dahulu untuk memulai analisis.")


