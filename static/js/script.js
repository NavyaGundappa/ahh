$(document).ready(function () {

    // Highlight current menu link
    const current_link = window.location.pathname.replace('/', '');
    var listItems = $("#primary-menu li");
    $('.menu-item').removeClass('current-menu-item');
    listItems.each(function () {
        var item = $(this);
        if (item.children().attr('href') == current_link) {
            item.addClass('current-menu-item');
        }
    });




if($('#HomeSlider').length>0){
    $('#HomeSlider').owlCarousel({
        loop: true,
        items: 1,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplayHoverPause: true,
        nav: true,
        dots: true,
        navText: ["<i class='fa fa-chevron-left'></i>","<i class='fa fa-chevron-right'></i>"],
        responsive: {
            0: {
                nav: false, // Hide arrows on mobile
                dots: true  // Show dots on mobile
            },
            768: {
                nav: true,  // Show arrows on desktop
                dots: false // Hide dots on desktop
            }
        }
    });
}





    // Owl Carousel - Service Carousel (Departments)
    if ($('.service-carousel').length > 0) {
        $('.service-carousel').owlCarousel({
            loop: true,
            margin: 30,
            autoplay: true,
            autoplayTimeout: 3500,
            nav: true,
            touchDrag: true,
            autoplayHoverPause: true,
            navText: [
                "<i class='fa fa-chevron-left'></i>",
                "<i class='fa fa-chevron-right'></i>"
            ],
            responsive: {
                0: { items: 2 },
                600: { items: 3 },
                1000: { items: 4 },
                1300: { items: 5 }
            }
        });
    }

    // Owl Carousel - Speciality Carousel
    // Speciality Carousel
if ($('.speciality-carousel').length > 0) {
    $('.speciality-carousel').owlCarousel({
        loop: true,
        margin: 30,
        autoplay: true,
        autoplayTimeout: 3500,
        nav: true,
        dots: true,
        touchDrag: true,
        autoplayHoverPause: true,
        navText: [
            "<i class='fa fa-chevron-left'></i>",
            "<i class='fa fa-chevron-right'></i>"
        ],
        responsive: {
            0: {
                items: 1,
                nav: false, // Hide arrows on mobile
                dots: true  // Show dots on mobile
            },
            600: {
                items: 2,
                nav: true,  // Show arrows on tablet+
                dots: false // Hide dots on tablet+
            },
            1000: {
                items: 3,
                nav: true,
                dots: false
            },
            1300: {
                items: 4,
                nav: true,
                dots: false
            }
        }
    });
}

// Doctors Carousel
if ($('.doctors-carousel').length > 0) {
    $('.doctors-carousel').owlCarousel({
        loop: true,
        margin: 30,
        autoplay: true,
        autoplayTimeout: 3500,
        nav: true,
        dots: true,
        touchDrag: true,
        autoplayHoverPause: true,
        navText: [
            "<i class='fa fa-chevron-left'></i>",
            "<i class='fa fa-chevron-right'></i>"
        ],
        responsive: {
            0: {
                items: 1,
                nav: false, // Hide arrows on mobile
                dots: true  // Show dots on mobile
            },
            600: {
                items: 2,
                nav: true,  // Show arrows on tablet+
                dots: false // Hide dots on tablet+
            },
            1000: {
                items: 3,
                nav: true,
                dots: false
            },
            1300: {
                items: 4,
                nav: true,
                dots: false
            }
        }
    });
}

    // About section tab switch
    $('.tab-item').click(function () {
        $('.about-tab').hide();
        $('.tab-item').removeClass('active');
        $(this).addClass('active');
        $(`${$(this).attr('data-id')}`).show();
    });

    // Department tab switch
    $('.department-grid .item').click(function () {
        $('.department-tab').hide();
        $('.department-grid .item').removeClass('active');
        $(this).addClass('active');
        $(`.${$(this).attr('data-department')}`).show();
    });

    // Init AOS animations
    AOS.init();

    // Careers form handling
    if ($('form#careers').length > 0) {
        $('a.apply-btn').on('click', function () {
            $('input#post').val($(this).data("id"));
        });

        const form = document.querySelector("#careers");
        const submitButton = document.querySelector("#submit");
        const scriptURL = 'https://script.google.com/macros/s/AKfycbxb5RZMtRzWNC9GYZRf5_zFJOIL4oU3hKnzs4Csc_A4jv1krGH1LexHx6V7OOhM6Z4/exec';

        form.addEventListener('submit', e => {
            submitButton.disabled = true;
            e.preventDefault();
            let requestBody = new FormData(form);
            fetch(scriptURL, { method: 'POST', body: requestBody })
                .then(() => {
                    submitButton.disabled = false;
                    $('form#careers').html('<p class="p-5">Thank you!<br/><br/>Your application has been submitted, our HR team will get in touch with you shortly</p>');
                })
                .catch(() => {
                    submitButton.disabled = false;
                    $('form#careers').html('<p class="p-5">Sorry!<br/><br/>We could not submit your details due to technical issues. Please send your details/resume to hr@aarogyahastha.com.</p>');
                });
        });
    }
});

// Fetch Doctor Info function
var fetchDoctorInfo = function (qstring, type) {
    var request = $.ajax({
        url: "assets/data/doctors.php",
        method: "POST",
        data: qstring,
        dataType: "html"
    });

    request.done(function (msg) {
        if (type == 'list') {
            $('#doctors-list .doctor-section .row').append(msg);
            $('html, body').scrollTop($("#doctors-list").offset().top);
            $('#doctors-list .doctor-section .row .doctor-item').on('click', function () {
                if ($('#doctor-profile').length > 0) {
                    var postData = { 'doctor': $(this).data('doctor') };
                    fetchDoctorInfo(postData, 'item');
                } else {
                    location.href = "appointment#" + $(this).data('doctor');
                }
            });
        }
        if (type == 'item') {
            $('.doctor-details .row').html(msg);
            $('#doctor-profile').fadeIn('slow');
            $('html, body').stop().animate({
                'scrollTop': $('#doctor-profile').offset().top
            }, 800, 'swing', function () {
                window.location.hash = doctor;
            });
        }
    });

    request.fail(function () { return false; });
};
$('.department-grid .item').click(function () {
    // Remove active from all and add to clicked
    $('.department-grid .item').removeClass('active');
    $(this).addClass('active');

    // Get the title and content from clicked item
    let title = $(this).find('h4').text();
    let content = $(this).find('.content').html();

    // Replace the details panel content
    $('.department-sub-services-details h4').text(title);
    $('.department-sub-services-details .content').html(content);
});

