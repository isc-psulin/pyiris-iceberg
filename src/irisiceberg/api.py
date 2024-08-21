from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from irisiceberg.utils import Base, get_alchemy_engine, Configuration
import pandas as pd
import sys 

app = FastAPI()
templates = Jinja2Templates(directory="/Users/psulin/projects/irisiceberg/templates")

# Load configuration
sys.path.append("/Users/psulin/projects/irisiceberg/configs")
import testing_configs

config = getattr(testing_configs, 'iris_src_local_target')
config = Configuration(**config)
#config = Configuration(testing_configs.iris_src_local_target)  # You might need to adjust this based on how you load your configuration
print(f"CONFIG - {config}")
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
