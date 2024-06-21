from django.contrib import admin

from.models import UserAccount

# Register your models here.

@admin.register(UserAccount)
class UniversalAdmin(admin.ModelAdmin):

    search_fields       = ('first_name', 'email', 'contact' )
    exclude = ('password',)

    #def get_list_display(self, request):
    #    return [field.name for field in self.model._meta.concrete_fields]

    def get_list_display(self, request):

        #list_name = [field.name for field in self.model._meta.concrete_fields]
        list_display = [field.name for field in self.model._meta.concrete_fields]

        return list_display
