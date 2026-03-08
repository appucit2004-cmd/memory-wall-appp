/**
 * Digital Memory Wall - Frontend JavaScript
 * Handles form validation, photo preview, animations
 */

document.addEventListener('DOMContentLoaded', () => {
    initPhotoUpload();
    initMemoryForm();
    initScrollAnimations();
});

// ========== Photo Upload with Preview ==========
function initPhotoUpload() {
    const photoInput = document.getElementById('photo');
    const uploadArea = document.getElementById('photoUploadArea');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const removePreview = document.getElementById('removePreview');

    if (!photoInput || !uploadArea) return;

    uploadArea.addEventListener('click', () => photoInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length && files[0].type.startsWith('image/')) {
            photoInput.files = files;
            showPreview(files[0]);
        }
    });

    photoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            showPreview(file);
        }
    });

    if (removePreview) {
        removePreview.addEventListener('click', (e) => {
            e.stopPropagation();
            photoInput.value = '';
            uploadPlaceholder.style.display = 'block';
            imagePreview.style.display = 'none';
        });
    }

    function showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            uploadPlaceholder.style.display = 'none';
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// ========== Memory Form Submission ==========
function initMemoryForm() {
    const form = document.getElementById('memoryForm');
    const messageInput = document.getElementById('message');
    const wordCountEl = document.getElementById('wordCount');
    const wordErrorEl = document.getElementById('wordError');
    const submitBtn = document.getElementById('submitBtn');
    const successModal = document.getElementById('successModal');

    if (!form) return;

    // Word counter
    if (messageInput && wordCountEl) {
        messageInput.addEventListener('input', () => {
            const text = messageInput.value.trim();
            const words = text ? text.split(/\s+/).filter(w => w.length > 0).length : 0;
            wordCountEl.textContent = words;

            if (wordErrorEl) {
                if (words >= 2000) {
                    wordErrorEl.style.display = 'none';
                    wordCountEl.parentElement.classList.add('valid');
                } else {
                    wordErrorEl.style.display = words > 0 ? 'block' : 'none';
                    wordCountEl.parentElement.classList.remove('valid');
                }
            }
        });
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = messageInput?.value?.trim() || '';
        const words = message ? message.split(/\s+/).filter(w => w.length > 0).length : 0;

        if (words < 2000) {
            if (wordErrorEl) wordErrorEl.style.display = 'block';
            messageInput?.focus();
            return;
        }

        const formData = new FormData(form);
        const btnText = submitBtn?.querySelector('.btn-text');
        const btnLoading = submitBtn?.querySelector('.btn-loading');

        if (submitBtn) {
            submitBtn.disabled = true;
            if (btnText) btnText.style.display = 'none';
            if (btnLoading) btnLoading.style.display = 'inline';
        }

        try {
            const response = await fetch('/submit', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                if (successModal) {
                    successModal.classList.add('active');
                }
            } else {
                const errors = data.errors || ['Something went wrong. Please try again.'];
                alert(errors.join('\n'));
            }
        } catch (err) {
            alert('Network error. Please try again.');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                if (btnText) btnText.style.display = 'inline';
                if (btnLoading) btnLoading.style.display = 'none';
            }
        }
    });
}

// ========== Scroll Animations for Dashboard ==========
function initScrollAnimations() {
    const cards = document.querySelectorAll('.memory-card[data-aos="fade-up"]');
    if (!cards.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('aos-animate');
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    cards.forEach(card => observer.observe(card));
}
