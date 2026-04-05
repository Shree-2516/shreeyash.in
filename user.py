from app import create_app

app = create_app(include_main=True, include_admin=False)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
