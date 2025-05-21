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


# --- PARAMÈTRES DE MISE EN PAGE GLOBALE ---
ETIQUETTE_LARGEUR =     8.0 * cm
ETIQUETTE_HAUTEUR =     5.5 * cm
ETIQUETTES_PAR_PAGE_X = 2
ETIQUETTES_PAR_PAGE_Y = 4
ESPACEMENT_X =          1 * cm
ESPACEMENT_Y =          1 * cm
MARGE_PAGE_GAUCHE =     2.0 * cm
MARGE_PAGE_DROITE =     2.0 * cm
MARGE_PAGE_HAUT =       1.5 * cm
MARGE_PAGE_BAS =        2.0 * cm

# --- PARAMÈTRES DE MISE EN PAGE DES ÉTIQUETTES (COORDONNÉES RELATIVES À L'ÉTIQUETTE) ---
ETIQUETTE_MISE_EN_PAGE = {
    'logo': {                       'x': -0.5 * cm,     'y': 3.3 * cm,      'width': 2.3 * cm,  'height': 2.3 * cm},
    'aop': {                        'x': 6.3 * cm,      'y': 3.3 * cm,      'width': 2.3 * cm,  'height': 2.3 * cm},
    'nom_fromage': {                'x': 1.85 * cm,      'y': 4.7 * cm,     'font_size_delta': 2.5, 'max_chars_line': 13, 'line_spacing_factor': 2.7, 'max_chars_line_without_aop':18},
    'lait_origine_fabrication': {   'x': 0.0 * cm,      'y': 2.7 * cm,      'font_size_delta': 2},
    'type_fromage': {               'x': 0.0 * cm,      'y': 2.2 * cm,      'font_size_delta': 2},
    'matiere_grasse': {             'x': 0.0 * cm,      'y': 1.7 * cm,      'font_size_delta': 2},
    'producteur': {                 'x': 0.0 * cm,      'y': 1.2 * cm,      'font_size_delta': 2},
    'localisation_production': {    'x': 0.0 * cm,      'y': 0.7 * cm,      'font_size_delta': 2},
    'prix_barre': {                 'x': 3.5 * cm,      'y': 0.1 * cm,      'font_size_delta': 2, 'line_thickness': 0.8},
    'prix_promo': {                 'x': 3.5 * cm,      'y': -0.5 * cm,     'font_size_delta': 2},
    'promo_image': {                'x': 5.5 * cm,      'y': -0.0 * cm,     'width': 2.85 * cm, 'height': 2 * cm},
    'prix_normal': {                'x': 3.5 * cm,      'y': -0.5 * cm,     'font_size_delta': 3},
    'coup_de_coeur': {              'x': 0.0 * cm,      'y': -0.8 * cm,     'width': 2.86 * cm, 'height': 1.2 * cm},
    'nouveaute': {                  'x': 0.8 * cm,      'y': -0.8 * cm,     'width': 1.89 * cm, 'height': 1.4 * cm},
}

def generer_etiquettes_action(modeladmin, request, queryset):
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_bold = ParagraphStyle(name='Bold', parent=style_normal, fontName='Helvetica-Bold', fontSize=16)

    logo_path = find('logo.png')
    aop_path = find('aop-fr.png')
    promo_path = find('promo.png')
    coup_de_coeur_path = find('coup_de_coeur.png')
    nouveaute_path = find('nouveaute.png')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Calcul des offsets de départ pour la première étiquette
    current_x_offset = MARGE_PAGE_GAUCHE
    current_y_offset = A4[1] - MARGE_PAGE_HAUT - ETIQUETTE_HAUTEUR
    etiquette_count = 0

    for fromage in queryset:
        # Assurez-vous que l'étiquette s'adapte à la page suivante si elle déborde
        if (etiquette_count % (ETIQUETTES_PAR_PAGE_X * ETIQUETTES_PAR_PAGE_Y) == 0 and etiquette_count != 0):
            # Dessiner les traits pointillés de la page précédente avant de passer à la nouvelle
            draw_dotted_lines(p)
            p.showPage()
            current_x_offset = MARGE_PAGE_GAUCHE
            current_y_offset = A4[1] - MARGE_PAGE_HAUT - ETIQUETTE_HAUTEUR

        # --- Dessin des éléments de l'étiquette ---

        # Logo
        logo_conf = ETIQUETTE_MISE_EN_PAGE['logo']
        try:
            img_logo = Image(logo_path, width=logo_conf['width'], height=logo_conf['height'])
            img_logo.drawOn(p, current_x_offset + logo_conf['x'], current_y_offset + logo_conf['y'])
        except Exception as e:
            print(f"Erreur lors de l'affichage du logo: {e}")

        # AOP
        if fromage.aop:
            aop_conf = ETIQUETTE_MISE_EN_PAGE['aop']
            try:
                img_aop = Image(aop_path, width=aop_conf['width'], height=aop_conf['height'])
                img_aop.drawOn(p, current_x_offset + aop_conf['x'], current_y_offset + aop_conf['y'])
            except Exception as e:
                print(f"Erreur lors de l'affichage de l'image AOP: {e}")

        # Nom du fromage
        nom_conf = ETIQUETTE_MISE_EN_PAGE['nom_fromage']
        p.setFont(style_bold.fontName, style_bold.fontSize + nom_conf['font_size_delta'])
        nom_fromage = fromage.nom
        y_text = current_y_offset + nom_conf['y']
        line_height = (style_bold.fontSize + nom_conf['font_size_delta']) / 72 * cm

        # Déterminer la limite de caractères par ligne en fonction de la présence de l'AOP
        current_max_chars_line = nom_conf['max_chars_line']
        if not fromage.aop and 'max_chars_line_without_aop' in nom_conf:
            current_max_chars_line = nom_conf['max_chars_line_without_aop']

        if len(nom_fromage) <= current_max_chars_line:
            p.drawString(current_x_offset + nom_conf['x'], y_text, nom_fromage)
        else:
            lines = []
            current_line = ""
            for word in nom_fromage.split():
                if len(current_line + word) <= current_max_chars_line:  # Utiliser la nouvelle variable
                    current_line += (word + " ")
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            lines.append(current_line.strip())

            for line in lines:
                p.drawString(current_x_offset + nom_conf['x'], y_text, line)
                y_text -= line_height * nom_conf['line_spacing_factor']
        p.setFont(style_normal.fontName, style_normal.fontSize + ETIQUETTE_MISE_EN_PAGE['lait_origine_fabrication']['font_size_delta'])

        # Origine du lait et fabrication
        lait_conf = ETIQUETTE_MISE_EN_PAGE['lait_origine_fabrication']
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
                p.drawString(current_x_offset + lait_conf['x'], current_y_offset + lait_conf['y'], f"Lait{'s' if fromage.origine_lait.count() > 1 else ''}: {texte.capitalize()}")

        # Type de pâte
        type_conf = ETIQUETTE_MISE_EN_PAGE['type_fromage']
        if fromage.type_fromage:
            p.drawString(current_x_offset + type_conf['x'], current_y_offset + type_conf['y'], f"Type: {fromage.type_fromage.nom}")

        # Matière grasse
        mg_conf = ETIQUETTE_MISE_EN_PAGE['matiere_grasse']
        if fromage.matiere_grasse:
            p.drawString(current_x_offset + mg_conf['x'], current_y_offset + mg_conf['y'], f"{fromage.matiere_grasse}% de matière grasse")

        # Producteur
        prod_conf = ETIQUETTE_MISE_EN_PAGE['producteur']
        if fromage.producteur:
            p.drawString(current_x_offset + prod_conf['x'], current_y_offset + prod_conf['y'], f"Producteur: {fromage.producteur}")

        # Localisation de la production
        loc_conf = ETIQUETTE_MISE_EN_PAGE['localisation_production']
        texte_loc = []
        if fromage.ville_production: texte_loc.append(fromage.ville_production.capitalize())
        if fromage.departement_production or fromage.code_postal :
            if fromage.ville_production:
                if fromage.code_postal :
                    texte_loc.append(f"({str(fromage.code_postal)})")
                else :
                    texte_loc.append(f"({str(fromage.departement_production)})")
            else :
                if fromage.code_postal:
                    texte_loc.append(f"{str(fromage.code_postal)}")
                else :
                    texte_loc.append(f"{str(fromage.departement_production)}")
        if fromage.pays_production: texte_loc.append(fromage.pays_production.capitalize())
        texte_loc = ' '.join(texte_loc)
        if fromage.pays_production:
            p.drawString(current_x_offset + loc_conf['x'], current_y_offset + loc_conf['y'], f"{texte_loc}")

        # Prix de vente et promotion
        if fromage.prix_vente and fromage.prix_promotion is not None and fromage.en_promotion:
            promo_price_conf = ETIQUETTE_MISE_EN_PAGE['prix_promo']
            normal_price_conf = ETIQUETTE_MISE_EN_PAGE['prix_barre']

            p.setFont(style_normal.fontName, style_normal.fontSize + normal_price_conf['font_size_delta'])
            p.setStrokeColor(black)
            p.setLineWidth(normal_price_conf['line_thickness'])

            prix_vente_x = current_x_offset + normal_price_conf['x']
            prix_vente_y = current_y_offset + normal_price_conf['y']
            p.drawString(prix_vente_x, prix_vente_y, f"{fromage.prix_vente}€")
            p.line(
                prix_vente_x - 0.1 * cm,
                prix_vente_y + 0.1 * cm,
                prix_vente_x + len(f"{fromage.prix_vente}€") * p.stringWidth(f"{fromage.prix_vente}€", style_normal.fontName, style_normal.fontSize + 2) * 0.2 + 0.2 * cm,
                prix_vente_y + 0.1 * cm)

            p.setFont(style_bold.fontName, style_bold.fontSize + promo_price_conf['font_size_delta'])
            unite_vente = fromage.unite_prix_vente
            unite_nom = ""
            if unite_vente:
                unite_nom = unite_vente.nom
            prix_promotion_texte = f"{fromage.prix_promotion}€ {unite_nom}"
            p.setFillColor(darkred)
            p.drawString(current_x_offset + promo_price_conf['x'], current_y_offset + promo_price_conf['y'], f"{prix_promotion_texte}")
            p.setFont(style_bold.fontName, style_bold.fontSize + 4) # Reset font to default for other elements
            p.setFillColor(black)

            promo_img_conf = ETIQUETTE_MISE_EN_PAGE['promo_image']
            if promo_path:
                try:
                    img_promo = Image(promo_path, width=promo_img_conf['width'], height=promo_img_conf['height'])
                    img_promo.drawOn(p, current_x_offset + promo_img_conf['x'], current_y_offset + promo_img_conf['y'])
                except Exception as e:
                    print(f"Erreur lors de l'affichage de l'image promo: {e}")

        elif fromage.prix_vente: # Affichage normal si pas de promotion
            normal_price_conf = ETIQUETTE_MISE_EN_PAGE['prix_normal']
            p.setFont(style_bold.fontName, style_bold.fontSize + normal_price_conf['font_size_delta'])
            unite_vente = fromage.unite_prix_vente
            unite_nom = ""
            if unite_vente:
                unite_nom = unite_vente.nom
            texte = f"{fromage.prix_vente}€ {unite_nom}"
            p.drawString(current_x_offset + normal_price_conf['x'], current_y_offset + normal_price_conf['y'], f"{texte}")

        # Coup de cœur ou Nouveauté
        if fromage.coup_de_coeur is True:
            cdc_conf = ETIQUETTE_MISE_EN_PAGE['coup_de_coeur']
            try:
                img_coup_de_coeur = Image(coup_de_coeur_path, width=cdc_conf['width'], height=cdc_conf['height'])
                img_coup_de_coeur.drawOn(p, current_x_offset + cdc_conf['x'], current_y_offset + cdc_conf['y'])
            except Exception as e:
                print(f"Erreur lors de l'affichage de l'image coup_de_coeur: {e}")
        elif fromage.nouveaute is True:
            nouveaute_conf = ETIQUETTE_MISE_EN_PAGE['nouveaute']
            try:
                img_nouveaute = Image(nouveaute_path, width=nouveaute_conf['width'], height=nouveaute_conf['height'])
                img_nouveaute.drawOn(p, current_x_offset + nouveaute_conf['x'], current_y_offset + nouveaute_conf['y'])
            except Exception as e:
                print(f"Erreur lors de l'affichage de l'image nouveauté: {e}")

        etiquette_count += 1

        # Mettre à jour les offsets pour la prochaine étiquette
        current_x_offset += ETIQUETTE_LARGEUR + ESPACEMENT_X

        # Nouvelle ligne si 2 étiquettes sur la ligne
        if etiquette_count % ETIQUETTES_PAR_PAGE_X == 0:
            current_x_offset = MARGE_PAGE_GAUCHE
            current_y_offset -= ETIQUETTE_HAUTEUR + ESPACEMENT_Y


    # Dessiner les traits pointillés pour la dernière page
    draw_dotted_lines(p)

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etiquettes_fromages_selectionnes.pdf"'
    return response

# Helper function to draw dotted lines for page layout
def draw_dotted_lines(p):
    p.setStrokeColor(black)
    p.setDash(1, 2)

    # Dessiner les lignes horizontales
    for i in range(ETIQUETTES_PAR_PAGE_Y + 1):
        y = A4[1] - MARGE_PAGE_HAUT - i * (ETIQUETTE_HAUTEUR + ESPACEMENT_Y)
        # Ajuster la longueur des lignes horizontales en fonction des marges de la page
        p.line(MARGE_PAGE_GAUCHE - ESPACEMENT_X / 2, y, A4[0] - MARGE_PAGE_DROITE + ESPACEMENT_X / 2, y)

    # Dessiner les lignes verticales
    for i in range(ETIQUETTES_PAR_PAGE_X + 1):
        x = MARGE_PAGE_GAUCHE + i * (ETIQUETTE_LARGEUR + ESPACEMENT_X) - ESPACEMENT_X / 2
        # Ajuster la longueur des lignes verticales en fonction des marges de la page
        p.line(x, A4[1] - MARGE_PAGE_HAUT + ESPACEMENT_Y / 2, x, MARGE_PAGE_BAS - ESPACEMENT_Y / 2)


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