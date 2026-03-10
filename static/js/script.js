document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Theme Toggle Logic ---
    const themeBtn = document.getElementById('theme-btn');
    // themeBtn තිබේ නම් පමණක් ක්‍රියාත්මක කරන්න
    if (themeBtn) {
        const themeIcon = themeBtn.querySelector('i');
        const htmlElement = document.documentElement;

        // Check Local Storage
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            htmlElement.setAttribute('data-theme', savedTheme);
            updateIcon(savedTheme, themeIcon);
        }

        themeBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme, themeIcon);
        });

        function updateIcon(theme, icon) {
            if (!icon) return;
            if (theme === 'light') {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            } else {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }
        }
    }

    // --- 2. Interactive Search ---
    const searchInput = document.querySelector('.search-wrapper input');
    const ctaHeading = document.querySelector('.cta-box h2');
    
    if(searchInput && ctaHeading) {
        const originalCtaText = ctaHeading.innerText;
        searchInput.addEventListener('input', (e) => {
            const val = e.target.value;
            if(val.length > 0) {
                ctaHeading.innerHTML = `Searching for <span style="color:var(--accent-secondary)">"${val}"</span>...`;
            } else {
                ctaHeading.innerText = originalCtaText;
            }
        });
    }

    // --- 3. Button Ripple/Scale Effect ---
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            if(this.id === 'theme-btn') return;
            this.style.transform = "scale(0.92)";
            setTimeout(() => {
                this.style.transform = "scale(1)";
            }, 150);
        });
    });

    // --- 4. Wishlist Toggle ---
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation(); 
            const icon = btn.querySelector('i');
            btn.classList.toggle('active');
            
            if (icon.classList.contains('fa-regular')) {
                icon.classList.remove('fa-regular');
                icon.classList.add('fa-solid');
            } else {
                icon.classList.remove('fa-solid');
                icon.classList.add('fa-regular');
            }
        });
    });

    // --- 5. File Upload ---
    const uploadTrigger = document.getElementById('upload-trigger');
    const fileInput = document.getElementById('file-input');

    if (uploadTrigger && fileInput) {
        uploadTrigger.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const fileName = e.target.files[0].name;
                alert(`Preparing upload for: ${fileName}`);
            }
        });
    }
    
    // --- 6. 3D Tilt Effect ---
    const cards = document.querySelectorAll('.book-card, .cat-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const xRot = ((y - rect.height / 2) / rect.height) * -5; 
            const yRot = ((x - rect.width / 2) / rect.width) * 5; 
            
            card.style.transform = `perspective(1000px) rotateX(${xRot}deg) rotateY(${yRot}deg) scale(1.02)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });

    // --- 7. Enhanced Password Visibility Toggle (Global) ---
    const passwordToggles = document.querySelectorAll('.toggle-password-icon');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            
            if (input) {
                const isPassword = input.getAttribute('type') === 'password';
                input.setAttribute('type', isPassword ? 'text' : 'password');
                
                this.classList.toggle('fa-eye');
                this.classList.toggle('fa-eye-slash');
                
                input.style.borderColor = 'var(--accent-secondary)';
                setTimeout(() => input.style.borderColor = '', 500);
            }
        });
    });

    // --- 8. Hamburger Menu Logic (FIXED) ---
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const navMenu = document.getElementById('nav-menu');
    
    if (hamburgerBtn && navMenu) {
        // Icon එක සොයාගැනීම (HTML එකේ icon එක නැති වුනොත් දෝෂ මගහැරීමට optional chaining භාවිතා කිරීම හොදයි)
        const icon = hamburgerBtn.querySelector('i');
        
        hamburgerBtn.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            
            // Icon Animation
            if (icon) {
                if (navMenu.classList.contains('active')) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-xmark');
                    document.body.style.overflow = 'hidden'; // Stop scrolling
                } else {
                    icon.classList.remove('fa-xmark');
                    icon.classList.add('fa-bars');
                    document.body.style.overflow = 'auto'; // Resume scrolling
                }
            }
        });

        // Close menu when a link is clicked
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                if (icon) {
                    icon.classList.remove('fa-xmark');
                    icon.classList.add('fa-bars');
                }
                document.body.style.overflow = 'auto';
            });
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!navMenu.contains(e.target) && !hamburgerBtn.contains(e.target) && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                if (icon) {
                    icon.classList.remove('fa-xmark');
                    icon.classList.add('fa-bars');
                }
                document.body.style.overflow = 'auto';
            }
        });
    }

    // --- 9. Profile Dropdown Logic (User Menu) ---
    const profileTrigger = document.getElementById('profileTrigger');
    const profileDropdown = document.getElementById('profileDropdown');

    if (profileTrigger && profileDropdown) {
        profileTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            profileDropdown.classList.toggle('active');
        });

        document.addEventListener('click', (e) => {
            if (!profileDropdown.contains(e.target) && e.target !== profileTrigger) {
                profileDropdown.classList.remove('active');
            }
        });
        
        profileDropdown.addEventListener('click', (e) => {
             e.stopPropagation();
        });
    }

    // --- 10. Forgot Password Logic ---
    const forgotForm = document.getElementById('forgot-password-form');
    // අවශ්‍ය නම් මෙහි Logic එක uncomment කර ගන්න.

    console.log("LibroJet scripts loaded successfully.");


// --- 11. Password Match Validation (Sign Up) ---
    const signupPass = document.getElementById('signup-pass');
    const signupConfirm = document.getElementById('signup-confirm');

    if (signupPass && signupConfirm) {
        
        function validateMatch() {
            const passVal = signupPass.value;
            const confirmVal = signupConfirm.value;

            // Confirm Password field එක හිස් නම් සාමාන්‍ය පරිදි තබන්න
            if (confirmVal.length === 0) {
                signupConfirm.style.borderColor = '';
                signupConfirm.style.boxShadow = 'none';
                return;
            }

            // Password දෙක සමානදැයි පරීක්ෂා කිරීම
            if (passVal === confirmVal) {
                // සමාන නම් - කොළ පාට (Green)
                signupConfirm.style.borderColor = '#22c55e'; // Green Color
                signupConfirm.style.boxShadow = '0 0 10px rgba(34, 197, 94, 0.3)';
            } else {
                // අසමාන නම් - රතු පාට (Red)
                signupConfirm.style.borderColor = '#ef4444'; // Red Color
                signupConfirm.style.boxShadow = '0 0 10px rgba(239, 68, 68, 0.3)';
            }
        }

        // Input කරන සෑම විටම පරීක්ෂා කරන්න
        signupConfirm.addEventListener('input', validateMatch);
        
        // ප්‍රධාන Password එක වෙනස් කළොත් නැවත check කරන්න
        signupPass.addEventListener('input', validateMatch);
    }



});

// --- Flash Messages Auto-Hide Logic ---
document.addEventListener('DOMContentLoaded', () => {
    // තිරයේ ඇති සියලුම alert (Flash messages) සොයා ගැනීම
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // තත්පර 5ක් (මිලි තත්පර 5000ක්) රැඳී සිටීම
        setTimeout(() => {
            // Smooth ලෙස මැකී යාමට (Fade out)
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)'; // මඳක් ඉහළට ගොස් මැකී යාම
            
            // Fade out වූ පසු HTML වලින් සම්පූර්ණයෙන්ම ඉවත් කිරීම
            setTimeout(() => {
                alert.remove();
            }, 500); 
            
        }, 5000); // මෙහි 5000 යනු තත්පර 5යි. ඔබට අවශ්‍ය නම් වෙනස් කරගත හැක.
    });
});



// static/js/script.js හි අගට මෙය එකතු කරන්න

// --- 👇 Modern Toast Notification Logic 👇 ---
document.addEventListener('DOMContentLoaded', () => {
    // තිරයේ ඇති සියලුම Toast පණිවිඩ සොයා ගැනීම
    const toasts = document.querySelectorAll('.toast-card');
    
    toasts.forEach(toast => {
        // තත්පර 5ක් (මිලි තත්පර 5000ක්) රැඳී සිටීම
        setTimeout(() => {
            hideToast(toast); // පණිවිඩය සඟවන Function එක
        }, 5000); 
    });
});

// පණිවිඩය අලංකාරව සඟවන Function එක
function hideToast(toastElement) {
    if (!toastElement) return;
    
    // CSS හි ඇති 'hide' class එක එක් කිරීම (එවිට Fade-out animation එක ක්‍රියාත්මක වේ)
    toastElement.classList.add('hide');
    
    // Animation එක අවසන් වූ පසු (තත්පර 0.4 කින්) HTML වලින් සම්පූර්ණයෙන්ම ඉවත් කිරීම
    setTimeout(() => {
        toastElement.remove();
        
        // (Optional) Toast container එක හිස් නම් එය සම්පූර්ණයෙන්ම සඟවමු
        const container = document.getElementById('toastContainer');
        if (container && container.children.length === 0) {
            // container.style.display = 'none';
        }
    }, 400); 
}

// Close (X) බොත්තම එබූ විට ක්‍රියාත්මක වන Function එක
function closeToast(buttonElement) {
    // බොත්තම අයිති Toast Card එක සොයාගෙන එය සඟවන්න
    const toast = buttonElement.closest('.toast-card');
    hideToast(toast);
}
// ------------------------------------------------




// ==========================================
// OVERRIDE DEFAULT BROWSER ALERT WITH MODERN TOAST
// ==========================================

window.alert = function(message) {
    // 1. Toast Container එක පිටුවේ නැත්නම් එය අලුතින් සෑදීම
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    // 2. පණිවිඩයේ වචන අනුව වර්ණය සහ අයිකනය ස්වයංක්‍රීයව තේරීම
    let category = 'info';
    let iconClass = 'fa-circle-info';
    let lowerMsg = message.toLowerCase();

    if (lowerMsg.includes('success')) {
        category = 'success';
        iconClass = 'fa-circle-check';
    } else if (lowerMsg.includes('error') || lowerMsg.includes('fail') || lowerMsg.includes('wrong')) {
        category = 'error';
        iconClass = 'fa-circle-xmark';
    } else if (lowerMsg.includes('please') || lowerMsg.includes('warning') || lowerMsg.includes('sorry')) {
        category = 'warning';
        iconClass = 'fa-triangle-exclamation';
    }

    // 3. අලුත් Toast HTML එක නිර්මාණය කිරීම
    const toast = document.createElement('div');
    toast.className = `toast-card glass-toast ${category}`;
    toast.setAttribute('role', 'alert');
    
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fa-solid ${iconClass}"></i>
        </div>
        <div class="toast-content">
            <p class="toast-message">${message}</p>
        </div>
        <button type="button" class="toast-close" onclick="closeToast(this)" title="Close">
            <i class="fa-solid fa-xmark"></i>
        </button>
        <div class="toast-progress"></div>
    `;

    // 4. Container එකට Toast එක ඇතුළත් කිරීම
    container.appendChild(toast);

    // 5. තත්පර 5කින් පසු එය ස්වයංක්‍රීයව මැකී යාමට සැලැස්වීම
    setTimeout(() => {
        if (typeof hideToast === 'function') {
            hideToast(toast); // කලින් හැදූ function එක කෝල් කිරීම
        } else {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 400);
        }
    }, 5000);
};



// ==========================================
// LIBROJET PAGE PRELOADER LOGIC (ONCE PER SESSION)
// ==========================================

// පිටුව Load වෙන්න පටන් ගන්නා විටම මෙය ක්‍රියාත්මක වේ
const preloader = document.getElementById('libro-preloader');

if (preloader) {
    // Session Storage එකේ 'preloader_shown' කියා එකක් ඇත්දැයි බැලීම
    if (!sessionStorage.getItem('librojet_preloader_shown')) {
        
        // පළමු වතාවට පැමිණි විට පමණක් Animation එක පෙන්වීම
        window.addEventListener('load', () => {
            setTimeout(() => {
                preloader.classList.add('preloader-hidden');
                
                setTimeout(() => {
                    preloader.remove();
                    // Preloader එක පෙන්වූ බව බ්‍රවුසරයේ මතකයට දැමීම
                    sessionStorage.setItem('librojet_preloader_shown', 'true');
                }, 600); 
                
            }, 800); // තත්පර 0.8 ක් අලංකාරව පෙන්වා මැකී යාමට සැලැස්වීම
        });

    } else {
        // මීට පෙර අඩවියට පැමිණ තිබේ නම්, ක්ෂණිකවම Preloader එක මකා දැමීම (Animation රහිතව)
        preloader.style.display = 'none';
        preloader.remove();
    }
}