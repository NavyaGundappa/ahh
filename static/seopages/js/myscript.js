

$(document).ready(function () {
  // Auto-expand the first FAQ
  $(".faqs-container .faq-singular:first")
    .addClass("active")
    .children(".faq-answer")
    .slideDown();

  // Toggle FAQs
  $(".faq-question").on("click", function () {
    const parent = $(this).parent();

    if (parent.hasClass("active")) {
      parent.removeClass("active").children(".faq-answer").slideUp();
    } else {
      $(".faq-singular.active .faq-answer").slideUp();
      $(".faq-singular").removeClass("active");
      parent.addClass("active").children(".faq-answer").slideDown();
    }
  });
});
$(document).ready(function () {
  $(".Realated-carousel").owlCarousel({
    loop: true,
    margin: 20,
    nav: true,
    autoHeight: true,
    autoplayHoverPause: true,
    dots: true,
    autoplay: true,
    autoplayTimeout: 3000,
    navText: [
      '<i class="fa-solid fa-arrow-left"></i>',
      '<i class="fa-solid fa-arrow-right"></i>'
    ],
    responsive: {
      0: {
        items: 1
      },
      768: {
        items: 2
      },
      1024: {
        items: 3
      }
    }
  });
});
// $(document).ready(function () {
//   $(".seo_case_study").owlCarousel({
//     loop: true,
//     margin: 20,
//     nav: true,
//     autoHeight: true,
//     autoplayHoverPause: true,
//     dots: true,
//     responsive: {
//       0: {
//         items: 1
//       },
//       576: {
//         items: 1
//       },
//       768: {
//         items: 2
//       },
//       1200: {
//         items: 4
//       }
//     }
//   });
// });

var owl = $(".seo-testiminoal");
owl.owlCarousel({
  items: 3,
  margin: 30,
  loop: true,
  center: true,
  autoHeight: true,
  autoplayHoverPause: true,
  dots: false,
  nav: false,
  responsive: {
    0: {
      items: 1
    },
    767: {
      items: 2
    },
    1200: {
      items: 3
    }
  }
});

$(".next").click(function () {
  owl.trigger("next.owl.carousel");
});
$(".prev").click(function () {
  owl.trigger("prev.owl.carousel");
});

$(".meet_our_div").owlCarousel({
  loop: true,
  margin: 20,
  nav: true,
  autoHeight: true,
  dots: true,
  navText: false,
  autoplayHoverPause: true,
  responsive: {
    0: {
      items: 1
    },
    600: {
      items: 2
    },
    1200: {
      items: 3,
      loop: false
    }
  }
});

$(".service-carousel").owlCarousel({
  loop: true,
  margin: 20,
  nav: true,
  autoHeight: true,
  dots: true,
  navText: false,
  autoplayHoverPause: true,
  navText: [
    '<i class="fa-solid fa-arrow-left"></i>',
    '<i class="fa-solid fa-arrow-right"></i>'
  ],
  responsive: {
    0: {
      items: 1
    },
    600: {
      items: 2
    },
    900: {
      items: 3
    },
    1200: {
      items: 4,
      loop: false
    }
  }
});

$(document).ready(function () {
  $(".over_lay_div").owlCarousel({
    loop: true,
    margin: 15,
    nav: true,
    autoHeight: true,
    dots: true,
    autoplay: false,
    autoplayHoverPause: true,
    autoplayTimeout: 4000,
    smartSpeed: 800,
    responsive: {
      0: { items: 1 },
      600: { items: 2 },
      1250: { items: 2.5 },
      1300: { items: 3.5 },
    }
  });
});

$(document).ready(function () {
  $(".main_div_facilities").owlCarousel({
    loop: true,
    margin: 20,
    nav: true,
    autoHeight: true,
    dots: true,
    autoplay: true,
    autoplayHoverPause: true,
    autoplayTimeout: 4000,
    smartSpeed: 800,
    navText: [
      '<i class="fa-solid fa-arrow-left"></i>',
      '<i class="fa-solid fa-arrow-right"></i>'
    ],
    responsive: {
      0: { items: 1 },
      600: { items: 2 },
      900: { items: 3 },
      1300: { items: 4 }
    }
  });
});



$(document).ready(function () {
  $(".journey-steps").owlCarousel({
    loop: true,
    margin: 20,
    nav: true,
    autoHeight: true,
    dots: true,
    autoplay: true,
    autoplayTimeout: 4000,
    autoplayHoverPause: true,
    responsive: {
      0: { items: 1 },      // Mobile: 1 item
      800: { items: 2 },    // Tablet: 2 items
      1000: { items: 3 }    // Desktop: 4 items
    }
  });
});

