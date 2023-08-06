from django.contrib import admin

from huscy.consents import models


class ConsentAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name', 'version'


class ConsentCategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name'


class ConsentFileAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = 'consent', 'consent_version', 'created_at', 'filehandle'
    readonly_fields = 'created_at',


admin.site.register(models.Consent, ConsentAdmin)
admin.site.register(models.ConsentCategory, ConsentCategoryAdmin)
admin.site.register(models.ConsentFile, ConsentFileAdmin)
