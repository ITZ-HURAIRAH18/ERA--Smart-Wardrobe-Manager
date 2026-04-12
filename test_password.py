import psycopg2
from urllib.parse import quote
import os
from dotenv import load_dotenv

load_dotenv()

# Your connection details
host = "aws-1-ap-northeast-1.pooler.supabase.com"
port = 5432
database = "postgres"
user = "postgres.dguwytbcyinsmliyvvge"
password_raw = "fLfXx6Ff-iX$wce"
password_encoded = quote(password_raw, safe='')

print(f"Testing password formats:\n")
print(f"Raw password: {password_raw}")
print(f"URL-encoded: {password_encoded}\n")

# Test 1: Using connection string with raw password
print("Test 1: Connection string with raw password")
try:
    connection_string = f"postgresql://{user}:{password_raw}@{host}:{port}/{database}"
    print(f"String: {connection_string}")
    conn = psycopg2.connect(connection_string)
    print("✅ SUCCESS with raw password!\n")
    conn.close()
except Exception as e:
    print(f"❌ Failed: {e}\n")

# Test 2: Using connection string with URL-encoded password
print("Test 2: Connection string with URL-encoded password")
try:
    connection_string = f"postgresql://{user}:{password_encoded}@{host}:{port}/{database}"
    print(f"String: {connection_string}")
    conn = psycopg2.connect(connection_string)
    print("✅ SUCCESS with URL-encoded password!\n")
    conn.close()
except Exception as e:
    print(f"❌ Failed: {e}\n")

# Test 3: Using individual parameters
print("Test 3: Using individual connection parameters")
try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password_raw
    )
    print("✅ SUCCESS with individual parameters!\n")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print("Database version:", cursor.fetchone())
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Failed: {e}\n")

print("\n⚠️  If all tests fail, verify your password in Supabase console!")
