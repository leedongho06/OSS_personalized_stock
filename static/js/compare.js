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

    function buildDataset(metric) {
        return {
            label: METRIC_LABELS[metric],
            data: STOCK_DATA.map(s => s[metric] ?? 0),
            backgroundColor: COLORS.slice(0, STOCK_DATA.length),
            borderColor: BORDER_COLORS.slice(0, STOCK_DATA.length),
            borderWidth: 1.5,
            borderRadius: 6,
        };
    }

    const ctx = document.getElementById('compareChart').getContext('2d');
    let currentMetric = 'per';

    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: names,
            datasets: [buildDataset(currentMetric)],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: { duration: 500, easing: 'easeOutQuart' },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#2d3748',
                    bodyFont: { size: 13 },
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: ctx => ` ${METRIC_LABELS[currentMetric]}: ${ctx.raw}`,
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
                    ticks: { font: { size: 11 }, color: '#718096' },
                },
            },
        },
    });

    document.querySelectorAll('.compare-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.compare-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMetric = btn.dataset.metric;
            chart.data.datasets = [buildDataset(currentMetric)];
            chart.update();
        });
    });
});
