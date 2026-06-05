// 투자 성향 직접 선택: 라디오 선택 시 박스 강조 + 제출 버튼 활성화
document.querySelectorAll('input[name="style"]').forEach(radio => {
    radio.addEventListener('change', () => {
        document.querySelectorAll('.style-option-box').forEach(box => box.classList.remove('selected'));
        radio.closest('.style-option').querySelector('.style-option-box').classList.add('selected');
        document.getElementById('direct-submit').disabled = false;
    });
});
