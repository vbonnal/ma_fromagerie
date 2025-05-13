from django.db import models

class TypeFromage(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

class Fromage(models.Model):
    nom = models.CharField(max_length=200)
    lait_cru = models.BooleanField(default=False)
    pays_production = models.CharField(max_length=100)
    ville_production = models.CharField(max_length=100, blank=True, null=True)
    departement_production = models.CharField(max_length=100, blank=True, null=True)
    producteur = models.CharField(max_length=200, blank=True, null=True)
    type_fromage = models.ForeignKey(TypeFromage, on_delete=models.CASCADE)
    a_imprimer = models.BooleanField(default=False)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    en_stock = models.BooleanField(default=False)
    aop = models.BooleanField(default=False)

    def __str__(self):
        return self.nom
