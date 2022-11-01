window.addEventListener('load', function () {

    // Selecteer een uitwisseling op basis van de gemaaktOp datum
    // De event handler toont/verbergt delen van de HTML aan de hand van de data-u* attributen
    function SelecteerUitwisseling(e) {
        var gemaaktOp = e.detail;

        // Dropdown selectie
        var elt = document.getElementById('uitwisselingselector_gemaaktOp');
        elt.value = gemaaktOp;

        // Volgende / vorige buttons
        var button = document.getElementById('uitwisselingselector_volgende')
        if (elt.selectedIndex == -1) {
            button.dataset.uw = '';
            button.disabled = true
        } else if (elt.selectedIndex == 0) {
            button.dataset.uw = '';
            button.disabled = true
        } else {
            button.dataset.uw = elt.options[elt.selectedIndex - 1].value;
            button.disabled = false
        }
        button = document.getElementById('uitwisselingselector_vorige')
        if (elt.selectedIndex == -1) {
            button.dataset.uw = '';
            button.disabled = true
        } else if (elt.selectedIndex == elt.options.length - 1) {
            button.dataset.uw = '';
            button.disabled = true
        } else {
            button.dataset.uw = elt.options[elt.selectedIndex + 1].value;
            button.disabled = false
        }

        // Selectie van HTML elementen op basis van dataset waarden
        document.querySelectorAll("[data-uw]").forEach((button) => {
            if (gemaaktOp == button.dataset.uw) {
                button.classList.add('huidige-uw')
            } else {
                button.classList.remove('huidige-uw')
            }
        });

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
    }
    window.addEventListener('uitwisseling', SelecteerUitwisseling)

    // Stuur het globale event uit
    function uitwisselingselector_selecteer(gemaaktOp) {
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
