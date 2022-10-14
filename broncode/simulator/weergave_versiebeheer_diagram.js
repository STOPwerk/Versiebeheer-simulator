window.addEventListener('load', function () {

    // Initialiseer het diagram als het in beeld komt
    Applicatie.InitialseerDiagram('DIAGRAM_ID_svg');

    // Selecteer het tonen van alle/alleen actuele toestanden
    function ToonNietMeerActueleToestanden(e) {
        var toon = e && e.srcElement.checked
        document.querySelectorAll(".DIAGRAM_ID_th").forEach((elt) => {
            if (toon) {
                elt.style.display = '';
            } else {
                elt.style.display = 'none';
            }
        });
        document.querySelectorAll(".DIAGRAM_ID_toon_th").forEach((elt) => {
            if (elt.checked != toon) {
                elt.checked = toon;
            }
        });

    }
    // Event handlers voor de elementen in het diagram
    document.querySelectorAll(".DIAGRAM_ID_toon_th").forEach((elt) => {
        elt.addEventListener('click', ToonNietMeerActueleToestanden);
    });
    ToonNietMeerActueleToestanden();

    function ToonGeenVerwerkteUitwisselingen() {
        // Zet een evt vorige selectie uit
        document.querySelectorAll("[data-DIAGRAM_ID_ntc]").forEach((elt) => {
            elt.classList.remove('vbd_ntc');
        });
        document.querySelectorAll("[data-DIAGRAM_ID_e]").forEach((elt) => {
            elt.classList.remove('nvt');
            elt.classList.remove('iv');
            elt.classList.remove('vw');
            elt.classList.remove('ts');
            elt.classList.remove('ts');
            elt.classList.remove('tv');
            elt.classList.remove('to');
        });
    }

    var toonVerwerkteMomentopnamen = false;

    function ToonVerwerkteUitwisselingen(data_tv) {
        var selectie = data_tv.split(';');
        document.querySelectorAll("[data-DIAGRAM_ID_ntc='" + selectie[0] + "']").forEach((elt) => {
            elt.classList.add('vbd_ntc');
        });
        for (var i = 1; i < selectie.length; i++) {
            elts = selectie[i].split('=');
            if (elts[1].length > 0) {
                for (const id of elts[1].split(',')) {
                    document.querySelectorAll("[data-DIAGRAM_ID_e='" + id + "']").forEach((elt) => {
                        for (var c of elts[0].split(' ')) {
                            elt.classList.add(c);
                        }
                    });
                }
            }
        }
    }

    // Reageren op toestandselectie
    function ToonVerwerkteUitwisselingenVoorToestand(e, deselecteer = true) {
        if (deselecteer) {
            ToonGeenVerwerkteUitwisselingen();
        }
        if (toonVerwerkteMomentopnamen && e.detail.NogTeConsolideren) {
            document.querySelectorAll('[data-DIAGRAM_ID_tv]').forEach((elt) => {
                if (elt.dataset) {
                    if (elt.dataset.ti && elt.dataset.ti == e.detail.Identificatie) {
                        ToonVerwerkteUitwisselingen(elt.dataset.DIAGRAM_ID_tv)
                    }
                }
            });
        } else if (e.detail.Toon) {
            document.querySelectorAll('[data-DIAGRAM_ID_tv]').forEach((elt) => {
                if (elt.dataset) {
                    if (elt.dataset.DIAGRAM_ID_tv.startsWith(e.detail.Identificatie + ';')) {
                        ToonVerwerkteUitwisselingen(elt.dataset.DIAGRAM_ID_tv)
                    }
                }
            });
        }
    }
    window.addEventListener('diagram_DIAGRAM_ID', ToonVerwerkteUitwisselingenVoorToestand)


    // Controleer of verwerkingen getoond moeten worden
    function ToonVerwerkteUitwisselingenAanUit(e) {
        toonVerwerkteMomentopnamen = e.srcElement.checked;
        ToonGeenVerwerkteUitwisselingen();
        if (e.srcElement.type == 'checkbox') {
            document.querySelectorAll("[data-DIAGRAM_ID_tv]").forEach((elt) => {
                if (elt != e.srcElement) {
                    elt.checked = toonVerwerkteMomentopnamen;
                }
            });
        }
        if (e.srcElement.dataset && e.srcElement.dataset.ti) {
            var event = {
                detail: {
                    NogTeConsolideren: true,
                    Identificatie: e.srcElement.dataset.ti
                }
            };
            ToonVerwerkteUitwisselingenVoorToestand(event, false);
        } else if (toonVerwerkteMomentopnamen) {
            ToonVerwerkteUitwisselingen(e.srcElement.dataset.DIAGRAM_ID_tv)
        }
    }

    // Event handlers voor de checkboxes voor tonen verwerkte momentopnanem
    document.querySelectorAll("input.DIAGRAM_ID_tv").forEach((elt) => {
        elt.addEventListener('click', ToonVerwerkteUitwisselingenAanUit);
    });

});
