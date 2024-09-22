<script>
    document.addEventListener("DOMContentLoaded", function() {
        const blogCards = document.querySelectorAll('.blog-card');

        blogCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                // Добавляем класс тряски к другим карточкам
                blogCards.forEach(otherCard => {
                    if (otherCard !== card) {
                        otherCard.classList.add('shake');
                    }
                });
            });

            card.addEventListener('mouseleave', () => {
                // Убираем класс тряски
                blogCards.forEach(otherCard => {
                    otherCard.classList.remove('shake');
                });
            });
        });
    });
</script>
