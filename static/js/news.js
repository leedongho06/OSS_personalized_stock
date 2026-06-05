document.addEventListener("DOMContentLoaded", function() {
    // 하이라이트할 핵심 주식 종목 이름들
    const targetKeywords = ["삼성전자", "SK하이닉스", "카카오", "NAVER", "네이버", "현대차", "기아", "셀트리온", "LG화학", "두산", "한전", "LG유플러스", "이마트"];

    const textElements = document.querySelectorAll('.news-title, .news-desc');

    textElements.forEach(el => {
        let htmlContent = el.innerHTML;
        targetKeywords.forEach(keyword => {
            // 단어를 찾아서 예쁜 형광펜 디자인 태그로 감싸줍니다.
            const regex = new RegExp(keyword, "g");
            htmlContent = htmlContent.replace(regex, `<span class="highlight-word">${keyword}</span>`);
        });
        el.innerHTML = htmlContent;
    });
});
