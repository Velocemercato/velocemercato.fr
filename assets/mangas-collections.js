(() => {
  const active = new Map();

  document.addEventListener('click', event => {
    const button = event.target.closest('.vm-collection-play');
    if (!button) return;
    const playlist = button.dataset.playlist;
    const screen = button.closest('.vm-collection-screen');
    if (!screen || !/^PL[A-Za-z0-9_-]{10,60}$/.test(playlist || '')) return;

    const frame = document.createElement('iframe');
    frame.title = button.getAttribute('aria-label') || 'Collection officielle sur YouTube';
    frame.src = 'https://www.youtube-nocookie.com/embed/videoseries?list=' + playlist + '&autoplay=1&playsinline=1&rel=0';
    frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    const dialog = screen.closest('dialog');
    if (dialog) active.set(screen, {dialog, poster: [...screen.childNodes].map(node => node.cloneNode(true))});
    screen.replaceChildren(frame);
  });

  for (const dialog of document.querySelectorAll('dialog')) {
    dialog.addEventListener('close', () => {
      for (const [screen, playback] of active) {
        if (playback.dialog === dialog) {
          screen.replaceChildren(...playback.poster);
          active.delete(screen);
        }
      }
    });
  }
})();
