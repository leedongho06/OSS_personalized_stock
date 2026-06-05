(() => {
    const STORAGE_KEY = 'stock_recent_searches';
    const MAX_ITEMS = 5;

    const form      = document.getElementById('rec-form');
    const container = document.getElementById('recent-searches');

    function load() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        } catch {
            return [];
        }
    }

    function save(companies) {
        let list = load();
        const key = [...companies].sort().join(',');
        list = list.filter(item => [...item].sort().join(',') !== key);
        list.unshift(companies);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(0, MAX_ITEMS)));
        render();
    }

    function remove(index) {
        const list = load();
        list.splice(index, 1);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
        render();
    }

    function clearAll() {
        localStorage.removeItem(STORAGE_KEY);
        render();
    }

    function apply(companies) {
        window.clearTagsAll?.();
        companies.forEach(c => window.addTag?.(c));
    }

    function esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function render() {
        if (!container) return;
        const list = load();

        if (list.length === 0) {
            container.innerHTML = '';
            return;
        }

        container.innerHTML = `
            <div class="recent-header">
                <span class="recent-title">최근 검색</span>
                <button type="button" class="recent-clear-all">전체 삭제</button>
            </div>
            <div class="recent-chips"></div>
        `;

        const chipsEl = container.querySelector('.recent-chips');

        list.forEach((companies, i) => {
            const chip = document.createElement('div');
            chip.className = 'recent-chip';
            chip.innerHTML =
                `<span class="recent-chip-text">${esc(companies.join(', '))}</span>` +
                `<button type="button" class="recent-chip-x" data-i="${i}" aria-label="삭제">✕</button>`;

            chip.querySelector('.recent-chip-text').addEventListener('click', () => apply(companies));
            chip.querySelector('.recent-chip-x').addEventListener('click', e => {
                e.stopPropagation();
                remove(i);
            });

            chipsEl.appendChild(chip);
        });

        container.querySelector('.recent-clear-all').addEventListener('click', clearAll);
    }

    form?.addEventListener('submit', () => {
        const companies = [...form.querySelectorAll('input[name="companies"]')]
            .map(el => el.value)
            .filter(Boolean);
        if (companies.length > 0) save(companies);
    });

    render();
})();
