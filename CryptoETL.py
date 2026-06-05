import requests
import pandas as pd
import psycopg2
import os


def extract():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": "bitcoin,ethereum"
    }
    resp = requests.get(url, params=params)

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
    except Exception as e:
        print("❌ extract: request/json error:", e)
        return pd.DataFrame()

    # 如果 API 返回错误结构（例如 429）
    if not isinstance(data, list):
        print("❌ extract: API returned non-list:", data)
        return pd.DataFrame()

    return pd.DataFrame(data)
def transform(df):
    expected_cols = ["id", "symbol", "current_price", "market_cap"]

    # 如果缺列，打印并返回空 DF
    for col in expected_cols:
        if col not in df.columns:
            print("Missing column:", col)
            print("Actual columns:", df.columns)
            return pd.DataFrame()

    df = df[expected_cols]
    df["timestamp"] = pd.Timestamp.now("UTC")
    return df


def load_to_postgres(df):
    if df.empty:
        print("⚠️ load: empty df, skipping write")
        return
    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost")
        database="crypto_db",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS crypto_prices (
            id TEXT,
            timestamp TIMESTAMPTZ,
            symbol TEXT,
            current_price NUMERIC,
            market_cap NUMERIC,
            PRIMARY KEY (id, timestamp)
        );
    """)

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO crypto_prices (id, timestamp, symbol, current_price, market_cap)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id, timestamp)
            DO UPDATE SET
                current_price = EXCLUDED.current_price,
                market_cap = EXCLUDED.market_cap;
        """, (
            row["id"],
            row["timestamp"],
            row["symbol"],
            row["current_price"],
            row["market_cap"]
        ))

    conn.commit()
    print("UPSERT completed")
    cur.close()
    conn.close()


def etl():
    df_raw =extract()
    df_clean = transform(df_raw)
    load_to_postgres(df_clean)


if __name__ == "__main__":
    etl()
