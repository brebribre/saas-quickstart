from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Store in environment variables
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Store securely


class SupabaseConnector:
    def __init__(self):
        """
        Initialize connection to Supabase.
        """
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def fetch_rows(self, name: str, limit: int = 10):
        """
        Fetch rows from a specified table.

        :param name: Table name
        :param limit: Number of rows to fetch (default: 10)
        :return: List of rows or None if an error occurs
        """
        try:
            response = self.supabase.table(name).select("*").limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching data from {name}: {e}")
            return None

    def insert(self, table_name: str, data: list, upsert: bool = False):
        """
        Insert or upsert data into a table.

        :param table_name: Name of the Supabase table
        :param data: List of dictionaries representing the rows to insert
        :param upsert: If True, updates existing rows instead of inserting duplicates
        :return: Response data or None if an error occurs
        """
        if not data:
            print("No data provided for insertion.")
            return None

        try:
            query = self.supabase.table(table_name).upsert(data) if upsert else self.supabase.table(table_name).insert(
                data)
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error inserting into {table_name}: {e}")
            return None
