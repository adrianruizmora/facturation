import fonctions as fonction
import os

def main():
    try:
        conn = fonction.mysqlconnect()
        cursor = conn.cursor()
        print("\nConnection à la base de donées réussie ! \n")
        
    except Exception as error:
        print('My Error', error)

    fonction.menu(cursor,conn) 

if __name__ == '__main__':
    main()
