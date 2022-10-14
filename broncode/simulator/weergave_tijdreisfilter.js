window.addEventListener('load', function () {


    // Reageer op het instellen van een tijdreisfilter
    function ToonSTOPModule(e) {
        if (e.detail.WorkId == 'WORK_ID') {
            document.querySelectorAll('[data-UNIEK_ID_module]').forEach((elt) => {
                if (e.detail.Code == elt.dataset.UNIEK_ID_module) {
                    elt.style.display = 'block'
                } else {
                    elt.style.display = 'none'
                }
            });
        }
    }
    window.addEventListener('tijdreisfilter', ToonSTOPModule)
    document.querySelectorAll('[data-UNIEK_ID_module]').forEach((elt) => {
        elt.style.display = 'none'
    });


    const ontvangenOp = 1
    const bekendOp = 2
    const juridischWerkendVanaf = 4
    const geldigVanaf = 8
    const laatstOntvangen = 16
    const actueel = 32
    const exTunc = 64
    const exNunc = 128

    var exNuncKeuze = ontvangenOp | bekendOp | juridischWerkendVanaf | geldigVanaf
    var exTuncKeuze = exTunc | ontvangenOp | juridischWerkendVanaf
    var exNuncGeselecteerd = true

    // Interpreteer de stand van de controls en pas de bedrijfsregels toe
    function WerkStatusControlsBij(filter) {
        var disabled = juridischWerkendVanaf;

        // Niet alle combinaties zijn toegestaan
        exNuncGeselecteerd = ((filter & exTunc) == 0);
        var huidigeSelectie;
        if (exNuncGeselecteerd) {
            filter = filter | exNunc;

            var magLaatstOntvangenKiezen = false;
            var magActueelKiezen = true;
            if ((filter & (ontvangenOp | bekendOp | geldigVanaf)) != 0) {
                magActueelKiezen = false;
                magLaatstOntvangenKiezen = ((filter & ontvangenOp) != 0);
            }
            if (!magLaatstOntvangenKiezen) {
                filter = filter & ~laatstOntvangen;
                disabled |= laatstOntvangen;
            }
            if (!magActueelKiezen) {
                filter = filter & ~actueel;
                disabled |= actueel;
            }
            huidigeSelectie = exNuncKeuze = filter;
            exTuncKeuze = (exTuncKeuze & ~bekendOp) | (huidigeSelectie & bekendOp)
        } else {
            filter = (filter & ~bekendOp & ~geldigVanaf & ~actueel) | ontvangenOp;
            disabled |= bekendOp | geldigVanaf | actueel | ontvangenOp;
            huidigeSelectie = exTuncKeuze = filter;
            exNuncKeuze = (exNuncKeuze & ~laatstOntvangen) | (huidigeSelectie & laatstOntvangen)
        }

        document.querySelectorAll('[data-UNIEK_ID_filter]').forEach((elt) => {
            elt.disabled = ((disabled & elt.dataset.UNIEK_ID_filter) != 0);
            elt.checked = ((filter & elt.dataset.UNIEK_ID_filter) != 0);
        });

        // Stuur een event uit
        filter = filter & ~exNunc;
        var idxfilter = '|' + filter + '|'
        var event = new CustomEvent('tijdreisfilter', {
            detail: {
                WorkId: 'WORK_ID',
                Code: huidigeSelectie & ~exNunc,
                ToestandTijdreisIndexInSelectie: (idx) => !idx.includes(idxfilter),
                TijdstempelInSelectie: (eersteLetter) => {
                    if (eersteLetter == 'o') {
                        return (huidigeSelectie & ontvangenOp) != 0;
                    }
                    if (eersteLetter == 'b') {
                        return (huidigeSelectie & bekendOp) != 0;
                    }
                    if (eersteLetter == 'g') {
                        return (huidigeSelectie & geldigVanaf) != 0;
                    }
                    return (eersteLetter == 'j');
                }
            }
        });
        window.dispatchEvent(event)
    }
    WerkStatusControlsBij(exNuncGeselecteerd ? exNuncKeuze : exTuncKeuze);

    // Pas het filter toe op de tabel met toestanden
    function PasFilterToe() {
        var filter = 0;

        // Haal de instellingen op
        document.querySelectorAll('[data-UNIEK_ID_filter]').forEach((elt) => {
            if (elt.checked) {
                filter += parseInt(elt.dataset.UNIEK_ID_filter);
            }
        });

        if ((filter & exTunc) != 0) {
            if (exNuncGeselecteerd) {
                WerkStatusControlsBij(exTuncKeuze);
                return;
            }
        } else if (!exNuncGeselecteerd) {
            WerkStatusControlsBij(exNuncKeuze);
            return;
        }
        WerkStatusControlsBij(filter);
    }

    // Event handlers voor de selectie van een toestand
    document.querySelectorAll('[data-UNIEK_ID_filter]').forEach((elt) => {
        elt.addEventListener('click', PasFilterToe);
    });
});

