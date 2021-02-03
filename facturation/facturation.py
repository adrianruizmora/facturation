import fonctions as fonction
import os

def main():
    try:
        conn = fonction.mysqlconnect()
        fonction.menu(conn)
        conn.close() 
    except Exception as error:
        print('My Error', error)
  

if __name__ == '__main__':
    main()
