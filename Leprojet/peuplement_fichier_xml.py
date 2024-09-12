import xml.etree.ElementTree as ET
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Leprojet.settings')
django.setup()

from appli_visualisation.models import Category, Employee, Email_address

employees_file = "../employes_enron.xml"

# Charger le fichier XML
tree = ET.parse(employees_file)
root = tree.getroot()

# Parcourir chaque élément <employee> ie par arborescence
for employee in root.findall('employee'):
    # Récupération des informations et ajout dans la base de donnée

    #Récupération et ajout de la catégorie si elle n'existe pas encore dans la base de donnée
    category = employee.get('category') if employee.get('category') is not None else "Unknown"

    try :
        cat=Category.objects.get(category_name = category)
    except Exception:
        cat=Category(category_name = category)
        cat.save()

    #Récupération et ajout de l'employé.e
    lastname = employee.find('lastname').text
    firstname = employee.find('firstname').text
    mailbox = employee.find('mailbox').text if employee.find('mailbox') is not None else ""

    empl=Employee(last_name=lastname,first_name=firstname,mailbox=mailbox,category=cat)
    empl.save()

    #Récupération et ajout de la / des adresses mail de l'employé
    email_addresses = [email.attrib['address'] for email in employee.findall('email')]
    for email_add in email_addresses:
        email = Email_address(email_address_name=email_add,employee=empl,interne=True)
        email.save()