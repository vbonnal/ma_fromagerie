from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Fromage, LaitOrigineAnimal, LaitFabrication

class FromageForm(forms.ModelForm):
    origine_lait = forms.ModelMultipleChoiceField(
        queryset=LaitOrigineAnimal.objects.all(),
        widget=FilteredSelectMultiple("Origine(s) du lait", is_stacked=False),
        required=False
    )
    lait_fabrication = forms.ModelChoiceField(
        queryset=LaitFabrication.objects.all(),
        empty_label="Sélectionner le type de fabrication"
    )

    class Meta:
        model = Fromage
        fields = ['nom', 'lait_fabrication','en_stock', 'aop', 'origine_lait',
                  'matiere_grasse', 'pays_production', 'code_postal', 'ville_production',
                  'departement_production', 'producteur', 'type_fromage', 'prix_achat',
                  'unite_prix_achat','prix_vente', 'unite_prix_vente', 'prix_promotion','en_promotion',
                  'nouveaute','coup_de_coeur','a_imprimer']