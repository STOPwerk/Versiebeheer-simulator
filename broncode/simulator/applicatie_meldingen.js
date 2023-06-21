window.addEventListener('load', function () {
    function Meldingen_Aanpassen(e) {
        var show = e.srcElement.checked;
        var idx = e.srcElement.id.lastIndexOf('_');
        var ernst = e.srcElement.id.substring(idx + 1);
        var container = document.getElementById(e.srcElement.id.substring(0, idx));
        var matches = container.querySelectorAll("tr.entry_" + ernst);

        for (var i = 0; i < matches.length; i++) {
            matches[i].style.display = show ? '' : 'none';
        }
    }

    document.querySelectorAll(".meldingen_checkbox").forEach((checkbox) => {
        checkbox.addEventListener('change', Meldingen_Aanpassen);
    });
});
