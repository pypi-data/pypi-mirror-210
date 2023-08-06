from NEMO.models import Area, Project, UserPreferences
from django.db import models


class UserPreferencesDefaultProject(models.Model):
    user_preferences = models.OneToOneField(UserPreferences, on_delete=models.CASCADE, related_name="default_project")
    default_project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_preferences.user) + " - " + (self.default_project or "")

    class Meta:
        verbose_name = "Default project"


class Reader(models.Model):
    class ReaderType(object):
        ENTRANCE = 1
        EXIT = 2
        Choices = (
            (ENTRANCE, "Entrance"),
            (EXIT, "Exit"),
        )

    reader_id = models.CharField(max_length=250, unique=True)
    site_id = models.CharField(max_length=250)
    reader_name = models.CharField(max_length=250)
    installed = models.BooleanField()
    data = models.JSONField()
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.CASCADE)
    reader_type = models.PositiveIntegerField(null=True, choices=ReaderType.Choices)
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reader_name


class Cardholder(models.Model):
    cardholder_id = models.CharField(max_length=250, unique=True)
    cardholder_name = models.CharField(max_length=250, blank=True, null=True)
    key_name = models.CharField(max_length=250)
    key_value = models.CharField(max_length=250)
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cardholder_id
