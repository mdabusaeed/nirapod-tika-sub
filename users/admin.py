from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User   

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('phone_number','email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name','address', 'email','role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser','groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}), 
    )
    add_fieldsets = (
        (None, {  
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    search_fields = ('phone_number','email', 'first_name', 'last_name')
    ordering = ('phone_number',)   
    

admin.site.register(User, CustomUserAdmin)

