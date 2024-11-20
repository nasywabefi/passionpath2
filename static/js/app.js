
// navbar scroll
window.onscroll = function () {
    const navbar = document.querySelector('.navbar-custom');
    if (document.body.scrollTop > 10 || document.documentElement.scrollTop > 10) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
};

// eye pada passowrd login dan register
document.getElementById('toggle-password').addEventListener('click', function () {
    const passwordInput = document.getElementById('password');
    const icon = this.querySelector('i');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
});

// card login register
$(document).ready(function () {
    function adjustLayout() {
        if ($(window).width() > 768) {
            $('.card').css('margin', 'auto');
            $('.col-md-6 img').css({
                'width': '100%',
                'height': 'auto'
            });
        } else {
            $('.card').css('margin', '1rem');
            $('.col-md-6 img').css({
                'width': '100%',
                'height': 'auto'
            });
        }
    }

    adjustLayout();
    $(window).resize(function () {
        adjustLayout();
    });
});


// icon toggle navbar
$(document).ready(function () {
    $('#menu-icon').click(function () {
        $('.navbar-custom').toggleClass('open');
    });
});


