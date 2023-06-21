window.addEventListener('load', function () {

    // Initialiseer het diagram als het in beeld komt
    Applicatie.InitialseerDiagram('bgvb_svg');

    // Event handler om een activiteit te selecteren
    function selecteer_activiteit(e) {
        Applicatie.EnkeleTouchStartClick(e);
        var src = e.srcElement;
        while (typeof src !== 'undefined') {
            var uitgevoerdOp = src.dataset['bgvba'];
            if (typeof uitgevoerdOp !== 'undefined') {
                /* Stuur globaal event uit */
                Applicatie.SelecteerActiviteit(uitgevoerdOp);
                break;
            }
            src = src.parentElement;
        }
    }
    document.querySelectorAll("[data-bgvba]").forEach((elt) => {
        Applicatie.AddTouchStartClickListener(elt, selecteer_activiteit);
    });

    // Reageer op projectactieselectie (globaal event)
    function SelecteerActiviteit(e) {
        // Selecteer de juiste details en elementen in het diagram
        document.querySelectorAll('[data-bgvba]').forEach((elt) => {
            if (elt.dataset.bgvba == e.detail) {
                elt.classList.add('huidige-act');
            } else {
                elt.classList.remove('huidige-act');
            }
        });
    }
    window.addEventListener('activiteit', SelecteerActiviteit)
});
