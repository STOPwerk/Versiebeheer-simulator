window.addEventListener('load', function () {

    // Reageer op projectactieselectie (globaal event)
    function SelecteerProjectActie(e) {
        // Selecteer het resultaat
        document.querySelectorAll("[data-pav]").forEach((elt) => {
            if (elt.dataset.pav <= e.detail && (!elt.hasAttribute('data-pat') || e.detail < elt.dataset.pat)) {
                elt.style.display = '';
            } else {
                elt.style.display = 'none';
            }
        });
    }
    window.addEventListener('projectactie', SelecteerProjectActie)
});
