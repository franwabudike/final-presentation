document.addEventListener('DOMContentLoaded', () => {
    function loadHTML(url, elementId) {
        // Updated URL to include the 'static' folder
        fetch(`static/${url}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load ${url}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(html => {
                document.getElementById(elementId).innerHTML = html;
                const currentPath = window.location.pathname.split('/').pop();
                const navLinks = document.querySelectorAll('.nav-link');
                navLinks.forEach(link => {
                    if (link.getAttribute('href') === currentPath) {
                        link.classList.add('active');
                    }
                });
            })
            .catch(error => console.error(`Error loading ${url}:`, error));
    }

    loadHTML('header.html', 'header-placeholder');
    loadHTML('footer.html', 'footer-placeholder');
});