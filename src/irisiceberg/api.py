import sys 

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker
from irisiceberg.utils import get_alchemy_engine, Base, get_from_list, MyBaseSettings
from irisiceberg.app import load_config
import pandas as pd
from pydantic import BaseModel
from pyiceberg.catalog import load_catalog
from pathlib import Path

app = FastAPI()
templates = Jinja2Templates("templates")

# Load configuration
# config = load_config()
# engine = get_alchemy_engine(config)
# Session = sessionmaker(bind=engine)

exclude_tables = []

class QueryRequest(BaseModel):
    query: str

class IcebergQueryRequest(BaseModel):
    table_name: str

 
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    tables = []
    inspector = inspect(app.engine)
    for table_name in inspector.get_table_names():
        if table_name in Base.metadata.tables:
            if table_name not in exclude_tables:
                print(f"Getting data for jobs table {table_name}")
                tables.append({
                    "name": table_name,
                    "columns": [column['name'] for column in inspector.get_columns(table_name)]
                })

    return templates.TemplateResponse("index.html", {"request": request, "tables": tables, "grid_type": app.config.grid_type})

@app.get("/search/{table_name}")
async def search_table(table_name: str, q: str = Query(None), job_id: int = Query(None), limit: int = Query(500, ge=1, le=1000)):
    if table_name not in Base.metadata.tables:
        return JSONResponse(content={"error": "Table not found"}, status_code=404)

    with app.Session() as session:
        conditions = []
        params = {"limit": limit}

        if q:
            conditions.extend([f"LOWER(CAST({col['name']} AS VARCHAR)) LIKE :search" for col in inspect(app.engine).get_columns(table_name)])
            params["search"] = f"%{q.lower()}%"

        if job_id and table_name in ['iceberg_job_step', 'log_entries']:
            conditions.append("job_id = :job_id")
            params["job_id"] = job_id

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT TOP :limit * FROM {table_name}
        WHERE {where_clause}
        """
        print(f"Query in search table {query}")
        result = session.execute(text(query), params)
        
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        print(len(df.index))
        
        # Convert Timestamp columns to strings
        for col in df.select_dtypes(include=['datetime64']).columns:
            df[col] = df[col].astype(str)
        df = df.fillna(value="")
        print(df.info())
        return JSONResponse(content=df.to_dict(orient="records"))

@app.get("/dataview", response_class=HTMLResponse)
async def dataview(request: Request):
    return templates.TemplateResponse("dataview.html", {"request": request, "grid_type": app.config.grid_type})


@app.post("/execute_query")
async def execute_query(query_request: QueryRequest):
    try:
        with app.Session() as session:
            result = session.execute(text(query_request.query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            # Convert Timestamp columns to strings
            for col in df.select_dtypes(include=['datetime64']).columns:
                df[col] = df[col].astype(str)

            df = df.fillna(value="")
            print(f"Records retrieved = {len(df)}")
            return JSONResponse(content={
                "columns": df.columns.tolist(),
                "data": df.to_dict(orient="records")
            })
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.post("/execute_iceberg_query")
async def execute_iceberg_query(query_request: IcebergQueryRequest):
   # try:

    print(f"execute_iceberg_query - {query_request}")
    print(app.iceberg_catalog)
    
    table = app.iceberg_catalog.load_table(query_request.table_name)
    print(table)
    if table:
        df = table.scan(limit=1000).to_pandas()
        print(f"{len(df)} records returned")
        # Convert Timestamp columns to strings
        for col in df.select_dtypes(include=['datetime64']).columns:
            df[col] = df[col].astype(str)
        df = df.fillna(value="")
        
        return JSONResponse(content={
            "columns": df.columns.tolist(),
            "data": df.to_dict(orient="records")
        })
    else:
        return JSONResponse(content={"error": "Table not found"}, status_code=404)
    # except Exception as e:
    #     return JSONResponse(content={"error": str(e)}, status_code=400)


#if __name__ == "__main__":
    
# need to use --config_string so pydantic doesn't throw unrecognized arg
if len(sys.argv) > 2:
    if sys.argv[1] != '--config_string':
        raise Exception("Only --config_string arg accepted")
    config_file_path = sys.argv[2]
    app.config = load_config(config_file_path)
else:
    app.config = load_config()

app.engine = get_alchemy_engine(app.config)
app.Session = sessionmaker(bind=app.engine)

app.target_iceberg = get_from_list(app.config.icebergs, app.config.target_iceberg)
app.iceberg_catalog = load_catalog(**app.target_iceberg.model_dump())

import uvicorn
# uvicorn.run('api:app', host="0.0.0.0", port=8002, reload=True)
if __name__ == "__main__":
    config = uvicorn.Config("api:app", port=8002, log_level="info")
    server = uvicorn.Server(config)
    server.run()   
