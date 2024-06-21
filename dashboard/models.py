# dashboard/models.py
# from django.contrib.auth.models import User
from django.db import models
from login.models import UserAccount
from django.utils import timezone
from django.db import models
from django.core.mail import send_mail
from datetime import timedelta

class Note(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification
    in_trash = models.BooleanField(default=False)  # Indique si la note est dans la corbeille
    trash_date = models.DateTimeField(null=True, blank=True)  # Date à laquelle la note a été mise dans la corbeille
    
    def __str__(self):
        return self.title


class SearchHistory(models.Model):
    user= models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    query = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.query


class Video(models.Model):
    video_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    thumbnail = models.URLField()
    description = models.TextField()
    link = models.URLField()

class Favorite(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

class OfflineVideo(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file_path = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.title


class Playlist(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    videos = models.ManyToManyField(Video)



class Homework(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)  # Utilisateur qui a créé le devoir
    title = models.CharField(max_length=255)  # Titre du devoir
    description = models.TextField()  # Description du devoir
    subject = models.CharField(max_length=100)  # Matière du devoir
    due = models.DateTimeField()  # Date d'échéance
    is_finished = models.BooleanField(default=False)  # Statut de complétion
    priority = models.CharField(max_length=50, default='medium')  # Priorité
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification
    trash_date = models.DateTimeField(null=True, blank=True)  # Date de suppression (corbeille)
    in_trash = models.BooleanField(default=False)  # Indique si le devoir est dans la corbeille
    
    def __str__(self):
        return self.title

class TimelineEvent(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='timeline_events')  # Devoir associé
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)  # Qui a créé l'événement
    description = models.TextField()  # Description de l'événement
    timestamp = models.DateTimeField(default=timezone.now)  # Date et heure de l'événement
    reactions = models.JSONField(default=dict)  # Réactions (émojis, etc.)
    mentions = models.ManyToManyField(UserAccount, related_name='mentioned_in_events', blank=True)  # Utilisateurs mentionnés
    
    def __str__(self):
        return f"Événement pour {self.homework.title} par {self.user.last_name} à {self.timestamp}"

# models.py

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
class Todo(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=50)
    tags = models.ManyToManyField('Tag', blank=True)
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    is_finished = models.BooleanField(default=False)
    audio = models.FileField(upload_to='audios/', null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    file = models.FileField(upload_to='files/', null=True, blank=True)
    
    def get_priority_display(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority, 'Unknown')

   
class UserSearch(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query
class SearchQuery(models.Model):
    query = models.CharField(max_length=255, unique=True)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.query
    
# dashboard/models.py

class Section(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title
