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
            let linksOutButton = document.querySelector(`[data-linksto="${target}"]`);

            document.querySelector(target).setAttribute('src', url);

            linksOutButton.setAttribute('href', url);

            // Toggle the example / usage area
            var dottedName = el.getAttribute('data-element-dotted-name');
            // No clue why querySelector causes issues. Use jQuery.
            //document.querySelector('.element-usage').setAttribute('style': 'display: none');
            $('.element-usage').hide();
            document.querySelector('[data-usage-dotted-name="' + dottedName + '"]').setAttribute('style', 'display: auto');
        });
    }

    for (let i = 0; i < Toggles.length; i++) {
        onClick(Toggles[i]);
    }
});
