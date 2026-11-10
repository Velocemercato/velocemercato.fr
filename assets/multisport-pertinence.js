(() => {
  const relevant = {"nba": "\\bNBA\\b|\\bbasket(?:-ball)?\\b|Wemb|LeBron|Curry|Embiid|Spurs|Lakers|Celtics|Warriors|Knicks|Sixers|Thunder|Nuggets|Grizzlies|Heat|Bulls|Bucks|Raptors|Mavericks|Timberwolves|Clippers|Pacers|Rockets", "nfl": "\\bNFL\\b|football américain|Super Bowl|quarterback|touchdown|Ravens|Chiefs|Eagles|Patriots|Bills|Cowboys|Bears|Vikings|Broncos|Seahawks|49ers|Steelers|Dolphins|Lions|Bengals|Rams|Chargers", "f1": "\\bF1\\b|Formule 1|Formula 1|Grand Prix|Verstappen|Leclerc|Antonelli|Hamilton|Norris|Russell|Piastri|McLaren|Ferrari", "motogp": "MotoGP|Moto2|Moto3|Grand Prix moto|Márquez|Marquez|Bagnaia|Quartararo|Acosta|Bezzecchi|Sepang", "tennis": "tennis|\\bATP\\b|\\bWTA\\b|Roland.Garros|Wimbledon|Alcaraz|Sinner|Djokovic|Swiatek|Sabalenka", "rugby": "rugby|Top 14|XV de France|Six Nations|All Blacks|Stade Toulousain|Champions Cup", "cyclisme": "cyclisme|\\bUCI\\b|Tour de France|Tour d.Italie|Tour d.Espagne|Giro|Vuelta|Pogacar|Vingegaard|Evenepoel", "nhl": "\\bNHL\\b|hockey sur glace|Stanley Cup|Canadiens de Montréal|Maple Leafs|Bruins|Rangers|Red Wings|Oilers|Penguins", "mlb": "\\bMLB\\b|baseball|World Series|Yankees|Dodgers|Mets|Astros|Phillies|Red Sox|Blue Jays", "mma": "\\bUFC\\b|\\bMMA\\b|arts martiaux mixtes|octogone|Pereira|Makhachev|Jon Jones|Adesanya|McGregor", "ski": "\\bski\\b|ski alpin|ski de fond|biathlon|descente|slalom|super.G|sports d.hiver|Coupe du monde FIS|Odermatt|Shiffrin|Pinturault|Fourcade|Boe"};
  const negative = {"nba": "Kardashian|OnlyFans|Tissot|Mbappé|Real Madrid|programme TV|TV-Programme|sneakers", "nfl": "programme TV|sneakers|casquette", "f1": "parfum|montre de luxe|jeu vidéo", "motogp": "jeu vidéo|moto électrique.*prix"};
  const gaming = new RegExp("\\b(?:gta(?:\\s*(?:vi|[56]))?|grand theft auto|playstation|xbox|nintendo|fortnite|minecraft|roblox|esports?|e-sports?|nba\\s*2k\\w*|madden|ea\\s*(?:sports\\s*)?fc|fifa\\s*2[0-9]|jeux? vid[eé]o|gaming|steam|ubisoft|activision|call of duty)\\b", 'i');
  window.VM_Multisport = {
    isRelevant(sport, title) {
      if (typeof title !== 'string' || !Object.hasOwn(relevant, sport)) return false;
      return !gaming.test(title) && new RegExp(relevant[sport], 'i').test(title)
        && !(negative[sport] && new RegExp(negative[sport], 'i').test(title));
    }
  };
})();
