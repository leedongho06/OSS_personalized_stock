document.addEventListener("DOMContentLoaded", () => {
    const COLORS = [
        'rgba(49, 130, 206, 0.8)',
        'rgba(72, 187, 120, 0.8)',
        'rgba(237, 137, 54, 0.8)',
        'rgba(160, 89, 200, 0.8)',
        'rgba(229, 62, 62, 0.8)',
    ];
    const BORDER_COLORS = COLORS.map(c => c.replace('0.8', '1'));

    const METRIC_LABELS = { per: 'PER', pbr: 'PBR', score: '유사도' };

    const names = STOCK_DATA.map(s => s.name);

    function getValue(s, metric) {
        const v = s[metric];
        if (v === null || v === undefined) return null;
        if (metric === 'score') return Math.round(v * 10000) / 100; // 0.0038 → 0.38%
        return v;
    }

    function buildDataset(metric) {
        return {
            label: METRIC_LABELS[metric],
            data: STOCK_DATA.map(s => getValue(s, metric)),
            backgroundColor: COLORS.slice(0, STOCK_DATA.length),
            borderColor: BORDER_COLORS.slice(0, STOCK_DATA.length),
            borderWidth: 1.5,
            borderRadius: 6,
        };
    }

    function hasData(metric) {
        return STOCK_DATA.some(s => getValue(s, metric) !== null && getValue(s, metric) !== 0);
    }

    const ctx = document.getElementById('compareChart').getContext('2d');
    const noDataEl = document.getElementById('compareNoData');
    let currentMetric = 'per';
    let chart = null;

    function renderChart(metric) {
        if (!hasData(metric)) {
            ctx.canvas.style.display = 'none';
            noDataEl.style.display = 'flex';
            return;
        }
        ctx.canvas.style.display = 'block';
        noDataEl.style.display = 'none';

        const suffix = metric === 'score' ? '%' : '';

        if (chart) {
            chart.data.datasets = [buildDataset(metric)];
            chart.options.scales.y.ticks.callback = v => v + suffix;
            chart.options.plugins.tooltip.callbacks.label = c => ` ${METRIC_LABELS[metric]}: ${c.raw}${suffix}`;
            chart.update();
        } else {
            chart = new Chart(ctx, {
                type: 'bar',
                data: { labels: names, datasets: [buildDataset(metric)] },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 500, easing: 'easeOutQuart' },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#2d3748',
                            bodyFont: { size: 13 },
                            padding: 10,
                            displayColors: false,
                            callbacks: {
                                label: c => ` ${METRIC_LABELS[metric]}: ${c.raw}${suffix}`,
                            },
                        },
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 12, weight: '600' }, color: '#4a5568' },
                        },
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(160,174,192,0.2)' },
                            ticks: {
                                font: { size: 11 },
                                color: '#718096',
                                callback: v => v + suffix,
                            },
                        },
                    },
                },
            });
        }
    }

    renderChart(currentMetric);

    document.querySelectorAll('.compare-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.compare-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMetric = btn.dataset.metric;
            renderChart(currentMetric);
        });
    });
});
