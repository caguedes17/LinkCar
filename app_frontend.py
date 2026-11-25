"""Inicializador seguro do site LinkCar: preserva o app.py original.
Execute: python -m flask --app app_frontend run
"""
from app import app  # reutiliza autenticação, Match, CRUD e favoritos existentes
from frontend_routes import frontend

app.register_blueprint(frontend)

if __name__ == "__main__":
    app.run(debug=False)
