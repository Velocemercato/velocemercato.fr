// Outils communs des pages de services : échappement, e-mail et chargement de données.
window.VMP = (() => {
  const esc = text => String(text ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  // Rien n’est envoyé sans que la personne valide dans son application e-mail.
  const mail = (subject, body) => {
    if (window.vmMail) return window.vmMail(subject, body);
    location.href = 'mailto:vminvest.fr@gmail.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  };
  const json = async url => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(url, {cache: 'no-store', signal: controller.signal});
      if (!response.ok) throw new Error('Chargement indisponible');
      const data = await response.json();
      if (!Array.isArray(data)) throw new Error('Liste indisponible');
      return data;
    } finally { clearTimeout(timer); }
  };
  const val = (form, name) => (form.elements[name]?.value || '').trim();
  return {esc, mail, json, val};
})();
