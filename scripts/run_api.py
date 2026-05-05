import os
import sys
import uvicorn

# إضافة المجلد الرئيسي للمسار عشان بايثون يشوف مجلد app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    )
