# Gestion d'étiquettes pour un commerce de fromagerie

Ce projet est une application web Django pour la gestion d'une fromagerie, incluant la gestion des fromages, de leurs caractéristiques (lait, origine, producteur, etc.) et la génération d'étiquettes PDF personnalisées pour l'impression.

Ce projet a été réalisé dans le cadre d'un stage BBA (de Toulouse Business School) en mai-juin 2025 dans un commerce de vente de fromages (La Fromagerie Pescalune à Lunel, France). 

Le stagiaire a formalisé le cahier des charges, spécifié les besoins fonctionnels issus de discussions avec sa tutrice et a confié la réalisation de l'application web à un développeur python. Le stagiaire a ensuite assuré les interactions entre le développeur et sa tutrice dans la phase de mise en oeuvre sur pythonanywhere et a assuré la formation de sa tutrice à l'utilisation de l'application web.

## Fonctionnalités

* **Gestion des Fromages :** Crud complet pour les fromages (ajout, suppression, modification) avec de nombreuses caractéristiques (nom, type de lait, origine animale, matière grasse, prix, etc.).
* **Gestion des Catégories :** Types de fromage, types de fabrication du lait, origine animale du lait, unités de prix.
* **Génération d'Étiquettes PDF :** Action personnalisée dans l'interface d'administration pour générer des étiquettes imprimables pour les fromages sélectionnés, avec des informations détaillées et des indicateurs visuels (AOP, promotion, coup de cœur, nouveauté).
* **Marquage d'Impression :** Possibilité de marquer les fromages pour impression et de décocher ce marqueur après génération des étiquettes.
* **Affichage des Promotions :** Le prix original est barré et le prix promotionnel est affiché en rouge si le fromage est en promotion.
* **Gestion de l'Inventaire :** Champ pour indiquer si un fromage est en stock.

## Technologies Utilisées

* **Django :** Framework web Python.
* **ReportLab :** Bibliothèque Python pour la génération de PDF.
* **PythonAnywhere :** Plateforme d'hébergement.
g
## Licence
Ce projet est sous licence MIT (https://opensource.org/licenses/MIT). 
Cela signifie que vous êtes libre d'utiliser, de copier, de modifier, de fusionner, de publier, de distribuer, de sous-licencier et/ou de vendre des copies du logiciel, sous réserve de l'inclusion de l'avis de droit d'auteur et de cet avis de permission dans toutes les copies ou parties substantielles du Logiciel.
Copyright Notice:
* Copyright (c) 2025 Vincent BONNAL

## Installation Locale

Suivez ces étapes pour configurer le projet en local.

### Prérequis

* Python 3.x
* pip (gestionnaire de paquets Python)

### Étapes

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/vbonnal/ma_fromagerie.git
    cd ma_fromagerie
    ```

2.  **Créez un environnement virtuel (très recommandé) :**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Linux/macOS
    # venv\Scripts\activate   # Sur Windows
    ```

3.  **Installez les dépendances :**
    ```bash
    pip install django reportlab Pillow
    ```
    *(Note: Pillow est nécessaire pour le traitement des images par ReportLab.)*

4.  **Créez le fichier de réglages locaux:**
    Créez un fichier `local_settings.py` dans le répertoire ma_fromagerie/ma_fromagerie que `settings.py`. Ce fichier contiendra vos informations sensibles qu'il ne faudra pas communiquer.

    ```python
    # local_settings.py
    from .settings import BASE_DIR    

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    # Ajoutez d'autres paramètres spécifiques à votre environnement local si nécessaire
    ```

5.  **Exécutez les migrations :**
    ```bash
    python manage.py makemigrations fromagerie # Ou le nom de votre app
    python manage.py migrate
    ```

6.  **Créez un superutilisateur (pour accéder à l'admin) :**
    ```bash
    python manage.py createsuperuser
    ```
    Suivez les instructions pour créer votre utilisateur.

7.  **Collectez les fichiers statiques :**
    ```bash
    python manage.py collectstatic
    ```
    *(Assurez-vous que vos images (logo, aop, promo, etc.) sont bien placées dans un répertoire `static` à la racine de votre application `fromagerie` càd dans le répertoire `/ma_fromagerie/fromagerie/static/` ou dans un répertoire statique global défini dans `settings.py`.)*

8.  **Démarrez le serveur de développement :**
    ```bash
    python manage.py runserver
    ```

    Accédez à l'interface d'administration via `http://127.0.0.1:8000/admin/`.

## Déploiement sur PythonAnywhere.com

PythonAnywhere est une plateforme d'hébergement facile à utiliser pour les applications Python.

### Prérequis pour PythonAnywhere

* Un compte PythonAnywhere (compte gratuit ou payant). Substituez ci-après le nom de votre compte à la place de la valeur `votre_utilisateur`
* Un accès au code du dépôt public de GitHub (si vous lisez ce document, c'est le cas): https://github.com/vbonnal/ma_fromagerie.git

### Étapes

1.  **Préparez votre code et les ressources nécessaires (images):**
    * **`local_settings.py` :** Comme mentionné, ce fichier ne doit **pas** être commité sur Git. Il contiendra vos informations sensibles spécifiques à PythonAnywhere. Il est normalement exclu de git via le fichier .gitignore
    * préparez votre logo d'entreprise qui doit être carré (sinon, il faudra configurer certains paramètres dans '/ma_fromagerie/fromagerie/admin.py', notamment les valeurs de la clé `logo` du dictionaire `ETIQUETTE_MISE_EN_PAGE`)
2.  **Configuration sur PythonAnywhere :**

    * **Accédez à l'onglet "Web" :** Cliquez sur "Add a new web app" et suivez les étapes pour configurer une application Django.
    * **Chemin du code :** Spécifiez le chemin vers votre dépôt Git (par exemple, `/home/votre_utilisateur/votre_depot`).
    * **Environnement virtuel :** Créez un environnement virtuel directement sur PythonAnywhere et installez vos dépendances (`pip install -r requirements.txt`).
    * **Fichiers statiques :** Dans l'onglet "Web" de votre application, sous la section "Static files", ajoutez les chemins pour vos fichiers statiques (par exemple, URL `/static/` et chemin `/home/votre_utilisateur/votre_depot/static/`).
    * **WSGI configuration file :** Éditez le fichier `wsgi.py` (accessible depuis l'onglet "Web") pour qu'il pointe vers votre projet Django. Il ressemble souvent à ceci :

        ```python
        # /var/www/votre_utilisateur_pythonanywhere_com_wsgi.py
        import os
        import sys

        # Ajoutez le chemin de votre projet au PYTHONPATH
        path = '/home/votre_utilisateur/votre_depot' # Remplacez par le chemin réel
        if path not in sys.path:
            sys.path.insert(0, path)

        os.environ['DJANGO_SETTINGS_MODULE'] = 'votre_projet.settings' # Remplacez votre_projet par le nom de votre dossier Django

        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        ```
        *(Assurez-vous que le chemin et le nom du module de réglages sont corrects)*

    * **Créer `local_settings.py` sur PythonAnywhere :**
        Sur PythonAnywhere, allez dans l'onglet "Files" et naviguez jusqu'au répertoire de votre projet (là où se trouvent `settings.py`). Créez un nouveau fichier nommé `local_settings.py` avec le contenu suivant (ne le commitez **JAMAIS** sur Git) :

        ```python
        # /home/votre_utilisateur/votre_depot/votre_projet/local_settings.py (remplacer votre_depot et votre_projet)
        import os
        from .settings import BASE_DIR

        SECRET_KEY = 'votre_clé_secrète_pour_pythonanywhere_plus_longue_et_plus_aléatoire' # vous pouvez utiliser par exemple le générateur de https://djecrety.ir/
        DEBUG = False # IMPORTANT : Toujours False en production !
        ALLOWED_HOSTS = ['votre_nom_utilisateur.pythonanywhere.com'] # Remplacez par votre vrai nom d'hôte PythonAnywhere
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
             }
        }
        # Ajoutez ici d'autres réglages spécifiques à PythonAnywhere ou à la production
        ```

    * **Exécuter les commandes Django sur PythonAnywhere :**
        Ouvrez une console Bash dans l'onglet "Consoles" de PythonAnywhere. Naviguez jusqu'au répertoire de votre projet (là où se trouve `manage.py`) :

        ```bash
        cd /home/votre_utilisateur/votre_depot/votre_projet # Adaptez le chemin
        source ~/.virtualenvs/votre_venv_nom/bin/activate # Adaptez le nom de votre venv
        python manage.py makemigrations fromagerie
        python manage.py migrate
        python manage.py createsuperuser
        python manage.py collectstatic
        ```
        *(N'oubliez pas d'adapter les chemins et noms de venv/projet/app)*

    * **Recharger l'application web :** Dans l'onglet "Web", cliquez sur le bouton "Reload" pour que les changements soient pris en compte.

## Sécurité

La sécurité est primordiale pour toute application web. Voici les mesures clés mises en place et celles à surveiller :

1.  **`SECRET_KEY` :**
    * **Mesure :** La `SECRET_KEY` est stockée dans un fichier `local_settings.py` qui n'est **PAS** versionné par Git.
    * **Importance :** C'est une clé cryptographique utilisée par Django pour des opérations de sécurité (signatures de sessions, protection CSRF, etc.). Elle doit être unique et secrète.
    * **Recommandation :** Assurez-vous que la clé utilisée en production (sur PythonAnywhere) est différente et encore plus complexe que celle utilisée en développement.

2.  **`ALLOWED_HOSTS` :**
    * **Mesure :** La liste des hôtes autorisés est définie dans `local_settings.py`, avec des valeurs spécifiques pour le développement (`127.0.0.1`, `localhost`) et la production (`votre_nom_utilisateur.pythonanywhere.com`).
    * **Importance :** Cette mesure de sécurité empêche les attaques par en-tête d'hôte, qui pourraient permettre à un attaquant de rediriger le trafic vers son propre site web.
    * **Recommandation :** Ne jamais laisser `ALLOWED_HOSTS = ['*']` en production.

3.  **Base de Données :**
    * **Mesure :** Les réglages de la base de données sont définis dans `local_settings.py`. Par défaut, SQLite est utilisé pour la simplicité en développement et sur PythonAnywhere pour les petits projets.
    * **Importance :** Pour des applications plus grandes ou avec des exigences de performance/concurrence plus élevées, il est recommandé d'utiliser une base de données plus robuste comme PostgreSQL ou MySQL.
    * **Recommandation :** Si vous passez à une autre base de données, assurez-vous d'utiliser des identifiants et mots de passe forts, et d'éviter de les exposer dans votre code versionné (toujours dans `local_settings.py` ou des variables d'environnement).

4.  **`DEBUG = False` en production :**
    * **Mesure :** Le réglage `DEBUG` est mis à `False` dans `local_settings.py` sur PythonAnywhere.
    * **Importance :** En mode `DEBUG = True`, Django affiche des traces d'erreurs détaillées qui peuvent contenir des informations sensibles sur votre projet et votre serveur. `DEBUG = False` cache ces informations et affiche une page d'erreur générique.
    * **Recommandation :** Toujours s'assurer que `DEBUG` est `False` en production.

5.  **Fichiers statiques et médias :**
    * **Mesure :** Les chemins pour les fichiers statiques sont configurés dans PythonAnywhere.
    * **Importance :** S'assurer que Django ne sert pas lui-même les fichiers statiques et médias en production (c'est le rôle du serveur web, comme Nginx sur PythonAnywhere) est une bonne pratique de performance et de sécurité.
    * **Recommandation :** Confirmer que vos `STATIC_ROOT` et `MEDIA_ROOT` sont correctement configurés et collectés.

## Auteurs
* Vincent BONNAL
* Clément BONNAL
---
