// 종목별 투자 비율 도넛 차트
// 데이터는 템플릿에서 window.PORTFOLIO_CHART_DATA 로 주입됩니다.
(function () {
    const payload = window.PORTFOLIO_CHART_DATA;
    if (!payload || !document.getElementById('portfolioChart')) return;

    const colors = [
        '#3182ce', '#63b3ed', '#90cdf4',
        '#2b6cb0', '#bee3f8', '#ebf8ff',
        '#1a365d', '#2a4365', '#2c5282', '#2d3748'
    ];

    new Chart(document.getElementById('portfolioChart'), {
        type: 'doughnut',
        data: {
            labels: payload.labels,
            datasets: [{
                data: payload.data,
                backgroundColor: colors.slice(0, payload.data.length),
                borderWidth: 2,
                borderColor: '#fff',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
})();
