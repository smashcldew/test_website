const track = document.querySelector(".carousel-track");

if (track) {
    fetch("../back/data.json")
        .then(res => res.json())
        .then(projects => {
            
            projects.forEach(project => {
                const slide = document.createElement("div");
                slide.className = "carousel-slide";
                slide.innerHTML = `
                    <img src="${project.image}" class="slide-image">
                    `;
                track.appendChild(slide);
            });

            const slides = document.querySelectorAll(".carousel-slide");
            const prevBtn = document.getElementById("prev-btn");
            const nextBtn = document.getElementById("next-btn");
            const dotsContainer = document.getElementById("carousel-dots");

            let index = 0;
            
            projects.forEach((_, i) => {
                const dot = document.createElement("span");
                dot.className = "dot";

                if (i === 0) dot.classList.add("active");

                dot.addEventListener("click", () => {
                    showSlide(i);
                });
                dotsContainer.appendChild(dot);
            });

            function showSlide(i) {
                index = i;
                
                if (index >= slides.length) index = 0;
                if (index < 0) index = slides.length - 1;

                track.style.transform = `translateX(-${index * 100}%)`;

                const dots = document.querySelectorAll(".dot");
                dots.forEach(dot => dot.classList.remove("active"));
                dots[index].classList.add("active");
            }

            let interval = setInterval(() => {
                showSlide(index + 1);
            }, 3000);

            track.addEventListener("mouseenter", () => {
                clearInterval(interval);
            });

            track.addEventListener("mouseleave", () => {
                interval = setInterval(() => {
                    showSlide(index + 1);
                }, 3000);
            });

            if (prevBtn && nextBtn) {
                nextBtn.addEventListener("click", () => {
                    showSlide(index + 1);
                });
                prevBtn.addEventListener("click", () => {
                    showSlide(index - 1);
                });
            }
        });
}
