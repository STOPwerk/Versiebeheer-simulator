window.addEventListener('load', function () {

    const bgSpec = document.getElementById('_bg_proces');
    const bgSpecData = document.getElementById('_bg_proces_data');
    const fileInputFout = document.getElementById('_specificatie_fout');
    const fileInputFoutmelding = document.getElementById('_specificatie_foutmelding');
    const startSpec = document.getElementById('_start');
    const startSpecKnop = document.getElementById('_start_edit');
    const opties = document.getElementById('_opties');
    const specInput = document.getElementById('_specificatie');
    const startknop = document.getElementById('startknop');
    const download = document.getElementById('_download_specificatie');
    const voorbeeld = document.getElementById('voorbeeld');

    startknop.style.display = 'none';
    startSpec.style.display = 'none';
    fileInputFout.style.display = 'none';
    specInput.style.display = 'none';

    function Optie(eltNaam, optieNaam) {
        var elt = document.getElementById(eltNaam);
        if (BGProcesGenerator.Opties[optieNaam]) {
            elt.checked = true;
            elt.disabled = true;
        } else {
            opties.style.display = '';
            elt.addEventListener('click', e => BGProcesGenerator.Opties[optieNaam] = e.target.checked);
        }
    }

    var bgpg;
    try {
        bgpg = BGProcesGenerator.LeesSpecificatie(bgSpec, voorbeeld.value);
    }
    catch (error) {
        fileInputFout.style.display = '';
        fileInputFoutmelding.innerText = error;
    }
    if (bgpg) {
        startSpec.style.display = '';
        opties.style.display = 'none';
        Optie('_optie_regelingen', 'MeerdereRegelingen');
        Optie('_optie_io', 'InformatieObjecten');
        Optie('_optie_annotaties', 'Annotaties');
        Optie('_optie_nonstop', 'NonStopAnnotaties');
        startSpecKnop.addEventListener('click', e => {
            startSpec.style.display = 'none';
            specInput.style.display = '';
            bgpg.Start(bgSpecData, startknop, download)
        });
    }
});
