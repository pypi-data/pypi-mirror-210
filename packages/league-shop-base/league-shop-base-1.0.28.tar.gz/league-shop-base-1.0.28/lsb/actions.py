from django.contrib import admin


@admin.action(description='Mark as handleveled')
def mark_as_handleveled(modeladmin, request, queryset):
    queryset.update(is_handleveled=True)


@admin.action(description='Clear handleveled')
def clear_handleveled(modeladmin, request, queryset):
    queryset.update(is_handleveled=False)
