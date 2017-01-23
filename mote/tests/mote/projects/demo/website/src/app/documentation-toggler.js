import { ready } from './helpers/document-ready';

ready(function() {
    const Toggles = document.querySelectorAll('.Documentation-toggler');

    for (let i = 0; i < Toggles.length; i++) {
        // Set the is off state on the toggles
        let toggle = Toggles[i];
        toggle.classList.add('is-off');

        // Set the hidden state on the panels
        let panel = Toggles[i].getAttribute('href');
        document
            .querySelector(panel)
            .classList
            .add('is-hidden');
    }

    function onClick(el) {
        el.addEventListener('click', (e) => {
            e.preventDefault();

            el.classList.toggle('is-off');

            let target = document.querySelector(el.getAttribute('href'));

            if (target.classList.contains('is-hidden')) {
                target.classList.remove('is-hidden');
            } else {
                target.classList.add('is-hidden');
            }
        });
    }

    for (let i = 0; i < Toggles.length; i++) {
        onClick(Toggles[i]);
    }
});
