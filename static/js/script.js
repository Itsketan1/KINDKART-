/* =====================================================
   KindKart Main JavaScript
   Version: 1.0
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    initializeTheme();

    initializeMobileMenu();

    initializeSmoothScroll();

    initializeActiveNavigation();

    initializeScrollAnimation();

    initializeCounters();

});

/* =====================================================
   DARK MODE
===================================================== */

function initializeTheme() {

    const button = document.getElementById("themeToggle");

    if (!button) return;

    const body = document.body;

    const icon = button.querySelector("i");

    const savedTheme = localStorage.getItem("kindkart-theme");

    if (savedTheme === "dark") {

        body.classList.add("dark");

        icon.classList.remove("fa-moon");

        icon.classList.add("fa-sun");

    }

    button.addEventListener("click", () => {

        body.classList.toggle("dark");

        if (body.classList.contains("dark")) {

            localStorage.setItem("kindkart-theme", "dark");

            icon.classList.remove("fa-moon");

            icon.classList.add("fa-sun");

        } else {

            localStorage.setItem("kindkart-theme", "light");

            icon.classList.remove("fa-sun");

            icon.classList.add("fa-moon");

        }

    });

}

/* =====================================================
   MOBILE MENU
===================================================== */

function initializeMobileMenu() {

    const menuButton = document.getElementById("menuBtn");

    const navigation = document.querySelector(".nav-links");

    if (!menuButton || !navigation) return;

    menuButton.addEventListener("click", () => {

        navigation.classList.toggle("show-menu");

    });

}

/* =====================================================
   SMOOTH SCROLL
===================================================== */

function initializeSmoothScroll() {

    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {

        link.addEventListener("click", function (e) {

            const target = document.querySelector(this.getAttribute("href"));

            if (!target) return;

            e.preventDefault();

            target.scrollIntoView({

                behavior: "smooth"

            });

        });

    });

}

/* =====================================================
   ACTIVE NAVIGATION
===================================================== */

function initializeActiveNavigation() {

    const currentPath = window.location.pathname;

    const navLinks = document.querySelectorAll(".nav-links a");

    navLinks.forEach(link => {

        if (link.getAttribute("href") === currentPath) {

            link.classList.add("active-link");

        }

    });

}

/* =====================================================
   SCROLL ANIMATION
===================================================== */

function initializeScrollAnimation() {

    const elements = document.querySelectorAll(

        ".feature-card,.campaign-card,.section-header"

    );

    if (!("IntersectionObserver" in window)) {

        elements.forEach(element => {

            element.classList.add("visible");

        });

        return;

    }

    const observer = new IntersectionObserver(

        entries => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {

                    entry.target.classList.add("visible");

                    observer.unobserve(entry.target);

                }

            });

        },

        {

            threshold: 0.15

        }

    );

    elements.forEach(element => {

        observer.observe(element);

    });

}

/* =====================================================
   COUNTER ANIMATION
===================================================== */

function initializeCounters() {

    const counters = document.querySelectorAll(".hero-stats h2");

    if (counters.length === 0) return;

    counters.forEach(counter => {

        const text = counter.innerText;

        const target = parseInt(text.replace(/\D/g, ""));

        if (isNaN(target)) return;

        let value = 0;

        const step = Math.max(1, Math.ceil(target / 100));

        const interval = setInterval(() => {

            value += step;

            if (value >= target) {

                value = target;

                clearInterval(interval);

            }

            if (text.includes("+")) {

                counter.innerText = value + "+";

            } else {

                counter.innerText = value;

            }

        }, 20);

    });

}

/* =====================================================
   TOAST NOTIFICATION
===================================================== */

function showToast(message, type = "success") {

    const toast = document.createElement("div");

    toast.className = `toast ${type}`;

    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => {

        toast.classList.add("show");

    }, 100);

    setTimeout(() => {

        toast.classList.remove("show");

        setTimeout(() => {

            toast.remove();

        }, 400);

    }, 3000);

}

/* =====================================================
   SCROLL TO TOP
===================================================== */

const scrollButton = document.createElement("button");

scrollButton.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';

scrollButton.className = "scroll-top";

document.body.appendChild(scrollButton);

window.addEventListener("scroll", () => {

    if (window.scrollY > 300) {

        scrollButton.classList.add("show");

    } else {

        scrollButton.classList.remove("show");

    }

});

scrollButton.addEventListener("click", () => {

    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

});