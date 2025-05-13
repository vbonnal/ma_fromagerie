from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black
from io import BytesIO
from django.contrib.staticfiles.finders import find

from .models import TypeFromage, Fromage

admin.site.register(TypeFromage)

ETIQUETTE_LARGEUR = 9 * cm
ETIQUETTE_HAUTEUR = 6.5 * cm
ETIQUETTES_PAR_PAGE_X = 2
ETIQUETTES_PAR_PAGE_Y = 2
ESPACEMENT_X = 1 * cm
ESPACEMENT_Y = 1 * cm

def generer_etiquettes_action(modeladmin, request, queryset):
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_bold = ParagraphStyle(name='Bold', parent=style_normal, fontName='Helvetica-Bold', fontSize=10)

    logo_path = find('fromagerie-pescalune-round-150x150.png')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    x_offset = ESPACEMENT_X
    y_offset = A4[1] - ESPACEMENT_Y - ETIQUETTE_HAUTEUR
    etiquette_count = 0

    for fromage in queryset:
        # Ajouter le logo (si le fichier existe)
        try:
            img = Image(logo_path, width=1.5 * cm, height=1.5 * cm)
            img.drawOn(p, x_offset + 0.5 * cm, y_offset + 5 * cm)
        except:
            pass

        # Ajouter les informations du fromage
        p.setFont(style_bold.fontName, style_bold.fontSize)
        p.drawString(x_offset + 3 * cm, y_offset + 5.5 * cm, fromage.nom)
        p.setFont(style_normal.fontName, style_normal.fontSize)
        p.drawString(x_offset + 0.5 * cm, y_offset + 4.5 * cm, f"Lait: {'cru' if fromage.lait_cru else 'pasteurisé'}")
        p.drawString(x_offset + 0.5 * cm, y_offset + 4 * cm, f"Pays: {fromage.pays_production}")
        if fromage.ville_production:
            p.drawString(x_offset + 0.5 * cm, y_offset + 3.5 * cm, f"Ville: {fromage.ville_production}")
        if fromage.departement_production:
            p.drawString(x_offset + 0.5 * cm, y_offset + 3 * cm, f"Département: {fromage.departement_production}")
        if fromage.producteur:
            p.drawString(x_offset + 0.5 * cm, y_offset + 2.5 * cm, f"Producteur: {fromage.producteur}")
        p.drawString(x_offset + 0.5 * cm, y_offset + 2 * cm, f"Type: {fromage.type_fromage.nom}")
        p.setFont(style_bold.fontName, 11)
        p.drawString(x_offset + 0.5 * cm, y_offset + 1.5 * cm, f"Prix: {fromage.prix_vente} €")

        etiquette_count += 1
        x_offset += ETIQUETTE_LARGEUR + ESPACEMENT_X

        # Nouvelle ligne si 2 étiquettes sur la ligne
        if etiquette_count % ETIQUETTES_PAR_PAGE_X == 0:
            x_offset = ESPACEMENT_X
            y_offset -= ETIQUETTE_HAUTEUR + ESPACEMENT_Y

        # Nouvelle page après 4 étiquettes
        if etiquette_count % (ETIQUETTES_PAR_PAGE_X * ETIQUETTES_PAR_PAGE_Y) == 0:
            p.showPage()
            y_offset = A4[1] - ESPACEMENT_Y - ETIQUETTE_HAUTEUR

    # Dessiner les traits pointillés pour la découpe (sur toutes les pages)
    p.setStrokeColor(black)
    p.setDash(1, 2) # Longueur du tiret, longueur de l'espace

    # Traits horizontaux
    for i in range(ETIQUETTES_PAR_PAGE_Y + 1):
        y = A4[1] - ESPACEMENT_Y - i * (ETIQUETTE_HAUTEUR + ESPACEMENT_Y)
        p.line(ESPACEMENT_X / 2, y, A4[0] - ESPACEMENT_X / 2, y)

    # Traits verticaux
    for i in range(ETIQUETTES_PAR_PAGE_X + 1):
        x = ESPACEMENT_X + i * (ETIQUETTE_LARGEUR + ESPACEMENT_X) - ESPACEMENT_X / 2
        p.line(x, A4[1] - ESPACEMENT_Y / 2, x, ESPACEMENT_Y / 2)

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etiquettes_fromages_selectionnes.pdf"'
    return response

generer_etiquettes_action.short_description = "Générer les étiquettes PDF (4 par page A4) des fromages sélectionnés"

def decocher_a_imprimer_action(modeladmin, request, queryset):
    queryset.update(a_imprimer=False)
decocher_a_imprimer_action.short_description = "Décocher 'A imprimer' pour les fromages sélectionnés"

class FromageAdmin(admin.ModelAdmin):
    search_fields = ('nom', 'pays_production')
    list_display = ('nom', 'en_stock', 'type_fromage', 'pays_production', 'prix_achat', 'prix_vente', 'aop', 'a_imprimer')
    list_filter = ('a_imprimer', 'en_stock', 'type_fromage', 'pays_production', 'lait_cru', 'aop')
    actions = [generer_etiquettes_action, decocher_a_imprimer_action]
    list_editable = ('en_stock', 'a_imprimer',)

admin.site.register(Fromage, FromageAdmin)