from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('time_form/', views.time_view, name='time_form'),
    path('add_guard/', views.add_guard, name='add_guard'),
    path('guards/', views.guards_view, name='guards_list'),
    path('make_schedule/', views.make_schedule, name='make_schedule'),
    path('full_schedule/', views.full_schedule, name='full_schedule'),
    path('reset-all-guard-fields/', views.reset_all_guard_fields, name='reset_all_guard_fields'),
    path('guard/update/<int:guard_id>/', views.update_guard, name='update_guard'),
    path('delete_guard/<int:guard_id>/', views.delete_guard, name='delete_guard'),

]
