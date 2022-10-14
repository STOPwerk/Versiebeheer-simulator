window.addEventListener('load', function () {

    function ToonGeenToelichting() {
        // Deselecteer alle elementen en toelichtingen
        document.querySelectorAll("[data-UNIEK_ID_e]").forEach((elt) => {
            elt.classList.remove("geselecteerd");
        });
        document.querySelectorAll("[data-UNIEK_ID_t]").forEach((elt) => {
            elt.style.borderWidth = "0px";
            elt.classList.remove("geselecteerd");
        });
    }

    // Reageren op de selectie van een toestand (globaal event)
    function ToonToestand(e) {
        if (e.detail.WorkId == 'WORK_ID') {
            if (e.detail.SelectieMomentopname) {
                return;
            }
            ToonGeenToelichting();
            var selector = '[data-UNIEK_ID_ti="' + e.detail.Identificatie + '"]'
            document.querySelectorAll(selector).forEach((elt) => {
                elt.classList.add("geselecteerd");
            });
            if (e.detail.Identificatie >= 0) {
                // Update de NTC selectie
                window.dispatchEvent(new CustomEvent('diagram_UNIEK_ID', {
                    detail: {
                        NogTeConsolideren: true,
                        Identificatie: e.detail.Identificatie
                    }
                }));
            }
        }
    }
    window.addEventListener('toestand', ToonToestand)

    // Reageren op de selectie van een momentopname (globaal event)
    function ToonMomentopname(e) {
        if (e.detail.WorkId == 'WORK_ID') {
            ToonGeenToelichting();
            var selector = '[data-UNIEK_ID_mo="' + e.detail.UniekId + '"]'
            document.querySelectorAll(selector).forEach((elt) => {
                elt.classList.add("geselecteerd");
            });
            // Annuleer de NTC selectie
            window.dispatchEvent(new CustomEvent('diagram_UNIEK_ID', {
                detail: {
                    NogTeConsolideren: false
                }
            }));
        }
    }
    window.addEventListener('momentopname', ToonMomentopname)

    // Functie om de elementen en toelichting te laten zien/te selecteren afhankelijk van waar het staat
    function ToonToelichting(e) {
        Applicatie.EnkeleTouchStartClick(e);

        if (e.srcElement.dataset.UNIEK_ID_ti) {
            Applicatie.SelecteerToestand('WORK_ID', e.srcElement.dataset.UNIEK_ID_ti, e.srcElement.dataset.UNIEK_ID_tid);
        }
        else {
            Applicatie.SelecteerMomentopname('WORK_ID', e.srcElement.dataset.UNIEK_ID_mo);
        }
    }

    // Event handlers voor de elementen in het diagram
    document.querySelectorAll("[data-UNIEK_ID_e]").forEach((elt) => {
        Applicatie.AddTouchStartClickListener(elt, ToonToelichting);
    });
});
