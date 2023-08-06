
from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class AccountTypeListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('account type')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        return (
            ('unranked', 'Unranked'),
            ('ranked', 'Ranked'),
            ('handleveled', 'Handleveled'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value() is None:
            return queryset

        account_type = self.value()
        if account_type == 'unranked':
            queryset = queryset.filter(
                Q(rank__isnull=True) | Q(rank='UNRANKED'),
                is_handleveled=False
            )
        elif account_type == 'handleveled':
            queryset = queryset.filter(is_handleveled=True)
        elif account_type == 'ranked':
            queryset = queryset.filter(rank__isnull=False).exclude(rank='UNRANKED')
        elif account_type == 'baremetal':
            queryset = queryset.filter(is_baremetal=True)
        return queryset
