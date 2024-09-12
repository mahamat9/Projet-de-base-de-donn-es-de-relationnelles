import os
import django

from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.http import HttpResponse
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import datetime
from django.db.models.functions import Substr
from django.db.models import Value, CharField, IntegerField
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Leprojet.settings')
django.setup()
from appli_visualisation.models import Content_Type, Charset, Content, Subject, Email_address, Message, Reciever


def home(request):
    """
    Vue pour la page d'accueil de l'application.
    """
    return render(request, 'home.html')

def search_employees(request):
    if request.method == 'GET':
        critere = request.GET.get('critere')
        valeur = request.GET.get('valeur')
        if critere == 'nom':
            query = """
            SELECT e.last_name, e.first_name, e.mailbox, c.category_name, ea.email_address_name
            FROM appli_visualisation_employee e
            LEFT JOIN appli_visualisation_category c ON e.category_id = c.id
            LEFT JOIN appli_visualisation_email_address ea ON e.id = ea.employee_id
            WHERE e.last_name = %s
            """
        elif critere == 'email':
            query = """
            SELECT T_fin.last_name, T_fin.mailbox, T_fin.first_name, T_fin.category, T_fin.email_address
            FROM ((
                SELECT e.id
                FROM appli_visualisation_employee e
                JOIN appli_visualisation_category c ON e.category_id = c.id
                JOIN appli_visualisation_email_address ea ON e.id = ea.employee_id
                WHERE ea.email_address_name = %s
                ) AS T1
                JOIN (
                    SELECT e.id, e.last_name, e.first_name, e.mailbox, c.category_name AS category, ea.email_address_name AS email_address
                    FROM appli_visualisation_employee e
                    LEFT JOIN appli_visualisation_category c ON e.category_id = c.id
                    LEFT JOIN appli_visualisation_email_address ea ON e.id = ea.employee_id
                ) AS T2
                ON T1.id = T2.id
            ) AS T_fin
            """
        else:
            return render(request, 'recherche_employes.html')

        with connection.cursor() as cursor:
            cursor.execute(query, [valeur])
            employees = cursor.fetchall()

        return render(request, 'recherche_employes_result.html', {'employees': employees})
    else:
        return render(request, 'recherche_employes.html') 
 


def employes_par_nbr(request):
    if request.method == 'POST':
        start_date = datetime.fromisoformat(request.POST.get('date_debut'))
        end_date = datetime.fromisoformat(request.POST.get('date_fin'))
        x = request.POST.get('x')
        min_or_max = request.POST.get('min_or_max')
        internal = request.POST.get('interne')
        external = request.POST.get('externe')

        query = """
        SELECT e.last_name, e.first_name, COUNT(m.id) AS total_emails
        FROM appli_visualisation_employee e
        LEFT JOIN appli_visualisation_email_address ea ON e.id = ea.employee_id
        LEFT JOIN appli_visualisation_message m ON ea.id = m.sender_email_id
        WHERE m.send_date BETWEEN %s AND %s
        """

        params = [start_date, end_date]

        # Filtrage interne-externe
        if internal == 'true' and external == 'false': #seulement les seulement les emails internes
            query += "AND ea.interne = true "
        elif internal == 'false' and external == 'true': #emails externes
            query += "AND ea.interne = false "
        elif internal == 'true' and external == 'true': #emails internes et externes
            pass

        query += """
        GROUP BY e.id
        """

        # Filtrage par nombre d'e-mails
        if x:
            if min_or_max == 'min':
                query += "HAVING COUNT(m.id) > %s "
            elif min_or_max == 'max':
                query += "HAVING COUNT(m.id) < %s "
            params.append(x)
        else:
            query += "HAVING COUNT(m.id) > 0 "

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            employees = cursor.fetchall()

        return render(request, 'employes_par_nbr_result.html', {'employees': employees})
    else:
        return render(request, 'employes_par_nbr_form.html')

def employee_communication(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        start_date = datetime.fromisoformat(request.POST.get('start_date'))
        end_date = datetime.fromisoformat(request.POST.get('end_date'))

        query = """
        SELECT DISTINCT e.id, e.first_name, e.last_name
        FROM appli_visualisation_employee e
        JOIN appli_visualisation_email_address ea ON e.id = ea.employee_id
        JOIN appli_visualisation_message m ON ea.id = m.sender_email_id OR ea.id IN (SELECT email_address_id FROM appli_visualisation_reciever WHERE message_id = m.id)
        WHERE m.send_date BETWEEN %s AND %s
        AND m.sender_email_id IN (SELECT id FROM appli_visualisation_email_address WHERE email_address_name IN (
        SELECT ea.email_address_name
        FROM appli_visualisation_email_address ea
        JOIN appli_visualisation_employee e ON ea.employee_id = e.id
        WHERE e.first_name = %s AND e.last_name = %s
        ))
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [start_date, end_date, first_name, last_name])
            employees = cursor.fetchall()

        return render(request, 'employee_communication.html', {'employees': employees})
    else:
        return render(request, 'employee_communication_form.html')

def couples_communication(request):
    if request.method == 'POST':
        start_date = datetime.fromisoformat(request.POST.get('start_date'))
        end_date = datetime.fromisoformat(request.POST.get('end_date'))
        threshold = request.POST.get('threshold')

        query = """
        SELECT ea1.email_address_name AS sender, ea2.email_address_name AS receiver, COUNT(m.id) AS total_emails
        FROM appli_visualisation_message m
        JOIN appli_visualisation_email_address ea1 ON m.sender_email_id = ea1.id
        JOIN appli_visualisation_reciever r ON m.id = r.message_id
        JOIN appli_visualisation_email_address ea2 ON r.email_address_id = ea2.id
        WHERE m.send_date BETWEEN %s AND %s
        GROUP BY sender, receiver
        HAVING COUNT(m.id) > %s
        ORDER BY total_emails DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [start_date, end_date, threshold])
            couples = cursor.fetchall()
        return render(request, 'couples_communication.html', {'couples': couples})

    else:
        return render(request, 'couples_communication_form.html')

    
#Requete avec que du django à partir de cette question

def jours_plus_echanges(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        internal_days = Message.objects.filter(
            send_date__range=[start_date, end_date],
            sender_email__interne=True
        ).values('send_date').annotate(total=Count('id')).order_by('-total')[:5]

        external_days = Message.objects.filter(
            send_date__range=[start_date, end_date],
            sender_email__interne=False
        ).values('send_date').annotate(total=Count('id')).order_by('-total')[:5]

        return render(request, 'jours_plus_echanges_result.html', {'internal_days': internal_days, 'external_days': external_days})
    else:
        return render(request, 'jours_plus_echanges_form.html')



def mots_cles(request):
    if request.method == 'POST':
        key_words = request.POST.get('key_words')
        presentation = request.POST.get('presentation')

        query_contenu = SearchQuery(key_words)
        
        contenus = []

        MAX_SEGMENT_LENGTH = 10000

        # Obtenir tous les objets
        objects = Content.objects.all()

        for obj in objects:
            texte = obj.text
            # Calculer le nombre de segments nécessaires
            num_segments = (len(texte) + MAX_SEGMENT_LENGTH - 1) // MAX_SEGMENT_LENGTH
            for i in range(num_segments):
                segment = texte[i*MAX_SEGMENT_LENGTH:(i+1)*MAX_SEGMENT_LENGTH]
                rank = SearchRank(SearchVector(Value(segment, output_field=CharField())), query_contenu)

                # Annoter l'objet avec le segment et le rang
                obj_segment = Content.objects.annotate(
                    segment=Value(segment, output_field=CharField()),
                    rank=rank,
                    segment_index=Value(i, output_field=IntegerField())
                ).filter(rank__gt=0).first()  # Filtrer les segments pertinents
                
                if obj_segment:
                    contenus.append(obj_segment)
        
        if presentation == 'expediteur':
            employees = Employee.objects.filter(
                id__in=Message.objects.filter(
                    id__in=[content.message_id for content in contenus]
                ).values_list('sender_id', flat=True)
            )
        elif presentation == 'destinataire':
            employees = Employee.objects.filter(
                id__in=Message.objects.filter(
                    id__in=[content.message_id for content in contenus]
                ).values_list('recipient_id', flat=True)
            )

        return render(request, 'mots_cles_result.html', {'contenus': contenus, 'presentation': presentation, 'employees': employees})
    else:
        return render(request, 'mots_cles_form.html')

    
def messages_by_subject_view(request):
    if request.method == 'POST':
        sujet = request.POST.get('sujet')
        subjects = Subject.objects.prefetch_related('message_set').filter(subject_name=sujet)
        return render(request, 'messages_by_subject.html', {'subjects': subjects})
    else:
        return render(request, 'contenu_conversations_form.html')

def message_detail_view(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    context = {
        'message': message,
    }
    return render(request, 'message_detail.html', context)


def potato(request):
    return render(request, 'potato.html')