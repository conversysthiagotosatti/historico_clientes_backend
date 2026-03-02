from django.db import models
from django.contrib.auth import get_user_model
import hashlib

User = get_user_model()


# ==========================================
# ORGANIZATION
# ==========================================
class Organization(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ==========================================
# UNIDADE
# ==========================================
class Unidade(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="unidades"
    )

    nome = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    hostname = models.CharField(max_length=255)

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hostname


# ==========================================
# LINK
# ==========================================
class Link(models.Model):
    unidade = models.OneToOneField(
        Unidade,
        on_delete=models.CASCADE,
        related_name="link"
    )

    # MPLS
    designacao_mpls = models.CharField(max_length=255, null=True, blank=True)
    rede_mpls = models.CharField(max_length=255, null=True, blank=True)
    ip_mpls = models.GenericIPAddressField(null=True, blank=True)
    ip_mpls_fortigate = models.GenericIPAddressField(null=True, blank=True)
    mask_mpls = models.GenericIPAddressField(null=True, blank=True)
    velocidade_mpls = models.IntegerField(null=True, blank=True)
    ip_lo_pe_mpls = models.GenericIPAddressField(null=True, blank=True)

    # BLD
    designacao_bld = models.CharField(max_length=255, null=True, blank=True)
    ip_bld_pe = models.GenericIPAddressField(null=True, blank=True)
    ip_bld_fortigate = models.GenericIPAddressField(null=True, blank=True)
    msk_bld = models.GenericIPAddressField(null=True, blank=True)
    velocidade_bld = models.IntegerField(null=True, blank=True)
    ip_lo_pe_bld = models.GenericIPAddressField(null=True, blank=True)

    # LAN
    rede_pri_lan = models.GenericIPAddressField(null=True, blank=True)
    ip_pri_lan_fortigate = models.GenericIPAddressField(null=True, blank=True)
    mascara_pri_lan = models.GenericIPAddressField(null=True, blank=True)

    rede_sec_lan = models.CharField(max_length=255, null=True, blank=True)
    ip_sec_lan_fortigate = models.GenericIPAddressField(null=True, blank=True)
    mask_sec_lan = models.GenericIPAddressField(null=True, blank=True)

    vlan_id = models.IntegerField(null=True, blank=True)

    # Loopbacks
    loopback_soc = models.GenericIPAddressField(null=True, blank=True)
    loopback_grc = models.GenericIPAddressField(null=True, blank=True)
    loopback_cae = models.GenericIPAddressField(null=True, blank=True)


    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        partes = []

        if self.velocidade_mpls:
            partes.append(f"MPLS {self.velocidade_mpls}Mb")

        if self.velocidade_bld:
            partes.append(f"BLD {self.velocidade_bld}Mb")

        descricao = " / ".join(partes) if partes else "Sem link"

        return f"{self.unidade.hostname} | {descricao}"


# ==========================================
# SCRIPT TEMPLATE
# ==========================================
class ScriptTemplate(models.Model):
    TIPO_CHOICES = [
        ("SEM_VLAN", "SEM VLAN"),
        ("COM_VLAN", "COM VLAN"),
    ]

    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    versao = models.CharField(max_length=20)
    template = models.TextField()

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} v{self.versao}"


# ==========================================
# SCRIPT GERADO
# ==========================================
class ScriptGerado(models.Model):
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE)
    template = models.ForeignKey(ScriptTemplate, on_delete=models.PROTECT)

    script = models.TextField()
    hash_script = models.CharField(max_length=64)

    gerado_por = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    gerado_em = models.DateTimeField(auto_now_add=True)

    def gerar_hash(self):
        return hashlib.sha256(self.script.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.hash_script:
            self.hash_script = self.gerar_hash()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unidade.hostname} | {self.template.nome} | {self.gerado_em}"