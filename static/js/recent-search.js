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

})();
