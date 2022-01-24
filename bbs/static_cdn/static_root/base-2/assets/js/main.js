/* ===================================================================
    
    Author          : Kazi Sahiduzzaman
    Template Name   : Lenda - App Landing HTML Template
    Version         : 1.0
    
* ================================================================= */
(function($) {
    "use strict";

    $(document).ready( function() {


		
		/* ==================================================
			# Accordion Menu
		 =============================================== */

			$(document).on('click','.panel-group .panel',function(e) {
				e.preventDefault();
				$(this).addClass('panel-active').siblings().removeClass('panel-active');
			});

		/* ==================================================
			#  Menu
		 =============================================== */
		
		$(window).scroll(function() {    
			var scroll = $(window).scrollTop();

			//>=, not <=
			if (scroll >= 50) {
			//clearHeader, not clearheader - caps H
			$(".navbar").addClass("fixed-top");
			}else {
				$(".navbar").removeClass("fixed-top");
			}
		}); //missing );
		
		/* ==================================================
			# Smooth Scroll
		 =============================================== */

		const links = document.querySelectorAll(".smooth-menu");

		for (const link of links) {
			link.addEventListener("click", clickHandler);
		}

		function clickHandler(e) {
			e.preventDefault();
			const href = this.getAttribute("href");
			const offsetTop = document.querySelector(href).offsetTop;

			scroll({
				top: offsetTop,
				behavior: "smooth"
			});
		}
		
		/* ==================================================
            # Gallery  Slider
         ===============================================*/
		
		$('.gallery-sldr').owlCarousel({
            loop: true,
            margin:30,
            nav: false,
            navText: [
                "<i class='icofont-long-arrow-left'></i>",
                "<i class='icofont-long-arrow-right'></i>"
            ],
            dots: true,
            autoplay: true,
            responsive: {
                0: {
                    items: 1
                },
                768: {
                    items: 2
                },
                992: {
                    items: 3
                }
            }
        });
		
       
        /* ==================================================
            # Hero Slider Carousel
         ===============================================*/
		
        $('.hero-sldr').owlCarousel({
            loop: true,
            nav: true,
            dots: false,
            autoplay: true,
			autoplayTimeout:9000,
            items: 1,
            navText: [
                "<i class='ti-angle-left'></i>",
                "<i class='ti-angle-right'></i>"
            ],
        });
		
		
		/* ==================================================
			Preloader Init
		 ===============================================*/
		
		$(window).on('load', function() {
			// Animate loader off screen
			$(".se-pre-con").fadeOut("slow");
		});

		
		/* ==================================================
			# Scroll to top
		 =============================================== */
		
        //Get the button
        var mybutton = document.getElementById("scrtop");

        // When the user scrolls down 20px from the top of the document, show the button
        window.onscroll = function() {scrollFunction()};

        function scrollFunction() {
          if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            mybutton.style.display = "block";
          } else {
            mybutton.style.display = "none";
          }
        }
		
    }); // end document ready function
})(jQuery); // End jQuery

