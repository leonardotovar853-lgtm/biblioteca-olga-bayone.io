const menuToggle = document.querySelector('.menu-toggle');
const options = document.querySelector('.options');

menuToggle.addEventListener('click', () => {
    options.classList.toggle('active');
    menuToggle.classList.toggle('active');
});

document.addEventListener('click', (event) => {
    if (!menuToggle.contains(event.target) && !options.contains(event.target)) {
        options.classList.remove('active');
        menuToggle.classList.remove('active');
    }
});


