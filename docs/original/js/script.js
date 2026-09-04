// ============================================================
// FAQ АККОРДЕОН
// ============================================================

document.addEventListener('DOMContentLoaded', function () {
  const faqQuestions = document.querySelectorAll('.faq-question');

  faqQuestions.forEach((question) => {
    question.addEventListener('click', function () {
      // Закрываем все другие ответы
      const allAnswers = document.querySelectorAll('.faq-answer');
      allAnswers.forEach((answer) => {
        if (answer !== this.nextElementSibling) {
          answer.classList.remove('open');
        }
      });

      // Убираем активный класс у всех вопросов
      const allQuestions = document.querySelectorAll('.faq-question');
      allQuestions.forEach((q) => {
        if (q !== this) {
          q.classList.remove('active');
        }
      });

      // Переключаем текущий
      this.classList.toggle('active');
      const answer = this.nextElementSibling;
      answer.classList.toggle('open');
    });
  });
});

// ============================================================
// ПЛАВНАЯ ПРОКРУТКА К ЯКОРЯМ
// ============================================================

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    }
  });
});

// ============================================================
// ТЕКУЩАЯ ДАТА В ПОДВАЛЕ
// ============================================================

const yearElement = document.getElementById('current-year');
if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
}
