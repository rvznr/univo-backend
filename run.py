from app import create_app

print("🔁 Flask app başlatılıyor...")  # DEBUG

app = create_app()

if __name__ == "__main__":
    print("🚀 Flask sunucu çalışıyor...")  # DEBUG
    app.run(host="0.0.0.0", port=5000)
