window.addEventListener('load', function () {

    // Event handler om een activiteit te selecteren
    function selecteer_activiteit(e) {
        Applicatie.EnkeleTouchStartClick(e);
        var src = e.srcElement;
        while (typeof src !== 'undefined') {
            var uitgevoerdOp = src.dataset['bga'];
            if (typeof uitgevoerdOp !== 'undefined') {
                /* Stuur globaal event uit */
                Applicatie.SelecteerActiviteit(uitgevoerdOp);
                break;
            }
            src = src.parentElement;
        }
    }
    document.querySelectorAll("[data-bga]").forEach((elt) => {
        Applicatie.AddTouchStartClickListener(elt, selecteer_activiteit);
    });

    // Reageer op projectactieselectie (globaal event)
    function SelecteerActiviteit(e) {
        // Selecteer in de tabel
        document.querySelectorAll('[data-bga]').forEach((elt) => {
            if (elt.dataset.bga == e.detail) {
                elt.classList.add('huidige-act');
            } else {
                elt.classList.remove('huidige-act');
            }
        });
    }
    window.addEventListener('activiteit', SelecteerActiviteit)
});
