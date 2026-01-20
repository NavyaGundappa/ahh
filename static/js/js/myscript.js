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




  if ($('#HomeSlider').length > 0) {
    $('#HomeSlider').owlCarousel({
      loop: true,
      items: 1,
      autoplay: true,
      autoplayTimeout: 5000,
      autoplayHoverPause: true,
      nav: true,
      dots: true,
      navText: ["<i class='fa fa-chevron-left'></i>", "<i class='fa fa-chevron-right'></i>"],
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

  // Doctors Carousel
  if ($('.doctors-carousel').length > 0) {
    $('.doctors-carousel').owlCarousel({
      loop: true,
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
          margin: 10,
          dots: true  // Show dots on mobile
        },
        600: {
          items: 2,
          nav: true,  // Show arrows on tablet+
          margin: 10,
          dots: false // Hide dots on tablet+
        },
        1100: {
          items: 3,
          nav: true,
          margin: 10,
          dots: false
        },
        1300: {
          items: 4,
          nav: true,
          margin: 20,
          dots: false
        }
      }
    });
  }


  // Init AOS animations
  AOS.init();

});


// Initialize Carousel
document.addEventListener("DOMContentLoaded", function () {
  // Re-init when tabs change
  var tabEls = document.querySelectorAll('button[data-bs-toggle="pill"]');
  tabEls.forEach(function (tabEl) {
    tabEl.addEventListener('shown.bs.tab', function (event) {
      initLifeCarousels();
    });
  });

  function initLifeCarousels() {
    // Destroy existing before re-init to prevent bugs
    $('.life-glance-carousel').trigger('destroy.owl.carousel');

    $('.life-glance-carousel').owlCarousel({
      loop: true,
      margin: 20,
      nav: true,
      autoplay: true,
      autoplayTimeout: 3500,
      autoplayHoverPause: true,
      dots: true,
      responsive: {
        0: { items: 1 },
        600: { items: 2 },
        1000: { items: 2 }
      },
      navText: [
        '<i class="fas fa-chevron-left"></i>',
        '<i class="fas fa-chevron-right"></i>'
      ]
    });
  }

  $('a[data-bs-toggle="pill"]').on('shown.bs.tab', function (e) {
    // Find the active tab pane
    var activeTabId = $(e.target).attr('data-bs-target');

    // Find the carousel within that active tab pane
    var $activeCarousel = $(activeTabId).find('.life-glance-carousel');

    // Trigger the 'refresh' event on the found carousel
    $activeCarousel.trigger('refresh.owl.carousel');
  });

  // Initial Load
  initLifeCarousels();
});


$(document).ready(function () {
  // --- 1. MOBILE NAVIGATION LOGIC ---
  const mobileMenuToggle = $('#mobile-menu-toggle');
  const mobileMenuClose = $('#mobile-menu-close');
  const mobileNav = $('#mobile-nav');
  const navOverlay = $('.nav-overlay');

  if (mobileMenuToggle.length) {
    const openNav = () => {
      mobileNav.addClass('active');
      navOverlay.addClass('active');
      $('body').css('overflow', 'hidden');
    };
    const closeNav = () => {
      mobileNav.removeClass('active');
      navOverlay.removeClass('active');
      $('body').css('overflow', '');
    };

    // MODIFIED: This now toggles the menu
    mobileMenuToggle.on('click', () => {
      if (mobileNav.hasClass('active')) {
        closeNav();
      } else {
        openNav();
      }
    });

    mobileMenuClose.on('click', closeNav);
    navOverlay.on('click', closeNav);
  }

  // --- 2. MOBILE SIDEBAR LOGIC ---
  const mobileSidebarToggle = $('#mobile-sidebar-toggle');
  const sidebar = $('.left-sidebar');

  if (mobileSidebarToggle.length && sidebar.length) {
    const toggleSidebar = () => {
      sidebar.toggleClass('show-mobile-sidebar');
    };
    mobileSidebarToggle.on('click', function (event) {
      event.stopPropagation();
      toggleSidebar();
    });
    $(document).on('click', function (event) {
      if (sidebar.hasClass('show-mobile-sidebar') && !sidebar.is(event.target) && sidebar.has(event.target).length === 0 && !mobileSidebarToggle.is(event.target) && mobileSidebarToggle.has(event.target).length === 0) {
        toggleSidebar();
      }
    });
  }

  // --- 3. SCROLL-TO-TOP BUTTON ---
  const scrollBtn = $('#scrollToTopBtn');
  if (scrollBtn.length) {
    $(window).on('scroll', function () {
      if ($(window).scrollTop() > 300) {
        scrollBtn.css('display', 'flex');
      } else {
        scrollBtn.hide();
      }
    });
    scrollBtn.on('click', function (e) {
      e.preventDefault();
      $('html, body').animate({ scrollTop: 0 }, 'smooth');
    });
  }


});

// Standalone Functions and Modal Logic
function showChromePopup() {
  const popup = document.getElementById("chrome-popup");
  if (popup) popup.classList.add("is-visible");
}
function hideChromePopup() {
  const popup = document.getElementById("chrome-popup");
  if (popup) popup.classList.remove("is-visible");
}
document.addEventListener("keydown", e => {
  if (e.key === "Escape") hideChromePopup();
});


document.addEventListener('DOMContentLoaded', () => {
  const reviewModal = document.getElementById('review-modal');
  if (reviewModal) {
    // Open modal
    document.querySelectorAll('.write-review-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.preventDefault();
        reviewModal.style.display = 'flex';
      });
    });

    // Close modal on X
    reviewModal.querySelector('.close-button').addEventListener('click', () => {
      reviewModal.style.display = 'none';
    });

    // Close modal if clicking outside
    window.addEventListener('click', e => {
      if (e.target === reviewModal) reviewModal.style.display = 'none';
    });

    // Handle form submit with AJAX
    reviewModal.querySelector('#review-form').addEventListener('submit', async e => {
      e.preventDefault();

      const form = e.target;
      const formData = new FormData(form);

      try {
        const res = await fetch("/submit-review", {
          method: "POST",
          body: formData
        });

        if (res.ok) {
          alert("✅ Your message has been submitted successfully!");
          form.reset(); // clear form fields
          reviewModal.style.display = "none"; // close modal
        } else {
          alert("❌ Error submitting message. Please try again.");
        }
      } catch (err) {
        console.error(err);
        alert("⚠️ Something went wrong. Please try later.");
      }
    });
  }
});


document.addEventListener("DOMContentLoaded", function () {

  // 1. FIX FOR SCROLL-TO-TOP ON REFRESH
  if (history.scrollRestoration) {
    history.scrollRestoration = 'manual';
  }
  window.scrollTo(0, 0);


  // Function to hide/show sidebar based on scroll position
  function toggleSidebarOnYouTubeSection() {
    const youtubeSection = document.getElementById('youtube-section');
    const sidebar = document.querySelector('.left-sidebar'); // Adjust selector as needed

    if (!youtubeSection || !sidebar) return;

    const rect = youtubeSection.getBoundingClientRect();
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;

    // Check if YouTube section is in view (with some threshold)
    const isInView = rect.top <= windowHeight / 2 && rect.bottom >= windowHeight / 2;

    if (isInView) {
      sidebar.style.display = 'none';
    } else {
      sidebar.style.display = 'block'; // or whatever its default display value is
    }
  }

  // Add scroll event listener
  window.addEventListener('scroll', toggleSidebarOnYouTubeSection);

  // Also call on page load in case the section is already in view
  window.addEventListener('load', toggleSidebarOnYouTubeSection);

  function toggleSidebarOnYouTubeSection() {
    const youtubeSection = document.getElementById('youtube-section');
    const sidebar = document.querySelector('.left-sidebar');

    if (!youtubeSection || !sidebar) return;

    const rect = youtubeSection.getBoundingClientRect();
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;

    const isInView = rect.top <= windowHeight / 2 && rect.bottom >= windowHeight / 2;

    if (isInView) {
      sidebar.classList.add('hidden');
    } else {
      sidebar.classList.remove('hidden');
    }
  }


  function debounce(func, wait) {
    let timeout;
    return function () {
      const context = this, args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(context, args), wait);
    };
  }

  window.addEventListener('scroll', debounce(toggleSidebarOnYouTubeSection, 10));

  // Function to check if element is in viewport
  function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.9 &&
      rect.bottom >= 0
    );
  }

  // Create debounced version of the function
  function debounce(func, wait) {
    let timeout;
    return function () {
      const context = this, args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(context, args), wait);
    };
  }

  // Initialize the counter animation function
  const checkCounters = animateCounters();

  // Check on load and scroll
  window.addEventListener('load', checkCounters);
  window.addEventListener('scroll', debounce(checkCounters, 10));

  // Also check immediately in case the section is already in view
  checkCounters();
});
document.addEventListener("DOMContentLoaded", function () {
  window.scrollTo(0, 0);
});


$(document).ready(function () {
  $(".Aarogya_new_faqs-container .Aarogya_new_faq-singular:first-child")
    .addClass("active")
    .children(".Aarogya_new_faq-answer")
    .slideDown();

  $(".Aarogya_new_faq-question").on("click", function () {
    let faqItem = $(this).parent();

    if (faqItem.hasClass("active")) {
      faqItem.removeClass("active");
      faqItem.find(".Aarogya_new_faq-answer").slideUp();
      faqItem.find(".Aarogya_new_faq-toggle i").removeClass("fa-chevron-up").addClass("fa-chevron-down");
    } else {
      $(".Aarogya_new_faq-singular").removeClass("active");
      $(".Aarogya_new_faq-answer").slideUp();
      $(".Aarogya_new_faq-toggle i").removeClass("fa-chevron-up").addClass("fa-chevron-down");

      faqItem.addClass("active");
      faqItem.find(".Aarogya_new_faq-answer").slideDown();
      faqItem.find(".Aarogya_new_faq-toggle i").removeClass("fa-chevron-down").addClass("fa-chevron-up");
    }
  });
});

// Add this JavaScript to handle the scroll behavior
document.addEventListener("DOMContentLoaded", function () {
  const navbar = document.querySelector('.nav-container');
  let lastScrollTop = 0;
  const scrollThreshold = 100; // Adjust this value as needed

  window.addEventListener('scroll', function () {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > lastScrollTop && scrollTop > scrollThreshold) {
      // Scrolling down
      navbar.classList.remove('hide');
    } else if (scrollTop < lastScrollTop) {
      // Scrolling up
      navbar.classList.add('hide');
    }

    lastScrollTop = scrollTop;

    // --- 4. OWL CAROUSEL AND OTHER PLUGINS ---
    if ($('.specialities-carousel').length) {
      $('.specialities-carousel').owlCarousel({ loop: true, margin: 30, autoplay: true, autoplayTimeout: 2500, autoplayHoverPause: true, nav: true, responsive: { 0: { items: 1 }, 600: { items: 2 }, 1000: { items: 3 } } });
    }
    // if ($('.doctors-carousel').length) {
    //   $('.doctors-carousel').owlCarousel({ loop: true, margin: 40, autoplay: true, autoplayTimeout: 3500, nav: true, responsive: { 0: { items: 1 }, 600: { items: 2 }, 1000: { items: 4 } } });
    // }
    if ($('.feedback-carousel').length) {
      $('.feedback-carousel').owlCarousel({
        loop: true,
        margin: 30,
        autoplay: true,
        autoplayTimeout: 5000,
        nav: false,
        dots: true,
        autoHeight: false,
        autoplayHoverPause: true,
        responsive: {
          0: { items: 1 },
          768: { items: 2 },
          1000: { items: 2 }
        }
      });
    }
    if ($('[data-vbg]').length) {
      $('[data-vbg]').youtube_background({ 'play-button': true });
    }
    $(window).on('resize', () => {
      $('[data-img-mob]').each(function () {
        $(this).attr('src', $(document).width() < 993 ? $(this).data('img-mob') : $(this).data('img-desk'));
      });
    }).trigger('resize');
  });
});


// Counter animation function
function animateCounter(counter) {
  const target = parseInt(counter.getAttribute('data-count'));
  const duration = 2000; // 2 seconds
  const increment = Math.ceil(target / (duration / 16)); // 60fps
  let current = 0;

  const updateCounter = () => {
    current += increment;
    if (current >= target) {
      counter.textContent = target;
      if (counter.nextElementSibling && counter.nextElementSibling.classList.contains('suffix')) {
        counter.textContent = target + counter.nextElementSibling.textContent;
      }
    } else {
      counter.textContent = current;
      requestAnimationFrame(updateCounter);
    }
  };

  updateCounter();
}

// Function to check if counters are in viewport
function isInViewport(element) {
  const rect = element.getBoundingClientRect();
  return (
    rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8 &&
    rect.bottom >= 0
  );
}

// Function to handle counter animation when scrolled into view

document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".number");

  counters.forEach(counter => {
    const updateCount = () => {
      const target = +counter.getAttribute("data-count");
      const count = +counter.innerText;
      const increment = target / 200; // Adjust speed

      if (count < target) {
        counter.innerText = Math.ceil(count + increment);
        requestAnimationFrame(updateCount);
      } else {
        counter.innerText = target;
      }
    };
    updateCount();
  });
});


$(document).ready(function () {

  // 1. Initialize Main Center Slider
  $("#HomeSlider").owlCarousel({
    items: 1,
    loop: true,
    margin: 0,
    autoplay: true,
    autoplayTimeout: 5000,
    nav: true,
    dots: true,
    animateOut: 'fadeOut'
  });

  // 2. Initialize Left and Right Sliders
  $("#LeftSlider, #RightSlider").owlCarousel({
    items: 1,
    loop: true,
    margin: 0,
    autoplay: true,
    autoplayTimeout: 4000,
    nav: false,
    dots: false,
    mouseDrag: false,
    touchDrag: false
  });

});

// Initialize counter animation handler
const checkCounters = handleCounterAnimation();

// Check on load and scroll
window.addEventListener('load', checkCounters);
window.addEventListener('scroll', checkCounters);

// Also check immediately
checkCounters();

function loadYouTubeVideo(wrapperId) {
  const wrapper = document.getElementById(wrapperId);
  const videoId = wrapper.getAttribute('data-video-id');

  if (!videoId) return;

  // Construct the full embed URL with autoplay enabled
  const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;

  // Create the iframe element
  const iframe = document.createElement('iframe');
  iframe.setAttribute('src', embedUrl);
  iframe.setAttribute('title', 'Patient Testimonial');
  iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
  iframe.setAttribute('allowfullscreen', '');

  // Apply the necessary styles for the iframe to fill the container
  iframe.style.position = 'absolute';
  iframe.style.top = '0';
  iframe.style.left = '0';
  iframe.style.width = '100%';
  iframe.style.height = '100%';
  iframe.style.border = '0';

  // Replace the current wrapper content (thumbnail/button) with the iframe
  wrapper.innerHTML = '';
  wrapper.appendChild(iframe);

  // Remove the onclick event so it doesn't try to load again
  wrapper.onclick = null;
}