// Utility Function to Load Partials
function loadPartial(id, file) {
    fetch(file)
        .then(response => {
            if (!response.ok) throw new Error(`Failed to load ${file}`);
            return response.text();
        })
        .then(html => {
            document.getElementById(id).innerHTML = html;
        })
        .catch(error => console.error(`Error loading ${file}:`, error));
}

// Load Header and Footer on Page Load
document.addEventListener("DOMContentLoaded", function () {
    loadPartial("header", "/partials/header.html"); // Header partial
    loadPartial("footer", "/partials/footer.html"); // Footer partial
});
