document.addEventListener('DOMContentLoaded', function () {
    // Найдем все элементы с классом .alert, чтобы автоматически скрывать их через 5 секунд
    const flashMessages = document.querySelectorAll('.alert');

    flashMessages.forEach(function (flash) {
        // Установим таймер для каждого flash-сообщения
        setTimeout(function () {
            const alertInstance = new bootstrap.Alert(flash);
            alertInstance.close();
        }, 5000);  // 5000 миллисекунд = 5 секунд
    });
});
