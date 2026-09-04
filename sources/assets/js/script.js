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

// ============================================================
// ВИЗИТНИЦА — ПОИСК И ФИЛЬТР ПО РАЗДЕЛАМ
// ============================================================

(function () {
  const input = document.getElementById('vz-search');
  const status = document.getElementById('vz-status');
  const cards = Array.prototype.slice.call(document.querySelectorAll('.vz-card'));
  const sections = Array.prototype.slice.call(document.querySelectorAll('.vz-section'));
  const chips = Array.prototype.slice.call(document.querySelectorAll('.vz-chip'));
  const empty = document.getElementById('vz-empty');

  // Страница без визитницы — блок просто ничего не делает.
  if (!input || !cards.length) return;

  const всего = status ? status.textContent : '';
  let раздел = 'all';

  function склонение(n, one, few, many) {
    const d = Math.abs(n) % 100;
    if (d >= 11 && d <= 14) return many;
    const e = d % 10;
    if (e === 1) return one;
    if (e >= 2 && e <= 4) return few;
    return many;
  }

  function применить() {
    const запрос = input.value.trim().toLowerCase();
    let найдено = 0;

    cards.forEach(function (card) {
      const подходит =
        (раздел === 'all' || card.dataset.section === раздел) &&
        (!запрос || card.dataset.search.indexOf(запрос) !== -1);
      card.hidden = !подходит;
      if (подходит) найдено++;
    });

    // Раздел без видимых карточек прячется целиком, у остальных
    // счётчик в заголовке показывает, сколько карточек осталось.
    sections.forEach(function (section) {
      const видимых = section.querySelectorAll('.vz-card:not([hidden])').length;
      section.hidden = видимых === 0;
      const счётчик = section.querySelector('.vz-section-title span');
      if (счётчик) {
        if (!счётчик.dataset.всего) счётчик.dataset.всего = счётчик.textContent;
        счётчик.textContent = запрос || раздел !== 'all' ? видимых : счётчик.dataset.всего;
      }
    });

    if (empty) empty.hidden = найдено > 0;

    if (status) {
      status.textContent =
        запрос || раздел !== 'all'
          ? 'Найдено ' + найдено + ' ' + склонение(найдено, 'подразделение', 'подразделения', 'подразделений')
          : всего;
    }
  }

  input.addEventListener('input', применить);

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (c) {
        c.classList.remove('is-active');
      });
      chip.classList.add('is-active');
      раздел = chip.dataset.filter;
      применить();
    });
  });
})();
