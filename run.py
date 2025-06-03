from app import create_app

print("📦 run.py başladı...")

app = create_app()

if __name__ == "__main__":
    print("🔥 Flask sunucusu başlatılıyor...")
    app.run(host="0.0.0.0", port=5000)
