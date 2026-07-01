
function darLike(id) {
    let likeCount = document.getElementById(`count-${id}`);
    let currentLikes = parseInt(likeCount.textContent);
    likeCount.textContent = currentLikes + 1;
}