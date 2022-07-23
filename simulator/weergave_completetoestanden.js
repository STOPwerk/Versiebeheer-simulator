window.addEventListener('load', function () {

    // Reageer op toestandselectie (globaal event)
    function ToonToestand(e) {
        if (e.detail.WorkId == 'WORK_ID') {
            // Selecteer in de tabel
            document.querySelectorAll('[data-UNIEK_ID_tid]').forEach((elt) => {
                if (elt.dataset.UNIEK_ID_tid == e.detail.UniekId) {
                    elt.classList.add('geselecteerd');
                } else {
                    elt.classList.remove('geselecteerd');
                }
            });
            // Selecteer de toelichting
            document.querySelectorAll('[data-UNIEK_ID_t]').forEach((elt) => {
                if (elt.dataset.UNIEK_ID_t == e.detail.UniekId) {
                    elt.style.display = '';
                } else {
                    elt.style.display = 'none';
                }
            });
        }
    }
    document.querySelectorAll('[data-UNIEK_ID_t]').forEach((elt) => {
        elt.style.display = 'none';
    });

    window.addEventListener('toestand', ToonToestand)

    // Selecteer een toestand in de tabel
    function SelecteerToestand(e) {
        Applicatie.EnkeleTouchStartClick(e);
        Applicatie.SelecteerToestand('WORK_ID', this.dataset.UNIEK_ID_ti, this.dataset.UNIEK_ID_tid);
    }

    // Event handlers voor de selectie van een toestand
    document.querySelectorAll('[data-UNIEK_ID_tid]').forEach((elt) => {
        Applicatie.AddTouchStartClickListener(elt, SelecteerToestand);
    });

    // Reageer op het instellen van een tijdreisfilter
    function ToonGefilterd(e) {
        if (e.detail.WorkId == 'WORK_ID') {
            document.querySelectorAll('[data-UNIEK_ID_f]').forEach((elt) => {
                if (e.detail.ToestandTijdreisIndexInSelectie(elt.dataset.UNIEK_ID_f)) {
                    elt.classList.remove('uit')
                } else {
                    elt.classList.add('uit')
                }
            });
            document.querySelectorAll('[data-UNIEK_ID_ts]').forEach((elt) => {
                if (e.detail.TijdstempelInSelectie(elt.dataset.UNIEK_ID_ts)) {
                    elt.classList.remove('wl')
                } else {
                    elt.classList.add('wl')
                }
            });
        }
    }
    window.addEventListener('tijdreisfilter', ToonGefilterd)
});

