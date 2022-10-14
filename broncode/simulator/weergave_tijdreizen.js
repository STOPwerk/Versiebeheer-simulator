window.addEventListener('load', function () {
    Applicatie.InitialseerDiagram('UNIEK_ID_ob_svg');
    Applicatie.InitialseerDiagram('UNIEK_ID_jg_svg');

    // Selecteer de elementen van het geldigheidsdiagram vanuit een beschikbaarheidsdiagram
    function ToonGeldigheid(elt) {
        document.getElementById('UNIEK_ID_jg_ob').innerText = elt.children[0].textContent
        document.getElementById('UNIEK_ID_jg_titel').style.display = '';

        var selectie = elt.dataset.UNIEK_ID_obt
        document.querySelectorAll('[data-UNIEK_ID_ob_g]').forEach((elt) => {
            if (selectie.includes('|' + elt.dataset.UNIEK_ID_ob_g + '|')) {
                elt.style.display = '';
            } else {
                elt.style.display = 'none';
            }
        });
        document.querySelectorAll('[data-UNIEK_ID_obt_g]').forEach((elt) => {
            if (elt.dataset.UNIEK_ID_obt_g == selectie) {
                elt.style.display = '';
            } else {
                elt.style.display = 'none';
            }
        });
    }
    function SelecteerGeldigheid(e) {
        Applicatie.EnkeleTouchStartClick(e);
        ToonGeldigheid(e.srcElement);
    }
    function VerbergGeldigheid() {
        document.querySelectorAll('[data-UNIEK_ID_ob_g]').forEach((elt) => {
            elt.style.display = 'none';
        });
        document.querySelectorAll('[data-UNIEK_ID_obt_g]').forEach((elt) => {
            elt.style.display = 'none';
        });
    }
    VerbergGeldigheid();

    // Event handlers voor de elementen in het beschikbaarheidsdiagram
    document.querySelectorAll('[data-UNIEK_ID_obt]').forEach((elt) => {
        Applicatie.AddTouchStartClickListener(elt, SelecteerGeldigheid);
    });

    // Reageren op toestandselectie (global event)
    var bevriesJGdiagram = false

    function ToonVerwerkteUitwisselingenVoorToestand(e) {
        if (e.detail.WorkId == 'WORK_ID') {
            // Weghalen selectie in diagrammen
            document.querySelectorAll('[data-UNIEK_ID_ob_e]').forEach((elt) => {
                elt.classList.remove('geselecteerd');
            });
            if (!bevriesJGdiagram) {
                VerbergGeldigheid();
            }
            // Selecteer toestand in rij en eleemnt in geldigheidsdiagram
            document.querySelectorAll('[data-UNIEK_ID_tid]').forEach((elt) => {
                if (elt.dataset.UNIEK_ID_tid == e.detail.UniekId) {
                    elt.classList.add('geselecteerd');
                    if (elt.hasAttribute('data-UNIEK_ID_ob_t')) {
                        // Selecteer in beschikbaarheidsdiagrammen
                        document.querySelectorAll("[data-UNIEK_ID_ob_e='" + elt.dataset.UNIEK_ID_ob_t + "']").forEach((svg) => {
                            svg.classList.add('geselecteerd');
                            if (!bevriesJGdiagram) {
                                ToonGeldigheid(svg);
                            }
                        });
                    }
                } else {
                    elt.classList.remove('geselecteerd');
                }
            });
            bevriesJGdiagram = false;
        }
    }
    window.addEventListener('toestand', ToonVerwerkteUitwisselingenVoorToestand)

    // Selecteer een toestand in de tabel
    function SelecteerToestand(e) {
        Applicatie.EnkeleTouchStartClick(e);

        // Pas het ontvangenOp-bekendOp diagram niet aan als in het juridischWerkendVanaf - GeldigVanaf diagram geklikt wordts
        bevriesJGdiagram = (e.srcElement.tagName.toLowerCase() == 'rect');
        Applicatie.SelecteerToestand('WORK_ID', this.dataset.UNIEK_ID_ti, this.dataset.UNIEK_ID_tid);
    }

    // Event handlers voor de elementen in de tabel en de elementen van het geldigheidsdiagram
    document.querySelectorAll('[data-UNIEK_ID_ti]').forEach((elt) => {
        Applicatie.AddTouchStartClickListener(elt, SelecteerToestand);
    });
});
