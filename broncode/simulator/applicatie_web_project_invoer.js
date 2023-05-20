window.addEventListener('load', function () {

    const box = document.querySelector('.box');
    const start_file = document.getElementById('_start_specificatie');
    const fileInput = document.getElementById('_start_specificatie_json');
    const fileInputFout = document.getElementById('_specificatie_fout');
    const fileInputFoutmelding = document.getElementById('_specificatie_foutmelding');
    const start_BG = document.getElementById('_start_soortBG');
    const specInput = document.getElementById('_specificatie');
    const bgSpec = document.getElementById('_bg_proces');
    const bgSpecData = document.getElementById('_bg_proces_data');
    const startknop = document.getElementById('startknop');
    const download = document.getElementById('_download_specificatie');

    startknop.style.display = 'none';
    fileInputFout.style.display = 'none';

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
                    startInvoer(BGProcesGenerator.LeesSpecificatie(bgSpec, evt.target.result));
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
            startInvoer(BGProcesGenerator.Selecteer(bgSpec, e.target.value));
        }
    }), false);

    function startInvoer(bgpg) {
        if (bgpg) {
            start_file.style.display = 'none';
            start_BG.style.display = 'none';
            specInput.style.display = '';
            bgpg.Start(bgSpecData, startknop, download);
        }
    }
});
