from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import UserClienteMembership, UserProfile, Equipe, EquipeMembro
#from .models_equipes import 

User = get_user_model()

@admin.register(UserClienteMembership)
class UserClienteMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "cliente", "role", "ativo", "criado_em")
    list_filter = ("role", "ativo", "cliente")
    search_fields = ("user__username", "user__email", "cliente__nome")
    autocomplete_fields = ("user", "cliente")

# USER PROFILE
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "tipo_usuario", "cliente", "criado_em")
    list_filter = ("tipo_usuario", "cliente")
    search_fields = ("user__username", "user__email")

# INLINE membros da equipe
class EquipeMembroInline(admin.TabularInline):
    model = EquipeMembro
    extra = 1
    autocomplete_fields = ["user"]

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "descricao")
    inlines = [EquipeMembroInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        equipe = form.instance
        membros_ids = set(equipe.membros.values_list("user_id", flat=True))

        errors = {}
        if getattr(equipe, "lider_id", None) and equipe.lider_id not in membros_ids:
            errors["lider"] = "O líder deve ser membro da equipe."
        if getattr(equipe, "gerente_id", None) and equipe.gerente_id not in membros_ids:
            errors["gerente"] = "O gerente deve ser membro da equipe."

        if errors:
            raise ValidationError(errors)


# EQUIPE MEMBRO
@admin.register(EquipeMembro)
class EquipeMembroAdmin(admin.ModelAdmin):
    list_display = ("equipe", "user", "papel", "ativo", "criado_em")
    list_filter = ("papel", "ativo")
    search_fields = ("user__username", "equipe__nome")