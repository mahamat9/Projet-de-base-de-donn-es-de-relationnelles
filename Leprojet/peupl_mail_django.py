import os
import django
import re
from datetime import datetime, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Leprojet.settings')
django.setup()

from appli_visualisation.models import Content_Type, Charset, Content, Subject, Email_address, Message, Reciever



# Définition du chemin du dossier principal
dossier_principal = "/home/mahamat/PROJET/maildir"


# Dictionnaire permettanr de transformer les chaînes de caractères des mois en nombres
dic_mois = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

def recuperer_metadonnees_email(chemin_fichier):
    """
    Récupère et sauvegarde les métadonnées d'un email à l'aide d'expressions régulières.

    Arguments:
        chemin_fichier (str): Chemin du fichier email à lire.

    Return:
        metadonnees: Dictionnaire contenant les métadonnées extraites.
    """
    # Gestion de l'ouverture des différents fichiers mails
    with open(chemin_fichier, "r", encoding = "UTF-8") as f:
        try:
            contenu_email = f.read()
        except UnicodeDecodeError:
            # Si python n'arrive pas à lire le fichier en utilisant un encodage utf-8
            with open(chemin_fichier, "r", encoding = "ISO-8859-15") as f:
                try:
                    contenu_email = f.read()
                except UnicodeError as e:
                    # On regarde si le fichier n'arrive pas à être décodé avec le nouvel encodage
                    # Si c'est le cas on affiche l'erreur et on passe au fichier suivant
                    print(chemin_fichier)
                    print(e)
                    return
            
    # On effectue la recherche des données dans le fichier dans le même ordre
    # que les différentes classes du fichier models.py pour pouvoir gérer les
    # clés étrangères

    # Recherche du Content-type
    match = re.search(r"Content-Type: (.*?);", contenu_email)
    if match:
        try :
            # On regarde si le content-type existe déjà dans la base de donnée
            ct = Content_Type.objects.get(ct_name = match.group(1))
        except Exception:
            # Enregistrement du content-type si il n'existe pas dans la base de donnée
            ct = Content_Type(ct_name = match.group(1))
            ct.save()
    else:
        try :
            ct = Content_Type.objects.get(ct_name = 'Inconnu')
        except Exception:
            # Enregistrement du content-type si il n'existe pas dans la base de donnée
            ct = Content_Type(ct_name = 'Inconnu')
            ct.save()

    # Recherche du charset
    match_charset = re.search(r"charset=(.*?)\n", contenu_email)
    if match_charset:
        try :
            # On regarde si le charset existe déjà dans la base de donnée
            chars = Charset.objects.get(charset_name = match_charset.group(1))
        except Exception:
            # Enregistrement du charset si il n'existe pas dans la base de donnée
            chars=Charset(charset_name = match_charset.group(1))
            chars.save()
    else:
        try :
            chars = Charset.objects.get(charset_name = 'Inconnu')
        except Exception:
            # Enregistrement du charset si il n'existe pas dans la base de donnée
            chars=Charset(charset_name = 'Inconnu')
            chars.save()
    
    # Recherche du contenu du message
    match = re.search(r"\n\n(.*)", contenu_email, re.DOTALL)
    if match:
        match_content = match.group(1)
        
        # On essaie de convertir le contenu dans l'encodage spécifié (UTF8)
        # pour éviter des erreurs d'affichage 
        if match_charset:
            try:
                match_content = match_content.encode(match_charset.group(1)).decode('utf-8')
            except UnicodeDecodeError:
                # En cas d'échec de décodage, conserve le corps dans l'encodage par défaut
                pass
            
        content = Content(text = match_content, content_type = ct, charset = chars)
        content.save()
    else:
        print(f"Erreur lors de la récupération du contenu du fichier {chemin_fichier}")
    
    # Recherche du sujet (Subject)
    match = re.search(r"Subject: (.*?)\n", contenu_email)
    if match:
        try :
            # On regarde si le sujet existe déjà dans la base de donnée
            subj = Subject.objects.get(subject_name = match.group(1))
        except Exception:
            # Enregistrement du sujet du mail si il n'existe pas dans la base de donnée
            subj = Subject(subject_name = match.group(1))
            subj.save()
    else:
        try :
            subj = Subject.objects.get(subject_name='Inconnu')
        except Exception:
            # Enregistrement du sujet 'Inconnu' si il n'existe pas dans la base de donnée
            subj = Subject(subject_name = 'Inconnu')
            subj.save()
    
    # Recherche de l'expéditeur (From)
    match = re.search(r"[^X-]From:(.*?)\n", contenu_email)
    if match:
        try :
            # On regarde si l'adresse email existe déjà dans la base de donnée
            sender = Email_address.objects.get(email_address_name = match.group(1).strip())
        except Exception:
            # Enregistrement de l'expéditeur si il n'existe pas dans la base de donnée
            # On regarde si l'email est interne
            interne = True if 'enron' in match.group(1).strip() else False
            sender = Email_address(email_address_name = match.group(1).strip(), employee = None, interne = interne)
            sender.save()

    # Recherche de la date d'envoi du message
    match = re.search(r'Date: ..., ([0-9]{1,2}) (...) ([0-9]{4}) ([0-9]{2}):([0-9]{2}):([0-9]{2}) .*?\n',
                      contenu_email)
    if match:        
        # Mise en forme de la date
        date = datetime(year = int(match.group(3)), month = dic_mois[match.group(2)], day = int(match.group(1)),
                        hour = int(match.group(4)), minute = int(match.group(5)), second = int(match.group(6)),
                        tzinfo=timezone.utc)
        # Enregistrement du message
        try :
            # On regarde si le message existe déjà dans la base de donnée
            message = Message.objects.get(send_date = date, content = content, subject = subj, sender_email = sender)
        except Exception:
            # Enregistrement du message si il n'existe pas dans la base de donnée
            message = Message(send_date = date, content = content, subject = subj, sender_email = sender)
            message.save()
    
    recievers = []
    # Recherche du/des destinataire(s)
    # Le [^X-] est pour éviter de capturer le 'X-To:' si jamais 'To:' n'est pas présent dans le mail
    # To:
    match = re.search(r"To:(.*?)\nSubject:", contenu_email)
    if match:
        # On sépare les adresses mail si plusieurs sont récupéerées
        match = match.group(1).split(sep = ',')
        recievers.extend(match)
        
    # Cc:
    match = re.search(r"[^X-]Cc:(.*?)\n", contenu_email)
    if match:
        # On sépare les adresses mail si plusieurs sont récupéerées
        match = match.group(1).split(sep = ',')
        recievers.extend(match)
        
    # Bcc:
    match = re.search(r"[^X-]Bcc:(.*?)\n", contenu_email)
    if match:
        # On sépare les adresses mail si plusieurs sont récupéerées
        match = match.group(1).split(sep = ',')
        recievers.extend(match)

    # Ajout des mails non enregistrés et peuplement de la table receveur
    for reciever in recievers:
        # On regarde si la chaîne de caractère capturée est d'une longueur inférieure à 85
        # et si la chaîne de caractère contient une addresse mail
        # pour pouvoir filtrer les erreurs de captures
        # voir le fichier Notes.txt pour plus de détails
        if len(reciever) < 85 and '@' in reciever:
            try :
                # On regarde si l'adresse email du receveur existe déjà dans la base de donnée
                email = Email_address.objects.get(email_address_name = reciever.strip())
            except Exception:
                # Enregistrement de l'adresse mail du receveur si elle n'existe pas dans la base de donnée
                # On regarde si l'email est interne
                interne = True if 'enron' in reciever else False
                email = Email_address(email_address_name = reciever.strip(), employee = None, interne = interne)
                email.save()
                
            # Peuplement de la table receveur
            try :
                # On regarde si le receveur de ce mail existe déjà dans la base de donnée
                # Pour éviter les doublons si le receveur est présent plusieurs fois dans la liste
                rec = Reciever.objects.get(message = message, email_address = email)
            except Exception:
                # Enregistrement du receveur si il n'existe pas dans la base de donnée
                rec = Reciever(message = message, email_address = email)
                rec.save()
    

def recuperer_metadonnees(chemin_dossier):
    """
    Parcourt le dossier principal et ses sous dossier pour récupérer et enregistrer
    les données de tous les fichiers.

    Arguments:
        chemin_dossier (str): Chemin du dossier principal.
    """
    for nom_fichier in os.listdir(chemin_dossier):
        chemin_complet = os.path.join(chemin_dossier, nom_fichier)

        # Appel récursif pour les sous-dossiers
        if os.path.isdir(chemin_complet):
            recuperer_metadonnees(chemin_complet)
            print(f"Données du dossier {chemin_complet} récupérées et sauvegardées dans la base de données avec succès !")
        # Récupération des métadonnées du fichier et enregistrement dans la base de donnée
        else:
            #if chemin_complet[-1] == '.':
            recuperer_metadonnees_email(chemin_complet)
                    
                    
if __name__ == '__main__':              
        
    # Lancement de la peuplement des métadonnées dans le dossier principal
    recuperer_metadonnees(dossier_principal)