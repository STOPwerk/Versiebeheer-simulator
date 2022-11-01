window.addEventListener('load', function () {

    // Event handler om een projectactie te selecteren
    function projecten_selecteer_pa(e) {
        Applicatie.EnkeleTouchStartClick(e);
        var src = e.srcElement;
        while (typeof src !== 'undefined') {
            var uitgevoerdOp = src.dataset['pa'];
            if (typeof uitgevoerdOp !== 'undefined') {
                /* Stuur globaal event uit */
                Applicatie.SelecteerProjectactie(uitgevoerdOp);
                break;
            }
            src = src.parentElement;
        }
    }
    document.querySelectorAll("[data-pa]").forEach((elt) => {
        Applicatie.AddTouchStartClickListener(elt, projecten_selecteer_pa);
    });

    // Reageer op projectactieselectie (globaal event)
    function SelecteerProjectActie(e) {
        // Selecteer in de tabel
        document.querySelectorAll('[data-pa]').forEach((elt) => {
            if (elt.dataset.pa == e.detail) {
                elt.classList.add('huidige-pa');
            } else {
                elt.classList.remove('huidige-pa');
            }
        });
    }
    window.addEventListener('projectactie', SelecteerProjectActie)
});
