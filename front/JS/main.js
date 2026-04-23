const track = document.querySelector(".carousel-track");

if (track) {
    fetch("https://test-website-f5nx.onrender.com/")
        .then(res => res.json())
        .then(projects => {
            
            projects.forEach(project => {
                const slide = document.createElement("div");
                slide.className = "carousel-slide";
                slide.style.position = "relative";
                slide.innerHTML = `
                    <img src="${project.image}" class="slide-image" style="width: 100%; height: 100%; object-fit: cover; filter: brightness(0.6); display: block;">
                    
                    <div class="carousel-caption" style="position: absolute; top: 50%; transform: translateY(-50%); left: 8%; color: white; max-width: 55%; text-align: left; padding-right: 20px;">
                        <h2 style="font-size: 36px; margin-bottom: 15px; letter-spacing: 2px; text-shadow: 2px 2px 5px rgba(0,0,0,0.8);">${project.title}</h2>
                        <p style="font-size: 18px; line-height: 1.6; color: #eee; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); margin: 0;">${project.content.substring(0, 45)}...</p>
                    </div>
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
