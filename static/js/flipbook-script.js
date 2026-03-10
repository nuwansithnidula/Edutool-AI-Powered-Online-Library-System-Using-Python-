document.addEventListener('DOMContentLoaded', () => {
    
    // 1. HTML එකේ සැඟවූ Input එකෙන් PDF ලින්ක් එක ලබාගැනීම
    const pdfInputElement = document.getElementById('pdfUrlInput');
    const url = pdfInputElement ? pdfInputElement.value : '';
    
    if (!url) {
        document.getElementById('page-info').textContent = "Error: PDF not found!";
        console.error("PDF path is missing!");
        return; 
    }
    
    // Quality එක වැඩි කිරීමට
    const renderScale = 2.0; 

    let pdfDoc = null;
    let totalPages = 0;
    let currentZoom = 1.0;
    let isBookInitialized = false;
    
    const flipbookEl = $('#flipbook');
    const viewport = $('#viewport');

    // PDF.js Worker
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';

    // 2. PDF එක Load කිරීම
    pdfjsLib.getDocument(url).promise.then(async function(pdfDoc_) {
        pdfDoc = pdfDoc_;
        totalPages = pdfDoc.numPages;
        document.getElementById('page-info').textContent = `Loading...`;

        // 🔥 අලුත් වෙනස 1: මුලින්ම පිටු 3ක් පමණක් Load කිරීම (ඉක්මනින් පොත පෙන්වීමට)
        const initialPagesToLoad = Math.min(3, totalPages);
        for (let i = 1; i <= initialPagesToLoad; i++) {
            await renderPage(i);
        }

        // මුල් පිටු 3 ආ සැණින් පොත පණගැන්වීම (පරිශීලකයාට දැන් කියවීමට පටන් ගත හැක)
        initTurnJs();
        document.getElementById('page-info').textContent = `1 / ${totalPages}`;

        // 🔥 අලුත් වෙනස 2: ඉතිරි පිටු ටික Background එකේ Load කිරීම (Lazy Loading)
        if (totalPages > initialPagesToLoad) {
            loadRemainingPages(initialPagesToLoad + 1, totalPages);
        }

    }).catch(function(error) {
        console.error('Error loading PDF:', error);
        document.getElementById('page-info').textContent = "Failed to load PDF";
        alert('PDF ගොනුව විවෘත කිරීමට නොහැකි විය.');
    });

    // 3. පිටු Render කිරීම
    async function renderPage(num) {
        const page = await pdfDoc.getPage(num);
        const viewportRaw = page.getViewport({scale: renderScale});

        const pageDiv = document.createElement('div');
        pageDiv.className = 'page';
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = viewportRaw.width;
        canvas.height = viewportRaw.height;
        canvas.style.width = '100%';
        canvas.style.height = '100%';

        const renderContext = {
            canvasContext: ctx,
            viewport: viewportRaw
        };

        await page.render(renderContext).promise;
        pageDiv.appendChild(canvas);

        // 🔥 අලුත් වෙනස 3: Background එකේ load වන පිටු, Turn.js එකට කෙලින්ම එකතු කිරීම
        if (isBookInitialized) {
            flipbookEl.turn('addPage', $(pageDiv), num);
        } else {
            document.getElementById('flipbook').appendChild(pageDiv);
        }
    }

    // ඉතිරි පිටු එකින් එක පසුබිමින් Load කරන Function එක
    async function loadRemainingPages(start, end) {
        for (let i = start; i <= end; i++) {
            await renderPage(i);
        }
        console.log("All pages loaded successfully in the background.");
    }

    // 4. Turn.js (Flipbook) ආරම්භ කිරීම
    function initTurnJs() {
        const screenH = $(window).height();
        let bookHeight = screenH * 0.85; 
        if (bookHeight > 800) bookHeight = 800; 
        let bookWidth = bookHeight * 0.7; 

        flipbookEl.turn({
            width: bookWidth,
            height: bookHeight,
            autoCenter: false, 
            duration: 1000,
            acceleration: true,
            gradients: true,
            elevation: 50,
            display: 'single', 
            pages: totalPages, // Turn.js එකට මුළු පිටු ගණන කලින්ම දැනුම් දීම
            when: {
                turned: function(e, page) {
                    document.getElementById('page-info').textContent = `${page} / ${totalPages}`;
                }
            }
        });

        isBookInitialized = true;
        updateZoom();

        // Keyboard Support
        $(document).keydown(function(e){
            if (e.keyCode == 37) flipbookEl.turn('previous');
            else if (e.keyCode == 39) flipbookEl.turn('next');
        });
    }

    // 5. Controls Logic
    document.getElementById('prev-btn').addEventListener('click', () => {
        if(isBookInitialized) flipbookEl.turn('previous');
    });

    document.getElementById('next-btn').addEventListener('click', () => {
        if(isBookInitialized) flipbookEl.turn('next');
    });

    // 6. Zoom Logic
    function updateZoom() {
        if(!isBookInitialized) return;

        flipbookEl.css({
            'transform': `scale(${currentZoom})`,
            'transform-origin': '0 0' 
        });

        document.getElementById('zoom-level').textContent = `${Math.round(currentZoom * 100)}%`;

        const currentBookWidth = flipbookEl.width() * currentZoom;
        const currentBookHeight = flipbookEl.height() * currentZoom;
        const viewportW = viewport.width();
        const viewportH = viewport.height();

        let marginLeft = (currentBookWidth < viewportW) ? (viewportW - currentBookWidth) / 2 : 20;
        let marginTop = (currentBookHeight < viewportH) ? (viewportH - currentBookHeight) / 2 : 20;

        flipbookEl.css({
            'margin-left': `${marginLeft}px`,
            'margin-top': `${marginTop}px`,
            'margin-bottom': `${marginTop}px`, 
            'margin-right': `${marginLeft}px`
        });
    }

    document.getElementById('zoom-in').addEventListener('click', () => {
        if (currentZoom < 3.0) { 
            currentZoom += 0.2;
            updateZoom();
        }
    });

    document.getElementById('zoom-out').addEventListener('click', () => {
        // 🔥 අලුත් වෙනස 4: Zoom එක 100% (1.0) ට වඩා අඩුවීම වැළැක්වීම
        if (currentZoom > 1.0) { 
            currentZoom -= 0.2;
            if(currentZoom < 1.0) currentZoom = 1.0; // ආරක්ෂිත පියවරක්
            updateZoom();
        }
    });

    $(window).resize(function() {
        if(isBookInitialized) { updateZoom(); }
    });

    // 7. Fullscreen Logic
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    fullscreenBtn.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            fullscreenBtn.querySelector('i').classList.replace('fa-expand', 'fa-compress');
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
                fullscreenBtn.querySelector('i').classList.replace('fa-compress', 'fa-expand');
            }
        }
    });

    // 8. Theme Toggle
    const themeBtn = document.getElementById('theme-btn');
    if (themeBtn) {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateIcon(savedTheme);
        }

        themeBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme);
        });

        function updateIcon(theme) {
            const icon = themeBtn.querySelector('i');
            if (theme === 'light') {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            } else {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }
        }
    }
});



// ==========================================
// LIBROJET PAGE PRELOADER LOGIC
// ==========================================

window.addEventListener('load', () => {
    const preloader = document.getElementById('libro-preloader');
    if (preloader) {
        // පිටුව ලෝඩ් වූ පසු තවත් කුඩා කාලයක් (තත්පර 0.4ක්) පෙන්වා මැකී යාමට (Smoothness එක සඳහා)
        setTimeout(() => {
            preloader.classList.add('preloader-hidden');
            
            // Animation එක අවසන් වූ පසු HTML DOM එකෙන් සම්පූර්ණයෙන්ම ඉවත් කිරීම
            setTimeout(() => {
                preloader.remove();
            }, 600); // CSS Transition කාලයට සමාන වේලාවක් (0.6s)
            
        }, 400); 
    }
});