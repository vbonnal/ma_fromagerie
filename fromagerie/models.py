from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TypeFromage(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

class LaitOrigineAnimal(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom

class LaitFabrication(models.Model):
    nom = models.CharField(max_length=50, unique=True, verbose_name="Type de fabrication")

    def __str__(self):
        return self.nom

class UnitePrix(models.Model):
    nom = models.CharField(max_length=50, unique=True, verbose_name="Unité de prix")

    def __str__(self):
        return self.nom


class Fromage(models.Model):
    nom = models.CharField(max_length=200)
    lait_fabrication = models.ForeignKey(
        LaitFabrication,
        on_delete=models.CASCADE,
        verbose_name="Type de lait (Fabrication)")
    origine_lait = models.ManyToManyField(
        LaitOrigineAnimal,
        verbose_name="Type de lait (Animal)", blank=True, null=True,
    )
    matiere_grasse = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Matière Grasse (%)", blank=True, null=True,
    )
    aop = models.BooleanField(default=False, blank=True, null=True,)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True,)
    unite_prix_achat = models.ForeignKey(
        UnitePrix,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='achats',
        verbose_name="Unité de prix (achat)",
    )
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True,)
    unite_prix_vente = models.ForeignKey(
        UnitePrix,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventes',
        verbose_name="Unité de prix (vente)"
    )
    prix_promotion = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True,)
    en_promotion = models.BooleanField(default=False, blank=True, null=True,)
    nouveaute = models.BooleanField(default=False, blank=True, null=True,)
    coup_de_coeur = models.BooleanField(default=False, blank=True, null=True,)
    en_stock = models.BooleanField(default=False, blank=True, null=True,)
    code_postal = models.CharField(max_length=5, blank=True, null=True, verbose_name="Code Postal (Commune)")
    ville_production = models.CharField(max_length=100, blank=True, null=True)
    departement_production = models.CharField(max_length=100, blank=True, null=True)
    pays_production = models.CharField(max_length=100, blank=True, null=True,)
    producteur = models.CharField(max_length=200, blank=True, null=True, verbose_name="Producteur")
    type_fromage = models.ForeignKey(TypeFromage, on_delete=models.CASCADE, blank=True, null=True,)
    a_imprimer = models.BooleanField(default=False, verbose_name="Etiquette à imprimer", blank=True, null=True,)

    def __str__(self):
        return self.nom
