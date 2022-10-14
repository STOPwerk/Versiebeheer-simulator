window.addEventListener('load', function () {

    // Hou bij wat de geselecteerde proefversie is voor een uitwisseling
    var proefversieVoorUitwisseling = {}
    // Hou bij welke annotatie is geselecteerd
    var annotatieId = 0;

    // Toon een proefversie
    function ToonProefversie(gemaaktOp, id) {
        // Bewaar de selectie
        proefversieVoorUitwisseling[gemaaktOp] = id;

        // Toon de HTML van de proefversie
        document.querySelectorAll('[data-DIAGRAM_ID]').forEach((elt) => {
            var pv = elt.dataset.DIAGRAM_ID.split(';')
            if (pv[0] == gemaaktOp) {
                if (pv[1] == id) {
                    elt.style.display = '';
                } else {
                    elt.style.display = 'none';
                }
            }
        });
        // Toon de annotatie/proefversie
        window.dispatchEvent(new CustomEvent('diagram_DIAGRAM_ID_d_' + id, {
            detail: {
                Identificatie: id + '-' + annotatieId,
                Toon: true
            },
            cancelable: true
        }));
    }

    // Selecteren van een proefversie
    function SelecteerProefversie(e) {
        var id = e.srcElement.dataset.DIAGRAM_ID_select.split(';');
        ToonProefversie(id[0], id[1])
    }
    // Event handlers voor de selectie van een instrumentversie
    document.querySelectorAll('[data-DIAGRAM_ID_select]').forEach((elt) => {
        elt.addEventListener('click', SelecteerProefversie);
    });

    // Selecteren van een annotatie
    function SelecteerAnnotatie(e) {
        var id = e.srcElement.dataset.DIAGRAM_ID_a_select.split(';')
        // Selecteer de annotatie voor alle proefversies
        annotatieId = id[2]
        document.querySelectorAll('[data-DIAGRAM_ID_a_select]').forEach((elt) => {
            var pva = elt.dataset.DIAGRAM_ID_a_select.split(';')
            if (pva[2] == id[2]) {
                elt.checked = true;
                if (pva[0] in proefversieVoorUitwisseling) {
                    // Werk diagram bij
                }
            }
        });
        // Toon de HTML voor de annotatie
        document.querySelectorAll('[data-DIAGRAM_ID_a]').forEach((elt) => {
            if (elt.dataset.DIAGRAM_ID_a == id[2]) {
                elt.style.display = '';
            } else {
                elt.style.display = 'none';
            }
        });
        // Toon de proefversie en werk het diagram bij
        ToonProefversie(id[0], id[1]);
    }

    // Event handlers voor de selectie van een instrumentversie
    document.querySelectorAll('[data-DIAGRAM_ID_a_select]').forEach((elt) => {
        elt.addEventListener('click', SelecteerAnnotatie);
    });

    // Reageer op uitwisselingselectie
    function SelecteerProefversieVoorUitwisseling(e) {
        if (!(e.detail in proefversieVoorUitwisseling)) {
            // Nog geen proefversie geselecteerd voor deze uitwisseling
            var gevonden = false;
            document.querySelectorAll('[data-DIAGRAM_ID_select]').forEach((elt) => {
                if (!gevonden) {
                    var pv = elt.dataset.DIAGRAM_ID_select.split(';');
                    if (pv[0] == e.detail) {
                        // Selecteer de eerste die gevonden wordt
                        gevonden = true;
                        elt.checked = true;
                        ToonProefversie(pv[0], pv[1]);
                    }
                }
            });

        }
    }
    window.addEventListener('uitwisseling', SelecteerProefversieVoorUitwisseling);
});

