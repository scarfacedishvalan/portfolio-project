from create_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run_server(debug=False, host = "0.0.0.0", port = 8080)