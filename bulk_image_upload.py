import os
import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=75.119.144.130;"
    "DATABASE=univo_db;"
    "UID=SA;"
    "PWD=YourStrong!Passw0rd;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)
cursor = conn.cursor()

note_content_ids = [  
    4, 4, 5, 6, 7, 9, 9, 11, 11, 11, 13, 13, 13,
    10, 11, 12, 1, 1, 20, 20, 21, 21, 22, 22, 23,
    29, 29, 31, 15, 15, 34, 34, 34, 35, 35, 35,
    36, 36, 37, 37, 38, 39, 39, 40, 40, 39, 39
]

image_files = [
    "c3.png", "c4.png", "spamfilter.jpg", "c5.png", "busse.png", "image.png", "image (1).png",
    "image_P.png", "image.png", "image_eva.png", "image_v.png", "image_x.png", "image_z.png",
    "image_a.png", "square.png", "complex.png", "image1_1.png", "image1_2.png", "image2_2.png",
    "image2_3.png", "image2_5.png", "image2_4.png", "image2_6.png", "image2_7.png", "image2_8.png",
    "image2_9.png", "image2_10.png", "image2_11.png", "image2_12.png", "image2_12.png",
    "image2_13.png", "image2_13.png", "image2_13.png", "image2_14.png", "image2_15.png",
    "image2_16.png", "image3_2.png", "image3_3.png", "image3_4.png", "image3_5.png", "image3_6.png",
    "image3_7.png", "image3_8.png", "image3_10.png", "image3_9.png", "image3_7.png", "image3_8.png"
]

image_folder = r"C:\temp"

for note_content_id, filename in zip(note_content_ids, image_files):
    file_path = os.path.join(image_folder, filename)
    if not os.path.exists(file_path):
        print(f"❌ Dosya bulunamadı: {file_path}")
        continue

    with open(file_path, "rb") as file:
        image_data = file.read()

    cursor.execute("""
        MERGE INTO note_images AS target
        USING (SELECT ? AS image_url) AS source
        ON target.image_url = source.image_url
        WHEN MATCHED THEN
            UPDATE SET image_data = ?, note_content_id = ?
        WHEN NOT MATCHED THEN
            INSERT (note_content_id, image_url, image_data)
            VALUES (?, ?, ?);
    """, filename, image_data, note_content_id, note_content_id, filename, image_data)

    print(f"✅ Yüklendi/Güncellendi: {filename}")

conn.commit()
cursor.close()
conn.close()
print("\n🎉 Tüm görseller başarıyla tamamlandı.")
