#!/bin/env python3

import os
import sys
import xml.etree.ElementTree as ET

try:
    from psycopg2 import connect
except ModuleNotFoundError:
    os.system("pip3 install psycopg2")
    from psycopg2 import connect

#Le modeule nécessaire pour utiliser le fichier .env
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    os.system("pip3 install dotenv")
    from dotenv import load_dotenv
load_dotenv()

"""
Ceux qui veulent utiliser le script doivent :
    - Installer le package psycopg2-binary
    - Modifier les variables de connexion à la base de données
    - Modifier le chemin du fichier XML dans la variable employees_file
"""

"""
Ce script extrait les données du fichier XML et les insère dans une base de données PostgreSQL.

Les adresses mails et les catégories(fonction) sont stockées dans des tableaux séparés.

"""


# Charger le fichier XML
employees_file = "../employes_enron.xml"

# Configuration de la base de données
database_name = os.environ.get("database_name")
database_user = os.environ.get("database_user")
database_password = os.environ.get("password")
database_host = os.environ.get("localhost")
database_port = os.environ.get("5432")

tree = ET.parse(employees_file)
root = tree.getroot()


# Connexion à la base de données
try:
    connection = connect(
        database = database_name,
        user = database_user,
        password = database_password,
        host = database_host,
        port = database_port
    )
    cursor = connection.cursor()
except Exception as e:
    print(f"Erreur de connexion à la base de données : {e}")
    sys.exit(1)

# Création des tables (si nécessaire)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Employee (
    "employee_id" serial PRIMARY KEY,
    "last_name" varchar(20) NOT NULL,
    "first_name" varchar(20) NOT NULL,
    "mailbox" varchar(20) NOT NULL,
    "category_id" integer
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Email_address (
    "email_address_id" serial PRIMARY KEY,
    "email_address_name" varchar(50) NOT NULL,
    "employee_id" integer REFERENCES Employee(employee_id),
    "interne" bool NOT NULL DEFAULT true
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Category (
    category_id serial PRIMARY KEY,
    category_name varchar(20) UNIQUE NOT NULL
);
""")



# Insérer les catégories dans la table Category
categories = set()  # Utiliser un ensemble pour stocker les catégories uniques
for employee in root.findall('employee'):
    category_name = employee.get('category')
    if category_name:
        categories.add(category_name)

# Insérer les catégories "uniques" dans la table Category
for category_name in categories:
    cursor.execute("""
        INSERT INTO Category (category_name)
        VALUES (%s)
        ON CONFLICT DO NOTHING;
    """, (category_name,))

# Définir une catégorie par défaut "Unknown"
default_category_id = 1  # Identifiant de catégorie par défaut (vous pouvez le modifier si nécessaire)
default_category_name = "Unknown"

# Parcourir les employés et insérer les données
for employee in root.findall('employee'):
    lastname = employee.find('last_name').text
    firstname = employee.find('firstname').text
    mailbox = employee.find('mailbox').text
    category_name = employee.get('category')

    # Vérifier si la catégorie existe
    cursor.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    category_id = cursor.fetchone()

    # Gérer la catégorie par défaut pour les employés dont la catégorie n'est pas connue
    if category_id is None:
        print(f"L'employé {lastname} {firstname} n'a aucune catégorie attribuée. Attribuer la catégorie par défaut 'Inconnu'.")
        category_id = default_category_id

    # Insérer l'employé dans la table Employee
    cursor.execute("""
        INSERT INTO Employee (last_name, first_name, mailbox, category_id)
        VALUES (%s, %s, %s, %s)
        RETURNING employee_id;
    """, (lastname, firstname, mailbox, category_id))
    
    employee_id = cursor.fetchone()[0] #recupération des employee_id pour le table des adresses mail
    
    # Insérer les adresses mail dans la table email_addresses
    for email in employee.findall('email'):
        email_address = email.attrib.get('address')
        if email_address:
            cursor.execute("""
                INSERT INTO Email_address (email_address_name, employee_id, interne)
                VALUES (%s, %s, %s);
            """, (email_address, employee_id, True))

# Enregistrer les modifications et fermer la connexion
connection.commit()
cursor.close()
connection.close()

print("**Données insérées avec succès dans la base de données PostgreSQL**")

