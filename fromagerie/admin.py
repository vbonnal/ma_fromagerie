from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, darkred
from io import BytesIO
from django.contrib.staticfiles.finders import find

from .forms import FromageForm
from .models import TypeFromage, Fromage, LaitOrigineAnimal, LaitFabrication, UnitePrix

admin.site.register(TypeFromage)
admin.site.register(LaitFabrication)
admin.site.register(UnitePrix)


ETIQUETTE_LARGEUR = 9 * cm
ETIQUETTE_HAUTEUR = 6.5 * cm
ETIQUETTES_PAR_PAGE_X = 2
ETIQUETTES_PAR_PAGE_Y = 3
ESPACEMENT_X = 1 * cm
ESPACEMENT_Y = 1 * cm

def generer_etiquettes_action(modeladmin, request, queryset):
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_bold = ParagraphStyle(name='Bold', parent=style_normal, fontName='Helvetica-Bold', fontSize=16)

    logo_path = find('fromagerie_pescalune.png')
    aop_path = find('aop-fr.png')
    promo_path = find('promo.png')
    coup_de_coeur_path = find('coup_de_coeur.png')
    nouveaute_path = find('nouveaute.png')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    x_offset = ESPACEMENT_X
    y_offset = A4[1] - ESPACEMENT_Y - ETIQUETTE_HAUTEUR
    etiquette_count = 0

    for fromage in queryset:
        try:
            img_logo = Image(logo_path, width=2.5 * cm, height=2.5 * cm)
            img_logo.drawOn(p, x_offset - 0.5 * cm, y_offset + 4 * cm)

            if fromage.aop :
                img_aop = Image(aop_path, width=2.5 * cm, height=2.5 * cm)
                img_aop.drawOn(p, x_offset + 7 * cm, y_offset + 4 * cm)
        except:
            pass

        # Informations du fromage
        # nom
        p.setFont(style_bold.fontName, style_bold.fontSize + 4)
        nom_fromage = fromage.nom
        max_chars_per_line = 13
        y_text = y_offset + 5.5 * cm
        line_height = style_bold.fontSize / 72 * cm  # Convertir la taille de police en cm (approximatif)

        if len(nom_fromage) <= max_chars_per_line:
            p.drawString(x_offset + 2.0 * cm, y_text, nom_fromage)
        else:
            lines = []
            current_line = ""
            for word in nom_fromage.split():
                if len(current_line + word) <= max_chars_per_line:
                    current_line += (word + " ")
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            lines.append(current_line.strip())  # Ajouter la dernière ligne

            for line in lines:
                p.drawString(x_offset + 2.0 * cm, y_text, line)
                y_text -= line_height * 3.5  # Ajuster l'espacement entre les lignes
        p.setFont(style_normal.fontName, style_normal.fontSize + 2)

        # origine du lait et fabrication
        if fromage.lait_fabrication or fromage.origine_lait.exists():
            texte_origines = []
            if fromage.origine_lait.exists():
                origines = [origine.nom.lower() for origine in fromage.origine_lait.all()]

                texte_origines.append(" et ".join(origines))

            texte_fabrication = ""
            if fromage.lait_fabrication:
                texte_fabrication = f"{fromage.lait_fabrication.nom.lower()}{'s' if fromage.origine_lait.count() > 1 else ''}"

            texte = ""
            if texte_origines and texte_fabrication:
                texte = f"{' et '.join(texte_origines)} {texte_fabrication}"
            elif texte_origines:
                texte = ' et '.join(texte_origines)
            elif texte_fabrication:
                texte = texte_fabrication

            if texte:
                p.drawString(x_offset + 0.0 * cm, y_offset + 3.5 * cm, f"Lait{'s' if fromage.origine_lait.count() > 1 else ''}: {texte.capitalize()}")

        # Type de pâte
        if fromage.type_fromage:
            p.drawString(x_offset + 0.0 * cm, y_offset + 3 * cm, f"Type: {fromage.type_fromage.nom}")

        # Matière grasse
        if fromage.type_fromage:
            p.drawString(x_offset + 0.0 * cm, y_offset + 2.5 * cm, f"{fromage.matiere_grasse}% de matière grasse")

        # Producteur
        if fromage.producteur:
            p.drawString(x_offset + 0.0 * cm, y_offset + 2.0 * cm, f"Producteur: {fromage.producteur}")

        # Localisation de la production
        texte =  []
        if fromage.ville_production: texte.append(fromage.ville_production.capitalize())
        if fromage.departement_production or fromage.code_postal :
            if fromage.ville_production:
                if fromage.code_postal :
                    texte.append(f"({str(fromage.code_postal)})")
                else :
                    texte.append(f"({str(fromage.departement_production)})")
            else :
                if fromage.code_postal:
                    texte.append(f"{str(fromage.code_postal)}")
                else :
                    texte.append(f"{str(fromage.departement_production)}")
        if fromage.pays_production: texte.append(fromage.pays_production.capitalize())
        texte = ' '.join(texte)
        if fromage.pays_production : p.drawString(x_offset + 0.0 * cm, y_offset + 1.5 * cm, f"Origine : {texte}")

        # Prix de vente


        # Affichage de l'image de promotion
        if fromage.prix_vente and fromage.prix_promotion is not None and fromage.en_promotion:
            p.setFont(style_normal.fontName, style_normal.fontSize+3 )  # Police plus petite
            p.setStrokeColor(black)
            p.setLineWidth(0.5)
            prix_vente_x = x_offset + 4.0 * cm
            prix_vente_y = y_offset + 1.0 * cm  # Ajuster la position verticale
            p.drawString(prix_vente_x, prix_vente_y, f"{fromage.prix_vente}€")
            p.line(
                prix_vente_x - 0.1 * cm,
                prix_vente_y + 0.1 * cm,
                prix_vente_x + len(f"{fromage.prix_vente}€") * p.stringWidth(f"{fromage.prix_vente}€", style_normal.fontName, style_normal.fontSize + 2) * 0.2 + 0.2 * cm,
                prix_vente_y + 0.1 * cm)  # Tracer la ligne

            p.setFont(style_bold.fontName, style_bold.fontSize + 4)
            unite_vente = fromage.unite_prix_vente
            unite_nom = ""
            if unite_vente:
                unite_nom = unite_vente.nom
            prix_promotion_texte = f"{fromage.prix_promotion}€ {unite_nom}"
            p.setFont(style_bold.fontName, style_bold.fontSize + 6)
            p.setFillColor(darkred)
            p.drawString(x_offset + 4.0 * cm, y_offset + 0.0 * cm, f"{prix_promotion_texte}")
            p.setFont(style_bold.fontName, style_bold.fontSize + 4)
            p.setFillColor(black)

            if promo_path:
                try:
                    img_promo = Image(promo_path, width=2.85 * cm, height=2 * cm)
                    img_promo.drawOn(p, x_offset + 5 * cm, y_offset + 0.5 * cm)  # Dessin original (peut être omis si vous ne voulez que la version tournée)
                except Exception as e:
                    print(f"Erreur lors de l'affichage de l'image promo: {e}")

        elif fromage.prix_vente:  # Affichage normal si pas de promotion
            p.setFont(style_bold.fontName, style_bold.fontSize + 4)
            unite_vente = fromage.unite_prix_vente
            unite_nom = ""
            if unite_vente:
                unite_nom = unite_vente.nom
            texte = f"{fromage.prix_vente}€ {unite_nom}"
            p.drawString(x_offset + 4.0 * cm, y_offset + 0.0 * cm, f"{texte}")

        if fromage.coup_de_coeur is True:
            try:
                img_coup_de_coeur = Image(coup_de_coeur_path, width=3.575 * cm, height=1.625 * cm)
                img_coup_de_coeur.drawOn(p, x_offset + 0.0 * cm, y_offset - 0.8 * cm)  # Dessin original (peut être omis si vous ne voulez que la version tournée)
            except Exception as e:
                print(f"Erreur lors de l'affichage de l'image coup_de_coeur: {e}")
        elif fromage.nouveaute is True:
            try:
                img_nouveaute = Image(nouveaute_path, width=2.7 * cm, height=2 * cm)
                img_nouveaute.drawOn(p, x_offset + 0.0 * cm, y_offset - 0.8 * cm)  # Dessin original (peut être omis si vous ne voulez que la version tournée)
            except Exception as e:
                print(f"Erreur lors de l'affichage de l'image nouveauté: {e}")


        etiquette_count += 1
        x_offset += ETIQUETTE_LARGEUR + ESPACEMENT_X

        # Nouvelle ligne si 2 étiquettes sur la ligne
        if etiquette_count % ETIQUETTES_PAR_PAGE_X == 0:
            x_offset = ESPACEMENT_X
            y_offset -= ETIQUETTE_HAUTEUR + ESPACEMENT_Y

        # Nouvelle page après 4 étiquettes
        if etiquette_count % (ETIQUETTES_PAR_PAGE_X * ETIQUETTES_PAR_PAGE_Y) == 0:
            p.setStrokeColor(black)
            p.setDash(1, 2)
            for i in range(ETIQUETTES_PAR_PAGE_Y + 1):
                y = A4[1] - ESPACEMENT_Y - i * (ETIQUETTE_HAUTEUR + ESPACEMENT_Y)
                p.line(ESPACEMENT_X / 2, y, A4[0] - ESPACEMENT_X / 2, y)
            for i in range(ETIQUETTES_PAR_PAGE_X + 1):
                x = ESPACEMENT_X + i * (ETIQUETTE_LARGEUR + ESPACEMENT_X) - ESPACEMENT_X / 2
                p.line(x, A4[1] - ESPACEMENT_Y / 2, x, ESPACEMENT_Y / 2)
            p.showPage()
            y_offset = A4[1] - ESPACEMENT_Y - ETIQUETTE_HAUTEUR

    # Dessiner les traits pointillés pour la dernière page
    p.setStrokeColor(black)
    p.setDash(1, 2)
    for i in range(ETIQUETTES_PAR_PAGE_Y + 1):
        y = A4[1] - ESPACEMENT_Y - i * (ETIQUETTE_HAUTEUR + ESPACEMENT_Y)
        p.line(ESPACEMENT_X / 2, y, A4[0] - ESPACEMENT_X / 2, y)
    for i in range(ETIQUETTES_PAR_PAGE_X + 1):
        x = ESPACEMENT_X + i * (ETIQUETTE_LARGEUR + ESPACEMENT_X) - ESPACEMENT_X / 2
        p.line(x, A4[1] - ESPACEMENT_Y / 2, x, ESPACEMENT_Y / 2)

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etiquettes_fromages_selectionnes.pdf"'
    return response

generer_etiquettes_action.short_description = "Générer les étiquettes PDF (6 par page A4) des fromages sélectionnés"

def decocher_a_imprimer_action(modeladmin, request, queryset):
    queryset.update(a_imprimer=False)
decocher_a_imprimer_action.short_description = "Décocher 'A imprimer' pour les fromages sélectionnés"

class FromageAdmin(admin.ModelAdmin):
    form = FromageForm
    search_fields = ('nom', 'pays_production')
    list_display = ('nom', 'en_stock', 'lait_fabrication','type_fromage', 'pays_production', 'prix_vente','unite_prix_vente', 'aop', 'a_imprimer')
    list_filter = ('a_imprimer', 'en_stock', 'type_fromage', 'pays_production', 'lait_fabrication', 'origine_lait', 'aop')
    actions = [generer_etiquettes_action, decocher_a_imprimer_action]
    list_editable = ('en_stock', 'a_imprimer',)

    def save_model(self, request, obj, form, change):
        obj.save()
        form.save_m2m() # Sauvegarde les relations ManyToMany après la sauvegarde de l'objet

admin.site.register(Fromage, FromageAdmin)

class LaitOrigineAnimalAdmin(admin.ModelAdmin):
    search_fields = ['nom']
    list_display = ['nom']
admin.site.register(LaitOrigineAnimal, LaitOrigineAnimalAdmin)