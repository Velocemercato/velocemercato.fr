/* Notifications locales uniquement : aucun push distant sans serveur VAPID. */
self.addEventListener('notificationclick',event=>{
  event.notification.close();
  const url=new URL(event.notification.data&&event.notification.data.url||'/notifications/',self.location.origin);
  if(url.origin!==self.location.origin)return;
  event.waitUntil(clients.matchAll({type:'window',includeUncontrolled:true}).then(windows=>{
    for(const w of windows){if(w.url===url.href&&'focus'in w)return w.focus();}
    return clients.openWindow(url.href);
  }));
});