// ============================
// EcoQuest Main JS
// ============================

// Auto-dismiss alerts after 4 seconds
document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.classList.remove("show");
            alert.classList.add("hide");
        }, 4000);
    });
});

// Confirm before deleting a user or submission
const deleteButtons = document.querySelectorAll(".btn-outline-danger");
deleteButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
        const confirmed = confirm("Are you sure you want to delete this?");
        if (!confirmed) {
            e.preventDefault();
        }
    });
});

// Toggle quiz answers (if you want to show/hide hints or explanation)
const answerToggles = document.querySelectorAll(".toggle-answer");
answerToggles.forEach((btn) => {
    btn.addEventListener("click", () => {
        const answer = btn.closest(".quiz-item").querySelector(".answer");
        answer.classList.toggle("d-none");
    });
});

// Smooth scroll for anchor links
const anchorLinks = document.querySelectorAll('a[href^="#"]');
anchorLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    });
});
