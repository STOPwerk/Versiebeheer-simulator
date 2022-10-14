window.addEventListener('load', function () {

    // Selecteer de analyse voor de toestand of onvolledige versie
    function SelecteerInstrumentversieVoorAnalyse(e, sectieId) {
        document.querySelectorAll('[data-' + sectieId + ']').forEach((elt) => {
            if (elt.dataset[sectieId] == e.srcElement.value) {
                elt.style.display = '';
            }
            else {
                elt.style.display = 'none';
            }
        });
    }

    // Reageren op een verandering van de (globale) toestandselectie
    function ToonToestand(e) {
        if (e.detail.WorkId == 'WORK_ID') {
            document.querySelectorAll(".UNIEK_ID").forEach((elt) => {
                if (e.detail.Identificatie >= 0) {
                    elt.style.display = '';
                }
                else {
                    elt.style.display = 'none';
                }
            });
            document.querySelectorAll("[data-UNIEK_ID_tid]").forEach((elt) => {
                if (elt.dataset.UNIEK_ID_tid == e.detail.UniekId) {
                    elt.style.display = '';
                }
                else {
                    elt.style.display = 'none';
                }
            });
        }
    }
    window.addEventListener('toestand', ToonToestand)

    // Voer initialisatie van sectie uit nadat het toestand event afgerond is,
    // anders kan het svg-diagram nog hidden zijn
    var sectieKlaarVoorGebruik = {}

    function MaakSectieKlaarVoorGebruik(e) {
        if (e.detail.WorkId == 'WORK_ID') {
            document.querySelectorAll("[data-UNIEK_ID_tid]").forEach((elt) => {
                if (elt.dataset.UNIEK_ID_tid == e.detail.UniekId) {
                    // Initialiseer de controle/diagram in deze sectie
                    var sectieId = 'UNIEK_ID_' + e.detail.UniekId
                    if (!(sectieId in sectieKlaarVoorGebruik)) {
                        sectieKlaarVoorGebruik[sectieId] = true;

                        if (document.getElementById(sectieId + '_svg') != null) {
                            // Event handlers voor de radio buttons
                            document.querySelectorAll('.' + sectieId + '_tv').forEach((elt) => {
                                elt.addEventListener('click', e => SelecteerInstrumentversieVoorAnalyse(e, sectieId));
                            });

                            // Selecteer de toestand
                            document.querySelectorAll('.' + sectieId + '_tv').forEach((elt) => {
                                if (elt.value == "0") {
                                    elt.click();
                                }
                            });
                        }
                    }
                }
            });
        }
    }
    window.addEventListener('toestand:after', MaakSectieKlaarVoorGebruik)

    // Verberg alle teksten
    document.querySelectorAll("[data-UNIEK_ID_tid]").forEach((elt) => {
        elt.style.display = 'none';
    });


    // Event handlers voor de radio buttons
    document.querySelectorAll('.UNIEK_ID_stap5ev').forEach((elt) => {
        elt.addEventListener('click', SelecteerInstrumentversieVoorAnalyse);
    });
});
