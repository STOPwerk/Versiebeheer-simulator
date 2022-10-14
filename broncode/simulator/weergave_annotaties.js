window.addEventListener('load', function () {

    // Selecteer de tijdlijn
    function SelecteerTijdlijn(e) {
        var filter;
        if (e.srcElement.value == '-1') {
            filter = '|-|'
        } else {
            filter = '|' + e.srcElement.value + '|'
        }
        // Selecteer in de tabel
        document.querySelectorAll('[data-DIAGRAM_ID_k]').forEach((elt) => {
            if (elt.dataset.DIAGRAM_ID_k.includes(filter)) {
                elt.classList.add('at_a_sel_tl');
            } else {
                elt.classList.remove('at_a_sel_tl');
            }
        });
    }
    document.querySelectorAll('[name="DIAGRAM_ID_selector"]').forEach((elt) => {
        elt.addEventListener('click', SelecteerTijdlijn);
    });

    var tijdreis = -1;

    // Selecteer de tijdreis
    function SelecteerTijdreis(e) {
        Applicatie.EnkeleTouchStartClick(e);
        var rij = e.srcElement.dataset.DIAGRAM_ID_tr;
        var filter
        if (rij == tijdreis) {
            filter = '|-|'
            tijdreis = -1;
        } else {
            filter = '|' + rij + '|'
            tijdreis = rij;
        }

        // Selecteer in de tabel
        document.querySelectorAll('[data-DIAGRAM_ID_r]').forEach((elt) => {
            if (elt.dataset.DIAGRAM_ID_r.includes(filter)) {
                elt.classList.add('at_a_sel_tr');
            } else {
                elt.classList.remove('at_a_sel_tr');
            }
        });
        // Selecteer toelichting
        document.querySelectorAll('[data-DIAGRAM_ID_rt]').forEach((elt) => {
            if (elt.dataset.DIAGRAM_ID_rt == tijdreis) {
                elt.style.display = '';
            } else {
                elt.style.display = 'none';
            }
        });
    }
    document.querySelectorAll('[data-DIAGRAM_ID_tr]').forEach((elt) => {
        Applicatie.AddTouchStartClickListener(elt, SelecteerTijdreis);
    });
});

