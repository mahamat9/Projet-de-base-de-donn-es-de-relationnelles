# Projet de base de données de relationnelles

# Guide de démarrage pour l'application de Visualisation d'Enron

Ce guide fournit des instructions détaillées sur l'installation, le peuplement de la base de données, le lancement de l'application et son utilisation. Suivez ces étapes pour commencer à utiliser l'application Enron Data Visualization.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants sur votre machine :
- Python
- Django
- PostgreSQL
- Git

## Installation

1. Clonez ce dépôt Git sur votre machine :
    ```bash 
    git clone https://github.com/mahamat9/Projet_BDDR_Enron 
    ```

2. Accédez au répertoire du projet :
    ```bash 
    cd Projet_BDDR_Enron
    ```

3. Configuration du fichier « .env » : Configurez les paramètres sensibles de l'application, notamment les informations d'accès à la base de données, en complétant le fichier ".env".

## Peuplement de la base de données

1. Téléchargez les données de l'affaire Enron depuis le lien suivant: https://math.univ-angers.fr/perso/jaclin/enron/.

2. Placez-vous dans le sous-dossier "Leprojet" :
    ```bash 
    cd Leprojet
    ```

3. Appliquez les migrations pour créer les tables de la base de données :
    ```bash 
    python manage.py migrate 
    ```

4. Remplacez les chemins des fichiers de données dans les scripts "peuplement_fichier_xml.py" et "peupl_mail_django.py", notamment celui des fichiers des employées(en xml) dans le premier et celui des mails dans le second.

5. Exécutez ces deux scripts pour insérer les données Enron dans les tables de la base de données :
    ```bash 
    python peuplement_fichier_xml.py
    python peupl_mail_django.py 
    ```

## Lancement de l'application

1. Lancez le serveur Django :
    ```bash
    python manage.py runserver 
    ```
    
2. Accédez à l'application dans votre navigateur en visitant l'URL http://127.0.0.1:8000/.

## Utilisation

Une fois l'application lancée, vous pouvez naviguer entre les différentes fonctionnalités proposées, telles que :

### Attributs d’un employé

- Utilisez la fonctionnalité de recherche pour trouver les attributs d'un employé par son nom ou par l'une de ses adresses e-mail.

### Employés par nombre de mails échangés

- Utilisez la fonctionnalité de recherche pour trouver les employés ayant envoyé et/ou reçu plus que (resp. moins que) x mails dans un intervalle de temps choisi, avec possibilité de faire la différence entre échanges internes et/ou internes-externes.

### Liste des employés ayant communiqué avec un employé donné

- Utilisez la fonctionnalité de recherche pour trouver la liste des employés ayant communiqué avec un employé donné sur un intervalle de temps donné.

### Couples d’employés par communication

- Utilisez la fonctionnalité de recherche pour trouver les couples d'employés ayant communiqué dans un intervalle de temps choisi, ordonnée suivant le nombre de mails échangés, tronquée au-dessous d’un seuil paramétrable.

### Jours avec le plus grand nombre d'échanges de mails

- Utilisez la fonctionnalité de recherche pour trouver les jours dans une période donnée ayant connu le plus grand nombre d’échanges de mails, en différenciant les échanges internes des échanges interne-externe.

### Mails contenant une liste de mots déterminés

- Utilisez la fonctionnalité de recherche pour trouver les mails contenant une liste de mots déterminés, avec diverses présentations (par expéditeur, par destinataire, etc.) et possibilité de visualiser le contenu d’un mail donné.

### Contenu d’une conversation

- Utilisez la fonctionnalité de recherche pour afficher le contenu d'une conversation, composée de mails, avec possibilité d'obtenir le contenu d'un mail donné.


## Contributions

Les contributions sont les bienvenues ! N'hésitez pas à soumettre une pull request pour toute amélioration ou correction.
