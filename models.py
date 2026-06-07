"""
Model de Usuário VOPT
─────────────────────
Estende AbstractBaseUser para ter controle total sobre os campos,
sem os campos desnecessários do User padrão do Django.
Compatível com djongo (MongoDB).
"""
import re
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# ─── Validadores ─────────────────────────────────────────────────────────────

CPF_RE  = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
CNPJ_RE = re.compile(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")


def validar_documento(valor):
    if not (CPF_RE.match(valor) or CNPJ_RE.match(valor)):
        raise ValidationError(
            "Documento inválido. Use CPF (000.000.000-00) ou CNPJ (00.000.000/0000-00)."
        )


def validar_nome(valor):
    if not re.match(r"^[A-Za-zÀ-ÿ\s'\-]+$", valor.strip()):
        raise ValidationError("Nome contém caracteres inválidos.")


def trial_expira():
    return timezone.now() + timedelta(days=30)


# ─── Manager ─────────────────────────────────────────────────────────────────

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, documento, password=None, **extra):
        if not email:
            raise ValueError("E-mail é obrigatório.")
        email = self.normalize_email(email)
        user  = self.model(email=email, nome=nome, documento=documento, **extra)
        user.set_password(password)   # bcrypt via Django
        user.full_clean()             # roda os validadores do modelo
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, documento, password=None, **extra):
        extra.setdefault("is_staff",     True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, nome, documento, password, **extra)


# ─── Model ───────────────────────────────────────────────────────────────────

class Usuario(AbstractBaseUser, PermissionsMixin):

    TIPO_CHOICES = [("pf", "Pessoa Física"), ("pj", "Pessoa Jurídica")]

    nome       = models.CharField(max_length=80,  validators=[validar_nome])
    email      = models.EmailField(unique=True)
    documento  = models.CharField(max_length=20,  validators=[validar_documento])

    # Tipo detectado automaticamente no save()
    tipo       = models.CharField(max_length=2, choices=TIPO_CHOICES, editable=False)

    trial_ativo = models.BooleanField(default=True)
    trial_fim   = models.DateTimeField(default=trial_expira)

    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    criado_em   = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["nome", "documento"]

    objects = UsuarioManager()

    class Meta:
        verbose_name        = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return f"{self.nome} <{self.email}>"

    def save(self, *args, **kwargs):
        # Define tipo PF/PJ automaticamente pelo formato do documento
        self.tipo = "pf" if CPF_RE.match(self.documento or "") else "pj"
        super().save(*args, **kwargs)

    @property
    def trial_dias_restantes(self):
        if not self.trial_ativo:
            return 0
        restante = (self.trial_fim - timezone.now()).days
        return max(restante, 0)
