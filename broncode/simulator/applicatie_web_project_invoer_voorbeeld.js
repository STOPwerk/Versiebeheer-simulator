window.addEventListener('load', function () {

    const bgSpec = document.getElementById('_bg_proces');
    const bgSpecData = document.getElementById('_bg_proces_data');
    const startknop = document.getElementById('startknop');
    const download = document.getElementById('_download_specificatie');
    const voorbeeld = document.getElementById('voorbeeld');

    var bgpg = BGProcesGenerator.LeesSpecificatie(bgSpec, voorbeeld.value);
    if (bgpg) {
        bgpg.Start(bgSpecData, startknop, download);
    }
});
