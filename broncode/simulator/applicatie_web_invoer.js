window.addEventListener('load', function () {

    var tekstVakIndex = 0
    function MaakNieuwTekstvak() {
        tekstVakIndex++;
        var p = document.createElement("p");
        p.innerHTML = 'Bestand: <code>onlineInvoer' + tekstVakIndex + '</code><br><textarea name = "onlineInvoer' + tekstVakIndex + '" class="bestand"></textarea>';
        document.getElementById('Invoer').insertBefore(p, document.getElementById('NieuwTekstvak'))
    }
    MaakNieuwTekstvak();
    document.getElementById('MaakTekstvak').addEventListener('click', MaakNieuwTekstvak);

    const box = document.querySelector('.box');
    const fileInput = document.querySelector('[name="files[]"');
    const fileList = document.querySelector('.file-list');

    let droppedFiles = [];

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
        droppedFiles = e.dataTransfer.files;
        fileInput.files = droppedFiles;
        updateFileList();
    }, false);

    fileInput.addEventListener('change', updateFileList);

    function checkFileName(name) {
        if (name.toLowerCase(name).endsWith('.json') || name.toLowerCase(name).endsWith('.xml')) {
            return name;
        } else {
            return '<span class="geen_invoer">' + name + ' - geen JSON/XML bestand; wordt genegeerd.</span>'
        }
    }

    function updateFileList() {
        const filesArray = Array.from(fileInput.files);
        if (filesArray.length > 1) {
            fileList.innerHTML = '<p>Bestanden:</p><ul><li>' + filesArray.map(f => checkFileName(f.name)).join('</li><li>') + '</li></ul>';
        } else if (filesArray.length == 1) {
            fileList.innerHTML = `<p>Bestand: ${checkFileName(filesArray[0].name)}</p>`;
        } else {
            fileList.innerHTML = '';
        }
    }
});
