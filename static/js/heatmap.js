document.querySelectorAll('.heatmap-cell').forEach(cell => {
    const rate = Math.abs(parseFloat(cell.dataset.rate));
    const isUp = parseInt(cell.dataset.up) === 1;
    // 0~3% 범위를 0~1로 정규화 (3% 초과는 최대 강도)
    const intensity = Math.min(rate / 3, 1);

    let bg, color;
    if (isUp) {
        // 빨간색: 연한 분홍 → 진한 빨강
        const g = Math.round(245 - 185 * intensity);
        const b = Math.round(245 - 185 * intensity);
        bg = `rgb(255,${g},${b})`;
        color = intensity > 0.45 ? '#fff' : '#c53030';
    } else {
        // 파란색: 연한 하늘 → 진한 파랑
        const r = Math.round(235 - 185 * intensity);
        const g = Math.round(248 - 188 * intensity);
        bg = `rgb(${r},${g},255)`;
        color = intensity > 0.45 ? '#fff' : '#2b6cb0';
    }
    cell.style.background = bg;
    cell.style.color = color;
});
