from django.contrib import admin
from django.urls import path

from lsb import list_filters
from lsb.actions import clear_handleveled
from lsb.actions import mark_as_handleveled

from .models import Champion
from .models import Product
from .models import Skin
from .utils.product import get_products_query_set
from .views import skins_download


@admin.register(Champion)
class ChampionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'roles',
        'lanes',
        'date_created',
        'date_modified',
    )

    search_fields = (
        'id',
        'name',
    )


@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):

    change_list_template = 'shop/skins_change_list.html'

    fieldsets = (
        (None, {
            'fields': (
                'tier',
                'name',
                'champion',
                'value',
                'date_created',
                'date_modified',
            )
        }),
        ('Additinal Info', {
            'fields': ('stock', 'sold'),
        }),
    )

    list_display = (
        'id',
        'name',
        'champion',
        'tier',
        'value',
        'date_created',
        'date_modified',
    )

    readonly_fields = (
        'tier',
        'name',
        'champion',
        'value',
        'date_created',
        'date_modified',
        'stock',
        'sold',
    )

    search_fields = (
        'id',
        'name',
        'champion__name',
    )

    list_filter = (
        'tier',
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('download/', skins_download)]
        return my_urls + urls

    def stock(self, obj):
        return obj.all_skins_products.filter(is_purchased=False).count()

    def sold(self, obj):
        return obj.all_skins_products.filter(is_purchased=True).count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    '''ProductAdmin class'''
    fields = (
        'username',
        'password',
        'level',
        'region',
        'blue_essence',
        'orange_essence',
        'mythic_essence',
        'country',
        'flash_key',
        'is_handleveled',
        'is_bare_metal',
        'rank',
        'division',
        'solo_wins',
        'solo_losses',
        'is_auth_error',
        'is_banned',
        'date_banned',
        'ban_reason',
        'all_skins',
        'skins',
        'owned_skins',
        'permanent_skins',
        'email',
        'date_sign_up',
        'dob',
        'ip_address',
        'city',
    )
    readonly_fields = (
        'all_skins',
    )
    list_display = (
        'id',
        'username',
        'region',
        'summoner_name',
        'discrete_level',
        'discrete_blue_essence',
        'orange_essence',
        'mythic_essence',
        'skin_count',
        'skin_score',
        'is_purchased',
        'country',
        'flash_key',
        'is_handleveled',
        'is_bare_metal',
        'rank',
        'division',
        'solo_wins',
        'solo_losses',
        'is_auth_error',
        'is_banned',
        'date_banned',
        'ban_reason',
        'email',
        'date_sign_up',
        'dob',
        'ip_address',
        'city',
        'date_created',
        'date_modified',
    )
    list_filter = (
        'date_modified',
        list_filters.AccountTypeListFilter,
        'discrete_level',
        'discrete_blue_essence',
        'region',
        'is_purchased',
        'is_banned',
        'is_auth_error',
        'is_handleveled',
        'is_bare_metal',
        'rank',
        'division',
    )
    search_fields = [
        'username',
        'summoner_name',
    ]
    actions = (
        mark_as_handleveled,
        clear_handleveled,
    )
    filter_horizontal = ('skins', 'permanent_skins', 'owned_skins')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return get_products_query_set(qs)

    def skin_count(self, obj):
        return obj.skin_count

    def skin_score(self, obj):
        return obj.skin_score

    skin_score.admin_order_field = 'skin_score'
    skin_count.admin_order_field = 'skin_count'
