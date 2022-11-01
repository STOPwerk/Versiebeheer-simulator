Applicatie = (function () {

    // Selectie van toestanden
    Applicatie = {}
    var geselecteerdeToestand = false;

    Applicatie.SelecteerGeenToestand = function (welMomentopname) {
        window.dispatchEvent(new CustomEvent('toestand', {
            detail: {
                Identificatie: -1,
                UniekId: -1,
                SelectieMomentopname: welMomentopname
            },
            cancelable: true
        }));
        window.dispatchEvent(new CustomEvent('toestand:after', {
            detail: {
                Identificatie: -1,
                UniekId: -1,
                SelectieMomentopname: welMomentopname
            },
            cancelable: true
        }));
        geselecteerdeToestand = false;
    }

    Applicatie.SelecteerToestand = function (wid, ti, tid) {
        if (geselecteerdeToestand) {
            if (geselecteerdeToestand.UniekId == tid) {
                // 2x dezelfde toestand: deselecteer de toestand
                Applicatie.SelecteerGeenToestand(wid, false);
                return;
            }
        }
        geselecteerdeToestand = {
            WorkId: wid,
            UniekId: tid,
            Identificatie: ti
        };

        window.dispatchEvent(new CustomEvent('toestand', {
            detail: geselecteerdeToestand,
            cancelable: true
        }));
        window.dispatchEvent(new CustomEvent('toestand:after', {
            detail: geselecteerdeToestand,
            cancelable: true
        }));
    }

    // Selectie van momentopnamen in het versiebeheer van LVBB
    Applicatie.SelecteerMomentopname = function (wid, mid) {
        window.dispatchEvent(new CustomEvent('momentopname', {
            detail: {
                WorkId: wid,
                UniekId: mid
            }
        }));
        Applicatie.SelecteerGeenToestand(wid, true);
    }

    // Selectie van uitwisselingen
    var toestanden = {
        TOESTANDEN_DATA
    };
    Applicatie.SelecteerUitwisseling = function (gemaaktOp) {
        window.dispatchEvent(new CustomEvent('uitwisseling', {
            detail: gemaaktOp
        }));
        if (geselecteerdeToestand) {
            var uniekId = -1;
            toestanden[geselecteerdeToestand.Identificatie].forEach((periode) => {
                if (periode[0] <= gemaaktOp) {
                    uniekId = periode[1];
                }
            });
            if (uniekId != geselecteerdeToestand.UniekId) {
                // Pas de toestandselectie aan 
                Applicatie.SelecteerToestand(geselecteerdeToestand.Identificatie, uniekId);
            }
        }
        // Uitwisselingen en projectacties delen dezelfde tijdlijn
        window.dispatchEvent(new CustomEvent('projectactie', {
            detail: gemaaktOp
        }));
    }

    // Selectie van projectacties
    Applicatie.SelecteerProjectactie = function (uitgevoerdOp) {
        Applicatie.SelecteerUitwisseling(uitgevoerdOp);
    }

    // Initialisatie van een diagram
    Applicatie.InitialseerDiagram = function (svgElementId) {
        // svgPanZoom werkt niet als de SVG hidden is
        // Wacht daarom totdat het diagram in beeld komt
        new IntersectionObserver(function (entries, observer) {
            if (entries[0].isIntersecting) {
                observer.unobserve(document.getElementById(svgElementId));

                svgPanZoom('#' + svgElementId, {
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: true,
                    center: true
                })
            }
        }, {
            threshold: 0
        }).observe(document.getElementById(svgElementId));
    }

    // Luister naar zowel een touch als een click event; niet gebruiken voor <input>s
    Applicatie.AddTouchStartClickListener = function (elt, handler) {
        elt.addEventListener('touchstart', handler);
        elt.addEventListener('click', handler);
    }

    // Voorkom dat een touchtstart event later nog als click event uitgevoerd wordt
    Applicatie.EnkeleTouchStartClick = function (e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
    }

    return Applicatie;
})();

