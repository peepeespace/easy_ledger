from django.contrib import admin

from db.models import (
    Ledger,
    Strategy,
    Order,
    Fill,
    Position,
    Universe,
)

admin.site.register(Ledger)
admin.site.register(Strategy)
admin.site.register(Order)
admin.site.register(Fill)
admin.site.register(Position)
admin.site.register(Universe)