# DevinNest-Backend
DevinNest相关后端项目

## Tech Stack
- **Framework**: FastAPI (Python)
- **Runtime**: Uvicorn
- **Validation**: Pydantic
- **AI Integration**: OpenAI SDK (Ready for extension)

## Project Structure
```
/app
  /api          # API Routes
  /core         # Config & Security
  /schemas      # Pydantic Models (Data Validation)
  /services     # Business Logic (LLM Integration)
  main.py       # Entry Point
```

## Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Server**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
