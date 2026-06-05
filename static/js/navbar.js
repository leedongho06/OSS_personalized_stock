// 모바일 네비게이션 햄버거 토글 (이벤트 위임)
document.addEventListener('click', function (e) {
    const toggle = e.target.closest('.navbar-toggle');
    if (!toggle) return;
    const links = document.querySelector('.navbar-links');
    if (links) links.classList.toggle('open');
});
