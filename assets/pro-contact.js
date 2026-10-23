/* Prépare un brouillon local. Aucune donnée n'est envoyée ni conservée par le site. */
(() => {
  document.querySelectorAll('[data-pro-contact]').forEach(form => {
    const service = form.elements.service;
    const allowed = new Set([...service.options].map(option => option.value));
    const preset = new URLSearchParams(location.search).get('offre');
    if (allowed.has(preset)) service.value = preset;
    document.querySelectorAll('a[data-offer]').forEach(link => {
      link.addEventListener('click', () => {
        if (allowed.has(link.dataset.offer)) {
          service.value = link.dataset.offer;
          result.hidden = true;
        }
      });
    });
    const result = form.querySelector('[data-pro-result]');
    const preview = form.querySelector('[data-pro-preview]');
    const mail = form.querySelector('[data-pro-mail]');
    const status = form.querySelector('[data-pro-status]');
    let message = '';
    // Un changement annule le brouillon pour éviter d'envoyer une ancienne sélection.
    form.addEventListener('input', event => {
      result.hidden = true;
      if (event.target.setCustomValidity) event.target.setCustomValidity('');
    });
    form.addEventListener('change', () => { result.hidden = true; });
    form.addEventListener('submit', event => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const label = service.selectedOptions[0].textContent;
      const name = form.elements.nom.value.trim();
      const need = form.elements.besoin.value.trim();
      if (!name || !need) {
        const field = !name ? form.elements.nom : form.elements.besoin;
        field.setCustomValidity('Précisez votre activité et votre besoin pour préparer votre demande.');
        field.reportValidity();
        return;
      }
      message = `Bonjour,\n\nJe souhaite échanger sur : ${label}.\n\nNom / activité : ${name}\nVille : ${form.elements.ville.value.trim() || 'À préciser'}\nDélai souhaité : ${form.elements.delai.value.trim() || 'À définir ensemble'}\n\nMon projet :\n${need}\n\nMerci !`;
      const subject = `Projet VM — ${label}`;
      const address = form.dataset.proContact;
      preview.textContent = `À : ${address}\nObjet : ${subject}\n\n${message}`;
      mail.href = `mailto:${address}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(message)}`;
      status.textContent = 'Brouillon prêt. Pour nous le transmettre, ouvrez votre messagerie puis appuyez sur Envoyer.';
      result.hidden = false;
      result.focus();
    });
    form.querySelector('[data-pro-copy]').addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(preview.textContent);
        status.textContent = 'Demande copiée. Collez-la dans votre messagerie et envoyez-la à ' + form.dataset.proContact + '.';
      } catch (_) {
        const range = document.createRange();
        range.selectNodeContents(preview);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        status.textContent = 'Sélectionnez Copier dans le menu, puis collez la demande dans votre messagerie.';
      }
    });
  });
})();
