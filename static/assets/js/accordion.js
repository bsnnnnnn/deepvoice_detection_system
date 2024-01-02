// accordion.js 파일에 저장
document.addEventListener('DOMContentLoaded', function() {
    var buttons = document.querySelectorAll('.accordion-button');

    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            var content = this.nextElementSibling;

            // 'active' 클래스를 추가 및 제거하여 아코디언 열기 및 닫기
            if (content.classList.contains('active')) {
                content.classList.remove('active');
            } else {
                content.classList.add('active');
            }
        });
    });
});
