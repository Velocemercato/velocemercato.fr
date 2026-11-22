// Maquettes de sites VM Studio. Le document utilise les mêmes blocs dans le studio et le salon.
export const DIRECTIONS = {
  manga: { nom: 'Manga original', description: 'Illustré et énergique', c1: '#ff763b', c2: '#ffd26a', fond: '#23203b', texte: '#fff5e8' },
  dimension: { nom: 'Relief', description: 'Profondeur et lumière', c1: '#c1a2ff', c2: '#ffcae9', fond: '#221934', texte: '#fff2ff' },
  editorial: { nom: 'Éditorial', description: 'Chaleureux et soigné', c1: '#8b4535', c2: '#713d31', fond: '#f8f1e5', texte: '#28221f' },
  contraste: { nom: 'Contraste', description: 'Franc et dynamique', c1: '#b6eb88', c2: '#b6eb88', fond: '#151f1d', texte: '#f4f2e8' },
  atelier: { nom: 'Clair', description: 'Lumineux et précis', c1: '#3155a4', c2: '#364f96', fond: '#f1f5fc', texte: '#1e2945' },
};

export const EXEMPLES_SITE = {
  cafe: { style: 'editorial', blocs: [
    { t: 'titre', titre: 'Maison Céleste', sous: 'Café de spécialité et pâtisseries maison.', bouton: 'Découvrir la carte' },
    { t: 'texte', titre: 'Une table, un café', texte: 'Passez pour un espresso rapide ou installez-vous avec une part de gâteau. Chez Céleste, on aime les deux.' },
    { t: 'produits', titre: 'À la carte', items: [{ nom: 'Cafés de spécialité' }, { nom: 'Pâtisseries maison' }, { nom: 'Boissons de saison' }] },
  ] },
  velo: { style: 'contraste', blocs: [
    { t: 'titre', titre: 'En Roue Libre', sous: 'Un atelier de réparation pour retrouver le plaisir de rouler.', bouton: 'Voir les réparations' },
    { t: 'produits', titre: 'À l’atelier', items: [{ nom: 'Révision du vélo' }, { nom: 'Freins et transmission' }, { nom: 'Pneus et crevaisons' }] },
    { t: 'texte', titre: 'Un vélo qui roule bien change tout', texte: 'Qu’il serve tous les jours ou seulement le dimanche, votre vélo mérite des réglages adaptés à votre façon de rouler.' },
  ] },
  interieur: { style: 'atelier', blocs: [
    { t: 'titre', titre: 'Ligne Claire', sous: 'Des intérieurs conçus autour de votre quotidien.', bouton: 'Découvrir l’approche' },
    { t: 'texte', titre: 'Votre manière d’habiter', texte: 'On commence par les pièces que vous utilisez vraiment, la lumière qui y entre et les objets que vous voulez garder.' },
    { t: 'produits', titre: 'Les étapes du projet', items: [{ nom: 'Conseil et conception' }, { nom: 'Matières et couleurs' }, { nom: 'Aménagement intérieur' }] },
  ] },
};

