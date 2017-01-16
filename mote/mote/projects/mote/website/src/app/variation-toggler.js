import { ready } from './helpers/document-ready';

ready(function() {
    const Toggles = document.querySelectorAll('[data-variation-toggle]');

    function onClick(el) {
        el.addEventListener('click', (e) => {
            e.preventDefault();

            for (let i = 0; i < Toggles.length; i++) {
                Toggles[i].classList.remove('is-active');
            }

            el.classList.add('is-active');

            let target = `#${el.getAttribute('data-variation-toggle')}`;
            let url = el.getAttribute('href');

            document.querySelector(target).setAttribute('src', url);
        });
    }

    for (let i = 0; i < Toggles.length; i++) {
        onClick(Toggles[i]);
    }
});
