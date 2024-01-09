document.addEventListener("DOMContentLoaded", function() {
    var currentLinks = document.querySelectorAll('.option a.current');

    currentLinks.forEach(function(link) {
        link.style.transition = 'font-size 0.3s';
    });

    document.querySelectorAll('.option a').forEach(function(link) {
        link.addEventListener('click', function() {
            document.querySelectorAll('.option a').forEach(function(el) {
                el.classList.remove('current');
            });
            link.classList.add('current');
            link.style.fontSize = '25px';
        });
    });
});