window.addEventListener('load', function () {

    const bgSpec = document.getElementById('_bg_proces');
    const bgSpecData = document.getElementById('_bg_proces_data');
    const fileInputFout = document.getElementById('_specificatie_fout');
    const fileInputFoutmelding = document.getElementById('_specificatie_foutmelding');
    const startSpec = document.getElementById('_start');
    const startSpecKnop = document.getElementById('_start_edit');
    const opties = document.getElementById('_opties');
    var meldingen = document.getElementById('_heeft_meldingen');
    var meldingentabel = document.getElementById('_meldingen');
    const specInput = document.getElementById('_specificatie');
    const startknop = document.getElementById('startknop');
    const download = document.getElementById('_download_specificatie');
    const voorbeeld = document.getElementById('voorbeeld');

    startknop.style.display = 'none';
    startSpec.style.display = 'none';
    fileInputFout.style.display = 'none';
    specInput.style.display = 'none';
    meldingen.style.display = 'none';

    function Optie(eltNaam, optieNaam, disable) {
        var elt = document.getElementById(eltNaam);
        if (BGProcesSimulator.Opties[optieNaam]) {
            elt.checked = true;
            elt.disabled = disable;
        }
        if (!disable) {
            opties.style.display = '';
            elt.addEventListener('click', e => BGProcesSimulator.Opties[optieNaam] = e.target.checked);
        }
    }

    function ToonSpecificatieMeldingen(tijdstip, meldingen) {
        var tr = document.createElement('tr');
        var td = document.createElement('td');
        td.rowSpan = meldingen.length;
        td.innerHTML = tijdstip.WeergaveInnerHtml();
        tr.appendChild(td);
        for (let melding of meldingen) {
            meldingentabel.appendChild(tr);
            td = document.createElement('td');
            td.innerHTML = melding;
            tr.appendChild(td);
            tr = document.createElement('tr');
        }
    }

    var bgpg;
    try {
        bgpg = BGProcesSimulator.LeesSpecificatie(bgSpec, voorbeeld.value);
    }
    catch (error) {
        fileInputFout.style.display = '';
        fileInputFoutmelding.innerText = error;
    }
    if (bgpg) {
        startSpec.style.display = '';

        opties.style.display = 'none';
        Optie('_optie_regelingen', 'MeerdereRegelingen', true);
        Optie('_optie_io', 'InformatieObjecten', true);
        Optie('_optie_annotaties', 'Annotaties', false);
        Optie('_optie_nonstop', 'NonStopAnnotaties', false);

        if (bgpg.HeeftSpecificatieMeldingen()) {
            bgpg.ToonSpecificatieMeldingen(ToonSpecificatieMeldingen);
            meldingen.style.display = '';
        }

        startSpecKnop.addEventListener('click', e => {
            startSpec.style.display = 'none';
            specInput.style.display = '';
            meldingen = document.getElementById('_heeft_meldingen2');
            meldingentabel = document.getElementById('_meldingen2');
            meldingen.style.display = 'none';
            bgpg.Start(bgSpecData, startknop, download)
            if (bgpg.HeeftSpecificatieMeldingen()) {
                bgpg.ToonSpecificatieMeldingen(ToonSpecificatieMeldingen);
                meldingen.style.display = '';
            }
        });
    }
});
