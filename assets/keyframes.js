(() => {
  'use strict';
  const sections = [...document.querySelectorAll('[data-character]')];
  const links = [...document.querySelectorAll('[data-character-link]')];
  function selectCharacter() {
    const requested = location.hash.slice(1);
    const active = sections.find(section => section.id === requested) || sections.find(section => !section.hidden) || sections[0];
    if (!active) return;
    sections.forEach(section => { section.hidden = section !== active; });
    links.forEach(link => {
      if (link.dataset.characterLink === active.id) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    document.title = active.querySelector('h1').textContent + ' · 独立关键帧 · AI Chibi Atlas';
  }
  window.addEventListener('hashchange', selectCharacter);
  selectCharacter();
})();
