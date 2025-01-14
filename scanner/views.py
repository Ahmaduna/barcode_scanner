from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from .models import Product, UserScore
import requests
import logging
import json

logger = logging.getLogger(__name__)

# Remplacez par votre clé API Barcode Lookup
BARCODE_LOOKUP_API_KEY = "m2cix88kkoh9k07wyjhgscoubwmxlm"

def map_category_to_recycling_type(category, packaging=""):
    """
    Mappe une catégorie ou emballage à un type de déchet spécifique.
    """
    category = category.lower()
    packaging = packaging.lower()

    if any(keyword in category + packaging for keyword in [
        "plastique", "carton", "papier", "emballage", "bouteille", "canette", "alu", "aluminium",
        "plastic", "cardboard", "paper", "packaging", "bottle", "can", "aluminum",
        "card-box", "pet-bottle", "mixed plastic-bag", "fr:sac plastique", "fr:bouteille en pet",
        "fr:carton plastique"
    ]):
        return "Recyclables"
    elif any(keyword in category + packaging for keyword in [
        "organique", "alimentaire", "compost", "déchet de cuisine", "fruits", "légumes", "épluchures",
        "organic", "food waste", "compostable", "kitchen waste", "fruits", "vegetables", "peelings",
        "fr:compost", "fr:épluchures", "fr:organique"
    ]):
        return "Compost"
    elif any(keyword in category + packaging for keyword in [
        "verre", "bocal", "bouteille en verre", "pot",
        "glass", "jar", "glass bottle", "container", "film", "wrapper",
        "fr:bocal", "fr:film", "fr:verre", "fr:pot"
    ]):
        return "Verre"
    elif any(keyword in category + packaging for keyword in [
        "metal", "can", "drink can", "canned", "steel-can", "fr:canette métal recyclabbe à l'infini",
        "fr:cannette aluminium", "fr:boîte métal à recycler", "fr:boîte en métal"
    ]):
        return "Métal"
    elif any(keyword in category + packaging for keyword in [
        "ordures ménagères", "non recyclable", "déchet général", "restes",
        "household waste", "non-recyclable", "general waste", "leftovers",
        "fr:non recyclable", "fr:restes", "fr:ordures ménagères"
    ]):
        return "Ordures ménagères"
    elif any(keyword in category + packaging for keyword in [
        "pile", "batterie", "électronique", "électroménager", "téléphone", "ordinateur", "déchet dangereux",
        "battery", "electronics", "appliance", "phone", "computer", "hazardous waste",
        "fr:pile", "fr:électronique", "fr:batterie", "fr:déchets dangereux"
    ]):
        return "Déchets spéciaux"

    return "Autre"

def map_recycling_type_to_bin_color(recycling_type):
    """
    Mappe le type de déchet à une couleur de poubelle.
    """
    bin_colors = {
        "Verre": {
            "color": "Verte",
            "rappel": "Le verre va dans la poubelle verte. Pas de bouchons ni couvercles."
        },
        "Recyclables": {
            "color": "Jaune",
            "rappel": "Plastique, carton et papier vont dans la poubelle jaune."
        },
        "Compost": {
            "color": "Compost",
            "rappel": "Les déchets organiques vont au compost."
        },
        "Métal": {
            "color": "Jaune",
            "rappel": "Le métal va dans la poubelle jaune."
        },
        "Ordures ménagères": {
            "color": "Grise/Noire",
            "rappel": "Les déchets non recyclables vont dans la poubelle grise ou noire."
        },
        "Déchets spéciaux": {
            "color": "Spéciale",
            "rappel": "Les déchets dangereux nécessitent un traitement particulier."
        },
        "Autre": {
            "color": "Grise/Noire",
            "rappel": "Catégorie inconnue. Veuillez vérifier localement."
        },
    }
    return bin_colors.get(recycling_type, bin_colors["Autre"])

def scan_barcode(request, barcode):
    """
    Vue pour traiter les requêtes d'identification de produit via un code-barres.
    """
    logger.info(f"Requête reçue avec le code-barres : {barcode}")

    # Vérifier si le produit existe déjà dans la base locale
    try:
        product = Product.objects.get(barcode=barcode)
        recycling_type = product.recycling_type
    except Product.DoesNotExist:
        product_data = fetch_from_openfoodfacts(barcode) or fetch_from_barcodelookup(barcode)
        if not product_data:
            return JsonResponse({'error': 'Produit non trouvé.'}, status=404)

        recycling_type = map_category_to_recycling_type(
            product_data.get("category", ""),
            product_data.get("packaging", "")
        )
        Product.objects.create(
            barcode=barcode,
            name=product_data.get("name", "Nom indisponible"),
            category=product_data.get("category", ""),
            brand=product_data.get("brand", ""),
            image_url=product_data.get("image_url", ""),
            recycling_type=recycling_type,
        )

    bin_info = map_recycling_type_to_bin_color(recycling_type)
    return JsonResponse({
        "recycling_type": recycling_type,
        "bin_color": bin_info["color"],
        "rappel": bin_info["rappel"],
    })
def scan_page(request):
    """
    Vue pour afficher la page de scan.
    """
    return render(request, 'scanner/scan.html')
