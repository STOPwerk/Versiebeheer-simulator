window.addEventListener('load', function () {

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
            document.querySelectorAll("[data-UNIEK_ID_ti]").forEach((elt) => {
                if (elt.dataset.UNIEK_ID_ti == e.detail.Identificatie) {
                    elt.style.display = '';
                }
                else {
                    elt.style.display = 'none';
                }
            });
        }
    }
    window.addEventListener('toestand', ToonToestand)


    // Verberg alle teksten
    document.querySelectorAll("[data-UNIEK_ID_ti]").forEach((elt) => {
        elt.style.display = 'none';
    });
});
