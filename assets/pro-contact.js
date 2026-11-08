/* Demande de devis VM Studio.
   - Avec data-pro-endpoint : envoi réel (FormSubmit, réponse JSON). La confirmation ne s'affiche
     QU'APRÈS une réponse de succès. En cas d'échec, un brouillon e-mail est proposé en secours.
   - Sans data-pro-endpoint : ancien mode « brouillon local » (aucun envoi).
   Rien n'est conservé par le site ni dans le navigateur (pas de localStorage, pas de cookie). */
(() => {
  const LOADED = Date.now();
  const MIN_DELAY = 3000;      // un humain met plus de 3 s à remplir le formulaire
  const COOLDOWN = 60000;      // une seule demande par minute depuis la page
  const TIMEOUT = 15000;

  document.querySelectorAll('[data-pro-contact]').forEach(form => {
    const service = form.elements.service;
    const allowed = new Set([...service.options].map(option => option.value));
    const result = form.querySelector('[data-pro-result]');
    const preview = form.querySelector('[data-pro-preview]');
    const mail = form.querySelector('[data-pro-mail]');
    const status = form.querySelector('[data-pro-status]');
    const sent = form.querySelector('[data-pro-sent]');
    const button = form.querySelector('[data-pro-send]') || form.querySelector('button[type=submit]');
    const endpoint = form.dataset.proEndpoint || '';
    const label0 = button ? button.textContent : '';
    let message = '';
    let busy = false;

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

    const field = name => (form.elements[name] ? String(form.elements[name].value || '').trim() : '');
    const show = (text, kind) => {
      if (!sent) return;
      sent.textContent = text;
      sent.className = 'pro-sent ' + kind;
      sent.hidden = false;
      sent.focus();
    };
    const buildDraft = () => {
      const label = service.selectedOptions[0].textContent;
      message = `Bonjour,\n\nJe souhaite échanger sur : ${label}.\n\nNom / activité : ${field('nom')}\n` +
        (form.elements.email ? `E-mail : ${field('email') || 'À préciser'}\n` : '') +
        `Ville : ${field('ville') || 'À préciser'}\nDélai souhaité : ${field('delai') || 'À définir ensemble'}\n\nMon projet :\n${field('besoin')}\n\nMerci !`;
      const subject = `${form.dataset.subject || '[VM Univers · Devis VM Studio]'} ${label}`;
      const address = form.dataset.proContact;
      preview.textContent = `À : ${address}\nObjet : ${subject}\n\n${message}`;
      mail.href = `mailto:${address}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(message)}`;
    };
    const showDraft = text => {
      buildDraft();
      status.textContent = text;
      result.hidden = false;
    };

    // Un changement annule le brouillon et l'ancien message pour éviter une sélection périmée.
    form.addEventListener('input', event => {
      result.hidden = true;
      if (sent && !busy) sent.hidden = true;
      if (event.target.setCustomValidity) event.target.setCustomValidity('');
    });
    form.addEventListener('change', () => { result.hidden = true; });

    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (busy) return;
      if (!form.reportValidity()) return;
      const name = field('nom');
      const need = field('besoin');
      if (!name || !need) {
        const target = !name ? form.elements.nom : form.elements.besoin;
        target.setCustomValidity('Précisez votre activité et votre besoin.');
        target.reportValidity();
        return;
      }
      if (!endpoint) {           // ancien mode : brouillon local seulement
        buildDraft();
        status.textContent = 'Brouillon prêt. Pour nous le transmettre, ouvrez votre messagerie puis appuyez sur Envoyer.';
        result.hidden = false;
        result.focus();
        return;
      }
      // Antispam : champ piège rempli → aucun envoi, aucune fausse confirmation.
      if (field('_honey')) return;
      if (Date.now() - LOADED < MIN_DELAY) {
        show('Merci de relire votre demande, puis d’appuyer à nouveau sur « Envoyer ».', 'err');
        return;
      }
      busy = true;
      result.hidden = true;
      if (sent) sent.hidden = true;
      button.disabled = true;
      button.textContent = 'Envoi en cours…';
      const data = {
        _subject: `${form.dataset.subject || '[VM Univers · Devis VM Studio]'} ${service.selectedOptions[0].textContent} — ${name}`.slice(0, 180),
        _template: 'table', _captcha: 'false', _honey: '',
        nom: name, email: field('email'), besoin_principal: service.selectedOptions[0].textContent,
        ville: field('ville'), delai: field('delai'), projet: need,
        consentement: form.elements.consentement && form.elements.consentement.checked ? 'oui' : 'non',
      };
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), TIMEOUT);
      let ok = false;
      let activation = false;
      try {
        const response = await fetch(endpoint, {
          method: 'POST', signal: controller.signal, credentials: 'omit',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(data),
        });
        const json = await response.json().catch(() => ({}));
        const reply = typeof json.message === 'string' ? json.message : '';
        activation = /activat|confirm.{0,28}(email|e-mail|form)/i.test(reply);
        ok = response.ok && !activation && (json.success === true || json.success === 'true');
      } catch (_) {
        ok = false;
      } finally {
        clearTimeout(timer);
      }
      busy = false;
      if (ok) {
        show(`✅ Demande envoyée ! Nous vous répondons à ${data.email}. Pensez à vérifier vos courriers indésirables.`, 'ok');
        form.reset();
        if (allowed.has(preset)) service.value = preset;
        button.textContent = 'Demande envoyée';
        setTimeout(() => { button.disabled = false; button.textContent = label0; }, COOLDOWN);
      } else {
        button.disabled = false;
        button.textContent = label0;
        show(activation
          ? 'Le formulaire attend une activation. Vous pouvez nous transmettre votre demande par e-mail ci-dessous.'
          : 'L’envoi n’a pas pu être confirmé. Vous pouvez utiliser votre messagerie si nécessaire.', 'err');
        showDraft('Votre brouillon est prêt. Ouvrez votre messagerie pour l’envoyer.');
      }
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
