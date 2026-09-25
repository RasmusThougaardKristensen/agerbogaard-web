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
