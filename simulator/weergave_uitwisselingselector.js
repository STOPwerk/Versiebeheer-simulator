window.addEventListener('load', function () {

    // Zet de knoppen voor de vorige/volgende uitwisseling
    function uitwisselingselector_button_status(elt) {
        var button = document.getElementById('uitwisselingselector_volgende')
        if (elt.selectedIndex == 0) {
            button.dataset.uw = '';
            button.disabled = true
        } else {
            button.dataset.uw = elt.options[elt.selectedIndex - 1].value;
            button.disabled = false
        }
        button = document.getElementById('uitwisselingselector_vorige')
        if (elt.selectedIndex == elt.options.length - 1) {
            button.dataset.uw = '';
            button.disabled = true
        } else {
            button.dataset.uw = elt.options[elt.selectedIndex + 1].value;
            button.disabled = false
        }
        document.querySelectorAll("[data-uw]").forEach((button) => {
            if (elt.value == button.dataset.uw) {
                button.classList.add('geselecteerd')
            } else {
                button.classList.remove('geselecteerd')
            }
        });
    }
    uitwisselingselector_button_status(document.getElementById('uitwisselingselector_gemaaktOp'))

    // Selecteer een uitwisseling op basis van de gemaaktOp datum
    // De event handler toont/verbergt delen van de HTML aan de hand van de data-u* attributen
    function uitwisselingselector_selecteer(gemaaktOp) {

        // Dropdown selectie
        var elt = document.getElementById('uitwisselingselector_gemaaktOp');
        elt.value = gemaaktOp;
        uitwisselingselector_button_status(elt)

        document.querySelectorAll("[data-u]").forEach((elt) => {
            if (elt.dataset.u == gemaaktOp) {
                elt.style.display = '';
            } else {
                elt.style.display = 'none';
            }
        });
        document.querySelectorAll("[data-uv]").forEach((elt) => {
            if (elt.dataset.uv <= gemaaktOp && (!elt.hasAttribute('data-ut') || gemaaktOp < elt.dataset.ut)) {
                elt.style.display = '';
            } else {
                elt.style.display = 'none';
            }
        });
        /* Stuur globaal event uit */
        Applicatie.SelecteerUitwisseling(gemaaktOp);
    }
    uitwisselingselector_selecteer("<!--START-->")

    // Event handler voor de knoppen om een uitwisseling te selecteren
    function uitwisselingselector_selecteer_uw(e) {
        Applicatie.EnkeleTouchStartClick(e);
        var gemaaktOp = e.srcElement.dataset['uw'];
        if (typeof gemaaktOp === 'undefined') {
            gemaaktOp = e.srcElement.parentElement.dataset.uw;
        }
        if (gemaaktOp != '') {
            uitwisselingselector_selecteer(gemaaktOp);
        }
    }
    document.querySelectorAll("[data-uw]").forEach((elt) => {
        Applicatie.AddTouchStartClickListener(elt, uitwisselingselector_selecteer_uw);
    });

    // Event handler voor de dropdown
    document.getElementById('uitwisselingselector_gemaaktOp').addEventListener('click', function (e) {
        uitwisselingselector_selecteer(e.srcElement.value)
    })

    // Pas breedte van beschrijving van scenario aan zodat de selector er nit voor zit.
    var intro = document.getElementById('intro')
    if (intro) {
        var rect = document.getElementById('uitwisselingselector').getBoundingClientRect()
        intro.style.width = rect.left
    }
});
