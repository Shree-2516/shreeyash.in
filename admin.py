from app import create_app

app = create_app(include_main=False, include_admin=True, admin_prefix="")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
