document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. TAB SWITCHING LOGIC ---
    window.switchTab = function(tabName) {
    // ... (පෙර තිබූ Active Class මාරු කරන කේතයන් එලෙසම තබන්න) ...
        document.querySelectorAll('.sidebar-nav li').forEach(li => li.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));

        const selectedTab = document.getElementById(`${tabName}-tab`);
        if (selectedTab) selectedTab.classList.add('active');

        // NEW: Wishlist එක තෝරා ගත්තේ නම් දත්ත ලෝඩ් කරන්න
        if (tabName === 'wishlist') {
            fetchWishlist();
        }
    };


    // --- 2. INPUT ACTIVATION LOGIC ---
    const editableInputs = document.querySelectorAll('.editable-input');
    const updateBtn = document.getElementById('update-btn');
    
    // Store initial values to compare later
    let initialData = {};
    editableInputs.forEach(input => {
        initialData[input.id] = input.value;
    });

    // Handle Click to Edit
    editableInputs.forEach(input => {
        // Add click listener to the parent container for better UX
        const container = input.closest('.dash-input-group');
        
        container.addEventListener('click', () => {
            // Enable editing
            input.removeAttribute('readonly');
            input.focus();
            container.classList.add('active-input');
        });

        // Detect changes
        input.addEventListener('input', checkForChanges);
        
        // On blur (focus lost), if value unchanged, make readonly again
        input.addEventListener('blur', () => {
            if (input.value === initialData[input.id]) {
                input.setAttribute('readonly', true);
                container.classList.remove('active-input');
            }
            // If changed, keep it active/editable looking
        });
    });

    // --- 3. PHOTO UPLOAD LOGIC ---
    const photoWrapper = document.getElementById('photo-wrapper');
    const fileInput = document.getElementById('profile-upload');
    const previewImg = document.getElementById('profile-preview');
    let isPhotoChanged = false;

    photoWrapper.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                isPhotoChanged = true;
                checkForChanges(); // Trigger button check
            }
            reader.readAsDataURL(file);
        }
    });

    // --- 4. CHECK FOR CHANGES & SHOW BUTTON ---
    function checkForChanges() {
        let hasChanges = false;
        
        // Check text inputs
        editableInputs.forEach(input => {
            if (input.value !== initialData[input.id]) {
                hasChanges = true;
            }
        });

        // Check photo
        if (isPhotoChanged) hasChanges = true;

        // Toggle button visibility
        if (hasChanges) {
            updateBtn.classList.remove('hidden');
        } else {
            updateBtn.classList.add('hidden');
        }
    }

    // --- 5. UPDATE BUTTON CLICK (SEND TO PYTHON BACKEND) ---
    // --- 5. UPDATE BUTTON CLICK (SEND TO PYTHON BACKEND) ---
    updateBtn.addEventListener('click', async () => {
        const formData = new FormData();
        
        // Append text data
        formData.append('first_name', document.getElementById('fname').value);
        formData.append('last_name', document.getElementById('lname').value);
        formData.append('birthday', document.getElementById('dob').value);
        formData.append('email', document.getElementById('email').value); // ID purposes

        // Append file if changed
        if (isPhotoChanged && fileInput.files[0]) {
            formData.append('profile_image', fileInput.files[0]);
        }

        updateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Updating...';

        // updateBtn.addEventListener ඇතුළත fetch කොටස මෙලෙස වෙනස් කරන්න
        // updateBtn.addEventListener('click', async () => { ... ඇතුළත ඇති fetch කොටස
        try {
            const response = await fetch('/update-profile', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                alert('Profile updated successfully!');

                // පින්තූරයක් upload කර ඇත්නම් සහ Backend එකෙන් අලුත් ලින්ක් එක ආවා නම්
                if (result.new_image_url) {
                    // බ්‍රව්සරයේ cache එක මඟහැර අලුත්ම පින්තූරයම load කිරීමට ?t= එකතු කිරීම
                    const newImagePath = result.new_image_url + "?t=" + new Date().getTime();

                    // 1. Profile Page එකේ පින්තූරය වෙනස් කිරීම
                    const profilePreview = document.getElementById('profile-preview');
                    if (profilePreview) {
                        profilePreview.src = newImagePath;
                    }

                    // 2. Base.html හි ඇති Desktop Menu පින්තූරය වෙනස් කිරීම
                    const desktopHeaderImg = document.getElementById('profileTrigger');
                    if (desktopHeaderImg) {
                        desktopHeaderImg.src = newImagePath;
                    }

                    // 3. Base.html හි ඇති Mobile Menu පින්තූරය වෙනස් කිරීම
                    const mobileHeaderImg = document.querySelector('.mobile-profile-img');
                    if (mobileHeaderImg) {
                        mobileHeaderImg.src = newImagePath;
                    }
                }

                // Button එක සැඟවීම සහ input සාමාන්‍ය තත්වයට පත් කිරීම
                updateBtn.classList.add('hidden');
                // අනෙකුත් input reset කේත...
                
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error updating profile:', error);
        }
    });
});


// --- WISHLIST FUNCTIONALITY ---


// 2. දත්ත ලබා ගන්නා ෆන්ෂන් එක
async function fetchWishlist() {
    const container = document.getElementById('wishlist-container');
    const loader = document.getElementById('wishlist-loading');
    const emptyMsg = document.getElementById('wishlist-empty');

    // UI Reset
    container.innerHTML = '';
    emptyMsg.classList.add('hidden');
    loader.style.display = 'block';

    try {
        const response = await fetch('/api/wishlist'); // ඔබේ Python API එක
        const data = await response.json();

        loader.style.display = 'none';

        if (!data.books || data.books.length === 0) {
            emptyMsg.classList.remove('hidden');
            return;
        }

        // Generate HTML Cards
        data.books.forEach(book => {
            const bookId = book.id || book._id;
            const imgUrl = book.thumbnail || "https://placehold.co/120x160?text=No+Cover";
            
            const cardHTML = `
                <div class="wishlist-card-horizontal" id="card-${bookId}">
                    <div class="w-card-img">
                        <img src="${imgUrl}" alt="${book.title}">
                    </div>
                    <div class="w-card-info">
                        <h4 class="w-card-title">${book.title}</h4>
                        <p class="w-card-author">By <span>${book.authors || 'Unknown'}</span></p>
                        
                        <button class="w-remove-btn" onclick="removeFromWishlist('${bookId}')" title="Remove">
                           <i class="fa-solid fa-xmark"></i>
                        </button>
                    </div>
                    <a href="/book/${bookId}" style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:1;" onclick="if(event.target.closest('button')) event.preventDefault();"></a>
                </div>
            `;
            container.innerHTML += cardHTML;
        });

    } catch (error) {
        console.error("Error loading wishlist:", error);
        loader.style.display = 'none';
        container.innerHTML = '<p style="color:red; text-align:center;">Failed to load wishlist.</p>';
    }
}

// 3. අයිතමයක් ඉවත් කිරීම (Remove)
// 3. අයිතමයක් ඉවත් කිරීම (Remove)
async function removeFromWishlist(bookId) {
    // පරණ confirm() කොටුව මෙතැනින් ඉවත් කර ඇත

    try {
        const response = await fetch('/api/wishlist/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ book_id: bookId })
        });

        const result = await response.json();

        if (result.action === 'removed') {
            // 👇 අලංකාර Toast පණිවිඩය 👇
            alert("Item successfully removed from wishlist.");

            const card = document.getElementById(`card-${bookId}`);
            if (card) {
                card.style.opacity = '0';
                setTimeout(() => {
                    card.remove();
                    if (document.getElementById('wishlist-container').children.length === 0) {
                        document.getElementById('wishlist-empty').classList.remove('hidden');
                    }
                }, 300);
            }
        } else {
            alert("Failed to remove item.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to connect to the server.");
    }
}