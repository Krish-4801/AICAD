// AICAD Presentation Logic

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // Slide Navigation State
    // ---------------------------------------------------------
    const slides = document.querySelectorAll('.slide-card');
    const totalSlides = slides.length;
    let currentSlideIndex = 0;

    const currentSlideNumSpan = document.getElementById('current-slide-num');
    const totalSlidesNumSpan = document.getElementById('total-slides-num');
    const indicatorsContainer = document.getElementById('indicators-container');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    totalSlidesNumSpan.textContent = totalSlides;

    // Create pagination dots
    for (let i = 0; i < totalSlides; i++) {
        const dot = document.createElement('div');
        dot.classList.add('indicator-dot');
        if (i === 0) dot.classList.add('active');
        dot.addEventListener('click', () => {
            goToSlide(i);
        });
        indicatorsContainer.appendChild(dot);
    }
    const dots = document.querySelectorAll('.indicator-dot');

    // Navigation function
    function goToSlide(index) {
        if (index < 0 || index >= totalSlides) return;
        
        // Deactivate current slide
        slides[currentSlideIndex].classList.remove('active');
        dots[currentSlideIndex].classList.remove('active');

        // Activate new slide
        currentSlideIndex = index;
        slides[currentSlideIndex].classList.add('active');
        dots[currentSlideIndex].classList.add('active');

        // Update indicators
        currentSlideNumSpan.textContent = currentSlideIndex + 1;
        
        // Update URL hash
        window.location.hash = `slide-${currentSlideIndex + 1}`;

        // Disable/enable controls
        btnPrev.disabled = currentSlideIndex === 0;
        btnNext.disabled = currentSlideIndex === totalSlides - 1;
    }

    // Hash routing
    function handleHashRoute() {
        const hash = window.location.hash;
        if (hash) {
            const match = hash.match(/^#slide-(\d+)$/);
            if (match) {
                const slideNum = parseInt(match[1], 10);
                if (slideNum >= 1 && slideNum <= totalSlides) {
                    goToSlide(slideNum - 1);
                    return;
                }
            }
        }
        goToSlide(0);
    }

    // Button event listeners
    btnPrev.addEventListener('click', () => {
        goToSlide(currentSlideIndex - 1);
    });

    btnNext.addEventListener('click', () => {
        goToSlide(currentSlideIndex + 1);
    });

    // Keyboard event listeners
    document.addEventListener('keydown', (e) => {
        // Only navigate if user is not typing in a code block or elsewhere (no inputs here, but good practice)
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.key === 'ArrowRight' || e.key === 'Space' || e.key === 'Enter') {
            e.preventDefault();
            if (currentSlideIndex < totalSlides - 1) {
                goToSlide(currentSlideIndex + 1);
            }
        } else if (e.key === 'ArrowLeft' || e.key === 'Backspace') {
            e.preventDefault();
            if (currentSlideIndex > 0) {
                goToSlide(currentSlideIndex - 1);
            }
        }
    });

    // Handle initial load and hash change
    window.addEventListener('hashchange', handleHashRoute);
    handleHashRoute();

    // ---------------------------------------------------------
    // Slide 6: Case Studies Gallery Logic
    // ---------------------------------------------------------
    const galleryItems = document.querySelectorAll('.gallery-item-desc');
    const gallerySlides = document.querySelectorAll('.gallery-slide');
    const galleryTitle = document.getElementById('gallery-title');
    const btnGalleryPrev = document.getElementById('btn-gallery-prev');
    const btnGalleryNext = document.getElementById('btn-gallery-next');

    let currentGalleryIndex = 0;
    const galleryData = [
        { key: 'engine', title: '1. Parametric Engine Cylinder' },
        { key: 'bracket', title: '2. L-Bracket Mounting Plate' },
        { key: 'nut', title: '3. M5 Hexagonal Clearance Nut' }
    ];

    function updateGallery(index) {
        if (index < 0 || index >= galleryData.length) return;

        // Deactivate previous active gallery elements
        galleryItems[currentGalleryIndex].classList.remove('active');
        gallerySlides[currentGalleryIndex].classList.remove('active');

        currentGalleryIndex = index;

        // Activate new gallery elements
        galleryItems[currentGalleryIndex].classList.add('active');
        gallerySlides[currentGalleryIndex].classList.add('active');
        galleryTitle.textContent = galleryData[currentGalleryIndex].title;
    }

    // Left descriptions clicks
    galleryItems.forEach((item, index) => {
        item.addEventListener('click', () => {
            updateGallery(index);
        });
    });

    // Gallery navigation buttons
    btnGalleryPrev.addEventListener('click', (e) => {
        e.stopPropagation();
        let newIndex = currentGalleryIndex - 1;
        if (newIndex < 0) newIndex = galleryData.length - 1;
        updateGallery(newIndex);
    });

    btnGalleryNext.addEventListener('click', (e) => {
        e.stopPropagation();
        let newIndex = currentGalleryIndex + 1;
        if (newIndex >= galleryData.length) newIndex = 0;
        updateGallery(newIndex);
    });
});
