from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from records import views
# All admin pages, including model permissions, require an active superuser.
admin.site.has_permission = lambda request: request.user.is_active and request.user.is_superuser
urlpatterns = [
    path('', views.public_file),
    path('style.css', views.public_file, {'asset': 'style.css'}),
    path('dashboard.js', views.public_file, {'asset': 'dashboard.js'}),
    path('data/synthetic_students.csv', views.public_file, {'asset': 'data/synthetic_students.csv'}),
    path('docs/dashboard.png', views.public_file, {'asset': 'docs/dashboard.png'}),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(success_url='/workspace/'), name='password_change'),
    path('workspace/', views.workspace, name='workspace'),
    path('workspace/students/<int:pk>/', views.edit_scores, name='edit_scores'),
    path('api/students/', views.students_api),
    path('api/students/<int:pk>/', views.student_api),
    path('api/students/<int:pk>/scores/', views.scores_api),
    path('api/subjects/', views.subjects_api),
    path('admin/', admin.site.urls),
]

# Local admin assets only; production serves collectstatic output through its web server.
from django.conf import settings
if settings.LOCAL:
    import django
    from pathlib import Path
    from django.views.static import serve
    urlpatterns += [path('static/admin/<path:path>', serve, {'document_root': Path(django.__file__).parent / 'contrib/admin/static/admin'})]
