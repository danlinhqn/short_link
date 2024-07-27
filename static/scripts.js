function showTab(tabId) {
    // Hide all tab content
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    // Remove active class from all tab links
    const links = document.querySelectorAll('.tab-link');
    links.forEach(link => link.classList.remove('active'));

    // Show the selected tab content and add active class to the selected link
    document.getElementById(tabId).classList.add('active');
    document.getElementById(`${tabId}-link`).classList.add('active');
}

// Show the first tab by default
document.addEventListener('DOMContentLoaded', function() {
    showTab('tab1');
});
