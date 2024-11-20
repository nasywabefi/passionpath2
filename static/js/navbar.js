// navbar scroll
window.onscroll = function () {
    const navbar = document.querySelector('.navbar-custom');
    if (document.body.scrollTop > 10 || document.documentElement.scrollTop > 10) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
};

// icon toggle navbar
$(document).ready(function () {
    $('#menu-icon').click(function () {
        $('.navbar-custom').toggleClass('open');
    });
});
