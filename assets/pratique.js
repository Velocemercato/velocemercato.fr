// Outils communs des pages de services : échappement, e-mail et chargement de données.
window.VMP = (() => {
  const esc = text => String(text ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  // Rien n’est envoyé sans que la personne valide dans son application e-mail.
  const mail = (subject, body) => {
    if (window.vmMail) return window.vmMail(subject, body);
    location.href = 'mailto:velocemercato.fr@gmail.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  };
  const json = url => fetch(url, {cache: 'no-store'}).then(r => r.ok ? r.json() : []).catch(() => []).then(d => Array.isArray(d) ? d : []);
  const val = (form, name) => (form.elements[name]?.value || '').trim();
  return {esc, mail, json, val};
})();
