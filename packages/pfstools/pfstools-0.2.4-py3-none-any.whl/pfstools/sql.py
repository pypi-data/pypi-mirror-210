import pyodbc
import pandas as pd
from sqlalchemy import create_engine, text 
from urllib.parse import quote_plus


from os import environ as env

# ---------------------
# load defaults
# ---------------------

try:
    import dotenv
    from dotenv import load_dotenv
    import os #provides ways to access the Operating System and allows us to read the environment variables
    load_dotenv()
    
except:
    print('package dotenv not installed')


if not "sql_driver" in env:
    sqldrivers = [d for d in  pyodbc.drivers() if 'SQL Server' in d]
    env["sql_driver"] = sqldrivers[-1] 


def sql_connection( server="", db=""):
    """
    returns a SQLalchemy connection object to specified sql server & db. 

    Connects via trusted (Windows) authentication only

    Uses default server and db if none specified.

    """
    db = db if db else env["sql_db"]
    server = server if server else env["sql_server"]
    driver = env["sql_driver"]

    connection_string = f"Driver={{{driver}}};Server={server};Database={db};Trusted_Connection=yes;"
    connection_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"

    #return pyodbc.connect(connection_string)
    return create_engine(connection_url).connect()

def _read_sql(con,
    sql: 'str | Sequence[str]' ,
    setup_sql: 'str | Sequence[str] | None' = None,
    index_col: 'str | Sequence[str] | None' = None,
    coerce_float: 'bool' = True,
    params=None,
    parse_dates=None,
    columns=None,
    chunksize: 'int | None' = None,
    ):  
     
    # execute setup queries if provided
    if setup_sql != None:
        if not isinstance(setup_sql, list):
            setup_sql = [setup_sql]
        for q in setup_sql:
            con.execute(text(q))
    if isinstance(sql, dict):
        df = { k : pd.read_sql(text(q), con) for k,q in sql.items()}
    elif isinstance(sql, list):       
        df = [pd.read_sql(text(q), con ) for q in sql]
    else:
        df = pd.read_sql(text(sql), con)
    
    return df

class SqlCnx:
    def __init__(self, server='', db='', persistent_cnx=False):
        self.server = server if server else (env["sql_server"] if "sql_server" in env else "")
        self.db = db if db else (env["sql_db"] if "sql_db" in env else "")
        self.driver = env['sql_driver']
        self.persistent = persistent_cnx
        if persistent_cnx:
            self.cnx = sql_connection(self.server, self.db)
        else:
            self.cnx = None        

    def connection(self):
        if self.cnx is None:
            return sql_connection(self.server, self.db)
        else:
            return self.cnx

    def connection_string(self):
         return f"Driver={{{self.driver}}};Server={self.server};Database={self.db};Trusted_Connection=yes;"

    def connection_url(self):
         return f"mssql+pyodbc:///?odbc_connect={quote_plus(self.connection_string())}"

    def read(self,sql: 'str | Sequence[str]' ,
        setup_sql: 'str | Sequence[str] | None' = None,
        index_col: 'str | Sequence[str] | None' = None,
        coerce_float: 'bool' = True,
        params=None,
        parse_dates=None,
        columns=None,
        chunksize: 'int | None' = None,
        ):  
 
        if self.persistent:
            df = _read_sql(self.cnx, sql, setup_sql, index_col, coerce_float, params, parse_dates, columns, chunksize)
        else:
            with self.connection() as con:
                df = _read_sql(con, sql, setup_sql, index_col, coerce_float, params, parse_dates, columns, chunksize)
        
        return df

    def exec(self,
        sql: 'str | Sequence[str]' ,
        server: 'str' ='',
        db : 'str' =''):


        with self.connection() as con:
            if isinstance(sql, str):
                sql = [sql]
            for q in list(sql):
                con.execute(text(q))
            con.commit()
            
    def __exit__(self):
        if not self.cnx is None:
            self.cnx.close()


    def to_sql(self,
        df,
        name: 'str',
        schema=None,
        if_exists: 'str' = 'replace',
        index: 'bool_t' = False,
        index_label=None,
        chunksize=None,
        dtype: 'DtypeArg | None' = None,
        method=None):

        """
        Based on pandas DataFrame.to_sql, but subbing parameters for server & db

        it assumes a SQL Server environment using Windows Authentication.

        Also changed defaults for if_exists (replace instead of fail)
        and index (False instead of True)

        """
        engine = create_engine(self.connection_url())   
        df.to_sql(name
                , engine
                , if_exists = if_exists
                , index=index
                , schema=schema
                , index_label=index_label
                , chunksize=chunksize
                , dtype=dtype
                , method=method)


    def running_jobs(self):
        jobs_q = """
        SELECT sj.Name as job_name, 
            sja.start_execution_date,
            sj.job_id,
            right(sj.job_id, 10) as job_id_end

        FROM msdb.dbo.sysjobs sj
        JOIN msdb.dbo.sysjobactivity sja
        ON sj.job_id = sja.job_id
        WHERE session_id = (
            SELECT MAX(session_id) FROM msdb.dbo.sysjobactivity)
            and sja.stop_execution_date is null
            and not sja.start_execution_date IS NULL

        """
        
        return self.read(jobs_q)



    def who2(self, link_jobs = False):
        
        whodf = self.read("exec sp_who2").apply(lambda x: x.str.strip())
        
        whodf["job_id_end"] = whodf.ProgramName.apply(
                lambda x: x.split("Job 0x")[1].split(" : Step")[0][-10:]
                if ("Job 0x" in x) & (" : Step" in x)
                else ""
            )

        whodf.columns = [
            "SPID",
            "Status",
            "Login",
            "HostName",
            "BlkBy",
            "DBName",
            "Command",
            "CPUTime",
            "DiskIO",
            "LastBatch",
            "ProgramName",
            "SPID2",
            "REQUESTID",
            "job_id_end",
        ]
        
        if link_jobs:
            jobs =   self.running_jobs 
            whodf = whodf.merge(jobs, how='left', on ='job_id_end')

        return whodf    
    

