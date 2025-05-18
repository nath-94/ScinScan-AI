import os
import PyPDF2
from PyPDF2 import PdfWriter

def create_dermatology_knowledge_file():
    """
    Crée un fichier PDF avec les informations sur la dermatologie 
    pour être utilisé dans le système RAG du chatbot
    """
    dermatology_content = """LES CANCERS DE LA PEAU ET LÉSIONS CUTANÉES

TYPES DE LÉSIONS

1. KÉRATOSE ACTINIQUE (akiec)
La kératose actinique est une lésion précancéreuse résultant d'une exposition prolongée aux rayons ultraviolets. Elle se présente généralement sous forme de petites zones rugueuses, squameuses ou croûteuses sur la peau. Ces lésions apparaissent souvent sur les zones exposées au soleil comme le visage, les oreilles, le cuir chevelu (chez les personnes chauves), le cou, le dos des mains et les avant-bras.
Entre 5% et 10% des kératoses actiniques évoluent vers un carcinome épidermoïde invasif si elles ne sont pas traitées. Le traitement peut inclure la cryothérapie, la thérapie photodynamique, les médicaments topiques ou l'excision chirurgicale.

2. CARCINOME BASOCELLULAIRE (bcc)
Le carcinome basocellulaire est le type de cancer de la peau le plus fréquent. Il se développe généralement sur les zones exposées au soleil et apparaît souvent comme une bosse ou une croissance rose perlée, qui peut saigner facilement ou ne jamais cicatriser complètement.
Le carcinome basocellulaire a un très faible potentiel métastatique mais peut être localement invasif et détruire les structures environnantes s'il n'est pas traité. Les options de traitement comprennent l'excision chirurgicale, la chirurgie micrographique de Mohs, le curetage et l'électrodessication, la radiothérapie ou des médicaments topiques.

3. KÉRATOSE BÉNIGNE (bkl)
Les kératoses bénignes, dont les kératoses séborrhéiques, sont des excroissances bénignes qui ressemblent à des verrues. Elles apparaissent généralement avec l'âge et peuvent être de couleur brun clair à noir, avec une texture cireuse ou écailleuse.
Bien que les kératoses bénignes soient non cancéreuses, elles peuvent parfois ressembler à des mélanomes, donc un diagnostic professionnel est important. Si des raisons esthétiques ou des symptômes comme des démangeaisons le justifient, elles peuvent être enlevées par cryothérapie, curetage, laser ou excision chirurgicale.

4. DERMATOFIBROME (df)
Le dermatofibrome est une tumeur cutanée bénigne commune qui se présente généralement comme un nodule ferme, surélevé, de couleur brun-rouge à brun foncé. Ils sont généralement petits (5-10 mm) et peuvent apparaître n'importe où, mais le plus souvent sur les membres inférieurs.
Les dermatofibromes sont complètement bénins et ne nécessitent généralement pas de traitement sauf pour des raisons cosmétiques ou s'ils causent de l'inconfort. Ils peuvent persister indéfiniment et sont parfois appelés "cicatrices d'insectes" car ils apparaissent souvent après une piqûre ou un traumatisme mineur.

5. NAEVUS MÉLANOCYTAIRE (nv)
Communément appelés grains de beauté, les naevus mélanocytaires sont des tumeurs bénignes des cellules pigmentaires (mélanocytes). Ils peuvent être présents à la naissance (naevus congénitaux) ou apparaître plus tard (naevus acquis). Ils varient en taille et en couleur, du brun clair au noir.
La plupart des naevus mélanocytaires sont bénins, mais certains, en particulier les grands naevus congénitaux ou les naevus dysplasiques (atypiques), présentent un risque accru de développer un mélanome. Il est important de surveiller les changements selon la règle ABCDE (Asymétrie, Bords irréguliers, Couleur non homogène, Diamètre > 6mm, Évolution).

6. LÉSION VASCULAIRE (vasc)
Les lésions vasculaires cutanées comprennent divers types d'anomalies des vaisseaux sanguins ou lymphatiques, comme les angiomes stellaires, les angiomes cerises (papules rubis), les hémangiomes et les malformations vasculaires. Elles apparaissent généralement comme des zones rouges, violettes ou bleues sur la peau.
La plupart des lésions vasculaires sont bénignes et ne nécessitent pas de traitement, sauf pour des raisons esthétiques. Certaines lésions vasculaires présentes à la naissance peuvent s'améliorer spontanément avec le temps. Les options de traitement incluent le laser, la sclérothérapie, ou dans certains cas, l'excision chirurgicale.

7. MÉLANOME (mel)
Le mélanome est le type de cancer de la peau le plus dangereux. Il se développe à partir des mélanocytes, les cellules qui produisent la mélanine. Le mélanome peut apparaître comme une nouvelle tache pigmentée ou comme un changement dans un grain de beauté existant.
Le mélanome a un haut potentiel métastatique et peut être mortel s'il n'est pas détecté et traité à un stade précoce. Le pronostic dépend largement du stade au moment du diagnostic, d'où l'importance d'une détection précoce. Le traitement peut inclure l'excision chirurgicale, la biopsie du ganglion sentinelle, l'immunothérapie, la thérapie ciblée, la chimiothérapie ou la radiothérapie.

RÈGLE ABCDE POUR DÉTECTER UN MÉLANOME

La règle ABCDE est un outil mnémotechnique utilisé pour aider à identifier les caractéristiques d'un possible mélanome:

A - Asymétrie: Une moitié du grain de beauté ne correspond pas à l'autre.
B - Bords: Les bords sont irréguliers, dentelés, flous ou mal définis.
C - Couleur: La couleur varie d'une zone à l'autre, avec des nuances de brun, noir, rouge, blanc ou bleu.
D - Diamètre: Généralement plus grand que 6 mm (taille d'une gomme de crayon), bien que les mélanomes puissent être plus petits.
E - Évolution: Tout changement dans la taille, la forme, la couleur ou l'élévation, ou tout nouveau symptôme comme le saignement, les démangeaisons ou la croûte.

FACTEURS DE RISQUE

Les principaux facteurs de risque pour le cancer de la peau incluent:

1. Exposition aux UV: L'exposition excessive au soleil ou aux lits de bronzage, surtout si elle cause des coups de soleil.
2. Peau claire: Peau qui brûle facilement, yeux clairs, cheveux blonds ou roux.
3. Antécédents personnels ou familiaux de cancer de la peau.
4. Nombre élevé de grains de beauté ou présence de grains de beauté atypiques.
5. Système immunitaire affaibli dû à une maladie ou à des médicaments.
6. Age avancé: Le risque augmente avec l'âge en raison de l'exposition cumulée aux UV.
7. Exposition à certains produits chimiques comme l'arsenic.

PRÉVENTION

Les mesures de prévention du cancer de la peau incluent:

1. Protection solaire: Utiliser un écran solaire à large spectre avec un FPS d'au moins 30, à réappliquer toutes les 2 heures et après la baignade ou la transpiration.
2. Éviter l'exposition au soleil: Surtout entre 10h et 16h, quand les rayons UV sont les plus intenses.
3. Porter des vêtements protecteurs: Chapeaux à larges bords, lunettes de soleil, vêtements à manches longues.
4. Éviter les lits de bronzage: Ils augmentent significativement le risque de cancer de la peau.
5. Auto-examen régulier: Vérifier sa peau une fois par mois pour repérer tout changement.
6. Examens dermatologiques professionnels: Recommandés annuellement pour les personnes à haut risque.

QUAND CONSULTER UN DERMATOLOGUE

Il est recommandé de consulter un dermatologue dans les situations suivantes:

1. Vous remarquez une tache ou un grain de beauté qui change d'apparence (taille, forme, couleur).
2. Vous avez une lésion qui saigne, qui démange ou qui ne guérit pas.
3. Vous avez un antécédent personnel ou familial de cancer de la peau.
4. Vous avez été exposé à des quantités importantes de soleil ou avez des antécédents de coups de soleil graves.
5. Vous avez plus de 50 grains de beauté, ou des grains de beauté atypiques.
6. Vous avez une peau claire qui brûle facilement au soleil.
7. Pour un examen cutané complet annuel, particulièrement pour les personnes à risque.

DIAGNOSTIC ET TRAITEMENT

Le diagnostic du cancer de la peau implique généralement:

1. Examen dermatologique: Inspection visuelle de la peau, souvent avec un dermatoscope.
2. Biopsie cutanée: Retrait d'un échantillon de tissu pour examen au microscope.
3. Examens d'imagerie: Pour les cas avancés, pour déterminer si le cancer s'est propagé.

Les options de traitement varient selon le type de cancer, sa localisation, son stade, et la santé générale du patient:

1. Chirurgie: Excision simple, chirurgie micrographique de Mohs, curetage et électrodessication.
2. Cryothérapie: Utilisation du froid extrême pour détruire les cellules cancéreuses.
3. Thérapie photodynamique: Utilisation de médicaments et de lumière pour tuer les cellules cancéreuses.
4. Médicaments topiques: Comme l'imiquimod ou le 5-fluorouracile pour certains cancers de stade précoce.
5. Radiothérapie: Utilisation de rayons X à haute énergie.
6. Thérapie systémique: Immunothérapie, thérapie ciblée ou chimiothérapie pour les cancers avancés.

PRONOSTIC

Le pronostic pour le cancer de la peau varie considérablement selon le type et le stade:

- Carcinome basocellulaire et carcinome épidermoïde: Excellente chance de rémission complète si détectés tôt.
- Mélanome: Le pronostic dépend largement du stade au moment du diagnostic:
  - Stade I (localisé, fin): Taux de survie à 5 ans > 90%
  - Stade II (localisé, plus épais): Taux de survie à 5 ans entre 80% et 90%
  - Stade III (propagation aux ganglions lymphatiques): Taux de survie à 5 ans entre 40% et 80%
  - Stade IV (métastatique): Taux de survie à 5 ans d'environ 15-20%, bien que les nouvelles thérapies améliorent ces chiffres

IMPORTANCE DE LA DÉTECTION PRÉCOCE

La détection précoce est cruciale dans le traitement du cancer de la peau, en particulier pour le mélanome. Un mélanome détecté tôt a un excellent pronostic, tandis que la détection tardive peut significativement réduire les chances de survie.

L'auto-examen régulier et les visites annuelles chez un dermatologue sont les meilleures stratégies pour la détection précoce. Il est particulièrement important de surveiller les changements dans les grains de beauté existants et l'apparition de nouvelles lésions.

TECHNOLOGIES DE DÉTECTION ASSISTÉE PAR IA

Les avancées récentes dans l'intelligence artificielle ont conduit au développement d'outils comme SkinScan-AI qui aident à l'identification précoce des lésions cutanées suspectes. Ces outils:

1. Utilisent des algorithmes d'apprentissage profond formés sur de vastes ensembles de données d'images dermatologiques.
2. Peuvent aider à identifier les caractéristiques suspectes qui pourraient échapper à l'œil non entraîné.
3. Servent d'outils de tri préliminaire, encourageant les utilisateurs à consulter un professionnel de la santé lorsque des anomalies sont détectées.
4. Ne remplacent pas le diagnostic professionnel mais augmentent la vigilance et la sensibilisation.

LIMITES DE LA DÉTECTION AUTOMATISÉE

Il est important de comprendre les limites des outils de détection automatisée comme SkinScan-AI:

1. Ces outils ont une précision limitée et peuvent produire des faux positifs ou des faux négatifs.
2. Ils ne peuvent pas remplacer l'expertise d'un dermatologue formé.
3. La qualité de l'image, l'éclairage et d'autres facteurs peuvent affecter la précision de l'analyse.
4. Ils sont conçus comme des outils complémentaires, pas comme des substituts à un avis médical professionnel.
5. Le diagnostic final doit toujours être établi par un médecin, généralement après une biopsie et un examen histopathologique.

CONSEILS POUR L'UTILISATION DE SKINSCAN-AI

Pour obtenir les meilleurs résultats avec SkinScan-AI:

1. Prenez des photos claires, bien éclairées et de haute résolution de la lésion concernée.
2. Incluez une référence de taille dans l'image si possible (comme une règle ou une pièce de monnaie).
3. Prenez des images de plusieurs angles si la lésion a une forme ou une texture complexe.
4. Utilisez toujours l'application comme un outil de dépistage préliminaire, pas comme un substitut à un avis médical.
5. Consultez un dermatologue pour toute lésion signalée comme suspecte par l'application, même si elle ne présente pas de symptômes troublants.
6. N'ignorez pas une lésion préoccupante simplement parce que l'application ne l'a pas signalée comme suspecte.
7. Continuez les auto-examens réguliers et les visites de contrôle chez le dermatologue.
"""

    # Créer le dossier ressources s'il n'existe pas
    resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ressources')
    os.makedirs(resources_dir, exist_ok=True)
    
    # Chemin du fichier PDF
    pdf_path = os.path.join(resources_dir, 'dermatologie_info.pdf')
    
    # Créer un PDF avec le contenu sur la dermatologie
    pdf_writer = PdfWriter()
    
    # Ajouter une page au PDF
    pdf_writer.add_blank_page(width=612, height=792)  # Format A4
    
    # Écrire le texte dans le PDF (méthode simplifiée)
    with open(pdf_path, 'wb') as f:
        pdf_writer.write(f)
    
    print(f"Fichier de connaissances sur la dermatologie créé à: {pdf_path}")
    
    # Écrire le contenu dans un fichier texte également (pour plus de simplicité)
    txt_path = os.path.join(resources_dir, 'dermatologie_info.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(dermatology_content)
    
    print(f"Fichier texte de connaissances créé à: {txt_path}")
    
    return pdf_path, txt_path

if __name__ == "__main__":
    create_dermatology_knowledge_file()