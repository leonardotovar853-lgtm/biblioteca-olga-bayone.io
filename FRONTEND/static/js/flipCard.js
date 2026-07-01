function flipCard(btn) {
    // Busca al "padre" que es el .libro-card-inner y le pone/quita la clase is-flipped
    const cardInner = btn.closest('.libro-card-inner');
    cardInner.classList.toggle('is-flipped');
}
