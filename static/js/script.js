// script.js

document.addEventListener("DOMContentLoaded", function () {
  // Sidebar links
  const links = document.querySelectorAll(".sidebar li");
  const sections = document.querySelectorAll(".main-section");

  // Function to show one section at a time
  function showSection(sectionId) {
    sections.forEach((sec) => {
      if (sec.id === sectionId) {
        sec.style.display = "block";
      } else {
        sec.style.display = "none";
      }
    });
  }

  // Sidebar click events
  links.forEach((link) => {
    link.addEventListener("click", function () {
      const target = this.dataset.target;
      if (target) {
        showSection(target);
      }
    });
  });

  // Initially show dashboard
  showSection("dashboard");

  // Optional: Toggle sidebar collapse
  const toggleBtn = document.querySelector("#sidebarToggle");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", function () {
      document.querySelector(".sidebar").classList.toggle("collapsed");
    });
  }
});