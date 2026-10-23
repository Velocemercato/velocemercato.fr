// Lieux à visiter par région. Coordonnées approchées, suffisantes pour la météo et l'itinéraire.
window.VM_LIEUX = [
  {region: 'Bourgogne-Franche-Comté', lieux: [
    ['Chapelle Notre-Dame-du-Haut', 'Ronchamp (70)', 47.7045, 6.6206, 'Patrimoine', 'La chapelle de Le Corbusier, classée à l’UNESCO, au-dessus de Ronchamp.'],
    ['Ballon d’Alsace', 'Lepuix (90)', 47.8216, 6.8418, 'Nature', 'Sommet des Vosges du Sud : randonnée, panorama sur les Alpes par temps clair.'],
    ['Citadelle et Lion de Belfort', 'Belfort (90)', 47.6365, 6.8650, 'Patrimoine', 'La forteresse de Vauban et le Lion de Bartholdi qui veille sur la ville.'],
    ['Plateau des Mille Étangs', 'Faucogney (70)', 47.8400, 6.5600, 'Nature', 'Des centaines d’étangs entre forêts et tourbières : balades et pêche.'],
    ['Citadelle de Besançon', 'Besançon (25)', 47.2310, 6.0310, 'Patrimoine', 'Chef-d’œuvre de Vauban avec musées et zoo, vue sur la boucle du Doubs.'],
    ['Saut du Doubs', 'Villers-le-Lac (25)', 47.0880, 6.7160, 'Nature', 'Une chute de 27 m à la frontière suisse, accessible en bateau ou à pied.'],
    ['Hospices de Beaune', 'Beaune (21)', 47.0216, 4.8379, 'Patrimoine', 'Les célèbres toits vernissés au cœur du vignoble bourguignon.'],
    ['Abbaye de Fontenay', 'Montbard (21)', 47.6390, 4.3890, 'Patrimoine', 'Abbaye cistercienne parmi les plus anciennes de France (UNESCO).']]},
  {region: 'Grand Est', lieux: [
    ['Château du Haut-Kœnigsbourg', 'Orschwiller (67)', 48.2495, 7.3444, 'Patrimoine', 'Château fort restauré dominant la plaine d’Alsace.'],
    ['Petite France', 'Strasbourg (67)', 48.5810, 7.7400, 'Ville', 'Maisons à colombages et canaux au pied de la cathédrale.'],
    ['Colmar et la Petite Venise', 'Colmar (68)', 48.0730, 7.3580, 'Ville', 'Quartier coloré au bord de la Lauch, marchés de Noël réputés.'],
    ['Lac de Gérardmer', 'Gérardmer (88)', 48.0700, 6.8550, 'Nature', 'La perle des Vosges : baignade, pédalo, tour du lac à pied.'],
    ['Cathédrale de Reims', 'Reims (51)', 49.2539, 4.0340, 'Patrimoine', 'La cathédrale des sacres et les caves de champagne.'],
    ['Place Stanislas', 'Nancy (54)', 48.6936, 6.1832, 'Ville', 'L’une des plus belles places d’Europe, illuminée le soir.']]},
  {region: 'Auvergne-Rhône-Alpes', lieux: [
    ['Mont-Blanc et Aiguille du Midi', 'Chamonix (74)', 45.8790, 6.8870, 'Montagne', 'Téléphérique jusqu’à 3 842 m face au toit de l’Europe.'],
    ['Lac d’Annecy', 'Annecy (74)', 45.8600, 6.1700, 'Nature', 'Eaux turquoise, vieille ville et piste cyclable autour du lac.'],
    ['Puy de Dôme', 'Orcines (63)', 45.7720, 2.9640, 'Nature', 'Volcan emblématique, accessible à pied ou en train panoramique.'],
    ['Vieux Lyon et Fourvière', 'Lyon (69)', 45.7620, 4.8220, 'Ville', 'Traboules, bouchons lyonnais et basilique sur la colline.'],
    ['Gorges de l’Ardèche', 'Vallon-Pont-d’Arc (07)', 44.3820, 4.4180, 'Nature', 'Pont d’Arc, canoë et grotte Chauvet 2.']]},
  {region: 'Île-de-France', lieux: [
    ['Tour Eiffel', 'Paris (75)', 48.8584, 2.2945, 'Ville', 'Le monument le plus visité, à voir aussi scintiller la nuit.'],
    ['Musée du Louvre', 'Paris (75)', 48.8606, 2.3376, 'Culture', 'La Joconde et des milliers de chefs-d’œuvre.'],
    ['Château de Versailles', 'Versailles (78)', 48.8049, 2.1204, 'Patrimoine', 'Galerie des Glaces, jardins et grandes eaux musicales.'],
    ['Château de Fontainebleau', 'Fontainebleau (77)', 48.4020, 2.7000, 'Patrimoine', 'Château des rois et forêt idéale pour l’escalade et la marche.'],
    ['Montmartre', 'Paris (75)', 48.8867, 2.3431, 'Ville', 'Sacré-Cœur, place du Tertre et vue sur tout Paris.']]},
  {region: 'Hauts-de-France', lieux: [
    ['Baie de Somme', 'Saint-Valery-sur-Somme (80)', 50.1850, 1.6330, 'Nature', 'Phoques, oiseaux migrateurs et petit train à vapeur.'],
    ['Côte d’Opale – Cap Blanc-Nez', 'Escalles (62)', 50.9270, 1.7130, 'Nature', 'Falaises face à l’Angleterre, randonnée sur le GR du littoral.'],
    ['Vieux-Lille', 'Lille (59)', 50.6400, 3.0630, 'Ville', 'Grand-Place, Vieille Bourse et estaminets.'],
    ['Château de Chantilly', 'Chantilly (60)', 49.1940, 2.4860, 'Patrimoine', 'Musée Condé, Grandes Écuries et crème Chantilly.'],
    ['Cathédrale d’Amiens', 'Amiens (80)', 49.8950, 2.3020, 'Patrimoine', 'La plus vaste cathédrale gothique de France et les hortillonnages.']]},
  {region: 'Normandie', lieux: [
    ['Mont-Saint-Michel', 'Le Mont-Saint-Michel (50)', 48.6361, -1.5115, 'Patrimoine', 'L’abbaye sur son rocher, à voir à marée haute.'],
    ['Falaises d’Étretat', 'Étretat (76)', 49.7070, 0.2030, 'Nature', 'Arches et aiguille, balade sur les falaises.'],
    ['Plages du Débarquement', 'Colleville-sur-Mer (14)', 49.3590, -0.8520, 'Histoire', 'Omaha Beach, cimetière américain et musées du D-Day.'],
    ['Giverny', 'Giverny (27)', 49.0750, 1.5330, 'Culture', 'La maison et les jardins de Claude Monet.'],
    ['Honfleur', 'Honfleur (14)', 49.4190, 0.2330, 'Ville', 'Vieux bassin, maisons étroites et peintres.']]},
  {region: 'Bretagne', lieux: [
    ['Côte de Granit Rose', 'Perros-Guirec (22)', 48.8260, -3.4900, 'Nature', 'Rochers roses et sentier des douaniers.'],
    ['Saint-Malo intra-muros', 'Saint-Malo (35)', 48.6490, -2.0260, 'Ville', 'Remparts, plages et fort à marée basse.'],
    ['Pointe du Raz', 'Plogoff (29)', 48.0390, -4.7370, 'Nature', 'Bout du monde breton face à l’océan.'],
    ['Golfe du Morbihan', 'Vannes (56)', 47.6000, -2.8000, 'Nature', 'Des dizaines d’îles à découvrir en bateau.'],
    ['Alignements de Carnac', 'Carnac (56)', 47.5940, -3.0760, 'Histoire', 'Plus de 3 000 menhirs alignés.']]},
  {region: 'Pays de la Loire', lieux: [
    ['Machines de l’île', 'Nantes (44)', 47.2070, -1.5640, 'Culture', 'Le Grand Éléphant et le Carrousel des mondes marins.'],
    ['Puy du Fou', 'Les Epesses (85)', 46.8890, -0.9300, 'Loisirs', 'Spectacles historiques géants, élu meilleur parc du monde.'],
    ['Château d’Angers', 'Angers (49)', 47.4700, -0.5600, 'Patrimoine', 'Forteresse et tapisserie de l’Apocalypse.'],
    ['Île de Noirmoutier', 'Noirmoutier-en-l’Île (85)', 47.0000, -2.2500, 'Nature', 'Passage du Gois à marée basse, marais salants.']]},
  {region: 'Centre-Val de Loire', lieux: [
    ['Château de Chambord', 'Chambord (41)', 47.6161, 1.5170, 'Patrimoine', 'Le plus grand château de la Loire et son escalier à double révolution.'],
    ['Château de Chenonceau', 'Chenonceaux (37)', 47.3249, 1.0703, 'Patrimoine', 'Le château des Dames enjambant le Cher.'],
    ['ZooParc de Beauval', 'Saint-Aignan (41)', 47.2480, 1.3530, 'Loisirs', 'L’un des plus beaux zoos du monde, pandas géants.'],
    ['Cathédrale de Chartres', 'Chartres (28)', 48.4477, 1.4878, 'Patrimoine', 'Vitraux bleus uniques et illuminations l’été.']]},
  {region: 'Nouvelle-Aquitaine', lieux: [
    ['Dune du Pilat', 'La Teste-de-Buch (33)', 44.5890, -1.2130, 'Nature', 'La plus haute dune d’Europe face au bassin d’Arcachon.'],
    ['Bordeaux – Miroir d’eau', 'Bordeaux (33)', 44.8410, -0.5700, 'Ville', 'Place de la Bourse et quais classés à l’UNESCO.'],
    ['Biarritz', 'Biarritz (64)', 43.4830, -1.5590, 'Ville', 'Rocher de la Vierge, surf et grandes plages.'],
    ['Futuroscope', 'Chasseneuil-du-Poitou (86)', 46.6690, 0.3680, 'Loisirs', 'Parc d’attractions autour de l’image et du futur.'],
    ['Lascaux IV', 'Montignac (24)', 45.0540, 1.1700, 'Histoire', 'Réplique de la grotte ornée préhistorique.']]},
  {region: 'Occitanie', lieux: [
    ['Cité de Carcassonne', 'Carcassonne (11)', 43.2060, 2.3640, 'Patrimoine', 'Cité médiévale aux 52 tours.'],
    ['Pont du Gard', 'Vers-Pont-du-Gard (30)', 43.9470, 4.5350, 'Patrimoine', 'Aqueduc romain, baignade dans le Gardon.'],
    ['Cirque de Gavarnie', 'Gavarnie (65)', 42.6950, -0.0100, 'Montagne', 'Amphithéâtre naturel et grande cascade des Pyrénées.'],
    ['Rocamadour', 'Rocamadour (46)', 44.7990, 1.6180, 'Patrimoine', 'Village accroché à la falaise.'],
    ['Toulouse – Capitole', 'Toulouse (31)', 43.6045, 1.4440, 'Ville', 'La ville rose, la Cité de l’espace et le canal du Midi.']]},
  {region: 'Provence-Alpes-Côte d’Azur', lieux: [
    ['Calanques de Marseille', 'Marseille (13)', 43.2100, 5.4500, 'Nature', 'Criques turquoise entre Marseille et Cassis.'],
    ['Gorges du Verdon', 'Moustiers-Sainte-Marie (04)', 43.7600, 6.3600, 'Nature', 'Le grand canyon européen, lac de Sainte-Croix.'],
    ['Promenade des Anglais', 'Nice (06)', 43.6950, 7.2650, 'Ville', 'Baie des Anges, Vieux-Nice et colline du Château.'],
    ['Palais des Papes', 'Avignon (84)', 43.9510, 4.8080, 'Patrimoine', 'Le plus grand palais gothique et le pont d’Avignon.'],
    ['Champs de lavande de Valensole', 'Valensole (04)', 43.8380, 5.9830, 'Nature', 'Floraison de mi-juin à mi-juillet.']]},
  {region: 'Corse', lieux: [
    ['Bonifacio', 'Bonifacio (2A)', 41.3870, 9.1590, 'Ville', 'Ville perchée sur les falaises de calcaire.'],
    ['Calanques de Piana', 'Piana (2A)', 42.2400, 8.6300, 'Nature', 'Roches rouges sculptées au-dessus de la mer (UNESCO).'],
    ['Plage de Palombaggia', 'Porto-Vecchio (2A)', 41.5600, 9.3300, 'Plage', 'Sable blanc, pins parasols et eau turquoise.']]},
  {region: 'Outre-mer', lieux: [
    ['Piton de la Fournaise', 'La Réunion (974)', -21.2440, 55.7080, 'Nature', 'Un des volcans les plus actifs du monde.'],
    ['Les Saintes', 'Guadeloupe (971)', 15.8700, -61.5900, 'Plage', 'Archipel et l’une des plus belles baies du monde.'],
    ['Montagne Pelée', 'Martinique (972)', 14.8090, -61.1650, 'Nature', 'Volcan, randonnée et forêt tropicale.'],
    ['Lagon de Mayotte', 'Mayotte (976)', -12.8270, 45.1660, 'Nature', 'Tortues, dauphins et baleines selon la saison.']]}
];

// Villes pour les tableaux météo. Les zones horaires sont fournies par l'API.
window.VM_VILLES = {
  france: [['Paris', 48.8566, 2.3522], ['Lyon', 45.7640, 4.8357], ['Marseille', 43.2965, 5.3698], ['Lille', 50.6292, 3.0573], ['Strasbourg', 48.5734, 7.7521], ['Belfort', 47.6380, 6.8628], ['Besançon', 47.2378, 6.0241], ['Dijon', 47.3220, 5.0415], ['Bordeaux', 44.8378, -0.5792], ['Toulouse', 43.6047, 1.4442], ['Nantes', 47.2184, -1.5536], ['Rennes', 48.1173, -1.6778], ['Nice', 43.7102, 7.2620], ['Montpellier', 43.6108, 3.8767], ['Ajaccio', 41.9192, 8.7386], ['Brest', 48.3904, -4.4861]],
  europe: [['Londres', 51.5072, -0.1276], ['Bruxelles', 50.8503, 4.3517], ['Genève', 46.2044, 6.1432], ['Berlin', 52.5200, 13.4050], ['Amsterdam', 52.3676, 4.9041], ['Madrid', 40.4168, -3.7038], ['Barcelone', 41.3874, 2.1686], ['Lisbonne', 38.7223, -9.1393], ['Rome', 41.9028, 12.4964], ['Vienne', 48.2082, 16.3738], ['Varsovie', 52.2297, 21.0122], ['Athènes', 37.9838, 23.7275], ['Stockholm', 59.3293, 18.0686], ['Dublin', 53.3498, -6.2603]],
  monde: [['New York', 40.7128, -74.0060], ['Montréal', 45.5019, -73.5674], ['Rio de Janeiro', -22.9068, -43.1729], ['Casablanca', 33.5731, -7.5898], ['Alger', 36.7538, 3.0588], ['Tunis', 36.8065, 10.1815], ['Dakar', 14.7167, -17.4677], ['Abidjan', 5.3600, -4.0083], ['Le Caire', 30.0444, 31.2357], ['Dubaï', 25.2048, 55.2708], ['Bangkok', 13.7563, 100.5018], ['Tokyo', 35.6762, 139.6503], ['Sydney', -33.8688, 151.2093], ['Pointe-à-Pitre', 16.2411, -61.5331], ['Fort-de-France', 14.6161, -61.0588], ['Saint-Denis (Réunion)', -20.8821, 55.4507]]
};
