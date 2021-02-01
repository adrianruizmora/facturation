import os
import platform
import getpass
import pymysql as mysql
from typing import NamedTuple
# import parser

class connection_info(NamedTuple):
    host : str
    user : str
    password : str
    db : str

def askCredentials():
    noErrors = True 
    while noErrors :
        credentials = connection_info
        credentials.host = input("Veuillez saisir l'IP de hôte : ")
        credentials.user = input("Veuillez saisir le nom d'utilisateur : ")
        credentials.password = getpass.getpass(prompt="Veuillez saisir votre mot de passe : ", stream=None)
        credentials.db = "db_facturation" 
        if credentials.host == '' or credentials.user == '' or credentials.password == '':
            print('\nVeuillez saisir des credentiels valides :')
        else:
            return credentials
    
def createCredentials():
    credentials = askCredentials()
    create_file = input("Voulez vous enregistrer vos informations dans un fichier credentiels.txt [Y/N] ? ")
    if create_file.upper() == 'Y':
        file = open("credentials.txt", "w+", encoding='utf-8')
        file.write(
            f"{credentials.host} \n" 
            f"{credentials.user} \n"
            f"{credentials.password} \n"
            f"{credentials.db} \n"
        )
        file.close()
    return credentials

def credentialsExists():
    return os.path.isfile(f"credentials.txt")

def mysqlconnect():

    if not credentialsExists():
        credentials = createCredentials()
        conn = mysql.connect(
            host=credentials.host,
            user=credentials.user,
            password=credentials.password,
            db=credentials.db,
        )
        if not conn:
            return 1
        else:
            return conn
    else:
        file = open("credentials.txt")
        file_lines = file.readlines()
        credentials = [line.strip() for line in file_lines]
        conn = mysql.connect(
            host=credentials[0],
            user=credentials[1],
            password=credentials[2],
            db=credentials[3],
            )
        if not conn:
            return 1
        else:
            return conn
    # cur.execute("SELECT @@version")
    # output = cur.fetchall()
    # print(output)
    # conn.close()   

def createClientSchema(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS clients (
        client_type TEXT,
        client_name TEXT,
        email_address TEXT,
        phone_number INT,
        street_address TEXT,
        town_city TEXT,
        zip_code INT)""")

def createInvoiceSchema(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS invoices (
    product_name  TEXT,
    product_ref   TEXT,
    quantity  INT,
    unit_price    INT,
    invoice_id    INT,
    client    TEXT,
    creation_date TEXT
    )""")

def clearSystem():
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        os.system('clear')
    else:
        os.system('cls')

def isNumber(message, user_input):
    while not user_input.isnumeric() or user_input.upper() == "SORTIE":
        user_input  = input(message)
        if user_input.isnumeric():
            user_input = int(user_input)
            return user_input
        elif user_input.upper() == "SORTIE":
            return "True"  
    return int(user_input)

def searchClient(cursor,conn):
    clearSystem()
    print("> Taper SORTIE à tout moment pour retourner au menu principal.")
    client_name = input("> Nom client : ")
    if client_name.upper() == "SORTIE": return menu(cursor, conn) 
    email_address = input("> Email : ")
    if email_address.upper() == "SORTIE": return menu(cursor, conn)
    if email_address == '': email_address = ' '
    if client_name == '': client_name = ' '
    search_by_command = """SELECT *
    FROM clients
    WHERE REGEXP_LIKE(client_name, %s)
    OR REGEXP_LIKE(email_address, %s)"""
    search_by_values = (client_name, email_address)
    cursor.execute(search_by_command, search_by_values)
    return cursor.fetchall()

def addClient(cursor,conn):
    clearSystem()
    print("> Taper SORTIE à tout moment pour retourner au menu principal.")
    number_of_clients = input("> Combien des clients voulez vous ajouter: ")
    if number_of_clients.upper() == "SORTIE": return menu(cursor,conn)
    number_of_clients = isNumber("> Erreur, veuillez sasir un nombre : ", number_of_clients)
    if number_of_clients == "True": return menu(cursor, conn)
    clients =[]
    for _ in range(number_of_clients):
        client_type = input("> Type de client [particulier/entreprise] : ")
        if client_type.upper() == "SORTIE" : return menu(cursor,conn)
        client_name = input("> Nom du client : ")
        if client_name.upper() == "SORTIE" : return menu(cursor,conn)
        email_address = input("> Adresse email du client : ")
        if email_address.upper() == "SORTIE" : return menu(cursor,conn)
        phone_number = input("> Numéro de télephone : ")
        if phone_number.upper() == "SORTIE" : return menu(cursor,conn)
        phone_number = isNumber("> Erreur, veuillez saisir un numero de téléphone : ", phone_number)
        if phone_number == "True": return menu(cursor, conn)
        street_address = input("> Rue : ")
        if street_address.upper() == "SORTIE" : return menu(cursor,conn)
        town_city = input("> Ville : ")
        if town_city.upper() == "SORTIE" : return menu(cursor,conn)
        zip_code = input("> Code postale : ")
        if client_type.upper() == "SORTIE" : return menu(cursor,conn)
        zip_code = isNumber("> Erreur, veuillez saisir un code postale : ", zip_code)
        if zip_code == "True": return menu(cursor, conn)
        client = (client_type.lower(), client_name.lower, email_address.lower(), phone_number, street_address.lower(), town_city.lower(), zip_code)
        clients.append(client)
    insert_clients = """INSERT INTO clients (
    client_type,
    client_name,
    email_address,
    phone_number,
    street_address,
    town_city,
    zip_code
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s)"""
    cursor.executemany(insert_clients,clients)
    conn.commit()
    print(cursor.rowcount, "ont été ajoutés.")

def menu(cursor,conn):
    clearSystem()
    createClientSchema(cursor)
    createInvoiceSchema(cursor)
    # cursor.execute("SHOW TABLES")
    # for x in cursor:
    #     print(x)

    # cursor.execute("SELECT * FROM clients")
    # clients = cursor.fetchall()
    # for client in clients:
    #     print(client)
    
    # cursor.execute("DROP TABLE clients")
    # for x in cursor:
    #     print(x)

    parametres = {
    '0' : ": Rechercher un client.",
    '1' : ": Ajouter un client.",
    '2' : ": Modifier un client.",
    '3' : ": Rechercher une facture.",
    '4' : ": Ajouter une facture",
    '5' : ": Modifier une facture.",
    '6' : ": Supprimmer un enregistrement.",
    '7' : ": Sortir du programme."
    }
    options = parametres.keys()
    options = sorted(options)
    option_selected = False
    print("- - - - Bienvenue au menu principal  - - - -\n")
    while not option_selected:
        for entry in options:
            print(entry, parametres[entry])
        print('\n')
        selected = input("Veuillez choisir une option : ")
        if selected == "0":
            print(searchClient(cursor,conn))
            option_selected = True
        elif selected == "1":
            addClient(cursor,conn)
            option_selected = True
        elif selected == "2":
            option_selected = True
            pass
        elif selected == "3":
            option_selected = True
            pass
        elif selected == "4":
            option_selected = True
            pass
        elif selected == "5":
            option_selected = True
            pass
        elif selected == "6":
            option_selected = True
            pass
        elif selected == "7":
           clearSystem()
           exit()
        else:
            clearSystem()
            menu(cursor,conn)
