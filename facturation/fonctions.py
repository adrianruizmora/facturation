import os
import platform
import getpass
import logging
import pymysql as mysql
from typing import NamedTuple

""" Logging implementation """
logging.basicConfig(filename="log_facturation.log", level=logging.INFO,
 format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

#Class immutable qui contient les identifiants de l'utilisateur 
#pour acceder à chaque element utiliser le symbole '.'
class connection_info(NamedTuple):
    host : str
    user : str
    password : str
    db : str
#fonction qui ne prend rien en parametre et qui retourne un des identifiants de type connection_info
#Demande à l'utilisateur de saisir des identifiants
def askCredentials():
    noErrors = True 
    while noErrors :
        credentials = connection_info
        credentials.host = input("Veuillez saisir l'IP de serveur : ")
        credentials.user = input("Veuillez saisir le nom d'utilisateur : ")
        credentials.password = getpass.getpass(prompt="Veuillez saisir votre mot de passe : ", stream=None)
        credentials.db = "db_facturation" 
        if credentials.host == '' or credentials.user == '' or credentials.password == '':
            print('\nVeuillez saisir des credentiels valides :')
        else:
            logging.info("Demande de saisi d'identifiants")
            return credentials

#fonction qui ne prend rien en parametre et qui retourne des identifiants de type connection_info
#demande à l'utilisateur de crée un fichier credentials.txt où l'ont sauvegarde les identifiants  
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
        logging.info("Creation de fichier d'identifiants")
    else:
        logging.info("Les identifiants n'ont pas été sauvegardés dans un fichier")
    return credentials

#fonction qui ne prend rien en parametre et qui retourne un True si le fichier credentials existe False sinon
def credentialsExists():
    logging.info("On regarde si les identifiants existent dans un fichier credentials.txt")
    return os.path.isfile(f"credentials.txt")

#fonction qui ne prend rien en parametre et qui retourne la connection à une base de données ou 1 si echec de connection
#si le fichier credentials.txt existe il utilise les identifiants sauvegardés dans ce dernier sinon,
#il demande à l'utilisateur de saisir des identifiants
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
            logging.info('Erreur de connection à la base de données !')
            return 1
        else:
            logging.info("Connection à la base de données réussie !")
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
            logging.info('Erreur de connection à la base de données !')
            return 1
        else:
            logging.info("Connection à la base de données réussie !")
            return conn

#fonction qui prend un cursor et qui ne retourne rien
#creation d'un schema pour la table clients
def createClientSchema(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS clients (
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    client_type TEXT,
    client_name TEXT,
    email_address TEXT,
    phone_number TEXT,
    street_address TEXT,
    town_city TEXT,
    zip_code TEXT)
    """)
    logging.info("Creation du schema clients")

#fonction qui prend un cursor et qui ne retourne rien
#creation d'un schema pour la table des factures
def createInvoiceSchema(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    client    TEXT,
    creation_date TEXT,
    total INT
    )""")
    logging.info("Creation du schema invoices")

#fonction qui prend un cursor et qui ne retourne rien
#creation d'un schema pour la table produits
def createProductsSchema(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
    id INT NOT NULL AUTO_INCREMENT,
    invoice_id    INT,
    product_name  TEXT,
    product_ref   TEXT,
    quantity  INT,
    unit_price    INT,
    PRIMARY KEY (id),
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
    )""")
    logging.info("Creation du schema products")

#fonction qui ne prend rien en parametre et qui ne retourne rien
# efface les derniers informations affichées dans le CLI, utilise la commande clear si l'OS est linux ou mac,
# la commande cls si windows
def clearSystem():
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        os.system('clear')
    else:
        os.system('cls')
    logging.info("Nettoyage du CLI")

#fonction qui prend un message et l'entrée utilisateur en parametre et qui renvoie l'input en le transformant en type int,
#ou un string "TRUE" si l'input est le mot "SORTIE"
def isNumber(message, user_input):
    while not user_input.isnumeric() or user_input.upper() == "SORTIE":
        user_input  = input(message)
        if user_input.isnumeric():
            user_input = int(user_input)
            return user_input
        elif user_input.upper() == "SORTIE":
            return "True"  
    logging.info("On verifie si l'input saisi par l'utilisateur est du text numerique ou sortie")
    return int(user_input)

#fonction qui prend une connexion et qui
#renvoie de manière rucursive la fonction même si, l'utilisateur veut effectuer une nouvelle recherche,
#renvoie un tuple des tuples des clients si le utilisateur ne veut pas effectuer une nouvelle recherche
#renvoie un menu si l'utilisateur veut retourner au menu principale
def searchClient(conn):
    cursor = conn.cursor()
    clearSystem()
    print("-------- Rechercher un client --------")
    print("> Taper SORTIE à tout moment pour retourner au menu principal.")
    client_name = input("> Nom client : ")
    if client_name.upper() == "SORTIE":
        return menu(conn) 
    email_address = input("> Email : ")
    if email_address.upper() == "SORTIE": 
        return menu(conn)
    if client_name == '':
        client_name = " "
    else:
        client_name = '^' + client_name
    if email_address == '':
        email_address = " "
    else:
        email_address = '^' + email_address
    sql_select = """SELECT *
    FROM clients
    WHERE REGEXP_LIKE(client_name, %s)
    OR REGEXP_LIKE(email_address, %s)"""
    values = (client_name, email_address)
    cursor.execute(sql_select, values)
    clients = cursor.fetchall()
    for client in clients:
        print(client)
    repeat_search = input("Voulez vous effectuer une nouvelle recherche ? [Y/N/SORTIE] : ")
    if repeat_search.upper() == "Y":
        logging.info("Recherche des clients terminé correctement, utilisateur veut effectuer une nouvelle recherche")
        return searchClient(conn)
    elif repeat_search.upper() == "N":
        logging.info("Recherche des clients terminé correctement")
        return clients
    else:
        logging.info("L'utilisateur veut retourner au menu principal")
        return menu(conn)

#fonction qui prend une connection et qui retourne un menu si l'utilisateur saisi le mot SORTIE,
#sinon elle retourne rien et ajoute un client sur la table clients
def addClient(conn):
    cursor = conn.cursor()
    clearSystem()
    print("-------- Ajouter un client --------")
    print("> Taper SORTIE à tout moment pour retourner au menu principal.")
    number_of_clients = input("> Combien des clients voulez vous ajouter: ")
    if number_of_clients.upper() == "SORTIE": 
        return menu(conn)
    number_of_clients = isNumber("> Erreur, veuillez sasir un nombre : ", number_of_clients)
    if number_of_clients == "True": 
        return menu(conn)
    clients_values =[]
    for _ in range(number_of_clients):
        client_type = input("> Type de client [particulier/entreprise] : ")
        if client_type.upper() == "SORTIE" : 
            return menu(conn)
        client_name = input("> Nom du client : ")
        if client_name.upper() == "SORTIE" : 
            return menu(conn)
        email_address = input("> Adresse email du client : ")
        if email_address.upper() == "SORTIE" : 
            return menu(conn)
        phone_number = input("> Numéro de télephone : ")
        if phone_number.upper() == "SORTIE" : 
            return menu(conn)
        street_address = input("> Rue : ")
        if street_address.upper() == "SORTIE" : 
            return menu(conn)
        town_city = input("> Ville : ")
        if town_city.upper() == "SORTIE" : 
            return menu(conn)
        zip_code = input("> Code postale : ")
        if zip_code.upper() == "SORTIE" : 
            return menu(conn)
        client = (client_type.lower(), client_name.lower(), email_address.lower(), phone_number.lower(), street_address.lower(), town_city.lower(), zip_code.lower())
        clients_values.append(client)
    sql_insert = """INSERT INTO clients (
    client_type,
    client_name,
    email_address,
    phone_number,
    street_address,
    town_city,
    zip_code
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s)"""
    cursor.executemany(sql_insert,clients_values)
    conn.commit()
    new_clients_added = cursor.rowcount
    print(new_clients_added, "ont été changés.")
    logging.info(f"{new_clients_added} nouveau clients ont été aujouté")

#fonction qui prend une connection et qui renvoie un menu
#modifie une ou plusieurs information d'un client
def editClient(conn):
    cursor = conn.cursor()
    print("-------- Modifier un client --------")
    print("> Taper SORTIE à tout moment pour retourner au menu principal.")
    clients = searchClient(conn)
    if len(clients) != 0:
        selected_client = input("Veuillez choisir le numero de client à modifier : ")
        if selected_client.upper() == "SORTIE" : 
            return menu(conn)
        selected_client = isNumber("Erreur, veuillez saisir un nombre : ", selected_client)
        if selected_client == "True" : 
            return menu(conn)
        while selected_client == 0:
            selected_client = isNumber("Erreur, veuillez saisir un nombre : ", selected_client)
            if selected_client == "True" : 
                return menu(conn)
        print("> Taper entrée pour sauter de champ et ne pas le modifier.")
        client_info = {}
        client_info["client_type"] = input("Type client [particulier/entreprise] : ")
        if client_info["client_type"].upper() == "SORTIE" : 
            return menu(conn)  
        client_info["client_name"] = input("Nom client : ")
        if client_info["client_name"].upper() == "SORTIE" : 
            return menu(conn)
        client_info["email_address"] = input("Email : ")
        if client_info["email_address"].upper() == "SORTIE" : 
            return menu(conn)
        client_info["phone_number"] = input("Numéro de téléphone : ")
        if client_info["phone_number"].upper() == "SORTIE" : 
            return menu(conn)
        client_info["street_address"] = input("Rue : ")
        if client_info["street_address"].upper() == "SORTIE" : 
            return menu(conn)
        client_info["town_city"] = input("Ville : ")
        if client_info["town_city"].upper() == "SORTIE" : 
            return menu(conn)
        client_info["zip_code"] = input("Code postale : ")
        if client_info["zip_code"].upper() == "SORTIE" : 
            return menu(conn)
        values = list(client_info.values())
        keys = list(client_info.keys())
        i = 0  
        client = clients[selected_client-1]
        for info in client[1:]:
            if values[i] == '':
                client_info[keys[i]] = info
            i += 1
        sql_update = """UPDATE clients SET
        client_type = %s,
        client_name = %s,
        email_address = %s,
        phone_number = %s,
        street_address = %s,
        town_city = %s,
        zip_code = %s
        WHERE id = %s"""
        client_new_values = tuple()
        for i in range(len(keys)):
            client_new_values += (client_info[keys[i]],)
        client_new_values  += (int(selected_client),)
        print(client_new_values)
        cursor.execute(sql_update,client_new_values)
        conn.commit()
        client_edited = cursor.rowcount
        print(client_edited, "ont été changés.")
        logging.info(f"{client_edited}L'utilisateur veut retourner au menu principal")
    else:
        return menu(conn)


# def addInvoice(conn):
#     print("--------- Ajouter une facture --------")
#     print("> Taper SORTIE à tout moment pour retourner au menu principal.")

#     pass

#fonction qui prend une connection et qui renvoie rien
#menu principal du programme qui permet de choisir une fonctionnalité
def menu(conn):
    clearSystem()
    cursor = conn.cursor()
    createClientSchema(cursor)
    createInvoiceSchema(cursor)
    createProductsSchema(cursor)
    # cursor.execute("SHOW TABLES")
    # for x in cursor:
    #     print(x)

    # cursor.execute("SELECT * FROM clients")
    # clients = cursor.fetchall()
    # for client in clients:
    #     print(client)
    
    # cursor.execute("DROP TABLE clients")
    # cursor.execute("DROP TABLE invoices")  
    # cursor.execute("DROP TABLE products")
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
    logging.info("Affichage du menu")
    print("- - - - Bienvenue au menu principal  - - - -\n")
    while not option_selected:
        for entry in options:
            print(entry, parametres[entry])
        print('\n')
        selected = input("Veuillez choisir une option : ")
        if selected == "0":
            logging.info("Option de recherche utilisateur choisi")
            searchClient(conn)
            option_selected = True
        elif selected == "1":
            logging.info("Option d'ajout d'utilisateur choisi")
            addClient(conn)
            option_selected = True
        elif selected == "2":
            logging.info("Option de modification d'utilisateur choisi")
            editClient(conn)
            option_selected = True
            pass
        elif selected == "3":
            logging.info("Option de recherche de facture choisi")
            option_selected = True
            pass
        elif selected == "4":
            logging.info("Option d'ajout d'une facture choisi")
            addInvoice(conn)
            option_selected = True
            pass
        elif selected == "5":
            logging.info("Option de modification d'une facture choisi")
            option_selected = True
            pass
        elif selected == "6":
            logging.info("Option de suppression d'un enregistrement choisi")
            option_selected = True
            pass
        elif selected == "7":
           logging.info("Option de sortir du programme choisi")
           clearSystem()
           exit()
        else:
            clearSystem()
            menu(conn)
