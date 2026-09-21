// Contact form: no server on a static site, so open the visitor's mail app pre-filled.
document.querySelectorAll('.contact-form').forEach(function (f) {
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(f);
    var body = (d.get('besked') || '') + '\n\n' + (d.get('navn') || '') + '\n' + (d.get('email') || '');
    window.location.href = 'mailto:info@agerbogaard.dk?subject=' +
      encodeURIComponent('Besked fra ' + (d.get('navn') || 'hjemmesiden')) + '&body=' + encodeURIComponent(body);
  });
});
// Mobile tab bar: highlight the section in view.
(function () {
  var tabs = [].slice.call(document.querySelectorAll('.m-tabbar a'));
  if (!('IntersectionObserver' in window) || !tabs.length) return;
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      tabs.forEach(function (t) {
        var on = t.getAttribute('href') === '#' + en.target.id;
        t.style.color = on ? 'var(--color-accent-700)' : 'var(--color-text)';
        t.style.opacity = on ? '1' : '.6';
      });
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  tabs.forEach(function (t) { var s = document.querySelector(t.getAttribute('href')); if (s) obs.observe(s); });
})();
