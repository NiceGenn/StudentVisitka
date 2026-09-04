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

// ============================================================
// СТРУКТУРА — РАСКРЫТИЕ КАРТОЧКИ ПОДРАЗДЕЛЕНИЯ
// ============================================================

(function () {
  const шапки = Array.prototype.slice.call(document.querySelectorAll('.vz-card-head'));

  // Страница без карточек — блок просто ничего не делает.
  if (!шапки.length) return;

  шапки.forEach(function (шапка) {
    шапка.addEventListener('click', function () {
      const состав = шапка.parentNode.querySelector('.vz-people');
      if (!состав) return;
      const открыть = состав.hidden;
      состав.hidden = !открыть;
      шапка.setAttribute('aria-expanded', открыть ? 'true' : 'false');
      шапка.parentNode.classList.toggle('is-open', открыть);
    });
  });
})();


// ============================================================
// КНОПКА «НАВЕРХ»
// ============================================================

(function () {
  const кнопка = document.createElement('button');
  кнопка.type = 'button';
  кнопка.className = 'to-top';
  кнопка.setAttribute('aria-label', 'Наверх');
  кнопка.hidden = true;
  кнопка.innerHTML =
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
    '<path d="M12 19V5M5 12l7-7 7 7" stroke="currentColor" stroke-width="2.2" ' +
    'stroke-linecap="round" stroke-linejoin="round"/></svg>';
  document.body.appendChild(кнопка);

  // Кнопка появляется, когда шапка уже ушла за край экрана.
  function проверить() {
    кнопка.hidden = window.pageYOffset < 400;
  }

  window.addEventListener('scroll', проверить, { passive: true });
  проверить();

  кнопка.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();
