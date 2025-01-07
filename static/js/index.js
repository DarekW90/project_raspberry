// ustawienie adresu serwera WebSocket
const socket = io.connect('http://192.168.0.18:5000');

// Flaga zapobiegaj?ca wielokrotnemu wlaczaniu alertu w krotkim czasie
let alertActive = false;

// Funkcja do wyswietlania popupu
function showPopup(message) {
    const popup = document.getElementById('popup');
    popup.textContent = message;
    popup.style.display = 'block';
    setTimeout(() => {
        popup.style.display = 'none';
    }, 10000); // Popup znika po 10 sekundach
}

// Funkcja do zmiany elementow zielonych na czerwone
function toggleAlertMode(isAlert) {
    const header = document.querySelector('header');
    const titles = document.querySelectorAll('h1, h2');
    const buttons = document.querySelectorAll('.cta a');

    if (isAlert) {
        header.classList.add('alert');
        titles.forEach(title => title.classList.add('alert'));
        buttons.forEach(button => button.classList.add('alert'));
    } else {
        header.classList.remove('alert');
        titles.forEach(title => title.classList.remove('alert'));
        buttons.forEach(button => button.classList.remove('alert'));
    }
}

// Nasluchiwanie na zdarzenie 'motion' z WebSocket
socket.on('motion', (data) => {
    if (data.status === 'motion_detected' && !alertActive) {
        alertActive = true; // Wlaczamy alert, aby nie byl uruchamiany wielokrotnie
        showPopup('Ruch wykryty! Sprawdz kamere!');
        toggleAlertMode(true);

        // Przywracanie stanu po 10 sekundach
        setTimeout(() => {
            toggleAlertMode(false);
            alertActive = false; // Resetujemy flage, aby umozliwia kolejne wykrycie ruchu
        }, 10000);
    }
});