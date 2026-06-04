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

})();
