"""
Questions du quiz sur les mitochondries et l'optimisation de la performance
Basé sur le transcript vidéo Achzod
"""

QUESTIONS = [
    {
        "id": 1,
        "question": "Que mesure la variabilité de fréquence cardiaque (HRV) ?",
        "options": [
            "La variation temporelle entre chaque battement de cœur en millisecondes",
            "Le nombre de battements par minute",
            "La pression artérielle systolique",
            "Le débit cardiaque total"
        ],
        "correct": 0,
        "explanation": "La HRV mesure la variation temporelle entre chaque battement de cœur en millisecondes. Ce n'est PAS la fréquence cardiaque mais la variation ENTRE les battements."
    },
    {
        "id": 2,
        "question": "Qu'est-ce qui reflète une HRV élevée ?",
        "options": [
            "Un état de stress et dominance sympathique",
            "Une dominance parasympathique et récupération optimale",
            "Un manque d'entraînement",
            "Une déshydratation sévère"
        ],
        "correct": 1,
        "explanation": "Une HRV élevée signifie une dominance parasympathique, indiquant que le corps est dans un état de récupération optimal."
    },
    {
        "id": 3,
        "question": "Combien de jours de repos consécutifs Achzod recommande-t-il en milieu de semaine ?",
        "options": [
            "1 jour",
            "2 jours (mercredi et jeudi typiquement)",
            "3 jours",
            "Aucun, repos uniquement le weekend"
        ],
        "correct": 1,
        "explanation": "Achzod recommande 2 jours de repos consécutifs en milieu de semaine (typiquement mercredi et jeudi) pour une récupération optimale au niveau cellulaire."
    },
    {
        "id": 4,
        "question": "Quel est le 'cycle vicieux' associé au magnésium et au stress ?",
        "options": [
            "Plus on mange, plus on grossit",
            "Le stress augmente le cortisol qui brûle le magnésium, et moins de magnésium augmente le stress",
            "Plus on s'entraîne, plus on a besoin de repos",
            "La caféine réduit l'absorption du magnésium"
        ],
        "correct": 1,
        "explanation": "Le cycle vicieux : le stress produit du cortisol qui brûle du magnésium. Moins de magnésium = plus de cortisol en réponse au stress, créant un cercle vicieux."
    },
    {
        "id": 5,
        "question": "Quelle enzyme nécessite du magnésium pour métaboliser la dopamine et l'œstrogène ?",
        "options": [
            "L'aromatase",
            "La COMT (Catéchol-O-méthyltransférase)",
            "La créatine kinase",
            "La lipase"
        ],
        "correct": 1,
        "explanation": "La COMT (Catéchol-O-méthyltransférase) est une enzyme magnésio-dépendante essentielle pour métaboliser la dopamine et l'œstrogène."
    },
    {
        "id": 6,
        "question": "Que se passe-t-il si la COMT ne fonctionne pas bien le soir ?",
        "options": [
            "On digère mal",
            "On ne peut pas dégrader la dopamine, causant insomnie et pensées en boucle",
            "On prend du poids",
            "On a des crampes musculaires"
        ],
        "correct": 1,
        "explanation": "Sans COMT fonctionnelle, la dopamine ne se dégrade pas le soir, causant un cerveau qui tourne à plein régime, de l'insomnie et des pensées intrusives."
    },
    {
        "id": 7,
        "question": "Quelle est la cascade biochimique du sommeil selon le transcript ?",
        "options": [
            "Dopamine → Sérotonine → Mélatonine",
            "Sérotonine → Mélatonine",
            "Mélatonine → Sérotonine",
            "Cortisol → Mélatonine"
        ],
        "correct": 1,
        "explanation": "La cascade du sommeil : haute sérotonine vous prépare à dormir, puis pendant le sommeil la sérotonine se convertit en mélatonine grâce à l'enzyme AANAT."
    },
    {
        "id": 8,
        "question": "Pourquoi prendre de la mélatonine en supplément peut provoquer des réveils 2-3h après ?",
        "options": [
            "Elle cause des cauchemars",
            "Elle est métabolisée rapidement par le foie et on n'a pas de réserve interne si pas assez de sérotonine",
            "Elle déshydrate",
            "Elle augmente le cortisol"
        ],
        "correct": 1,
        "explanation": "La mélatonine exogène est métabolisée en 2-3h par le foie. Sans réserve interne (qui nécessite de la sérotonine), on se réveille quand elle est éliminée."
    },
    {
        "id": 9,
        "question": "Quelle est la molécule énergétique universelle du corps ?",
        "options": [
            "Le glucose",
            "L'ATP (Adénosine Triphosphate)",
            "La créatine",
            "Le glycogène"
        ],
        "correct": 1,
        "explanation": "L'ATP (adénosine triphosphate) est la monnaie énergétique universelle du corps. Chaque contraction musculaire, pensée et battement de cœur nécessite de l'ATP."
    },
    {
        "id": 10,
        "question": "Quelle enzyme ne peut PAS fonctionner sans magnésium pour produire l'ATP ?",
        "options": [
            "La lipase",
            "L'ATP synthase",
            "L'amylase",
            "La protéase"
        ],
        "correct": 1,
        "explanation": "L'ATP synthase, l'enzyme clé pour fabriquer l'ATP dans les mitochondries, ne peut PAS fonctionner sans magnésium."
    },
    {
        "id": 11,
        "question": "Quel est le dosage de magnésium recommandé pour les athlètes ?",
        "options": [
            "100-200mg par jour",
            "300-400mg par jour (recommandation officielle)",
            "10mg par kg de poids corporel (800mg pour 80kg)",
            "50mg par jour"
        ],
        "correct": 2,
        "explanation": "Pour les athlètes qui s'entraînent intensément, la science suggère environ 10mg par kilogramme de poids corporel, soit 800mg pour quelqu'un de 80kg."
    },
    {
        "id": 12,
        "question": "Quelle forme de magnésium combine magnésium ET effet calmant via GABA ?",
        "options": [
            "Oxyde de magnésium",
            "Citrate de magnésium",
            "Bisglycinate de magnésium",
            "Chlorure de magnésium"
        ],
        "correct": 2,
        "explanation": "Le bisglycinate de magnésium contient de la glycine, un neurotransmetteur inhibiteur qui active les récepteurs GABA et calme le cerveau."
    },
    {
        "id": 13,
        "question": "Quel marqueur sanguin indirect suggère une déficience en magnésium ?",
        "options": [
            "CRP > 5",
            "Phosphatase alcaline (ALP) < 70 U/L",
            "Glucose > 100",
            "Cholestérol > 200"
        ],
        "correct": 1,
        "explanation": "Des études montrent que si la phosphatase alcaline (ALP) est inférieure à 70 U/L, on est probablement déficient en magnésium."
    },
    {
        "id": 14,
        "question": "Qu'est-ce que la GH (Growth Hormone) ?",
        "options": [
            "Une vitamine",
            "L'hormone anabolique ultime produite par l'hypophyse",
            "Un peptide digestif",
            "Un neurotransmetteur"
        ],
        "correct": 1,
        "explanation": "La GH (Growth Hormone) est l'hormone anabolique ultime produite par la glande hypophysaire qui régule croissance musculaire, lipolyse, récupération, etc."
    },
    {
        "id": 15,
        "question": "Quand la GH naturelle est-elle principalement sécrétée ?",
        "options": [
            "Le matin au réveil",
            "Pendant le sommeil profond (22h-2h du matin)",
            "Après les repas",
            "Pendant l'entraînement"
        ],
        "correct": 1,
        "explanation": "La GH est naturellement sécrétée en pulses principalement pendant le sommeil profond, entre 22h et 2h du matin environ."
    },
    {
        "id": 16,
        "question": "Quelle est la différence entre GHRP et GHRH ?",
        "options": [
            "Ce sont la même chose",
            "GHRP active directement la pituitaire (via ghréline), GHRH stimule l'hypothalamus",
            "GHRP est pour les femmes, GHRH pour les hommes",
            "GHRP brûle les graisses, GHRH construit le muscle"
        ],
        "correct": 1,
        "explanation": "Les GHRP imitent la ghréline et activent directement la pituitaire. Les GHRH stimulent l'hypothalamus qui ensuite dit à la pituitaire de libérer de la GH."
    },
    {
        "id": 17,
        "question": "Quel GHRP est le plus apprécié car il ne stimule presque pas la prolactine ?",
        "options": [
            "Hexaréline",
            "Semaréline (GHRP-2)",
            "Ipamoréline",
            "GHRP-6"
        ],
        "correct": 2,
        "explanation": "L'Ipamoréline est le GHRP le plus apprécié car il a très peu d'effets secondaires et ne stimule presque pas la prolactine."
    },
    {
        "id": 18,
        "question": "Pourquoi injecter les sécrétogènes dans un état de jeûne ?",
        "options": [
            "Pour éviter les nausées",
            "Parce que l'insuline bloque la GH",
            "Pour mieux absorber",
            "C'est un mythe, on peut les prendre après manger"
        ],
        "correct": 1,
        "explanation": "L'insuline et la GH sont antagonistes. Si vous avez de l'insuline circulante après un repas, la GH ne sera pas libérée. Il faut donc être à jeun."
    },
    {
        "id": 19,
        "question": "Quelle est la stack recommandée par Achzod pour les sécrétogènes ?",
        "options": [
            "100mcg Ipamoréline + 200mcg CJC",
            "125mcg Ipamoréline + 100mcg CJC-1295 sans DAC",
            "200mcg Hexaréline seul",
            "50mcg de chaque"
        ],
        "correct": 1,
        "explanation": "La stack préférée d'Achzod : 125 microgrammes d'Ipamoréline + 100 microgrammes de CJC-1295 sans DAC, injecté à jeun."
    },
    {
        "id": 20,
        "question": "Quel est le timing optimal pour injecter la GH exogène ?",
        "options": [
            "Le matin avant le cardio",
            "Juste avant le coucher pour synchroniser avec le pic naturel",
            "Après l'entraînement",
            "Pendant le repas"
        ],
        "correct": 1,
        "explanation": "La GH exogène devrait être injectée juste avant le coucher. Elle atteint son pic 2-3h après, coïncidant avec le pic naturel pour un effet synergique."
    },
    {
        "id": 21,
        "question": "Qu'est-ce que MOTS-c ?",
        "options": [
            "Un antioxydant",
            "Un peptide mitochondrial qui stimule la biogenèse mitochondriale",
            "Un supplément de magnésium",
            "Une forme de créatine"
        ],
        "correct": 1,
        "explanation": "MOTS-c est un peptide dérivé de l'ARN mitochondrial qui signale aux cellules de fabriquer plus de mitochondries (biogenèse mitochondriale)."
    },
    {
        "id": 22,
        "question": "Quelle est la différence entre glycolyse anaérobie et phosphorylation oxydative ?",
        "options": [
            "La glycolyse produit 1-2 ATP, la phosphorylation oxydative produit 30-35 ATP par glucose",
            "C'est la même chose",
            "La glycolyse est plus efficace",
            "La phosphorylation ne nécessite pas d'oxygène"
        ],
        "correct": 0,
        "explanation": "La glycolyse anaérobie produit 1-2 ATP par glucose (inefficace), tandis que la phosphorylation oxydative dans les mitochondries produit 30-35 ATP (15-17x plus efficace)."
    },
    {
        "id": 23,
        "question": "Qu'est-ce que le bleu de méthylène fait au niveau mitochondrial ?",
        "options": [
            "Il colore les cellules en bleu",
            "Il accepte des électrons et court-circuite la chaîne de transport, réduisant les fuites de radicaux libres",
            "Il détruit les mitochondries",
            "Il remplace l'oxygène"
        ],
        "correct": 1,
        "explanation": "Le bleu de méthylène est un accepteur d'électrons qui court-circuite certaines étapes de la chaîne de transport, résultant en moins de fuites de ROS et plus d'efficacité."
    },
    {
        "id": 24,
        "question": "Quel est le dosage recommandé de bleu de méthylène ?",
        "options": [
            "100-200mg/jour",
            "1-3mg/jour",
            "5-15mg/jour",
            "50mg/jour"
        ],
        "correct": 2,
        "explanation": "Le dosage recommandé de bleu de méthylène est de 5-15mg par jour, typiquement 10mg dans un verre d'eau."
    },
    {
        "id": 25,
        "question": "Pourquoi ne devrait-on JAMAIS combiner bleu de méthylène avec des ISRS ?",
        "options": [
            "Ça annule l'effet",
            "Risque de syndrome sérotoninergique (trop de sérotonine)",
            "Ça cause des nausées",
            "C'est un mythe, on peut les combiner"
        ],
        "correct": 1,
        "explanation": "Le bleu de méthylène inhibe la MAO, augmentant la sérotonine. Combiné avec des ISRS, cela crée un risque de syndrome sérotoninergique dangereux."
    },
    {
        "id": 26,
        "question": "Qu'est-ce que le glutathion ?",
        "options": [
            "Un acide gras",
            "L'antioxydant maître, un tripeptide (glutamate + cystéine + glycine)",
            "Une protéine musculaire",
            "Un neurotransmetteur"
        ],
        "correct": 1,
        "explanation": "Le glutathion est l'antioxydant maître du corps, un tripeptide composé de glutamate, cystéine et glycine, présent dans chaque cellule."
    },
    {
        "id": 27,
        "question": "Quelle est la forme de glutathion recommandée pour une meilleure absorption ?",
        "options": [
            "Glutathion standard oral",
            "Glutathion liposomal (500-1000mg/jour)",
            "Glutathion en poudre",
            "Glutathion synthétique"
        ],
        "correct": 1,
        "explanation": "Le glutathion liposomal (500-1000mg/jour) est recommandé car encapsulé dans des liposomes qui protègent le glutathion et améliorent l'absorption."
    },
    {
        "id": 28,
        "question": "Quel est le rôle du NAC (N-acétylcystéine) ?",
        "options": [
            "C'est un stimulant",
            "C'est un précurseur du glutathion (1200-1800mg/jour recommandé)",
            "C'est une vitamine",
            "C'est un minéral"
        ],
        "correct": 1,
        "explanation": "Le NAC fournit de la cystéine, l'acide aminé limitant pour la synthèse de glutathion. Plus de cystéine = plus de glutathion. Dosage : 1200-1800mg/jour."
    },
    {
        "id": 29,
        "question": "Qu'est-ce que NRF2 et pourquoi est-il important ?",
        "options": [
            "Un peptide",
            "Un facteur de transcription qui active la production d'enzymes antioxydantes endogènes",
            "Un neurotransmetteur",
            "Une hormone"
        ],
        "correct": 1,
        "explanation": "NRF2 est un facteur de transcription. Quand activé, il augmente la production d'enzymes antioxydantes (glutathion peroxydase, SOD, catalase)."
    },
    {
        "id": 30,
        "question": "Quels sont les agonistes GLP mentionnés dans le transcript ?",
        "options": [
            "Semaglutide (Ozempic), Liraglutide, Tirzepatide (Mounjaro)",
            "Metformine et insuline",
            "Testostérone et trenbolone",
            "Créatine et bêta-alanine"
        ],
        "correct": 0,
        "explanation": "Les agonistes GLP-1 incluent Semaglutide (Ozempic/Wegovy), Liraglutide (Victoza/Saxenda) et l'agoniste double Tirzepatide (Mounjaro/Zepbound)."
    },
    {
        "id": 31,
        "question": "Qu'est-ce qu'un agoniste double comme le Tirzepatide ?",
        "options": [
            "Il cible deux muscles",
            "Il active GLP-1 + GIP (meilleure perte de poids 20-25%)",
            "Il dure deux fois plus longtemps",
            "Il coûte deux fois moins cher"
        ],
        "correct": 1,
        "explanation": "Le Tirzepatide est un agoniste double GLP-1 + GIP, offrant de meilleurs résultats que GLP-1 seul (perte de poids de 20-25%, meilleure sensibilité insuline)."
    },
    {
        "id": 32,
        "question": "Quelle est l'erreur #1 mentionnée dans le transcript ?",
        "options": [
            "S'entraîner trop dur",
            "Sauter les bases (sommeil, magnésium, antioxydants, nutrition)",
            "Manger trop de glucides",
            "Ne pas faire de cardio"
        ],
        "correct": 1,
        "explanation": "L'erreur #1 est de vouloir commencer directement avec des peptides avancés sans optimiser les bases : sommeil, magnésium, antioxydants, nutrition."
    },
    {
        "id": 33,
        "question": "Pourquoi les analyses sanguines régulières sont-elles cruciales ?",
        "options": [
            "Pour impressionner son médecin",
            "On ne SENT pas une fonction hépatique dégradée, cholestérol élevé, ou inflammation avant que ce soit grave",
            "C'est uniquement pour les bodybuilders",
            "Ce n'est pas vraiment nécessaire"
        ],
        "correct": 1,
        "explanation": "Les analyses sanguines sont cruciales car on ne sent pas une fonction hépatique dégradée, un cholestérol à 300, ou une CRP élevée jusqu'à ce que ce soit grave."
    },
    {
        "id": 34,
        "question": "Combien de temps faut-il pour voir les effets de la biogenèse mitochondriale ?",
        "options": [
            "24-48 heures",
            "Quelques jours",
            "Des semaines (activation gènes → ARN → protéines → assemblage)",
            "Plusieurs années"
        ],
        "correct": 2,
        "explanation": "La biogenèse mitochondriale prend des semaines car les cellules doivent activer les gènes, transcrire l'ARN, traduire les protéines et assembler les mitochondries."
    },
    {
        "id": 35,
        "question": "Selon Achzod, à quoi ressembleront les preps dans 10 ans grâce aux avancées ?",
        "options": [
            "Plus de cardio, moins de calories",
            "4000-5000 calories, zéro cardio, juste de la musculation, déchiquetés sur scène",
            "Même approche qu'aujourd'hui",
            "Régimes plus restrictifs"
        ],
        "correct": 1,
        "explanation": "Dans 10 ans, grâce aux mitochondries optimisées et agonistes multi-récepteurs, les athlètes mangeront 4000-5000 calories, zéro cardio, juste musculation, et seront déchiquetés."
    }
]

def get_all_questions():
    """Retourne toutes les questions"""
    return QUESTIONS

def get_question_by_id(question_id):
    """Retourne une question spécifique par son ID"""
    for q in QUESTIONS:
        if q["id"] == question_id:
            return q
    return None
