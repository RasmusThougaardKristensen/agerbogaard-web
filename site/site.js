// Contact form: a static site has no server, so open the visitor's mail app pre-filled.
document.querySelectorAll('.contact-form').forEach(function (f) {
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(f);
    var body = (d.get('besked') || '') + '\n\n' + (d.get('navn') || '') + '\n' + (d.get('email') || '');
    window.location.href = 'mailto:info@agerbogaard.dk?subject=' +
      encodeURIComponent('Besked fra ' + (d.get('navn') || 'hjemmesiden')) + '&body=' + encodeURIComponent(body);
  });
});
// Menu: highlight the section currently in view (desktop header and mobile tab bar).
(function () {
  var links = [].slice.call(document.querySelectorAll('.site-nav a[href^="#"]'));
  if (!('IntersectionObserver' in window) || !links.length) return;
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      links.forEach(function (a) { a.classList.toggle('is-active', a.getAttribute('href') === '#' + en.target.id); });
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  links.forEach(function (a) { var s = document.querySelector(a.getAttribute('href')); if (s) obs.observe(s); });
})();
