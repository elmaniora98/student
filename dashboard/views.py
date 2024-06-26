from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.views import generic
from django.core.paginator import Paginator
from .models import Note
from .forms import NotesForm
import datetime
from django.utils import timezone
from django.core.checks import messages
from django.shortcuts import redirect, render
from .forms import *
from django.contrib import messages
from django.views import generic
import requests 
import wikipedia
from reportlab.pdfgen import canvas  # Bibliothèque pour générer des PDF
from .models import Homework, TimelineEvent
from .forms import HomeworkForm
from celery import shared_task
from django.core.mail import send_mail
from celery.utils.log import get_task_logger
from django.views.decorators.http import require_POST
from .models import Todo
from .forms import TodoForm
from django.http import JsonResponse
import logging
from django.conf import settings
from login.models import UserAccount
from .forms import YouTubeSearchForm
from .models import SearchHistory, Video, Favorite, OfflineVideo, Playlist
import youtube_dl
import wikipedia
from django.core.cache import cache
from .forms import DashboardForm
from .models import SearchQuery, UserSearch
from requests.exceptions import RequestException
from django.views.decorators.csrf import csrf_exempt
import json



def home(request):
    """
    This function renders the home page of the dashboard.

    Parameters:
    request (HttpRequest): The request object containing information about the client's request.

    Returns:
    render (HttpResponse): The rendered HTML template 'dashboard/home.html'.
    """
    return render(request,'dashboard/home.html')


@login_required
def notes(request):
    """
    Display a list of user's notes, with sorting, searching, and pagination.
    Also handle the creation of new notes.

    Parameters:
    request (HttpRequest): The request object containing the user's input.

    Returns:
    HttpResponse: The rendered notes.html template with the list of notes, form, search, and sort parameters.
    """
    # Récupérer les paramètres de tri et de recherche
    sort = request.GET.get('sort', 'date')  # Trier par date par défaut
    search = request.GET.get('search', '')  # Recherche par titre
    
    # Filtrer les notes par utilisateur, recherche, et tri
    if sort == 'title':
        all_notes = Note.objects.filter(user=request.user, in_trash=False, title__icontains=search).order_by('title')
    else:
        all_notes = Note.objects.filter(user=request.user, in_trash=False, title__icontains=search).order_by('-updated_at')
    
    # Pagination pour les notes
    paginator = Paginator(all_notes, 4)  # 4 notes par page
    page_number = request.GET.get('page')
    notes_page = paginator.get_page(page_number)
    
    # Gérer la création de nouvelles notes
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            new_note = form.save(commit=False)
            new_note.user = request.user
            new_note.save()
            messages.success(request, f"La note '{new_note.title}' a été créée avec succès.")
            return redirect("notes")  # Rediriger après création réussie
    else:
        form = NotesForm()

    # Contexte pour le template
    context = {
        'notes': notes_page,
        'form': form,
        'search': search,
        'sort': sort,
    }
    
    return render(request, 'dashboard/notes.html', context)

@login_required
def delete_note(request, pk):
    """
    Deletes a note from the user's account.

    Parameters:
    request (HttpRequest): The request object containing the user's session and POST data.
    pk (int): The primary key of the note to be deleted.

    Returns:
    HttpResponseRedirect: Redirects to the notes list page after deleting the note.
    """
    note = get_object_or_404(Note, id=pk, user=request.user)
    note.in_trash = True
    note.trash_date = datetime.now()
    note.save()
    messages.success(request, f"La note '{note.title}' a été envoyée à la corbeille.")
    return redirect("notes")

@login_required
def edit_note(request, pk):
    """
    This function allows a user to edit an existing note.

    Parameters:
    request (HttpRequest): The request object representing the user's input.
    pk (int): The primary key of the note to be edited.

    Returns:
    render (HttpResponse): The rendered edit_note.html template with the form filled with the existing note data.
    redirect (HttpResponseRedirect): If the form is valid, redirects to the notes list page.
    """
    note = get_object_or_404(Note, id=pk, user=request.user)
    if request.method == "POST":
        form = NotesForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, f"La note '{note.title}' a été modifiée avec succès.")
            return redirect("notes")
    else:
        form = NotesForm(instance=note)
    return render(request, 'dashboard/edit_note.html', {'form': form})

@login_required
def restore_note_from_trash(request, pk):
    """
    Restores a note from the trash for the authenticated user.

    Parameters:
    request (HttpRequest): The request object representing the current HTTP request.
    pk (int): The primary key of the note to be restored.

    Returns:
    HttpResponseRedirect: A redirect response to the 'notes' URL, indicating successful restoration.
    """
    note = get_object_or_404(Note, id=pk, user=request.user, in_trash=True)
    note.in_trash = False
    note.trash_date = None
    note.save()
    messages.success(request, f"La note '{note.title}' a été restaurée avec succès.")
    return redirect("notes")


def restore_homework_from_trash(request, pk):
    # Utilisez `in_trash` à la place de `is_deleted`
    homework = get_object_or_404(Homework, pk=pk, in_trash=True)
    homework.in_trash = False
    homework.trash_date = None
    homework.save()
    message="Une note a été restauré "
    return redirect('homework')

@login_required
def trash(request):
    # Récupérer les notes supprimées dans les dernières 48 heures
    trashed_notes = Note.objects.filter(user=request.user, in_trash=True, trash_date__gte=timezone.now() - timezone.timedelta(days=2)).order_by('-trash_date')

    context = {'trashed_notes': trashed_notes}
    return render(request, 'dashboard/trash.html', context)

@login_required
def download_note_as_text(request, pk):
    """
    Downloads a note as a text file.

    Parameters:
    request (HttpRequest): The incoming request object.
    pk (int): The primary key of the note to download.

    Returns:
    HttpResponse: The response containing the note content as a text file.
    """
    note = get_object_or_404(Note, id=pk, user=request.user)
    content = f"Title: {note.title}\nDescription: {note.description}"
    filename = f"{note.title}.txt"
    
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

class NotesDetailView(generic.DetailView):
    model = Note
    template_name = 'dashboard/note_detail.html'  # Spécifiez le template utilisé


@login_required
def homework(request):
    """
    View function to display and manage homework.

    Parameters:
    request (HttpRequest): The request object.

    Returns:
    HttpResponse: The rendered homework page.
    """
    # Filtrer par recherche, tri, et statut de complétion
    search = request.GET.get('search', '')  # Recherche par titre ou matière
    sort = request.GET.get('sort', 'date')  # Trier par date par défaut
    show_completed = request.GET.get('show_completed', 'no')  # Afficher les devoirs complétés
    
    filters = {'user': request.user, 'in_trash': False}
    if search:
        filters['title__icontains'] = search  # Ajouter la recherche au filtre
    if sort == 'title':
        all_homework = Homework.objects.filter(**filters).order_by('title')
    else:
        all_homework = Homework.objects.filter(**filters).order_by('-due')

    if show_completed == 'yes':
        all_homework = all_homework.filter(is_finished=True)  # Afficher les devoirs complétés
    else:
        all_homework = all_homework.filter(is_finished=False)  # Afficher les devoirs non complétés
    
    paginator = Paginator(all_homework, 6)  # 5 devoirs par page
    page_number = request.GET.get('page')
    homework_page = paginator.get_page(page_number)
    
    # Gérer la création de devoirs
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            new_homework = form.save(commit=False)
            new_homework.user = request.user
            new_homework.save()
            messages.success(request, f"Le devoir '{new_homework.title}' a été créé avec succès.")
            return redirect("homework")
    else:
        form = HomeworkForm()
    
    context = {
        'homework': homework_page,
        'form': form,
        'search': search,
        'sort': sort,
        'show_completed': show_completed,
    }
    
    return render(request, 'dashboard/homework.html', context)

@login_required
def edit_homework(request, pk):
    """
    Edit an existing homework.

    Parameters:
    request (HttpRequest): The request object.
    pk (int): The primary key of the homework to be edited.

    Returns:
    HttpResponse: The rendered edit homework form if the request method is GET.
    HttpResponseRedirect: Redirects to the homework list page if the form is valid.
    """
    homework = get_object_or_404(Homework, id=pk, user=request.user)
    if request.method == "POST":
        form = HomeworkForm(request.POST, instance=homework)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le devoir '{homework.title}' a été modifié avec succès.")
            return redirect("homework")
    else:
        form = HomeworkForm(instance=homework)
    
    context = {
        'form': form,
    }
    
    return render(request, 'dashboard/edit_homework.html', context)

def delete_homework(request, pk):
    """
    Deletes a homework from the database.

    Parameters:
    request (HttpRequest): The request object containing the user and the homework ID.
    pk (int): The primary key of the homework to be deleted.

    Returns:
    HttpResponseRedirect: Redirects to the homework list page after deleting the homework.
    """
    homework = get_object_or_404(Homework, id=pk, user=request.user)
    homework.in_trash = True
    homework.trash_date = timezone.now()  # Date of deletion
    homework.save()
    messages.success(request, f"Le devoir '{homework.title}' a été envoyé à la corbeille.")
    return redirect("homework")

@login_required
def trash(request):
    """
    This function handles the display of trashed notes and homeworks.
    It filters the trashed notes and homeworks based on the current date and time.

    Parameters:
    request (HttpRequest): The request object containing the user's session and request data.

    Returns:
    render (HttpResponse): The rendered HTML template 'dashboard/trash.html' with the trashed notes and homeworks.
    """
    trashed_notes = Note.objects.filter(trash_date__gte=datetime.now()-timedelta(hours=48))
    trashed_homeworks = Homework.objects.filter(trash_date__gte=datetime.now()-timedelta(hours=48))
    
    context = {
        'trashed_notes': trashed_notes,
        'trashed_homeworks': trashed_homeworks,
        'is_notes_page': 'notes' in request.path  # Check if the URL contains 'notes'
    }
    
    return render(request, 'dashboard/trash.html', context)
@login_required
def restore_homework_from_trash(request, pk):
    """
    Restores a homework from the trash.

    Parameters:
    request (HttpRequest): The request object containing user information.
    pk (int): The primary key of the homework to be restored.

    Returns:
    HttpResponseRedirect: Redirects to the homework list page.
    """
    # Utilisez `in_trash` à la place de `is_deleted`
    homework = get_object_or_404(Homework, pk=pk, in_trash=True)
    homework.in_trash = False
    homework.trash_date = None
    homework.save()
    return redirect('homework')

@login_required
def mark_homework_as_completed(request, pk):
    """
    Marks a specific homework as completed or incomplete based on its current status.

    Parameters:
    request (HttpRequest): The request object containing user information and the homework ID.
    pk (int): The primary key of the homework to be marked as completed or incomplete.

    Returns:
    HttpResponseRedirect: Redirects to the homework list page after marking the homework as completed or incomplete.
    """
    homework = get_object_or_404(Homework, id=pk, user=request.user)
    homework.is_finished = not homework.is_finished  # Inverser le statut
    homework.save()
    messages.success(request, f"Le statut du devoir '{homework.title}' a été mis à jour.")
    return redirect("homework")


@login_required
def download_homework_as_pdf(request, pk):
    """
    This function generates a PDF file containing the details of a specific homework.

    Parameters:
    request (HttpRequest): The request object containing user information and request data.
    pk (int): The primary key of the homework to be downloaded.

    Returns:
    HttpResponse: A response object containing the generated PDF file. The response has the appropriate content type and content disposition headers set.
    """
    homework = get_object_or_404(Homework, id=pk, user=request.user)
    
    # Générer un PDF avec ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{homework.title}.pdf"'
    
    pdf = canvas.Canvas(response)
    pdf.drawString(100, 800, f"Titre: {homework.title}")
    pdf.drawString(100, 780, f"Description: {homework.description}")
    pdf.drawString(100, 760, f"Sujet: {homework.subject}")
    pdf.drawString(100, 740, f"À rendre: {homework.due}")
    pdf.showPage()
    pdf.save()
    
    return response
    """
    This function generates a PDF file containing the details of a specific homework.

    Parameters:
    request (HttpRequest): The request object containing user information and request data.
    pk (int): The primary key of the homework to be downloaded.

    Returns:
    HttpResponse: A response object containing the generated PDF file. The response has the appropriate content type and content disposition headers set.
    """
    homework = get_object_or_404(Homework, id=pk, user=request.user)
    
    # Générer un PDF avec ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{homework.title}.pdf"'
    
    pdf = canvas.Canvas(response)
    pdf.drawString(100, 800, f"Titre: {homework.title}")
    pdf.drawString(100, 780, f"Description: {homework.description}")
    pdf.drawString(100, 760, f"Sujet: {homework.subject}")
    pdf.drawString(100, 740, f"À rendre: {homework.due}")
    pdf.showPage()
    pdf.save()
    
    return response

@login_required
def add_timeline_event(request, homework_id):
    """
    Add a new event to the timeline of a specific homework.

    Parameters:
    - request (HttpRequest): The request object containing the user's input.
    - homework_id (int): The ID of the homework to which the event will be added.

    Returns:
    - HttpResponseRedirect: Redirects to the timeline page of the specified homework.
    """
    homework = get_object_or_404(Homework, id=homework_id, user=request.user)
    if request.method == "POST":
        description = request.POST.get("description")
        mentions = request.POST.getlist("mentions")  # Utilisateurs mentionnés
        
        event = TimelineEvent.objects.create(
            homework=homework,
            user=request.user,
            description=description,
        )
        
        # Ajouter des mentions
        if mentions:
            for mention_id in mentions:
                mentioned_user = UserAccount.objects.get(id=mention_id)
                event.mentions.add(mentioned_user)
        
        messages.success(request, "Événement ajouté à la timeline.")
        return redirect('homework_timeline', pk=homework_id)
@login_required
def homework_timeline(request, pk):
    """
    This function retrieves and displays the timeline events for a specific homework.

    Parameters:
    - request: The request object containing the user's input.
    - pk: The primary key of the homework for which the timeline events are to be retrieved.

    Returns:
    - A render response object with the 'dashboard/homework_timeline.html' template and the context containing the timeline events and the homework object.
    """
    homework = get_object_or_404(Homework, id=pk, user=request.user)
    timeline_events = TimelineEvent.objects.filter(homework=homework).order_by('-timestamp')
    
    context = {
        'timeline_events': timeline_events,
        'homework': homework,
    }
    
    return render(request, 'dashboard/homework_timeline.html', context)



@login_required
def toggle_homework_status(request, pk):
    """
    Toggle the status of a homework.

    Parameters:
    - request: The request object containing the user's input.
    - pk: The primary key of the homework to be toggled.

    Returns:
    - A redirect response to the homework list page.
    """
    homework = get_object_or_404(Homework, id=pk, user=request.user)
    homework.is_finished = not homework.is_finished  # Inverser le statut
    homework.save()
    status = "terminé" if homework.is_finished else "en cours"
    messages.success(request, f"Le devoir '{homework.title}' est maintenant {status}.")
    return redirect("homework")



logger = get_task_logger(__name__)
# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task
def send_homework_reminder():
    """
    This function sends reminders for homeworks that are due soon.

    The function retrieves all homeworks that are not finished and have a due date
    within one hour from the current time. For each homework, it sends an email
    reminder to the user associated with the homework.

    Parameters:
    None

    Returns:
    None
    """
    reminder_date = datetime.now() + timedelta(hours=1)  # 1 hour before the deadline
    logger.info("Sending reminders for homeworks due soon.")
    
    homeworks = Homework.objects.filter(due__lte=reminder_date, is_finished=False)
    
    for homework in homeworks:
        send_mail(
            'Reminder: Homework Due Soon',
            f"The homework '{homework.title}' is due on {homework.due}.",
            'studentnote2005@gmail.com',
            [homework.user.email],
        )
        logger.info(f"Reminder sent for homework '{homework.title}'.")



# views.py

@login_required
def todo_list(request):
    """
    This function retrieves and displays the list of todos for the logged-in user.

    Parameters:
    request (HttpRequest): The request object containing information about the user and the request.

    Returns:
    render (HttpResponse): The rendered HTML template 'dashboard/todo_list.html' with the context containing the list of todos, the form for adding new todos, and a boolean indicating whether there are any todos.
    """
    todos = Todo.objects.filter(user=request.user).order_by('due_date')
    todo_done = not todos.exists()
    form = TodoForm()
    return render(request, 'dashboard/todo_list.html', {'todos': todos, 'form': form, 'todo_done': todo_done})
@login_required
@require_POST
def add_todo(request):
    """
    This function handles the POST request to add a new todo item.

    Parameters:
    request (HttpRequest): The request object containing information about the user and the request.

    Returns:
    JsonResponse: A JSON response indicating the success status of the operation and the details of the added todo item.
    """
    form = TodoForm(request.POST, request.FILES)
    if form.is_valid():
        todo = form.save(commit=False)
        todo.user = request.user
        todo.save()
        form.save_m2m()
        return JsonResponse({'success': True, 'todo': {
            'id': todo.id,
            'title': todo.title,
            'due_date': todo.due_date.strftime('%Y-%m-%d %H:%M:%S'),
            'priority': todo.get_priority_display(),
            'tags': ', '.join([tag.name for tag in todo.tags.all()]),
            'category': todo.category.name if todo.category else 'N/A',
            'audio': todo.audio.url if todo.audio else '',
            'video': todo.video.url if todo.video else '',
            'file': todo.file.url if todo.file else '',
            'update_url': f'/update-todo/{todo.id}/'
        }})
    return JsonResponse({'success': False})
@login_required
@require_POST
def delete_todo(request, todo_id):
    """
    Deletes a todo item associated with the logged-in user.

    Parameters:
    request (HttpRequest): The request object containing information about the user and the request.
    todo_id (int): The unique identifier of the todo item to be deleted.

    Returns:
    JsonResponse: A JSON response indicating the success status of the operation.
    """
    try:
        todo = Todo.objects.get(id=todo_id, user=request.user)
        todo.delete()
        return JsonResponse({'success': True})
    except Todo.DoesNotExist:
        return JsonResponse({'success': False})
@login_required
def update_todo(request, todo_id):
    """
    Updates the status of a todo item.

    Parameters:
    request (HttpRequest): The request object containing information about the user and the request.
    todo_id (int): The unique identifier of the todo item to be updated.

    Returns:
    HttpResponseRedirect: A redirect response to the todo list page.
    """
    todo = Todo.objects.get(id=todo_id, user=request.user)
    todo.is_finished = not todo.is_finished
    todo.save()
    return redirect('dashboard/todo_list')
""" 
@require_POST
def save_audio(request, todo_id):
    todo = Todo.objects.get(id=todo_id, user=request.user)
    if request.method == 'POST' and request.FILES.get('audio'):
        todo.audio = request.FILES['audio']
        todo.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

"""









@csrf_protect
def books(request):
    """
    Handles the book search functionality.

    Parameters:
    request (HttpRequest): The incoming request object.

    Returns:
    HttpResponse: The rendered book search template with the form and search results.
    """
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
                result_dict={
                    'title': answer['items'][i]['volumeInfo']['title'],
                    'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                    'description': answer['items'][i]['volumeInfo'].get('description'),
                    'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                    'categories': answer['items'][i]['volumeInfo'].get('categories'),
                    'rating': answer['items'][i]['volumeInfo'].get('pageRating'),
                    'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks', {}).get('thumbnail'),
                    'preview': answer['items'][i]['volumeInfo'].get('previewLink')
                }
                
                result_list.append(result_dict)
                context = {
                'form': form,
                'results': result_list
            }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()
    
    context = {'form': form}
    return render(request,"dashboard/books.html",context)

"""
from requests.exceptions import ConnectionError, Timeout
from django.shortcuts import render
from django.http import HttpResponseBadRequest  # Handle potential API errors

@csrf_protect
def dictionary(request):
  if request.method == "POST":
    form = DashboardForm(request.POST)
    text = request.POST['text']

    # Wiktionary API URL construction
    url = "https://api.wiktionary.org/query.php"
    params = {
      "action": "query",
      "format": "json",
      "list": "search",
      "srsearch": text,  # Search parameter for Wiktionary
      "lang": "fr",  # Specify French language
    }

    # Send GET request to Wiktionary API
    try:
      response = requests.get(url, params=params)
      response.raise_for_status()  # Raise an exception for non-200 status codes
      data = response.json()
    except (ConnectionError, Timeout) as e:
      return HttpResponseBadRequest(f"Error connecting to API: {str(e)}")
    except Exception as e:
      return HttpResponseBadRequest(f"Error fetching definition: {str(e)}")

    # Extract data from Wiktionary response (may require adjustments based on response structure)
    try:
      page_id = data["query"]["search"][0]["pageid"]  # Get page ID from search result

      # Construct URL to get definition using page ID
      definition_url = f"https://api.wiktionary.org/query.php?action=query&format=json&prop=revisions&rvprop=content&pageids={page_id}"
      definition_response = requests.get(definition_url)
      definition_data = definition_response.json()

      # Parse definition data (may require adjustments based on Wiktionary response structure)
      page = list(definition_data["query"]["pages"].values())[0]
      revisions = page.get("revisions", [])  # Check if revisions exist
      if revisions:
        content = revisions[0]["*"]  # Extract content from the first revision
        # You might need to parse the content (HTML) to extract the definition text

        # Example using BeautifulSoup (install if needed: pip install beautifulsoup4)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        definitions = soup.find_all('span', class_='sense-definition')  # Find definition elements
        if definitions:
          definition = definitions[0].text.strip()  # Get text of the first definition
        else:
          definition = "Definition not found"
      else:
        definition = "Definition not found"

      # Handle cases where data is missing (adjust as needed)
      phonetics = ""  # Wiktionary might not provide phonetics
      audio = ""  # Wiktionary might not provide audio
      example = ""  # You might need to parse the content for examples
      synonyms = []  # You might need to parse the content for synonyms

      context = {
          'form': form,
          'input': text,
          'phonetics': phonetics,
          'audio': audio,
          'definition': definition,
          'example': example,
          'synonyms': synonyms,
      }
    except Exception as e:
      context = {
          'form': form,
          'error': f"Erreur de traitement des données : {str(e)}",
      }
    else:
      context = {
          'form': form,
          'input': text,
          'error': f"Aucune définition trouvée pour '{text}'.",
      }

    return render(request, 'dashboard/dictionary.html', context)

  else:
    form = DashboardForm()
    context = {'form': form}

  return render(request, 'dashboard/dictionary.html', context)
"""

def section_detail(request, section_id):
    """
    Retrieve and display the details of a specific section.

    Parameters:
    request (HttpRequest): The request object representing the current web request.
    section_id (int): The unique identifier of the section to retrieve.

    Returns:
    HttpResponse: A rendered response object containing the section details template.
    """
    section = get_object_or_404(Section, id=section_id)
    context = {
        'section': section
    }
    return render(request, 'dashboard/section_detail.html', context)

def autocomplete(request):
    """
    This function handles the autocomplete feature for the search bar.
    It retrieves a list of suggestions based on the user's input.

    Parameters:
    request (HttpRequest): The request object containing the user's input.

    Returns:
    JsonResponse: A JSON response containing the list of suggestions.
    """
    if 'term' in request.GET:
        term = request.GET.get('term')
        suggestions = wikipedia.search(term, results=5)
        return JsonResponse(suggestions, safe=False)


@csrf_protect
def wiki(request):
    """
    This function handles the Wikipedia search functionality.
    It retrieves and displays the details of a Wikipedia page based on the user's input.

    Parameters:
    request (HttpRequest): The request object representing the current web request.

    Returns:
    HttpResponse: A rendered response object containing the Wikipedia search template.
    """
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            cache_key = f'wiki_{text}'
            search_data = cache.get(cache_key)

            if not search_data:
                try:
                    search = wikipedia.page(text)  # Augmenter le délai d'attente à 10 secondes
                    search_data = {
                        'title': search.title,
                        'link': search.url,
                        'details': search.summary,
                        'content': search.content.split('\n== '),  # Diviser les sections
                        'categories': search.categories,  # Ajouter les catégories
                        'images': search.images[:5]  # Limiter le nombre d'images affichées à 5
                    }
                    cache.set(cache_key, search_data, timeout=600)  # Cache pendant 5 minutes

                    # Enregistrer ou mettre à jour la recherche populaire
                    search_query, created = SearchQuery.objects.get_or_create(query=text)
                    search_query.count += 1
                    search_query.save()

                    # Enregistrer la recherche récente de l'utilisateur connecté
                    if request.user.is_authenticated:
                        UserSearch.objects.create(user=request.user, query=text)
                except wikipedia.exceptions.DisambiguationError as e:
                    context = {
                        'form': form,
                        'error': f"There are multiple results for your search. Please be more specific. Options: {', '.join(e.options)}",
                        'options': e.options
                    }
                    return render(request, 'dashboard/wiki.html', context)
                except wikipedia.exceptions.PageError:
                    context = {
                        'form': form,
                        'error': "The page does not exist. Please try another search query."
                    }
                    return render(request, 'dashboard/wiki.html', context)
                except RequestException as e:
                    context = {
                        'form': form,
                        'error': "There was a problem connecting to Wikipedia. Please try again later."
                    }
                    return render(request, 'dashboard/wiki.html', context)

            context = {
                'form': form,
                'title': search_data['title'],
                'link': search_data['link'],
                'details': search_data['details'],
                'content': search_data['content'],
                'categories': search_data['categories'],  # Ajouter les catégories au contexte
                'images': search_data['images']
            }
        else:
            context = {
                'form': form,
                'error': "Invalid form submission. Please enter a valid search query."
            }
    else:
        form = DashboardForm()
        popular_queries = SearchQuery.objects.order_by('-count')[:5]  # Les 5 recherches les plus populaires
        user_searches = UserSearch.objects.filter(user=request.user).order_by('-timestamp')[:5] if request.user.is_authenticated else []
        context = {
            'form': form,
            'popular_queries': popular_queries,
            'user_searches': user_searches
        }

    return render(request, 'dashboard/wiki.html', context)


@csrf_protect
def conversion(request):
    """
    Handles the conversion functionality for length and mass measurements.

    Parameters:
    request (HttpRequest): The request object representing the current web request.

    Returns:
    HttpResponse: A rendered response object containing the conversion template.
    """
    if request.method=='POST':
        form= ConversionForm(request.POST)
        if request.POST['measurement'] =='length':
            measurement_form = ConversionLengthForm()
            context = {
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input'in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer=''
                if input and int(input) >=0:
                    if first == 'yard' and second =='foot':
                        answer=f'{input} yard ={int (input)*3} foot'
                    if first == 'foot' and second =='yard':
                        answer=f'{input} foot ={int (input)/3} yard'
                context ={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }

        if request.POST['measurement'] =='mass':
            measurement_form = ConversionMassForm()
            context = {
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input'in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer=''
                if input and int(input) >=0:
                    if first == 'pound' and second =='kilogram':
                        answer=f'{input} pound ={int (input)*0.453592} kilogram'
                    if first == 'kilogram' and second =='pound':
                        answer=f'{input} kilogram ={int (input)/2.20462} pound'
                context ={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }   
    else:
        form=ConversionForm()
        context={
            'form':form,
            'input':False
        }
    return render(request,'dashboard/conversion.html',context)

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY

@login_required
def youtube_search(request):
    """
    This function handles the YouTube search functionality.
    It retrieves and displays the search results based on the user's input.

    Parameters:
    request (HttpRequest): The request object representing the current web request.

    Returns:
    HttpResponse: A rendered response object containing the YouTube search template.
    """
    form = YouTubeSearchForm()
    search_history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]
    popular_videos = get_popular_videos()
    offline_videos = OfflineVideo.objects.filter(user=request.user)

    if request.method == 'POST':
        form = YouTubeSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['text']
            language = form.cleaned_data['language']
            search_history_entry = SearchHistory(user=request.user, query=query)
            search_history_entry.save()
            results = search_youtube(query, language)
            return render(request, 'dashboard/youtube.html', {
                'form': form,
                'search_history': search_history,
                'results': results,
                'popular_videos': popular_videos,
                'offline_videos': offline_videos
            })

    return render(request, 'dashboard/youtube.html', {
        'form': form,
        'search_history': search_history,
        'popular_videos': popular_videos,
        'offline_videos': offline_videos
    })

def get_popular_videos():
    """
    This function retrieves the most popular videos from the YouTube API.

    Parameters:
    None

    Returns:
    list: A list of dictionaries, where each dictionary represents a video.
          Each dictionary contains the video's ID, title, thumbnail URL, and link.
    """
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&chart=mostPopular&regionCode=US&maxResults=30&key={YOUTUBE_API_KEY}'
    response = requests.get(url)
    data = response.json()
    videos = []

    for item in data['items']:
        video = {
            'id': item['id'],
            'title': item['snippet']['title'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'link': f'https://www.youtube.com/watch?v={item["id"]}'
        }
        videos.append(video)

    return videos

def search_youtube(query, language):
    """
    This function retrieves and processes search results from the YouTube API.

    Parameters:
    query (str): The search query string.
    language (str): The language code for the search results.

    Returns:
    list: A list of dictionaries, where each dictionary represents a video.
          Each dictionary contains the video's ID, title, thumbnail URL, description, and link.
    """
    # Construct the URL for the YouTube API search endpoint
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=30&key={YOUTUBE_API_KEY}&relevanceLanguage={language}'
    
    # Send a GET request to the YouTube API
    response = requests.get(url)
    
    # Parse the JSON response
    data = response.json()
    
    # Initialize an empty list to store the search results
    results = []

    # Iterate over the items in the search results
    for item in data['items']:
        # Extract relevant information from each item
        result = {
            'id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'description': item['snippet']['description'],
            'link': f'https://www.youtube.com/watch?v={item["id"]["videoId"]}'
        }
        
        # Add the result to the list of search results
        results.append(result)

    # Return the list of search results
    return results

@login_required
def add_favorite(request, video_id):
    """
    This function adds a video to the user's favorite list.

    Parameters:
    request (HttpRequest): The request object representing the current web request.
    video_id (str): The unique identifier of the video to be added to the favorite list.

    Returns:
    HttpResponseRedirect: A redirect response to the 'youtube_search' view.
    """
    user = request.user
    video = Video.objects.get(id=video_id)
    favorite, created = Favorite.objects.get_or_create(user=user, video=video)
    return redirect('youtube_search')

@login_required
def download_video(request, video_id):
    """
    Downloads a video from YouTube and saves it to the user's download directory.

    Parameters:
    request (HttpRequest): The request object representing the current web request.
    video_id (str): The unique identifier of the video to be downloaded.

    Returns:
    HttpResponseRedirect: A redirect response to the 'youtube_search' view.
    """
    user = request.user
    video = Video.objects.get(id=video_id)
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'media/downloads/{user.last_name}/{video.id}.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video.link])

    file_path = f'downloads/{user.last_name}/{video.id}.mp4'
    offline_video = OfflineVideo(user=user, video=video, file_path=file_path)
    offline_video.save()
    return redirect('youtube_search')

@login_required
def manage_playlists(request):
    """
    This function is responsible for managing user's playlists.
    It retrieves all playlists associated with the current user and renders them in a template.

    Parameters:
    request (HttpRequest): The request object representing the current web request.

    Returns:
    render (HttpResponse): A rendered response object containing the 'dashboard/playlists.html' template.
    The template is populated with the user's playlists.
    """
    user = request.user
    playlists = Playlist.objects.filter(user=user)
    return render(request, 'dashboard/playlists.html', {'playlists': playlists})

@login_required
def add_to_playlist(request, video_id, playlist_id):
    """
    This function adds a video to a specific playlist.

    Parameters:
    request (HttpRequest): The request object representing the current web request.
    video_id (str): The unique identifier of the video to be added to the playlist.
    playlist_id (int): The unique identifier of the playlist to which the video will be added.

    Returns:
    HttpResponseRedirect: A redirect response to the 'youtube_search' view.
    """
    user = request.user
    video = Video.objects.get(id=video_id)
    playlist = Playlist.objects.get(id=playlist_id, user=user)
    playlist.videos.add(video)
    return redirect('youtube_search')

@login_required
def create_playlist(request):
    """
    This function is responsible for creating a new playlist for the logged-in user.

    Parameters:
    request (HttpRequest): The request object representing the current web request.
        It should contain the POST data with the 'name' key for the playlist name.

    Returns:
    HttpResponseRedirect: A redirect response to the 'manage_playlists' view.
        If the request method is not POST, it renders the 'dashboard/create_playlist.html' template.

    Raises:
    None
    """
    user = request.user
    if request.method == 'POST':
        name = request.POST['name']
        playlist = Playlist(name=name, user=user)
        playlist.save()
        return redirect('manage_playlists')

    return render(request, 'dashboard/create_playlist.html')


@csrf_exempt
def send_suggestion(request):
    """
    This function handles sending suggestions to the admin.

    Parameters:
    request (HttpRequest): The request object representing the current web request.
        It should contain the POST data with the 'suggestion' key for the suggestion content.

    Returns:
    JsonResponse: A JSON response indicating the success or failure of the operation.
        If successful, it contains a 'success' key with a value of True.
        If unsuccessful, it contains a 'success' key with a value of False and an 'error' key with the error message.

    Raises:
    None
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            suggestion = data.get('suggestion')
            user_email = request.user.email

            if suggestion:
                send_mail(
                    subject='Nouvelle suggestion de rapprochement',
                    message=f'Suggestion: {suggestion}\nDe: {user_email}',
                    from_email=user_email,
                    recipient_list=['studentnote2005@gmail.com'],
                )
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Suggestion vide'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
