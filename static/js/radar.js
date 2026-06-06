document.addEventListener("DOMContentLoaded", () => {
    const AXES = ['성장성', '안정성', '배당', '가치', '모멘텀', '혁신성'];

    const STYLE_PROFILES = {
        '성장형':   [90, 35, 15, 50, 80, 85],
        '안정형':   [30, 90, 70, 65, 25, 30],
        '배당형':   [35, 80, 95, 70, 30, 20],
        '가치형':   [50, 70, 55, 95, 40, 45],
        '모멘텀형': [75, 30, 20, 40, 95, 70],
        '혁신형':   [85, 25, 10, 35, 70, 95],
        '균형형':   [60, 60, 55, 60, 55, 60],
    };

    /* ── HTML의 data-style 속성에서 Flask Jinja2 값을 읽어옵니다 ── */
    const container = document.getElementById('resultContainer');
    const rawStyle = (container && container.dataset.style) ? container.dataset.style.trim() : '';

    /* STYLE_PROFILES에서 매핑, 없으면 균형형 사용 */
    const scores = STYLE_PROFILES[rawStyle] ?? STYLE_PROFILES['균형형'];

    const ctx = document.getElementById('radarChart').getContext('2d');

    Chart.defaults.font.family = "'Segoe UI', 'Apple SD Gothic Neo', sans-serif";

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: AXES,
            datasets: [{
                label: rawStyle || '투자 성향',
                data: scores,
                backgroundColor: 'rgba(49, 130, 206, 0.15)',
                borderColor:     'rgba(49, 130, 206, 0.9)',
                borderWidth: 2.5,
                pointBackgroundColor: '#3182ce',
                pointBorderColor:     '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointHoverBackgroundColor: '#2b6cb0',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: {
                duration: 900,
                easing: 'easeOutQuart',
            },
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 25,
                        display: false,        // 숫자 눈금 숨김
                        backdropColor: 'transparent',
                    },
                    grid: {
                        color: 'rgba(160,174,192,0.25)',
                        circular: false,
                    },
                    angleLines: {
                        color: 'rgba(160,174,192,0.3)',
                    },
                    pointLabels: {
                        font: { size: 12, weight: '600' },
                        color: '#4a5568',
                        padding: 8,
                    },
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.label}  ${ctx.raw}점`,
                    },
                    backgroundColor: '#2d3748',
                    titleFont: { size: 0 },   // 타이틀 숨김
                    bodyFont:  { size: 13 },
                    padding: 10,
                    displayColors: false,
                }
            }
        }
    });

    const legendEl = document.getElementById('radarLegend');

    AXES.forEach((label, i) => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML =
            `<span class="legend-label">${label}</span>` +
            `<div class="legend-bar-wrap">` +
                `<div class="legend-bar" id="bar-${i}"></div>` +
            `</div>` +
            `<span class="legend-val">${scores[i]}</span>`;
        legendEl.appendChild(item);
    });

    /* 페이지 렌더 후 한 프레임 뒤에 width를 설정해야 transition이 동작 */
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            AXES.forEach((_, i) => {
                const bar = document.getElementById(`bar-${i}`);
                if (bar) bar.style.width = `${scores[i]}%`;
            });
        });
    });
});
