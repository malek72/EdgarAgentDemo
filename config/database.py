from config.config import MONGO,DB_CONNECTION,SUPABASE
from supabase import create_client, Client



if(DB_CONNECTION == 'mysql'):
    pass

if(DB_CONNECTION == 'supabase'):
    supabase_client = Client = create_client(SUPABASE['SUPABASE_URL'], SUPABASE['SUPABASE_KEY'])
    data = supabase_client.table("auth_codes").select("*").execute()

    if data.data:
        last_record = data.data[-1]
        BEARERTOKEN = last_record["access_token"]

