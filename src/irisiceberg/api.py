from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from irisiceberg.utils import Base, get_alchemy_engine, Configuration
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load configuration
config = Configuration()  # You might need to adjust this based on how you load your configuration
engine = get_alchemy_engine(config)
Session = sessionmaker(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    tables = []
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        if table_name in Base.metadata.tables:
            with Session() as session:
                query = session.query(Base.metadata.tables[table_name])
                df = pd.read_sql(query.statement, session.bind)
                tables.append({
                    "name": table_name,
                    "data": df.to_dict(orient="records"),
                    "columns": df.columns.tolist()
                })

    return templates.TemplateResponse("index.html", {"request": request, "tables": tables})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
