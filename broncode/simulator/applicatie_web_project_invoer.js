window.addEventListener('load', function () {

    const start_container = document.getElementById('_start');
    const start_BG = document.getElementById('_start_soortBG_container');
    const start_voorbeeld = document.getElementById('_start_voorbeeld');
    const start_file = document.getElementById('_start_specificatie_container');
    const fileInputBox = document.getElementById('_start_specificatie');
    const fileInput = document.getElementById('_start_specificatie_json');
    const fileInputFout = document.getElementById('_start_specificatie_fout');
    const fileInputFoutmelding = document.getElementById('_start_specificatie_foutmelding');
    const spec_info_container = document.getElementById('_start_specificatie_info_container');
    const spec_info_bg = document.getElementById('_start_specificatie_info_soortBG');
    const spec_info_naam = document.getElementById('_start_specificatie_info_naam');
    const spec_info_beschrijving = document.getElementById('_start_specificatie_info_beschrijving');
    const optie_ju_container = document.getElementById('_start_ju');
    const simulator_container = document.getElementById('_bgps_container');
    const simulator_IO = document.getElementById('_bgps_simulator');
    const simulator_startknop = document.getElementById('_start_startknop');
    const lvbb_form = document.getElementById('_bgps_lvbb_data');
    const lvbb_startknop = document.getElementById('_bgps_lvbb_startknop');
    const lvbb_download = document.getElementById('_bgps_download_lvbb_specificatie');
    const sim_download = document.getElementById('_bgps_download_specificatie');

    lvbb_startknop.style.display = 'none';
    fileInputFout.style.display = 'none';
    spec_info_container.style.display = 'none';
    optie_ju_container.style.display = 'none';
    simulator_container.style.display = 'none';
    simulator_startknop.style.display = 'none';

    function Optie(eltNaam, optieNaam, disable) {
        var elt = document.getElementById(eltNaam);
        if (BGProcesSimulator.Opties[optieNaam]) {
            elt.checked = true;
            elt.disabled = disable;
        }
    }
    function JU_Optie() {
        optie_ju_container.style.display = document.getElementById('_start_optie_annotaties').checked || document.getElementById('_start_optie_nonstop').checked ? '' : 'none';
    }

    var simulator;
    function LeesSpecificatie(json) {
        simulator_startknop.style.display = 'none';
        fileInputFout.style.display = 'none';
        simulator = undefined;
        try {
            simulator = BGProcesSimulator.LeesSpecificatie(simulator_IO, json);
        }
        catch (error) {
            fileInputFout.style.display = '';
            fileInputFoutmelding.innerText = error;
        }
        if (simulator) {
            start_BG.style.display = 'none';
            start_file.style.display = 'none';
            optie_ju_container.style.display = 'none';
            simulator_startknop.style.display = '';

            spec_info_bg.innerText = simulator.BevoegdGezag();
            spec_info_naam.innerHTML = simulator.Naam();
            if (simulator.Beschrijving()) {
                spec_info_beschrijving.innerHTML = simulator.Beschrijving();
            }
            spec_info_container.style.display = '';

            Optie('_start_optie_regelingen', 'MeerdereRegelingen', true);
            Optie('_start_optie_io', 'InformatieObjecten', true);
            Optie('_start_optie_annotaties', 'Annotaties', false);
            Optie('_start_optie_nonstop', 'NonStopAnnotaties', false);
            JU_Optie();
        }
    }
    simulator_startknop.addEventListener('click', e => {
        start_container.style.display = 'none';
        BGProcesSimulator.Opties.MeerdereRegelingen = document.getElementById('_start_optie_regelingen').checked;
        BGProcesSimulator.Opties.InformatieObjecten = document.getElementById('_start_optie_io').checked;
        BGProcesSimulator.Opties.Annotaties = document.getElementById('_start_optie_annotaties').checked;
        BGProcesSimulator.Opties.NonStopAnnotaties = document.getElementById('_start_optie_nonstop').checked;
        BGProcesSimulator.Opties.AnnotatiesViaUitgangssituatie = BGProcesSimulator.Opties.Annotaties || BGProcesSimulator.Opties.NonStopAnnotaties ? document.getElementById('_start_optie_ju').checked : false;
        simulator_container.style.display = '';
        simulator.Start(lvbb_form, lvbb_startknop, lvbb_download, sim_download);
    });

    if (start_voorbeeld !== null) {
        start_BG.style.display = 'none';
        start_file.style.display = 'none';
        LeesSpecificatie(start_voorbeeld.value);
    } else {
        ['drag', 'dragstart', 'dragend', 'dragover', 'dragenter', 'dragleave', 'drop'].forEach(event => fileInputBox.addEventListener(event, function (e) {
            e.preventDefault();
            e.stopPropagation();
        }), false);

        ['dragover', 'dragenter'].forEach(event => fileInputBox.addEventListener(event, function (e) {
            fileInputBox.classList.add('is-dragover');
        }), false);

        ['dragleave', 'dragend', 'drop'].forEach(event => fileInputBox.addEventListener(event, function (e) {
            fileInputBox.classList.remove('is-dragover');
        }), false);
        fileInputBox.addEventListener('drop', function (e) {
            fileInput.files = e.dataTransfer.files;
            leesSpecificatieFile();
        }, false);
        fileInput.addEventListener('change', leesSpecificatieFile);

        function leesSpecificatieFile() {
            simulator_startknop.style.display = 'none';
            fileInputFout.style.display = 'none';
            simulator = undefined;
            const filesArray = Array.from(fileInput.files);
            if (filesArray.length == 1) {
                var reader = new FileReader();
                reader.onload = function (evt) {
                    LeesSpecificatie(evt.target.result);
                }
                reader.onerror = function (evt) {
                    fileInputFout.style.display = 'none';
                    fileInputFoutmelding.innerText = 'Kan de specificatie niet lezen???';
                }
                reader.readAsText(filesArray[0], "UTF-8");
            }
        }

        ['_start_soortBG_Gemeente', '_start_soortBG_Rijk'].forEach(id => document.getElementById(id).addEventListener('click', function (e) {
            if (e.target.checked) {
                start_file.style.display = 'none';
                simulator = BGProcesSimulator.Selecteer(simulator_IO, e.target.value);
                simulator_startknop.style.display = '';
            }
        }), false);
    }
    ['_start_optie_annotaties', '_start_optie_nonstop'].forEach(id => document.getElementById(id).addEventListener('click', () => JU_Optie()), false);
});
