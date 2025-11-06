import os

# Define the base directory
BASE_DIR = "FastAPI_AdvisorAI"

# Define the folder hierarchy
folders = [
    f"{BASE_DIR}/app",
    f"{BASE_DIR}/app/core",
    f"{BASE_DIR}/app/services",
    f"{BASE_DIR}/app/models",
    f"{BASE_DIR}/app/controllers",
    f"{BASE_DIR}/app/routers",
]

# Define all files to create (empty or placeholders)
files = [
    f"{BASE_DIR}/app/__init__.py",
    f"{BASE_DIR}/app/core/__init__.py",
    f"{BASE_DIR}/app/core/config.py",
    f"{BASE_DIR}/app/core/utils.py",
    f"{BASE_DIR}/app/services/__init__.py",
    f"{BASE_DIR}/app/services/gemini_service.py",
    f"{BASE_DIR}/app/models/__init__.py",
    f"{BASE_DIR}/app/models/schemas.py",
    f"{BASE_DIR}/app/controllers/__init__.py",
    f"{BASE_DIR}/app/controllers/advisor_controller.py",
    f"{BASE_DIR}/app/routers/__init__.py",
    f"{BASE_DIR}/app/routers/advisor_router.py",
    f"{BASE_DIR}/app/main.py",
    f"{BASE_DIR}/.env",
    f"{BASE_DIR}/requirements.txt",
    f"{BASE_DIR}/README.md",
]

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create files
for file in files:
    with open(file, "w", encoding="utf-8") as f:
        f.write("")

print(f"✅ Folder structure created successfully under '{BASE_DIR}'")
