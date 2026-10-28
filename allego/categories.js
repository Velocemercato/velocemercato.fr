/* Allego — registre des catégories.
   Ajouter une catégorie = ajouter un objet à ce tableau : champs, sources,
   détecteurs, checklist et limites. Le moteur (app.js) est générique.
   niveau : 'complet' = parcours complet ; 'partiel' = contrôles génériques seulement. */
(function () {
  'use strict';

  // Libellés des sources d'information comparées entre elles.
  const SOURCES = {
    produit: 'Produit (gravure, sous le couvercle)',
    boite: 'Étiquette de la boîte',
    reglages: 'Affiché par l’appareil (Réglages, *#06#)',
    etiquette_g: 'Étiquette intérieure – chaussure gauche',
    etiquette_d: 'Étiquette intérieure – chaussure droite',
    annonce: 'Annonce du vendeur',
    facture: 'Facture / preuve d’achat'
  };

  /* Table locale des numéros de modèle AirPods, relevée d'après la page Apple
     « Identifier vos AirPods ». Peut être incomplète : à revérifier sur la page Apple. */
  const AIRPODS = [
    {id: 'ap4anc', name: 'AirPods 4 avec réduction active du bruit', buds: ['A3055', 'A3056', 'A3057'], cases: ['A3059'], re: /airpods\s*4\b.*(anc|r[ée]duction|bruit)/i},
    {id: 'ap4', name: 'AirPods 4', buds: ['A3050', 'A3053', 'A3054'], cases: ['A3058'], re: /airpods\s*4\b/i},
    {id: 'pro3', name: 'AirPods Pro 3', buds: [], cases: [], re: /pro\s*3\b|pro\s*\(?3e/i},
    {id: 'pro2', name: 'AirPods Pro (2e génération)', buds: ['A2698', 'A2699', 'A2931', 'A3047', 'A3048', 'A3049'], cases: ['A2700', 'A2968'], re: /pro\s*(2|ii)\b|pro\s*\(?2e|pro.*deuxi/i},
    {id: 'pro1', name: 'AirPods Pro (1re génération)', buds: ['A2083', 'A2084'], cases: ['A2190'], re: /airpods\s*pro\b/i},
    {id: 'max', name: 'AirPods Max', buds: ['A2096', 'A3184'], cases: [], re: /airpods\s*max/i},
    {id: 'ap3', name: 'AirPods (3e génération)', buds: ['A2564', 'A2565'], cases: ['A2566', 'A2897'], re: /airpods\s*(3\b|\(?3e|troisi)/i},
    {id: 'ap2', name: 'AirPods (2e génération)', buds: ['A2031', 'A2032'], cases: ['A1602', 'A1938'], re: /airpods\s*(2\b|\(?2e|deuxi)/i},
    {id: 'ap1', name: 'AirPods (1re génération)', buds: ['A1523', 'A1722'], cases: ['A1602'], re: /airpods\s*(1\b|\(?1re|premi)/i}
  ];

  // Identifie les générations compatibles avec un texte ou un numéro A….
  function airpodsFamilies(text) {
    if (!text) return [];
    const t = String(text);
    const nums = t.toUpperCase().match(/\bA\d{4}\b/g) || [];
    const byNum = new Set();
    nums.forEach(n => AIRPODS.forEach(f => { if (f.buds.includes(n) || f.cases.includes(n)) byNum.add(f.id); }));
    if (byNum.size) return [...byNum];
    const named = AIRPODS.find(f => f.re.test(t));
    return named ? [named.id] : [];
  }

  function phoneModel(text) {
    if (!text) return [];
    const t = String(text).toLowerCase();
    let m = t.match(/iphone\s*(\d{1,2}e?|se|x[rs]?)\s*(pro\s*max|pro|plus|mini|air)?/);
    if (m) return ['iPhone ' + (/^\d+e$/.test(m[1]) ? m[1] : m[1].toUpperCase()) + (m[2] ? ' ' + m[2].replace(/\s+/, ' ').replace(/\b\w/g, c => c.toUpperCase()) : '')];
    m = t.match(/galaxy\s*([a-z]\d{1,3}\s*(?:ultra|plus|\+|fe)?)/);
    if (m) return ['Galaxy ' + m[1].toUpperCase().replace(/\s+/g, ' ')];
    m = t.match(/pixel\s*(\d+\s*(?:pro\s*xl|pro|a)?)/);
    if (m) return ['Pixel ' + m[1].replace(/\s+/g, ' ')];
    return [];
  }

  // Questions communes : la réponse « bonne » est good ; un écart produit le constat.
  const Q = (id, section, q, opts) => Object.assign({id, section, q, good: 'oui', weak: false}, opts);

  const commonDocs = prefix => [
    Q(prefix + '_facture', 'provenance', 'Le vendeur présente une facture ou une preuve d’achat.', {
      role: 'facture',
      bad: 'Aucun document d’achat présenté.',
      why: 'Sans document, l’origine de l’objet repose uniquement sur la parole du vendeur. Ce n’est pas un indice de vol : beaucoup de particuliers n’ont plus leur facture.',
      next: 'Demandez une capture de la commande en ligne, un relevé ou tout autre justificatif. Vérifiez qu’il mentionne l’objet.'
    }),
    Q(prefix + '_facture_detail', 'provenance', 'Le document mentionne l’enseigne, la date et le modèle, et son identifiant (s’il y en a un) correspond à l’objet.', {
      role: 'facture_ok',
      bad: 'Le document ne permet pas de rattacher l’achat à cet exemplaire.',
      why: 'Une facture sans identifiant ou avec un identifiant différent peut concerner un autre exemplaire.',
      next: 'Demandez au vendeur d’expliquer la différence ; seule l’enseigne émettrice peut confirmer une facture.'
    }),
    Q(prefix + '_facture_nom', 'provenance', 'Le nom sur le document correspond au vendeur, ou il explique simplement la différence (cadeau, achat d’occasion…).', {
      weak: true,
      bad: 'Le nom sur le document ne correspond pas et aucune explication n’est donnée.',
      why: 'Un nom différent a souvent une explication banale ; c’est un point à clarifier, pas une accusation.',
      next: 'Posez la question simplement : « La facture est à un autre nom, comment l’avez-vous obtenu ? »'
    })
  ];

  const CATEGORIES = [
    {
      id: 'airpods', label: 'AirPods', icon: '🎧', group: 'Écouteurs, consoles et électronique', niveau: 'complet',
      keywords: /airpods|\bA(15|17|19|20|21|25|26|28|29|30|31)\d{2}\b/i,
      sources: ['produit', 'boite', 'reglages', 'annonce', 'facture'],
      fields: [
        {key: 'modele', label: 'Modèle (nom ou numéro A…)', kind: 'modele', hint: 'Ex. « AirPods Pro 2 » ou A2968', in: ['boite', 'reglages', 'annonce', 'facture']},
        {key: 'boitier', label: 'Numéro de modèle du boîtier', kind: 'anum', hint: 'Gravé sous le couvercle : A suivi de 4 chiffres', in: ['produit']},
        {key: 'ecouteurs', label: 'Numéros des écouteurs (gauche, droit)', kind: 'anum', hint: 'Gravés sur chaque écouteur, ex. A3047 A3048', in: ['produit']},
        {key: 'serie', label: 'Numéro de série', kind: 'serial', hint: '10 ou 12 caractères, sous le couvercle du boîtier', in: ['produit', 'boite', 'reglages', 'facture', 'annonce']},
        {key: 'reference', label: 'Référence Apple', kind: 'text', hint: 'Ex. MTJV3ZM/A, sur la boîte ou la facture', in: ['boite', 'facture']},
        {key: 'ean', label: 'Code-barres (EAN/UPC)', kind: 'gtin', hint: '12 ou 13 chiffres', in: ['boite']}
      ],
      family: airpodsFamilies,
      familyName: id => (AIRPODS.find(f => f.id === id) || {}).name || id,
      serialLengths: [10, 12],
      photoGuide: ['Intérieur du couvercle du boîtier (numéro de série)', 'Les deux écouteurs (numéros A…)', 'Étiquette de la boîte', 'Facture', 'Écran Réglages > Bluetooth > (i)', 'Capture de l’annonce'],
      official: {
        label: 'Vérifier la couverture sur le site d’Apple',
        url: 'https://checkcoverage.apple.com/',
        note: 'Allego n’interroge pas Apple. Copiez le numéro de série, consultez la page officielle, puis indiquez ci-dessous ce qu’elle affiche.'
      },
      links: [{label: 'Assistance Apple pour les AirPods', url: 'https://support.apple.com/fr-fr/airpods'}],
      checklist: [
        Q('a_reglages', 'contrefacon', 'Une fois les AirPods connectés à VOTRE téléphone, Réglages > Bluetooth > (i) affiche le même numéro de série que le boîtier.', {
          bad: 'Le numéro affiché par le téléphone diffère de celui du boîtier, ou n’apparaît pas.',
          why: 'Les copies affichent souvent un numéro absent ou générique. Un écouteur remplacé par Apple peut aussi expliquer un écart.',
          next: 'Comparez avec la boîte et la facture ; demandez si un élément a été remplacé et s’il y a un justificatif.'
        }),
        Q('a_modele_reglages', 'contrefacon', 'Le modèle affiché dans les réglages correspond à celui de l’annonce.', {
          bad: 'Le modèle affiché par le téléphone ne correspond pas à l’annonce.',
          why: 'Le vendeur a pu se tromper de génération, mais l’écart peut aussi signaler une copie.',
          next: 'Ajustez le prix au modèle réel ou renoncez si l’écart n’est pas expliqué.'
        }),
        Q('a_firmware', 'contrefacon', 'Une version de firmware s’affiche dans les réglages (i).', {
          bad: 'Aucune version de firmware n’est affichée.',
          why: 'Les AirPods d’origine affichent une version ; son absence est fréquente sur les copies.',
          next: 'Laissez les AirPods connectés quelques minutes puis revérifiez.'
        }),
        Q('a_ouverture', 'contrefacon', 'À l’ouverture du boîtier près d’un iPhone, la fenêtre de connexion affiche le bon modèle.', {
          weak: true,
          bad: 'La fenêtre de connexion n’apparaît pas ou affiche un autre modèle.',
          why: 'Indice faible : de nombreuses copies imitent cette fenêtre, et son absence peut venir du téléphone.',
          next: 'Faites le jumelage complet et vérifiez les réglages.'
        }),
        Q('a_jumelage', 'contrefacon', 'Le jumelage avec votre téléphone fonctionne et le son sort des deux écouteurs.', {
          bad: 'Le jumelage échoue ou un écouteur ne fonctionne pas.',
          why: 'Panne, écouteur incompatible ou copie : dans tous les cas, l’objet n’est pas conforme à l’annonce.',
          next: 'Ne payez pas avant un jumelage fonctionnel.'
        }),
        Q('a_fonctions', 'contrefacon', 'Les fonctions annoncées marchent : réduction de bruit, mode Transparence, détection d’oreille.', {
          bad: 'Une fonction annoncée ne marche pas.',
          why: 'Les copies imitent mal certaines fonctions ; une panne réelle est aussi possible.',
          next: 'Testez chaque fonction dans les réglages, oreillettes en place.'
        }),
        Q('a_finition', 'contrefacon', 'Gravures nettes, charnière ferme, aimants et voyant sans défaut visible.', {
          weak: true,
          bad: 'Finitions ou gravures douteuses.',
          why: 'Indice faible : l’usure normale peut aussi abîmer les finitions, et les bonnes copies sont soignées.',
          next: 'Comparez avec les photos officielles d’Apple.'
        }),
        Q('a_boite_produit', 'coherence', 'Le numéro de série de la boîte est le même que celui sous le couvercle.', {
          bad: 'La boîte et le boîtier portent des numéros différents.',
          why: 'Situation fréquente après un échange en garantie ou avec une boîte d’un autre exemplaire. Ce n’est pas une preuve de copie ni de vol.',
          next: 'Demandez l’explication et, si possible, le document d’échange Apple.'
        }),
        Q('a_compte', 'vol', 'Les AirPods sont encore associés à un autre compte Apple (message « non associés à votre compte », ou visibles dans Localiser du vendeur).', {
          good: 'non', isAccount: true,
          bad: 'Les AirPods semblent encore associés au compte Apple d’une autre personne.',
          why: 'Cela ne prouve pas un vol : beaucoup de vendeurs oublient de les retirer de leur compte. En revanche, vous ne pourrez pas les utiliser pleinement tant qu’ils restent associés.',
          next: 'Demandez au vendeur de les retirer de son compte devant vous : app Localiser > Appareils > les AirPods > Supprimer cet appareil.'
        })
      ].concat(commonDocs('a')),
      unavailable: [
        'Interrogation automatique d’Apple : impossible sans partenariat ; vous consultez vous-même la page officielle.',
        'Registre de vol : aucun registre public et fiable n’est accessible pour les AirPods.',
        'Lecture du numéro de série par Bluetooth : impossible depuis un site web.'
      ],
      expert: null
    },
    {
      id: 'telephone', label: 'Téléphone', icon: '📱', group: 'Téléphones, tablettes et ordinateurs', niveau: 'complet',
      keywords: /iphone|galaxy|pixel|xiaomi|redmi|oneplus|imei|smartphone/i,
      sources: ['boite', 'reglages', 'annonce', 'facture'],
      fields: [
        {key: 'modele', label: 'Modèle', kind: 'modele', hint: 'Ex. iPhone 13, Galaxy S23', in: ['boite', 'reglages', 'annonce', 'facture']},
        {key: 'capacite', label: 'Capacité', kind: 'text', hint: 'Ex. 128 Go', in: ['boite', 'reglages', 'annonce', 'facture']},
        {key: 'imei', label: 'IMEI', kind: 'imei', hint: '15 chiffres ; composez *#06# sur le téléphone', in: ['boite', 'reglages', 'facture', 'annonce']},
        {key: 'serie', label: 'Numéro de série', kind: 'serial', hint: 'Réglages > Général > Informations', in: ['boite', 'reglages', 'facture']},
        {key: 'ean', label: 'Code-barres (EAN/UPC)', kind: 'gtin', hint: '12 ou 13 chiffres', in: ['boite']}
      ],
      family: phoneModel,
      familyName: x => x,
      serialLengths: null,
      photoGuide: ['Écran après avoir composé *#06#', 'Étiquette de la boîte', 'Réglages > Général > Informations', 'Facture', 'Capture de l’annonce'],
      official: {
        label: 'iPhone : vérifier la couverture sur le site d’Apple',
        url: 'https://checkcoverage.apple.com/',
        note: 'Uniquement pour un iPhone. Allego n’interroge pas Apple : consultez la page et indiquez ci-dessous ce qu’elle affiche. Pour les autres marques, utilisez le site d’assistance du fabricant.'
      },
      links: [],
      checklist: [
        Q('p_imei', 'coherence', 'Le code *#06# affiche le même IMEI que la boîte et la facture.', {
          bad: 'L’IMEI affiché par le téléphone diffère de la boîte ou de la facture.',
          why: 'La boîte ou la facture peuvent appartenir à un autre téléphone (échange, boîte récupérée). L’écart empêche de rattacher les documents à cet exemplaire.',
          next: 'Demandez l’explication ; considérez les documents comme non rattachés à ce téléphone.'
        }),
        Q('p_compte', 'vol', 'Le verrouillage de compte est levé : iPhone, Localiser désactivé ; Android, compte Google retiré. Une réinitialisation faite devant vous ne demande aucun ancien compte.', {
          bad: 'Le téléphone reste lié au compte d’une autre personne.',
          why: 'Cela ne prouve pas un vol (oubli fréquent), mais un téléphone verrouillé sera inutilisable pour vous.',
          next: 'Ne payez pas avant que le vendeur ait retiré son compte et réinitialisé le téléphone devant vous.',
          blocking: true
        }),
        Q('p_mdm', 'provenance', 'Aucun profil de gestion n’est installé (iPhone : Réglages > Général > VPN et gestion de l’appareil).', {
          bad: 'Un profil de gestion d’entreprise ou d’école est présent.',
          why: 'Le téléphone peut appartenir à une organisation qui garde la main dessus. Ce n’est pas une preuve de vol.',
          next: 'Demandez une attestation de cession de l’organisation, ou renoncez.'
        }),
        Q('p_sim', 'coherence', 'Une carte SIM d’un autre opérateur fonctionne (pas de blocage opérateur).', {
          bad: 'Le téléphone refuse une autre carte SIM.',
          why: 'Blocage opérateur ou IMEI bloqué : seul l’opérateur peut le dire.',
          next: 'Demandez au vendeur de contacter son opérateur avant la vente.'
        }),
        Q('p_pieces', 'contrefacon', 'iPhone : Réglages > Général > Informations ne signale pas de pièce inconnue.', {
          bad: 'Le téléphone signale une pièce inconnue ou non d’origine.',
          why: 'Réparation avec des pièces non officielles : ce n’est pas une contrefaçon du téléphone, mais une information à connaître avant d’acheter.',
          next: 'Demandez quelle réparation a été faite et ajustez le prix.'
        }),
        Q('p_fonctions', 'contrefacon', 'Écran tactile, Face ID ou Touch ID, caméras, haut-parleurs et charge testés.', {
          bad: 'Une fonction ne marche pas.',
          why: 'Panne ou pièce remplacée : l’état réel ne correspond pas à l’annonce.',
          next: 'Ne payez pas avant d’avoir testé chaque fonction.'
        }),
        Q('p_batterie', 'contrefacon', 'L’état de la batterie est affiché et cohérent avec l’annonce.', {
          weak: true,
          bad: 'L’état de la batterie est absent ou différent de l’annonce.',
          why: 'Batterie remplacée ou usée : indice faible, mais à prendre en compte dans le prix.',
          next: 'Consultez Réglages > Batterie > État de la batterie.'
        })
      ].concat(commonDocs('p')),
      unavailable: [
        'Identification du modèle par l’IMEI : nécessite la base des codes TAC de la GSMA (accès sous licence).',
        'Consultation des IMEI déclarés volés : base GSMA ou opérateurs, accès réservé aux professionnels sous contrat.',
        'Vérification du verrouillage de compte à distance : aucun accès public chez Apple ni Google.'
      ],
      expert: null
    },
    {
      id: 'baskets', label: 'Baskets', icon: '👟', group: 'Vêtements, baskets et accessoires', niveau: 'complet',
      keywords: /nike|jordan|adidas|yeezy|new\s*balance|asics|dunk|sneaker|basket|\b[A-Z]{2}\d{4}-\d{3}\b/i,
      sources: ['etiquette_g', 'etiquette_d', 'boite', 'annonce', 'facture'],
      fields: [
        {key: 'modele', label: 'Marque et modèle', kind: 'modele', hint: 'Ex. Nike Dunk Low', in: ['boite', 'annonce', 'facture']},
        {key: 'reference', label: 'Référence (style code)', kind: 'style', hint: 'Ex. DD1391-100 (Nike), GZ5922 (Adidas)', in: ['etiquette_g', 'etiquette_d', 'boite', 'annonce', 'facture']},
        {key: 'taille', label: 'Taille', kind: 'size', hint: 'Ex. 42 EU ou US 8.5', in: ['etiquette_g', 'etiquette_d', 'boite', 'annonce', 'facture']},
        {key: 'dates', label: 'Dates de fabrication (étiquette)', kind: 'text', hint: 'Ex. 03/01/22 – 05/02/22', in: ['etiquette_g', 'etiquette_d']},
        {key: 'ean', label: 'Code-barres (EAN/UPC)', kind: 'gtin', hint: '12 ou 13 chiffres', in: ['boite']}
      ],
      family: text => {
        const m = String(text || '').match(/nike|jordan|adidas|yeezy|new\s*balance|asics|puma|vans|converse/i);
        return m ? [m[0].toLowerCase().replace(/\s+/g, ' ')] : [];
      },
      familyName: x => x.replace(/\b\w/g, c => c.toUpperCase()),
      serialLengths: null,
      photoGuide: ['Étiquette intérieure gauche', 'Étiquette intérieure droite', 'Étiquette de la boîte', 'Semelle extérieure', 'Talon et coutures arrière', 'Logo latéral de près', 'Semelle intérieure', 'Capture de l’annonce'],
      official: null,
      links: [],
      checklist: [
        Q('b_lr', 'coherence', 'Les étiquettes intérieures gauche et droite portent la même référence et la même taille.', {
          bad: 'Les deux chaussures n’ont pas la même référence ou la même taille.',
          why: 'Deux chaussures d’origines différentes, ou une paire reconstituée : à éclaircir avant d’acheter.',
          next: 'Demandez l’explication et comparez les deux étiquettes côte à côte.'
        }),
        Q('b_boite', 'coherence', 'L’étiquette de la boîte correspond aux étiquettes intérieures (référence, taille, coloris).', {
          bad: 'L’étiquette de la boîte ne correspond pas aux chaussures.',
          why: 'Une boîte d’une autre paire est courante sur le marché de l’occasion ; ce n’est pas une preuve de copie, mais la boîte ne prouve rien sur ces chaussures.',
          next: 'Basez-vous uniquement sur les étiquettes intérieures.'
        }),
        Q('b_details', 'contrefacon', 'Les détails propres au modèle (logo, couture du talon, semelle, forme) correspondent à des photos de référence fiables, comme le site de la marque.', {
          bad: 'Des détails diffèrent des photos de référence.',
          why: 'Les copies se trahissent souvent sur des détails précis du modèle. L’usure ou une variante de production peuvent aussi expliquer un écart.',
          next: 'Pour une paire de valeur, demandez une authentification par un service spécialisé.'
        }),
        Q('b_dates', 'contrefacon', 'Les dates de fabrication de l’étiquette sont antérieures à la sortie du modèle et plausibles.', {
          weak: true,
          bad: 'Les dates de fabrication paraissent incohérentes avec la sortie du modèle.',
          why: 'Indice faible : à vérifier avec la date de sortie officielle du coloris.',
          next: 'Recherchez la date de sortie de la référence exacte.'
        }),
        Q('b_finition', 'contrefacon', 'Coutures régulières, colle propre, logos nets et deux chaussures symétriques.', {
          weak: true,
          bad: 'Finitions irrégulières.',
          why: 'Indice faible : la qualité varie aussi chez les marques, et les bonnes copies sont soignées.',
          next: 'Prenez des photos de près pour comparer ou les montrer à un expert.'
        }),
        Q('b_usure', 'coherence', 'L’usure de la semelle correspond à l’état annoncé.', {
          bad: 'L’usure ne correspond pas à l’état annoncé.',
          why: 'Écart entre l’annonce et l’objet, utile pour négocier.',
          next: 'Ajustez le prix ou renoncez.'
        })
      ].concat(commonDocs('b')),
      unavailable: [
        'Authentification par photo : non proposée ; aucune méthode validée n’est intégrée.',
        'Vérification d’une référence auprès des marques : aucun service public des marques n’est disponible.',
        'Signalement de vol : aucun registre pour les chaussures.'
      ],
      expert: 'Pour une paire chère ou rare, faites appel à un service d’authentification spécialisé avant de payer.'
    }
  ];

  // Catégories prévues : contrôles génériques, limites indiquées honnêtement.
  const generic = (id, label, icon, group, opts) => Object.assign({
    id, label, icon, group, niveau: 'partiel',
    sources: ['produit', 'annonce', 'facture'],
    fields: [
      {key: 'modele', label: 'Marque et modèle', kind: 'modele', hint: '', in: ['produit', 'annonce', 'facture']},
      {key: 'reference', label: 'Référence ou identifiant', kind: 'text', hint: 'Numéro de série, de cadre, référence…', in: ['produit', 'annonce', 'facture']},
      {key: 'ean', label: 'Code-barres (EAN/UPC)', kind: 'gtin', hint: '', in: ['produit']}
    ],
    family: () => [], familyName: x => x, serialLengths: null,
    photoGuide: ['Vue d’ensemble', 'Étiquette ou plaque d’identification', 'Détails et défauts', 'Facture', 'Capture de l’annonce'],
    official: null, links: [], expert: null,
    checklist: [
      Q(id + '_ref', 'coherence', 'La référence ou l’identifiant sur l’objet correspond à l’annonce et au document.', {
        bad: 'La référence de l’objet diffère de l’annonce ou du document.',
        why: 'L’annonce ou le document concernent peut-être un autre exemplaire.',
        next: 'Demandez l’explication avant de payer.'
      }),
      Q(id + '_etat', 'coherence', 'L’état visible correspond à l’annonce.', {
        bad: 'L’état visible diffère de l’annonce.', why: 'Écart utile pour négocier.', next: 'Ajustez le prix ou renoncez.'
      }),
      Q(id + '_fonction', 'contrefacon', 'L’objet fonctionne devant vous (si applicable).', {
        bad: 'L’objet ne fonctionne pas comme annoncé.', why: 'Panne ou non-conformité.', next: 'Ne payez pas avant un essai.'
      })
    ].concat(opts.extra || []).concat(commonDocs(id))
  }, opts);

  CATEGORIES.push(
    generic('ordinateur', 'Tablette ou ordinateur', '💻', 'Téléphones, tablettes et ordinateurs', {
      keywords: /ipad|macbook|imac|laptop|ordinateur|tablette|thinkpad|surface/i,
      extra: [Q('o_compte', 'vol', 'Le compte du vendeur est retiré (Mac/iPad : Localiser désactivé ; PC : compte Microsoft retiré et chiffrement levé).', {
        bad: 'L’appareil reste lié au compte d’une autre personne.', why: 'Ne prouve pas un vol, mais l’appareil peut rester verrouillé.', next: 'Réinitialisation devant vous avant paiement.', blocking: true
      })],
      unavailable: ['Parcours détaillé pas encore écrit : contrôles génériques seulement.', 'Vérification du verrouillage d’activation à distance : aucun accès public.', 'Registre de vol : aucun accès autorisé intégré.']
    }),
    generic('console', 'Console et électronique', '🎮', 'Écouteurs, consoles et électronique', {
      keywords: /playstation|ps5|ps4|xbox|switch|nintendo|console|enceinte|casque/i,
      extra: [Q('c_compte', 'vol', 'Le compte du vendeur est retiré et la console n’est plus « console principale » de son compte.', {
        bad: 'La console reste liée au compte du vendeur.', why: 'Ne prouve pas un vol ; à régler avant la vente.', next: 'Demandez la désactivation devant vous.'
      })],
      unavailable: ['Parcours détaillé pas encore écrit.', 'Statut de bannissement en ligne : non vérifiable sans le fabricant.', 'Registre de vol : aucun accès autorisé intégré.']
    }),
    generic('vetements', 'Vêtements et accessoires', '👕', 'Vêtements, baskets et accessoires', {
      keywords: /veste|manteau|pull|t-shirt|jean|robe|composition|coton|polyester/i,
      extra: [Q('v_etiquettes', 'contrefacon', 'Les étiquettes de marque, de taille et de composition sont présentes et cohérentes entre elles.', {
        bad: 'Étiquettes absentes ou incohérentes.', why: 'Indice à confirmer : une étiquette peut aussi avoir été coupée.', next: 'Comparez avec le site de la marque.'
      })],
      unavailable: ['Parcours détaillé pas encore écrit.', 'Authentification par photo : non proposée.']
    }),
    generic('luxe', 'Sac de luxe', '👜', 'Sacs, montres et bijoux', {
      keywords: /louis\s*vuitton|chanel|herm[eè]s|dior|gucci|prada|sac/i,
      extra: [Q('l_marquages', 'contrefacon', 'Marquages, code de date ou puce, finitions et quincaillerie cohérents avec le modèle.', {
        bad: 'Marquages ou finitions douteux.', why: 'Seul un expert peut trancher sur un article de luxe.', next: 'Faites expertiser avant de payer.'
      })],
      unavailable: ['Authentification : dépend d’un expert ou de la marque.', 'Lecture des puces d’authentification : non intégrée.', 'Registre de vol : aucun accès autorisé intégré.'],
      expert: 'Pour un article de luxe, faites appel à un expert indépendant ou à la marque avant de payer.'
    }),
    generic('montre', 'Montre ou bijou', '⌚', 'Sacs, montres et bijoux', {
      keywords: /rolex|omega|cartier|montre|bijou|bague|collier|or\s*18|poin[cç]on/i,
      extra: [Q('m_papiers', 'provenance', 'Le numéro de la montre ou le poinçon correspond aux papiers et au certificat.', {
        bad: 'Le numéro ou le poinçon ne correspond pas aux papiers.', why: 'Les papiers concernent peut-être un autre objet.', next: 'Faites expertiser avant de payer.'
      })],
      unavailable: ['Authentification : dépend d’un horloger ou d’un bijoutier expert.', 'Registres de montres volées : accès non intégré.'],
      expert: 'Pour une montre ou un bijou de valeur, faites appel à un horloger ou à un bijoutier expert.'
    }),
    generic('velo', 'Vélo ou trottinette', '🚲', 'Vélos, trottinettes, outils et autres objets', {
      keywords: /v[ée]lo|vtt|trottinette|cadre|bicycode|vae/i,
      fields: [
        {key: 'modele', label: 'Marque et modèle', kind: 'modele', hint: '', in: ['produit', 'annonce', 'facture']},
        {key: 'reference', label: 'Numéro de cadre ou identifiant de marquage', kind: 'text', hint: 'Gravé sous le pédalier ou étiquette de marquage', in: ['produit', 'annonce', 'facture']}
      ],
      extra: [Q('v_cadre', 'provenance', 'Le numéro de cadre est lisible, non limé, et le marquage antivol est accompagné de son certificat.', {
        bad: 'Numéro de cadre illisible ou absent, ou pas de certificat de marquage.', why: 'Ne prouve rien seul, mais empêche tout rapprochement.', next: 'Demandez au vendeur de transférer le marquage à votre nom via l’opérateur agréé.'
      })],
      unavailable: ['Consultation du fichier national des cycles identifiés : uniquement via un opérateur de marquage agréé ; non intégrée.', 'Parcours détaillé pas encore écrit.']
    }),
    generic('autre', 'Outil ou autre objet', '🧰', 'Vélos, trottinettes, outils et autres objets', {
      keywords: /perceuse|visseuse|outil|makita|bosch|dewalt/i,
      unavailable: ['Contrôles génériques seulement.', 'Registre de vol : aucun accès autorisé intégré.']
    })
  );

  window.ALLEGO = {SOURCES, CATEGORIES, AIRPODS};
})();
