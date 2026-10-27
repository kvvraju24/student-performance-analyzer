from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models

code_validator = RegexValidator(r'\A[A-Za-z0-9_-]{1,32}\Z', 'Use 1–32 ASCII letters, digits, hyphens or underscores.')
cohort_validator = RegexValidator(r'\A[A-Za-z0-9 _-]{1,40}\Z', 'Use 1–40 ASCII letters, digits, spaces, hyphens or underscores.')

class Subject(models.Model):
    code = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=60)
    def __str__(self):
        return self.name

class Student(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=32, validators=[code_validator])
    cohort = models.CharField(max_length=40, validators=[cohort_validator])
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner', 'code'], name='unique_owner_student_code')]
        ordering = ['code', 'pk']
    def __str__(self):
        return self.code

class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'subject'], name='unique_student_subject'), models.CheckConstraint(condition=models.Q(value__gte=0, value__lte=100), name='score_0_to_100')]

class RateBucket(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)

class AccessToken(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    digest = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=40)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
