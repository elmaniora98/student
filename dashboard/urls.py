from django.urls import path 
from.import views



urlpatterns = [
    path('', views.home, name="home"),

     path('send-suggestion/', views.send_suggestion, name='send_suggestion'),

    path('notes/', views.notes, name='notes'),  # Afficher la liste des notes
    path('notes/delete/<int:pk>/', views.delete_note, name='delete-note'),  # Envoyer une note à la corbeille
    path('notes/edit/<int:pk>/', views.edit_note, name='edit-note'),  # Modifier une note
    path('notes/download/<int:pk>/', views.download_note_as_text, name='download-note-as-text'),  # Télécharger une note
    path('notes/restore/<int:pk>/', views.restore_note_from_trash, name='restore-note'),  # Restaurer une note
     path('notes/detail/<int:pk>/', views.NotesDetailView.as_view(), name='notes-detail'),  # Vue de détail d'une note
     path('notes/trash/', views.trash, name='trash'),  # Corbeille

    
    path('homework/', views.homework, name='homework'),  # Liste des devoirs
    path('homework/edit/<int:pk>/', views.edit_homework, name='edit-homework'),  # Modifier
    path('homework/delete/<int:pk>/', views.delete_homework, name='delete-homework'),  # Corbeille
   path('homework/restore/<int:pk>/', views.restore_homework_from_trash, name='restore-homework'),  # Restaurer
   path('homework/timeline/<int:pk>/', views.homework_timeline, name='homework_timeline'),  # Afficher la timeline
    path('homework/add_event/<int:pk>/', views.add_timeline_event, name='add_timeline_event'),  # Ajouter un événement
    path('homework/download/<int:pk>/', views.download_homework_as_pdf, name='download-homework-as-pdf'),  # Télécharger PDF
    # Changer le statut d'un devoir (terminé/en cours)
    path('homework/toggle-status/<int:pk>/', views.toggle_homework_status, name='toggle-homework-status'),
    path('homework/trash/', views.trash, name='trashs'),
    #path('update_homework/<int:pk>',views.update_homework, name='update-homework'),
    #path('delete_homework/<int:pk>',views.delete_homework,name="delete-homework"),

    
    path('youtube/', views.youtube_search, name='youtube_search'),
    path('youtube/favorite/<str:video_id>/', views.add_favorite, name='add_favorite'),
    path('youtube/download/<str:video_id>/', views.download_video, name='download_video'),
    path('youtube/playlists/', views.manage_playlists, name='manage_playlists'),
    path('youtube/playlists/create/', views.create_playlist, name='create_playlist'),
    path('youtube/playlists/add/<str:video_id>/<str:playlist_id>/', views.add_to_playlist, name='add_to_playlist'),


    path('todo/', views.todo_list, name='todo-list'),
    path('todo/add/', views.add_todo, name='add_todo'),
    path('delete/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    path('todo/update/<int:todo_id>/', views.update_todo, name='update_todo'),


     path('books',views.books, name='books'),
     path('books/<int:book_id>/', views.book_detail, name='book_detail'),

    path('dictionary',views.dictionary, name='dictionary'),

    path('wiki/', views.wiki, name='wiki'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('conversion',views.conversion,name = 'conversion'),


]