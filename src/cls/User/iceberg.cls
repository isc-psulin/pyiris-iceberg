Class User.iceberg  Extends %Persistent [ DdlAllowed ]
{

Property SettingsJSON As %Text(MAXLEN = 25000);

// Parameter CONFIG = {##class(User.iceberg).GetRawConfig()};

Parameter CONFIGPATH = "/home/irisowner/dev/local_testing_config.json";

ClassMethod LoadConfig() As %String
{
    set fileObj = ##class(%File).%New(..#CONFIGPATH)
    set status =  fileObj.Open("RU")
    set data = fileObj.Read()
    return data
}

ClassMethod GetRawConfig() As %String [ Language = python ]
{
    
    config_str = '''{
                "src_server": "LocalIRIS",
                "target_iceberg": "LocalTesting",
                "job_type": "initial_table_sync",
                "table_chunksize": 100,
                "sql_clause": "",
                "source_table_name": "iceberg_demo.titanic",
                "target_table_name": "iceberg_demo.titanic",
                "partition_field": "PassengerId",
                "grid_type": "tabulator",
                "servers": [
                    { 
                    "name": "LocalIRIS",
                    "dialect": "iris",
                    "database": "IRISAPP",
                    "driver": "com.intersystems.jdbc.IRISDriver",
                    "host": "0.0.0.0",
                    "password": "SYS",
                    "user": "_system",
                    "port": "1972",
                    "schemas": ["iceberg_demo"],
                    "connection_type": "db-api"
                    }
                ],
                "icebergs": [
                    {
                    "name": "LocalTesting",
                    "uri": "sqlite:////tmp//pyiceberg_catalog.db",
                    "warehouse": "//tmp//"
                    },
                    {
                    "name": "IRISCatalogLocalWarehouse",
                    "uri": "iris://_SYSTEM:SYS@localhost:1972/IRISAPP",
                    "warehouse": "/tmp/"
                    },
                    {
                    "name": "Azure",
                    "uri": "",
                    "adls.connection-string": "DefaultEndpointsProtocol=https;AccountName=?;AccountKey=?;EndpointSuffix=core.windows.net",
                    "adls.account-name": "",
                    "location": "abfs://?"
                    }

                
                ]
                }'''

    return config_str
}

ClassMethod GetConfig() As %String [ Language = python ]
{
    import json
    import iris
    from pyiris_iceberg.utils import Configuration

    #config_str = iris.cls('User.iceberg').GetRawConfig()
    config_str = iris.cls('User.iceberg').LoadConfig() 
    config_dict = json.loads(config_str)
    config = Configuration(**config_dict)
    return config
}

ClassMethod ListTables() As %Status [ Language = python ]
{
    import iris
    from pyiris_iceberg import app

    tables = []
    try:
        config = iris.cls(__name__).GetConfig() 
        tables = app.list_tables(config)
        print(f"Found {len(tables)} tables {tables}")
    except Exception as ex:
       print(f"Exception listing tables {ex}")

    return tables
}

ClassMethod InitialTableSync() As %Status [ Language = python ]
{
    import iris
    from pyiris_iceberg import app

    tables = []
    try:
        config = iris.cls(__name__).GetConfig() 
        app.initial_table_sync(config)
    except Exception as ex:
       print(f"Exception: {ex}")
}

ClassMethod UpdateTable() As %Status [ Language = python ]
{
    import iris
    from pyiris_iceberg import app

    tables = []
    try:
        config = iris.cls(__name__).GetConfig() 
        app.update_table(config)
    except Exception as ex:
       print(f"Exception: {ex}")
}

ClassMethod PurgeTable() As %Status [ Language = python ]
{
    import iris
    from pyiris_iceberg import app

    tables = []
    try:
        config = iris.cls(__name__).GetConfig() 
        app.purge_table(config)
        print(f"Purged table {config.target_table_name}")
    except Exception as ex:
       print(f"Exception listing tables {ex}")

    return tables
}

ClassMethod SelectAll() As %Status [ Language = python ]
{
    import iris
    from pyiris_iceberg import app

    tables = []
    try:
        config = iris.cls(__name__).GetConfig() 
        app.select_all(config)
    except Exception as ex:
       print(f"Exception listing tables {ex}")

    return tables
}

Storage Default
{
<Data name="icebergDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>SettingsJSON</Value>
</Value>
</Data>
<DataLocation>^User.icebergD</DataLocation>
<DefaultData>icebergDefaultData</DefaultData>
<IdLocation>^User.icebergD</IdLocation>
<IndexLocation>^User.icebergI</IndexLocation>
<StreamLocation>^User.icebergS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
