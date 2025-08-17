document.addEventListener("DOMContentLoaded", function () {
    const carousel = document.querySelector("#carouselExampleCaptions");
    const items = carousel.querySelectorAll(".carousel-item");
    const indicators = carousel.querySelectorAll(".carousel-indicators button");

    let currentIndex = 0;
    const totalItems = items.length;

    function showSlide(index) {
        items.forEach((item, i) => {
            item.classList.remove("active");
            indicators[i].classList.remove("active");
        });
        items[index].classList.add("active");
        indicators[index].classList.add("active");
        currentIndex = index;
    }

    function nextSlide() {
        let nextIndex = (currentIndex + 1) % totalItems;
        showSlide(nextIndex);
    }

    function prevSlide() {
        let prevIndex = (currentIndex - 1 + totalItems) % totalItems;
        showSlide(prevIndex);
    }

    // Next/Prev button functionality
    const nextBtn = carousel.querySelector(".carousel-control-next");
    const prevBtn = carousel.querySelector(".carousel-control-prev");

    nextBtn.addEventListener("click", () => {
        nextSlide();
    });

    prevBtn.addEventListener("click", () => {
        prevSlide();
    });

    // Indicator click
    indicators.forEach((btn, index) => {
        btn.addEventListener("click", () => {
            showSlide(index);
        });
    });

    // Auto slide (every 5s)
    setInterval(nextSlide, 5000);
});
