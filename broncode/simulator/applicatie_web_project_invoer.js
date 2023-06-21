window.addEventListener('load', function () {

    const box = document.querySelector('.box');
    const start_file = document.getElementById('_start_specificatie');
    const fileInput = document.getElementById('_start_specificatie_json');
    const fileInputFout = document.getElementById('_specificatie_fout');
    const fileInputFoutmelding = document.getElementById('_specificatie_foutmelding');
    const meldingen = document.getElementById('_heeft_meldingen');
    const meldingentabel = document.getElementById('_meldingen');
    const start_BG = document.getElementById('_start_soortBG');
    const specInput = document.getElementById('_specificatie');
    const bgSpec = document.getElementById('_bg_proces');
    const bgSpecData = document.getElementById('_bg_proces_data');
    const startknop = document.getElementById('startknop');
    const download = document.getElementById('_download_specificatie');

    startknop.style.display = 'none';
    fileInputFout.style.display = 'none';
    specInput.style.display = 'none';

    ['drag', 'dragstart', 'dragend', 'dragover', 'dragenter', 'dragleave', 'drop'].forEach(event => box.addEventListener(event, function (e) {
        e.preventDefault();
        e.stopPropagation();
    }), false);

    ['dragover', 'dragenter'].forEach(event => box.addEventListener(event, function (e) {
        box.classList.add('is-dragover');
    }), false);

    ['dragleave', 'dragend', 'drop'].forEach(event => box.addEventListener(event, function (e) {
        box.classList.remove('is-dragover');
    }), false);
    box.addEventListener('drop', function (e) {
        fileInput.files = e.dataTransfer.files;
        leesSpecificatie();
    }, false);
    fileInput.addEventListener('change', leesSpecificatie);

    function leesSpecificatie() {
        fileInputFout.style.display = '';
        bgSpecData.innerHTML = '';
        const filesArray = Array.from(fileInput.files);
        if (filesArray.length == 1) {
            var reader = new FileReader();
            reader.onload = function (evt) {
                try {
                    startInvoer(BGProcesSimulator.LeesSpecificatie(bgSpec, evt.target.result));
                }
                catch (error) {
                    fileInputFout.style.display = 'none';
                    fileInputFoutmelding.innerText = error;
                }
            }
            reader.onerror = function (evt) {
                fileInputFout.style.display = 'none';
                fileInputFoutmelding.innerText = 'Kan de specificatie niet lezen???';
            }
            reader.readAsText(filesArray[0], "UTF-8");
        } else {
            fileList.innerHTML = '';
        }
    }

    ['_soortBG_Gemeente', '_soortBG_Rijk'].forEach(id => document.getElementById(id).addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (e.target.checked) {
            startInvoer(BGProcesSimulator.Selecteer(bgSpec, e.target.value));
        }
    }), false);

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
    function startInvoer(bgpg) {
        if (bgpg) {
            start_BG.style.display = 'none';
            specInput.style.display = '';
            BGProcesSimulator.Opties.MeerdereRegelingen = document.getElementById('_optie_regelingen').checked;
            BGProcesSimulator.Opties.InformatieObjecten = document.getElementById('_optie_io').checked;
            BGProcesSimulator.Opties.Annotaties = document.getElementById('_optie_annotaties').checked;
            BGProcesSimulator.Opties.NonStopAnnotaties = document.getElementById('_optie_nonstop').checked;
            bgpg.Start(bgSpecData, startknop, download);
            if (bgpg.HeeftSpecificatieMeldingen()) {
                bgpg.ToonSpecificatieMeldingen(ToonSpecificatieMeldingen);
                meldingen.style.display = '';
            }
        }
    }
});
