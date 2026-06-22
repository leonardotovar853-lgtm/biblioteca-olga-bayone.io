const menuToggle = document.querySelector('.menu-toggle');
const options = document.querySelector('.options');
const navLinks = document.querySelectorAll('.options a');

function setMenuState(open) {
    options.classList.toggle('active', open);
    menuToggle.classList.toggle('active', open);
    menuToggle.setAttribute('aria-expanded', String(open));
}

menuToggle.addEventListener('click', () => {
    setMenuState(!options.classList.contains('active'));
});

navLinks.forEach(link => {
    link.addEventListener('click', () => {
        setMenuState(false);
    });
});

document.addEventListener('click', (event) => {
    if (!menuToggle.contains(event.target) && !options.contains(event.target)) {
        setMenuState(false);
    }
});


