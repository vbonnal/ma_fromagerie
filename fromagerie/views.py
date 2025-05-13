from django.http import HttpResponse
from django.shortcuts import get_list_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from django.contrib.staticfiles.finders import find

from fromagerie.models import Fromage


def generer_etiquettes_pdf(request):
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    # style Bold personnalisé vu que Bold nest pas disponible, cf print(styles.list())
    style_bold = ParagraphStyle(name='Bold', parent=style_normal, fontName='Helvetica-Bold', fontSize=10)

    logo_path = find('fromagerie-pescalune-round-150x150.png')
    fromages_a_imprimer = get_list_or_404(Fromage, a_imprimer=True)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(9*cm, 6.5*cm)) # Définition de la taille de l'étiquette

    if style_normal is None:
        style_normal = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=10)
    if style_bold is None:
        style_bold = ParagraphStyle(name='Bold', parent=style_normal, fontName='Helvetica-Bold')

    # logo_path = 'static/fromagerie-pescalune-round-150x150.png' # Remplacez par le chemin réel de votre logo
    # Ajout du logo (si le fichier existe)
    try:
        img = Image(logo_path, width=1.5*cm, height=1.5*cm)
        img.drawOn(p, 0.5*cm, 5*cm)
    except:
        # TODO : Gérer le cas où le logo n'est pas trouvé
        pass
    for fromage in fromages_a_imprimer:

        # Ajouter les informations du fromage
        p.setFont(style_bold.fontName, style_bold.fontSize)
        p.drawString(3*cm, 5.5*cm, fromage.nom)
        p.setFont(style_normal.fontName, style_normal.fontSize)
        p.drawString(0.5*cm, 4.5*cm, f"Lait: {'cru' if fromage.lait_cru else 'pasteurisé'}")
        p.drawString(0.5*cm, 4*cm, f"Pays: {fromage.pays_production}")
        if fromage.ville_production:
            p.drawString(0.5*cm, 3.5*cm, f"Ville: {fromage.ville_production}")
        if fromage.departement_production:
            p.drawString(0.5*cm, 3*cm, f"Département: {fromage.departement_production}")
        if fromage.producteur:
            p.drawString(0.5*cm, 2.5*cm, f"Producteur: {fromage.producteur}")
        p.drawString(0.5*cm, 2*cm, f"Type: {fromage.type_fromage.nom}")
        p.setFont(style_bold.fontName, 11)
        p.drawString(0.5 * cm, 1.5 * cm, f"Prix: {fromage.prix_vente} €")
        p.setFont(style_bold.fontName, 11)
        p.drawString(0.5*cm, 1.5*cm, f"Prix: {fromage.prix_vente} €")

        p.showPage() # Nouvelle page pour le fromage suivant

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etiquettes_fromages.pdf"'
    return response

