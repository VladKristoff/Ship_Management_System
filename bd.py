import psycopg2 

def connect_db():
    try:
        conn = psycopg2.connect(user="postgres",
                                password="1234",
                                host="localhost",
                                port="5432",
                                database="ships_bd")
        
        return conn
    
    except Exception as e:
        print(f"Ошибка подключения к базе данных {e}")