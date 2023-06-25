/*==============================================================================
 *
 * Applicatie om het proces bij het bevoegd gezag (en adviesbureau) te 
 * simuleren. De applicatie simuleert de interactie tussen BG-software 
 * en eindgebruiker. Het laat zien wat een eindgebruiker moet/kan doen 
 * bij maximale software ondersteuning. Het beschrijft ook wat de
 * software geautomatiseerd doet of kan doen. De simulator geeft ook
 * aan tot welke communicatie dat leidt (via STOP) in de keten. De
 * uitwisseling met de LVBB kan gedownload worden en als invoer gebruikt
 * worden voor de simulatie van de LVBB/landelijke voorzieningen.
 * 
 * Deze applicatie is slechts een mogelijke invulling van de werking
 * van BG-software, het dient er vooral voor om aan te geven dat veel
 * van de technische details rond STOP versiebeheer weggeautomatiseerd
 * kunnen worden.
 * 
 * De invoer van de eindgebruiker is beschikbaar als een specificatie
 * in JSON die gebruikt kan worden om deze simulatie nogmaals te bekijken.
 * 
 =============================================================================*/
//#region Simulator applicatie
/*------------------------------------------------------------------------------
 *
 * BGProcesSimulator - Leest een bg_proces.json specificatie voor de simulator,
 * en bevat de algehele aansturing van de simulator.
 * 
 *----------------------------------------------------------------------------*/
class BGProcesSimulator {

    //#region Initialisatie en start van applicatie
    /*--------------------------------------------------------------------------
     *
     * Initialisatie van de generator
     *
     -------------------------------------------------------------------------*/
    /**
     * Maak de generator aan
     * @param {HTMLElement} elt_invoer - Element waarin specificatieform wordt opgebouwd
     * @param {string} titel - Titel van de invoerpagina
     */
    constructor(elt_invoer, bgcode, titel) {
        this.#spec_invoer = elt_invoer;
        this.#titel = titel;
        this.#data.BGCode = bgcode;
        BGProcesSimulator.#This = this;
    }
    #spec_invoer = undefined;
    #titel;

    /**
     * Maak een nieuwe specificatie op basis van het type bevoegd gezag
     * @param {HTMLElement} elt_invoer - Element waarin specificatieform wordt opgebouwd
     * @param {string} soortBG - Gemeente of Rijk
     * @returns De generator voor het bevoegd gezag
     */
    static Selecteer(elt_invoer, soortBG) {
        let bgpg = undefined;
        if (soortBG == 'Gemeente') {
            bgpg = new GemeenteProcesGenerator(elt_invoer);
            bgpg.#data.BevoegdGezag = 'Gemeente';
        }
        else if (soortBG == 'Rijk') {
            bgpg = new RijkProcesGenerator(elt_invoer);
            bgpg.#data.BevoegdGezag = 'Rijk';
        }
        return bgpg;
    }

    /*--------------------------------------------------------------------------
     *
     * Maken van de invoerpagina
     *
     -------------------------------------------------------------------------*/
    /**
     * Start met de invoer van de specificatie
     * @param {HTMLElement} elt_data - element om JSON specificatie in op te slaan
     * @param {HTMLElement} startknop - element waarin de start knop staat van de simulator
     * @param {HTMLAnchorElement} downloadLink - element met de downloadlink voor de specificatie
     */
    Start(elt_data, startknop, downloadLink) {
        SpecificatieElement.AddEventListener(this.#spec_invoer)
        this.#elt_data = elt_data;
        this.#elt_startknop = startknop;
        this.#elt_download = downloadLink;

        // Zet de specificatie om naar een intern datamodel
        this.#VertaalSpecificatie();

        // Maak de eerste versie van de pagina.
        this.#MaakPagina();
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Instantie van de generator voor het huidige scena
     */
    static This() {
        return BGProcesSimulator.#This;
    }
    static #This;

    /**
     * Opties voor de applicatie; kunnen niet tijdens de invoer gewijzigd worden
     */
    static Opties = {
        /**
         * Geeft aan dat het scenario over meerdere regelingen gaat
         */
        MeerdereRegelingen: false,
        /**
         * Geeft aan dat het scenario ook over informatieobjecten
         */
        InformatieObjecten: false,
        /**
         * Geeft aan dat het scenario annotaties bij regelingen en informatieobjecten kent
         */
        Annotaties: false,
        /**
         * Geeft aan dat het scenario annotaties bij regelingen en informatieobjecten kent
         */
        NonStopAnnotaties: false
    }

    /**
     * De specificatie van het scenario
     */
    Specificatie() {
        return this.#data;
    }
    #data = { // Data voor het scenario
        BevoegdGezag: '',
        BGCode: '',
        Beschrijving: '',
        Uitgangssituatie: {},
        Projecten: {}
    };


    /**
     * De uitgangssituatie van het scenario
     */
    Uitgangssituatie() {
        return this.#uitgangssituatie;
    }
    #uitgangssituatie;

    /**
    * Vind een vrije naam voor een nieuw object
    * @param {string[]} alBekend - lijst met namen van de al bekende objecten.
    * @param {string} prefix - Prefix van de gegenereerde naam
    * @returns De vrije naam
    */
    static VrijeNaam(alBekend, prefix) {
        if (prefix == undefined) {
            prefix = '';
        }
        for (let idx = 1; true; idx++) {
            let naam = prefix + ('00' + idx).slice(-2);
            if (!alBekend.includes(naam)) {
                return naam;
            }
        }
    }
    //#endregion

    //#region Specificatie
    /**
     * Lees een eerder aangemaakte specificatie. De informatie uit de specificatie
     * wordt gekopieerd naar een specificatie die voor deze applicatie te begrijpen is.
     * @param {HTMLElement} elt_invoer - Element waarin specificatieform wordt opgebouwd
     * @param {string} json - JSON specificatie
     */
    static LeesSpecificatie(elt_invoer, json) {
        let bgpg = undefined;
        let data = JSON.parse(json);
        if (data.BevoegdGezag) {
            if (data.BevoegdGezag == 'Gemeente') {
                bgpg = new GemeenteProcesGenerator(elt_invoer);
                bgpg.#data.BevoegdGezag = 'Gemeente';
            }
            else if (data.BevoegdGezag == 'Rijk') {
                bgpg = new RijkProcesGenerator(elt_invoer);
                bgpg.#data.BevoegdGezag = 'Rijk';
            }
            else {
                throw new Error('Invalide specificatie - onbekend bevoegd gezag');
            }
        } else {
            throw new Error('Invalide specificatie - bevoegd gezag ontbreekt');
        }
        if (data.BGCode) {
            bgpg.#data.BGCode = data.BGCode;
        } else {
            throw new Error('Invalide specificatie - BGCode ontbreekt');
        }

        if (data.Beschrijving !== undefined) {
            bgpg.#data.Beschrijving = data.Beschrijving;
        }
        if (data.Startdatum !== undefined) {
            bgpg.#data.Startdatum = data.Startdatum;
        }
        new Startdatum(bgpg.#data);

        let regelingen = {};
        let projectBranches = {};
        let uuidAanwezig = {};
        function copyWijziging(tijdstip, onderdeel, target, src, extraProps) {
            // Kopieer de specificatie van een wijzg
            if (src === undefined) {
                return;
            }
            for (let instr in src) {
                if (extraProps.includes(instr)) {
                    // Activiteit-specifieke toevoeging aan de wijziging
                    target[instr] = src[instr];
                    continue;
                }
                // De rest moeten regelingen of informatieobjecten zijn
                let soortInstrument = Instrument.SoortInstrument(instr);
                if (soortInstrument !== undefined) {
                    if (src[instr] === null || src[instr] === false) {
                        target[instr] = src[instr];
                    } else if (src[instr] === true) {
                        throw new Error(`Specificatie van onbekende versie wordt niet ondersteund in deze applicatie: voor instrument ${instr} in ${onderdeel}.`);
                    } else if (typeof src[instr] === "number") {
                        target[instr] = src[instr];
                        if (!src[instr] in uuidAanwezig) {
                            uuidAanwezig[src[instr]] = false;
                        }
                    } else {
                        target[instr] = {};
                        if (src[instr].uuid !== undefined) {
                            uuidAanwezig[src[instr].uuid] = true;
                            Instrumentversie.UUIDGebruiktInSpecificatie(src[instr].uuid)
                            target[instr].uuid = src[instr].uuid;
                        }
                        if (soortInstrument == Instrument.SoortInstrument_Regeling) {
                            regelingen[instr] = true;
                        } else {
                            BGProcesSimulator.Opties.InformatieObjecten = true;
                        }
                        let herkend = ['uuid'];
                        let annotatieNamen = [...Instrument.SoortAnnotatiesVoorInstrument[soortInstrument]];
                        if (Instrument.NonStopAnnotatiesVoorInstrument.includes(soortInstrument)) {
                            annotatieNamen.push(Annotatie.SoortAnnotatie_NonSTOP);
                        }
                        for (let annotatie of annotatieNamen) {
                            if (annotatie in src[instr]) {
                                herkend.push(annotatie);
                                let value = src[instr][annotatie];
                                if (annotatie === Annotatie.SoortAnnotatie_NonSTOP) {
                                    // Moet object zijn met non-STOP annotaties als property
                                    if (typeof value == 'object') {
                                        let valide = {}
                                        for (let ns in value) {
                                            // Toegestaan: true | false
                                            if (typeof value[ns] === 'boolean') {
                                                valide[ns] = value[ns];
                                            }
                                            else {
                                                BGProcesSimulator.SpecificatieMelding(tijdstip, `Onbekende wijziging specificatie genegeerd voor non-STOP annotatie "${ns}" van ${onderdeel}, instrument ${instr}.`);
                                            }
                                        }
                                        if (Object.keys(valide).length > 0) {
                                            BGProcesSimulator.Opties.NonStopAnnotaties = true;
                                            target[instr][annotatie] = valide;
                                        }
                                    } else {
                                        BGProcesSimulator.SpecificatieMelding(tijdstip, `Onbekende wijziging specificatie genegeerd voor non-STOP annotaties van ${onderdeel}, instrument ${instr}.`);
                                    }
                                } else if (annotatie == Annotatie.SoortAnnotatie_Citeertitel) {
                                    // Toegestaan: "..."
                                    if (typeof value === 'string') {
                                        BGProcesSimulator.Opties.Annotaties = true;
                                        target[instr][annotatie] = value;
                                    } else {
                                        BGProcesSimulator.SpecificatieMelding(tijdstip, `Onbekende specificatie genegeerd voor STOP annotatie ${annotatie} van ${onderdeel}, instrument ${instr}.`);
                                    }
                                } else {
                                    // Toegestaan: true | false
                                    if (typeof value === 'boolean') {
                                        BGProcesSimulator.Opties.Annotaties = true;
                                        target[instr][annotatie] = value;
                                    } else {
                                        BGProcesSimulator.SpecificatieMelding(tijdstip, `Onbekende specificatie genegeerd voor STOP annotatie ${annotatie} van ${onderdeel}, instrument ${instr}.`);
                                    }
                                }
                            }
                        }
                        for (let prop in src[instr]) {
                            if (!herkend.includes(prop)) {
                                BGProcesSimulator.SpecificatieMelding(tijdstip, `Onbekende eigenschap "${prop}" genegeerd van ${onderdeel}, instrument ${instr}.`);
                            }
                        }
                    }
                }
                else {
                    BGProcesSimulator.SpecificatieMelding(tijdstip, `Onbekende eigenschap "${instr}" genegeerd van ${onderdeel}.`);
                }
            }
        }
        function copyActiviteiten(project, target, src) {
            let sequentie = [];
            for (let activiteit of src) {
                if (activiteit.Soort === undefined) {
                    throw new Error('Elke activiteit moet een eigenschap "Soort" hebben.')
                }
                let spec = Activiteit.SoortActiviteit[activiteit.Soort];
                if (spec === undefined) {
                    throw new Error(`Onbekende activiteit: "Soort" = "${activiteit.Soort}".`)
                }
                if (activiteit.Tijdstip === undefined) {
                    throw new Error(`Elke activiteit moet een eigenschap "Tijdstip" hebben ("Soort" = "${activiteit.Soort}").`)
                }
                let tijdstip = new Tijdstip(undefined, { Tijdstip: activiteit.Tijdstip }, 'Tijdstip', true);

                if (spec.KanVolgenOp !== true) {
                    if (spec.KanVolgenOp.length == 0) {
                        if (sequentie.length) {
                            throw new Error(`Activiteit "${activiteit.Soort}" (Tijdstip ${tijdstip.Specificatie}) moet de eerste activiteit in project ${project} zijn.`);
                        }
                    } else {
                        let voorgangerGevonden = false;
                        for (let soort of sequentie) {
                            if (spec.KanVolgenOp.includes(soort)) {
                                voorgangerGevonden = true;
                            }
                        }
                        if (!voorgangerGevonden) {
                            throw new Error(`Activiteit "${activiteit.Soort}" (Tijdstip ${tijdstip.Specificatie}) voldoet niet aan de bedrijfsregels voor de activiteiten die eraan vooraf moeten gaan.`);
                        }
                    }
                }
                if (spec.KanNietVolgenOp !== false) {
                    let voorgangerGevonden = false;
                    for (let soort of sequentie) {
                        if (spec.KanNietVolgenOp.includes(soort)) {
                            voorgangerGevonden = true;
                        }
                    }
                    if (voorgangerGevonden) {
                        throw new Error(`Activiteit "${activiteit.Soort}" (Tijdstip ${tijdstip.Specificatie}) voldoet niet aan de bedrijfsregels voor de activiteiten die eraan vooraf mogen gaan.`);
                    }
                }
                sequentie.push(activiteit.Soort);


                let targetActiviteit = {};
                target.push(targetActiviteit);
                for (let prop in activiteit) {
                    if (['Soort', 'Tijdstip', 'Beschrijving'].includes(prop) || spec.Props.includes(prop)) {
                        targetActiviteit[prop] = activiteit[prop];
                    } else if (spec.IsWijziging) {
                        // Moet een branch zijn
                        if (projectBranches[prop] === undefined) {
                            projectBranches[prop] = project
                        } else if (projectBranches[prop] !== project) {
                            throw new Error(`Branches moeten specifiek voor een project (of overig) zijn: "${prop}" (activiteit "${activiteit.Soort}", tijdstip ${activiteit.Tijdstip})`);
                        }
                        targetActiviteit[prop] = {};
                        let mprops = spec.MomentopnameTijdstempels ? ['JuridischWerkendVanaf', 'GeldigVanaf'] : [];
                        mprops.push(...spec.MomentopnameProps);
                        copyWijziging(tijdstip, `activiteit "${activiteit.Soort}", branch "${prop}"`, targetActiviteit[prop], activiteit[prop], mprops);
                    } else {
                        BGProcesSimulator.SpecificatieMelding(tijdstip, `Onbekende eigenschap "${prop}" genegeerd van activiteit "${activiteit.Soort}".`)
                    }
                }
            }
        }

        copyWijziging(new Tijdstip(undefined, Tijdstip.StartTijd(), 'Tijdstip', false), 'Uitgangssituatie', bgpg.#data.Uitgangssituatie, data.Uitgangssituatie, []);
        if (data.Projecten !== undefined) {
            for (let project in data.Projecten) {
                bgpg.#data.Projecten[project] = []
                copyActiviteiten(project, bgpg.#data.Projecten[project], data.Projecten[project]);
            }
        }
        let uuidOntbreekt = [];
        for (let uuid in uuidAanwezig) {
            if (!uuidAanwezig[uuid]) {
                uuidOntbreekt.push(uuid);
            }
        }
        if (uuidOntbreekt.length > 0) {
            throw new Error(`Er wordt verwezen naar instrumentversies met een uuid die niet in de specificatie voorkomt: ${uuidOntbreekt.join(', ')}`);
        }

        if (Object.keys(regelingen).length > 1) {
            BGProcesSimulator.Opties.MeerdereRegelingen = true;
        }
        SpecificatieElement.VerwijderElementen();

        return bgpg;
    }

    /**
     * Registreer een melding over onvolkomenheden of aandachtspunten in de specificatie
     * @param {Tijdstip} tijdstip - Tijdstip van de activiteit
     * @param {string} melding - Te tonen melding
     */
    static SpecificatieMelding(tijdstip, melding) {
        let key = tijdstip.DatumTijdHtml();
        if (BGProcesSimulator.#SpecificatieMeldingen[key] === undefined) {
            BGProcesSimulator.#SpecificatieMeldingen[key] = {
                Tijdstip: tijdstip,
                Meldingen: []
            };
        }
        BGProcesSimulator.#SpecificatieMeldingen[key].Meldingen.push(melding);
    }

    /**
     * Geeft aan of er meldingen over de specificatie zijn. Deze kunnen zowel bij het inlezen 
     * van de specificatie aangevuld worden als bij het wijzigen ervan, als een nieuwe activiteit
     * voor een eerdere datum leidt tot inconsistenties bij latere activiteiten.
     * @returns
     */
    HeeftSpecificatieMeldingen() {
        return Object.keys(BGProcesSimulator.#SpecificatieMeldingen).length;
    }

    /**
     * Methode om de specificatiemeldingen te tonen
     * @param {any} toon - Methode die een Tijdstip en een lijst met meldingen (string array) krijgt.
     */
    ToonSpecificatieMeldingen(toon) {
        for (let key of Object.keys(BGProcesSimulator.#SpecificatieMeldingen).sort()) {
            toon(BGProcesSimulator.#SpecificatieMeldingen[key].Tijdstip, BGProcesSimulator.#SpecificatieMeldingen[key].Meldingen);
        }
    }
    static #SpecificatieMeldingen = {};

    /**
     * Zet de ingelezen specificatie om in het interne datamodel
     */
    #VertaalSpecificatie() {
        // Maak de uitgangssituatie aan
        this.#uitgangssituatie = new Uitgangssituatie(this.#data);

        // Verzamel alle activiteitspecificaties en zet ze op tijdsvolgorde
        // Verwijder de specificatie van de activiteit
        let activiteitenSpecificatie = [];
        for (let naam of Object.keys(this.#data.Projecten)) {
            let project = new Project(naam);
            for (let activiteitSpecificatie of this.#data.Projecten[naam]) {
                activiteitenSpecificatie.push({
                    Activiteit: activiteitSpecificatie,
                    Project: project
                });
            }
            this.#data.Projecten[naam] = []
        }
        activiteitenSpecificatie.sort((x, y) => x.Activiteit.Tijdstip - y.Activiteit.Tijdstip);

        // Maak het interne datamodel voor activiteiten aan
        Consolidatiestatus.WerkBij();
        for (let activiteitSpecificatie of activiteitenSpecificatie) {
            let activiteit = Activiteit.LeesSpecificatie(activiteitSpecificatie.Project, activiteitSpecificatie.Activiteit);
            if (activiteit === undefined) {
                break;
            }
            Consolidatiestatus.WerkBij();
        }
    }

    /**
     * Filter om lege objecten uit de JSON te houden
     */
    static #ObjectFilter(key, value) {
        if (key[0] !== '_' && !BGProcesSimulator.#IsEmpty(value)) {
            return value;
        }
    }
    static #IsEmpty(value) {
        if (value === undefined || value === '') {
            return true;
        }

        if (Array.isArray(value)) {
            if (value.length == 0) {
                return true;
            }
            return value.every(BGProcesSimulator.#IsEmpty);
        }
        else if (typeof (value) === 'object') {
            let all = Object.values(value);
            if (all.length == 0) {
                return true;
            }
            return all.every(BGProcesSimulator.#IsEmpty);
        }
        return false;
    }
    //#endregion

    //#region Webpagina voor applicatie
    #MaakPagina() {
        let html = `
<div id="_bgpg_modal" class="modal">
  <div class="modal-content">
    <span class="modal-close"><span id="_bgpg_modal_volgende">&#x276F;&#x276F;</span> <span id="_bgpg_modal_ok">&#x2714;</span> <span id="_bgpg_modal_cancel">&#x2716;</span></span>
    <p id="_bgpg_modal_content"></p>
  </div>
</div>
<button data-accordion="_bg_s1" class="accordion_h active">${this.#titel}</button>
<div data-accordion-paneel="_bg_s1" class="accordion_h_paneel" style = "display: block">
<p>
<b>Beschrijving van het scenario</b><br>
Geef een korte beschrijving van het scenario waarvoor deze specificatie is opgesteld (optioneel)
${new Beschrijving(this.#data).Html('div')}
</p>
<p>
<b>Uitgangssituatie</b> per ${new Startdatum(this.#data).Html()}<br>
${this.#uitgangssituatie.Html()}
</p>
</div>
<button data-accordion="_bg_s2" class="accordion_h active">Simulatie - User interface</button>
<div data-accordion-paneel="_bg_s2" class="accordion_h_paneel" style = "display: block">
<table>
    <tr><td rowspan="2" id="_bg_activiteiten"></td>
    <th id="_bg_projecten" style="height: 1px" ></th>
    <th rowspan="2"></th>
    <th></th>
    </tr>
    <tr>
        <td class="w100" id="_bg_activiteit_detail"></td>
        <td rowspan="2" id="_bg_tijdstip_detail">
            <table>
                <tr><th style="height: 1px" class="nw">Status consolidatie</th></tr>
                <tr><td class="nw" style="height: 1px" id="_bg_consolidatie_status">TODO</td></tr>
                <tr><th class="nw" style="height: 1px">Status besluiten</th></tr>
                <tr><td class="nw" id="_bg_besluit_status">TODO</td></tr>
            </table>
        </td>
    </tr>
</table>
</div>
<button data-accordion="_bg_s3" class="accordion_h active">Simulatie - Binnen de software</button>
<div data-accordion-paneel="_bg_s3" class="accordion_h_paneel" style = "display: block">
<table class="w100">
    <tr>
        <td class="nw" style="height: 1px; width: 1px;">${BGProcesSimulator.Symbool_Inhoud}</td><td>Wijziging van regeling/informatieobject</td>
        <td rowspan="4" id="_bg_verwerking"></td>
    </tr>
    <tr>
        <td style="height: 1px">${BGProcesSimulator.Symbool_Tijdstempel}</td><td>Wijziging van inwerkingtreding</td>
    </tr>
    <tr>
        <td style="height: 1px">${BGProcesSimulator.Symbool_Uitwisseling}</td><td>Uitwisseling via STOP</td>
    </tr>
    <tr>
        <td colspan="2"><div id="_bg_versiebeheer"></div></td>
    </tr>
</table>
</div>
`
        this.#spec_invoer.insertAdjacentHTML('beforeend', html);
        this.ToonGewijzigdeSpecificatie();

        document.getElementById("_bgpg_modal_volgende").addEventListener('click', () => SpecificatieElement.SluitModal(true));
        document.getElementById("_bgpg_modal_ok").addEventListener('click', () => SpecificatieElement.SluitModal(true));
        document.getElementById("_bgpg_modal_cancel").addEventListener('click', () => SpecificatieElement.SluitModal(false));
        window.dispatchEvent(new CustomEvent('init_accordion', {
            cancelable: true
        }));
    }

    /**
     * Aangeroepen als de specificatie wijzigt
     */
    ToonGewijzigdeSpecificatie() {
        Consolidatiestatus.WerkBij();
        if (this.Specificatie().Beschrijving || this.Uitgangssituatie().Instrumentversies().length > 0 || this.Specificatie().Projecten.length > 0) {
            let json = JSON.stringify(this.Specificatie(), BGProcesSimulator.#ObjectFilter, 4).trim();
            this.#elt_data.value = json;
            this.#elt_download.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(json);
            this.#elt_download.style.visibility = 'visible';
        } else {
            this.#elt_download.href = '#';
            this.#elt_download.style.visibility = 'hidden';
        }
        if (Object.keys(this.Specificatie().Projecten).length > 0) {
            this.#elt_startknop.style.display = '';
        } else {
            this.#elt_startknop.style.display = 'none';
        }
        this.#MaakActiviteitenOverzicht();
    }
    #elt_data;
    #elt_download;
    #elt_startknop;

    #MaakActiviteitenOverzicht() {
        let activiteiten = Activiteit.Activiteiten();

        // Maak een lijst van projecten op volgorde van aanmaken
        let projecten = [];
        for (let activiteit of activiteiten) {
            if (!projecten.includes(activiteit.Project())) {
                projecten.push(activiteit.Project());
            }
        }
        let html = ''
        if (projecten.length === 0) {
            // TODO: button om eerste project te maken
        } else {
            // Maak eerst de headers en tabs voor de projecten
            html += '<table class="activiteiten_overzicht"><tr><th colspan="5" class="c nw">Actie eindgebruiker</th><th>&nbsp;&nbsp;&nbsp;</th></tr>';

            // Toon de activiteiten
            for (let activiteit of activiteiten) {
                let daguur = activiteit.Tijdstip().DagUurHtml();
                html += `<tr data-bga="${activiteit.Index()}"><td class="td0">Dag</td><td class="td1">${daguur[0]}</td><td class="tu">${daguur[1]}</td><td class="tz">${activiteit.Tijdstip().DatumTijdHtml()}</td>`;
                html += `<td class="nw">${activiteit.Naam()}</td><td class="ac"></td></tr>`;
            }
            html += '</table>';
        }
        document.getElementById('_bg_activiteiten').innerHTML = html;
        new VersiebeheerDiagram('_bg_versiebeheer').Teken();
        this.#LuisterNaarEvents();
        this.#SelecteerActiviteit(-1);
    }

    #ToonActiviteit() {
        let html = '';
        if (this.#huidigeActiviteit !== undefined) {
            html += `<span class="p_tab${(this.#huidigProject === undefined ? ' huidige-prj' : '')} huidige-act" data-prj="*"">Actieverslag</span>`;
            let projecten = [];
            for (let activiteit of Activiteit.Activiteiten(this.#huidigeActiviteit.Tijdstip())) {
                if (!projecten.includes(activiteit.Project())) {
                    projecten.push(activiteit.Project());
                }
            }
            for (let project of projecten) {
                html += `<span class="p_tab${(project === this.#huidigProject ? ' huidige-prj' : '')}${(this.#huidigeActiviteit !== undefined && this.#huidigeActiviteit.ToonInProject(project) ? ' huidige-act' : '')}" data-prj=${project.Index()}>${project.Naam()}</span>`;
            }
        }
        document.getElementById('_bg_projecten').innerHTML = html;

        // Update de consolidatie en besluitstatus
        if (this.#huidigeActiviteit !== undefined) {
            document.getElementById('_bg_consolidatie_status').innerHTML = this.#huidigeActiviteit.ConsolidatiestatusHtml();
        }
        // TODO besluitstatus
        [document.getElementById('_bg_tijdstip_detail'), document.getElementById('_bg_activiteit_detail'), document.getElementById('_bg_verwerking')].forEach((elt_status) => {
            if (this.#huidigeActiviteit === undefined) {
                elt_status.classList.remove('active');
            } else {
                elt_status.classList.add('active');
            }
        });

        // Pas de selectie van activiteiten aan
        let activiteitIndex = this.#huidigeActiviteit !== undefined ? this.#huidigeActiviteit.Index() : '-';
        document.querySelectorAll('[data-bga]').forEach((elt) => {
            if (elt.dataset.bga == activiteitIndex) {
                elt.classList.add('huidige-act');
            } else {
                elt.classList.remove('huidige-act');
            }
            let act = this.#ActiviteitViaIndex(elt.dataset.bga);
            if (act !== undefined && act.ToonInProject(this.#huidigProject)) {
                elt.classList.add('huidige-prj');
            } else {
                elt.classList.remove('huidige-prj');
            }
        });
        this.#LuisterNaarEvents();
    }
    #huidigeActiviteit;

    /**
     * Toon het verslag van de uitvoering van de activiteit
     */
    #ToonActiviteitUitvoering() {
        let elt = document.getElementById('_bg_activiteit_detail');
        elt.innerHTML = 'verslag';
        this.#ToonGerelateerdeActiviteitenProjecten("*");
    }

    /**
     * Toon het project voor het geselecteerde tijdstip
     */
    #ToonProject() {
        // Zoek de activiteit met de laatste wijziging voor dit project op
        let voorActiviteit = this.#huidigeActiviteit;
        if (voorActiviteit !== undefined && !voorActiviteit.ToonInProject(this.#huidigProject)) {
            for (let activiteit of Activiteit.Activiteiten(this.#huidigeActiviteit.Tijdstip())) {
                if (activiteit.ToonInProject(this.#huidigProject)) {
                    voorActiviteit = activiteit;
                }
            }
        }

        // Toon de detailinformatie
        let elt = document.getElementById('_bg_activiteit_detail');
        if (voorActiviteit !== undefined) {
            elt.innerHTML = voorActiviteit.ProjectstatusHtml(this.#huidigeActiviteit, this.#huidigProject);
        } else {
            elt.innerHTML = '';
        }

        this.#ToonGerelateerdeActiviteitenProjecten(this.#huidigProject.Index())
    }
    #huidigProject;

    /**
     * Past de opmaak aan van activiteiten die bij een project horen,
     * en projecten bij een activiteit
     * @param {any} projectIndex
     */
    #ToonGerelateerdeActiviteitenProjecten(projectIndex) {
        document.querySelectorAll('[data-prj]').forEach((elt) => {
            if (elt.dataset.prj == projectIndex) {
                elt.classList.add('huidige-prj');
            } else {
                elt.classList.remove('huidige-prj');
            }
        });
        document.querySelectorAll('[data-bga]').forEach((elt) => {
            let act = this.#ActiviteitViaIndex(elt.dataset.bga);
            if (act !== undefined && act.ToonInProject(this.#huidigProject)) {
                elt.classList.add('huidige-prj');
            } else {
                elt.classList.remove('huidige-prj');
            }
        });
    }
    //#endregion

    //#region Symbolen
    static Symbool_Inhoud = '&#128214;'; // https://unicode-table.com/en/1F4D6/ open book
    static Symbool_Tijdstempel = '&#128344;' // https://unicode-table.com/en/1F558/ clock 9
    static Symbool_Uitwisseling = '&#128721;' // https://unicode-table.com/en/1F6D1/ STOP sign
    //#endregion

    //#region UI events
    /**
     * Methode om event handlers te maken voor klikbare onderdelen van de UI
     */
    #LuisterNaarEvents() {
        document.querySelectorAll('[data-bga]').forEach((elt) => {
            if (elt.dataset.lne === undefined) {
                elt.dataset.lne = true;
                elt.addEventListener('click', (e) => BGProcesSimulator.#BehandelEvent(e));
            }
        });
        document.querySelectorAll('[data-prj]').forEach((elt) => {
            if (elt.dataset.lne === undefined) {
                elt.dataset.lne = true;
                elt.addEventListener('click', (e) => BGProcesSimulator.#BehandelEvent(e));
            }
        });
    }
    /**
     * Afhandeling van de events
     * @param {any} e
     */
    static #BehandelEvent(e) {
        if (e.currentTarget.dataset.bga !== undefined) {
            BGProcesSimulator.This().#SelecteerActiviteit(parseInt(e.currentTarget.dataset.bga), e.currentTarget.dataset.prj === undefined);
        }
        if (e.currentTarget.dataset.prj === "*") {
            BGProcesSimulator.This().#SelecteerProject();
        }
        else if (e.currentTarget.dataset.prj !== undefined) {
            BGProcesSimulator.This().#SelecteerProject(parseInt(e.currentTarget.dataset.prj));
        }
    }

    /**
     * Selecteer eerst de activiteit
     * @param {int} activiteitIndex - Index() van de activiteit
     */
    #SelecteerActiviteit(activiteitIndex, toonProject) {
        // Zoek uit welke activiteit geselecteerd is
        let activiteit = this.#ActiviteitViaIndex(activiteitIndex);
        if (activiteit === undefined) {
            // Kunnen we de huidig geselecteerde activiteit blijven gebruiken?
            activiteit = this.#huidigeActiviteit;
            if (activiteit !== undefined && !Activiteit.Activiteiten().includes(activiteit)) {
                // Nee, kan niet. Pak de laatste die ervoor zit
                activiteit = undefined;
                for (let act of Activiteit.Activiteiten()) {
                    if (act.Tijdstip().Vergelijk(this.#huidigeActiviteit.Tijdstip()) <= 0) {
                        activiteit = act;
                    } else {
                        break;
                    }
                }
            }
        }
        if (activiteit === undefined) {
            activiteit = Activiteit.Activiteiten()[0]
        }
        this.#huidigeActiviteit = activiteit;

        // Zoek uit of het huidige project daarbij getoond kan worden
        let projecten = [];
        let huidigProject = undefined;
        if (this.#huidigeActiviteit !== undefined) {
            for (let act of Activiteit.Activiteiten()) {
                if (act.Tijdstip().Vergelijk(this.#huidigeActiviteit.Tijdstip()) <= 0 && !projecten.includes(act.Project())) {
                    projecten.push(act.Project());
                }
            }
            // Kijk of het geselecteerde project al bestaat op dit tijdstip
            if (this.#huidigProject !== undefined) {
                if (!projecten.includes(this.#huidigProject)) {
                    huidigProject = undefined;
                } else if (!this.#huidigeActiviteit.ToonInProject(this.#huidigProject)) {
                    huidigProject = undefined;
                } else {
                    huidigProject = this.#huidigProject;
                }
            }
        }
        this.#huidigProject = huidigProject;

        // Pas de UI aan
        this.#ToonActiviteit();
        if (huidigProject === undefined) {
            this.#ToonActiviteitUitvoering();
        } else {
            this.#ToonProject();
        }
    }

    /**
     * Zoek een activiteit op aan de hand van de index
     * @param {any} activiteitIndex
     * @returns
     */
    #ActiviteitViaIndex(activiteitIndex) {
        for (let act of Activiteit.Activiteiten()) {
            if (act.Index() == activiteitIndex) {
                return act;
            }
        }
    }

    /**
     * Selecteer een project in het overzicht
     * @param {int} projectIndex - Index() van het project
     */
    #SelecteerProject(projectIndex) {
        if (this.#huidigeActiviteit === undefined) {
            // Kies eerst een activiteit
            return;
        }
        this.#huidigProject = undefined;
        if (projectIndex !== undefined) {
            for (let activiteit of Activiteit.Activiteiten(this.#huidigeActiviteit.Tijdstip())) {
                if (activiteit.Project().Index() === projectIndex) {
                    this.#huidigProject = activiteit.Project();
                    break;
                }
            }
        }
        if (this.#huidigProject === undefined) {
            projectIndex = "*";
        }
        document.querySelectorAll('[data-prj]').forEach((elt) => {
            if (elt.dataset.prj == projectIndex) {
                elt.classList.add('huidige-prj');
            } else {
                elt.classList.remove('huidige-prj');
            }
        });
        document.querySelectorAll('[data-bga]').forEach((elt) => {
            let act = this.#ActiviteitViaIndex(elt.dataset.bga);
            if (act !== undefined && act.ToonInProject(this.#huidigProject)) {
                elt.classList.add('huidige-prj');
            } else {
                elt.classList.remove('huidige-prj');
            }
        });
        if (this.#huidigProject === undefined) {
            this.#ToonActiviteitUitvoering();
        } else {
            this.#ToonProject();
        }
    }
    //#endregion

}

//#region Specialisaties voor bevoegd gezagen
/*------------------------------------------------------------------------------
 *
 * GemeenteProcesGenerator - Invulling van de procesgenerator voor
 * processtappen die gebruikelijk zijn voor een gemeente.
 * 
 *----------------------------------------------------------------------------*/
class GemeenteProcesGenerator extends BGProcesSimulator {
    constructor(elt_invoer) {
        super(elt_invoer, 'gm9999', 'Scenario voor een gemeente');
    }

    MogelijkePublicatie(isVaststellingsbesluitGepubliceerd) {
        if (isVaststellingsbesluitGepubliceerd) {
            return '(concept-)rectificatie';
        } else {
            return '(concept-)besluit';
        }
    }
}

/*------------------------------------------------------------------------------
 *
 * RijkProcesGenerator - invulling van de procesgenerator voor processtappen 
 * die gebruikelijk zijn voor de rijksoverheid.
 * 
 *----------------------------------------------------------------------------*/
class RijkProcesGenerator extends BGProcesSimulator {
    constructor(elt_invoer) {
        super(elt_invoer, 'mnre9999', 'Scenario voor de rijksoverheid');
    }

    MogelijkePublicatie(isVaststellingsbesluitGepubliceerd) {
        if (isVaststellingsbesluitGepubliceerd) {
            return '(concept-)vervolgbesluit of rectificatie';
        } else {
            return '(concept-)besluit';
        }
    }
}

//#endregion

//#region Weergave van het versiebeheer
class VersiebeheerDiagram {

    //#region Publieke interface
    /**
     * Maakt een generator voor het versiebeheerdiagram aan
     * @param {string} elt_id - identificatie van het HTML element waarin het diagram geplaatst moet worden
     */
    constructor(elt_id) {
        this.#elt_id = elt_id;
    }
    #elt_id;
    #svg = ''; // SVG tot nu toe

    /**
     * Tekent het diagram
     */
    Teken() {
        this.#MaakSvg();
        let svg_id = this.#elt_id + '_svg';
        document.getElementById(this.#elt_id).innerHTML = `<svg id="${svg_id}" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: 100%; height: 100%;" viewBox="0 0 ${this.#breedte} ${this.#hoogte}" version="1.1">
        ${this.#svg}
        Deze browser ondersteunt geen SVG
        </svg>`;

        // svgPanZoom werkt niet als de SVG hidden is
        // Wacht daarom totdat het diagram in beeld komt
        new IntersectionObserver(function (entries, observer) {
            if (entries[0].isIntersecting) {
                observer.unobserve(document.getElementById(svg_id));

                svgPanZoom('#' + svg_id, {
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: true,
                    center: true
                })
            }
        }, {
            threshold: 0
        }).observe(document.getElementById(svg_id));
    }

    //#endregion

    //#region Hulpfuncties en constanten
    #ElementBreedte = 60 // Breedte van een momentopname rechthoek in diagram-eenheden
    #ElementHoogte = 30 // Hoogte van een momentopname rechthoek in diagram - eenheden
    #TussenruimteBreedte = this.#ElementBreedte / 2;
    #TussenruimteHoogte = this.#ElementHoogte * 2;
    #TijdstipBreedte = 100 // Breedte van de tekst met een tijdstip
    #NaamBreedte = 100 // Breedte van de naam van een project of branch
    #NaamHoogte = 25 // Hoogte van de naam van een project of branch
    #Punt_d = 7 // Afstand punt - punt tot raakpunt haaks op de lijn
    #Punt_0 = 4 // Afstand punt - raakpunt langs de lijn
    #Punt_1 = 10 // Afstand punt - punt - raakpunt langs de lijn

    #Registreer(x, y, w, h, key) {
        if (key !== undefined) {
            this.#positie[key] = { x: x, y: y, w: w, h: h };
        }
        if (x + w + this.#TussenruimteBreedte > this.#breedte) {
            this.#breedte = x + w + this.#TussenruimteBreedte;
        }
        if (y + h + this.#TussenruimteHoogte > this.#hoogte) {
            this.#hoogte = y + h + this.#TussenruimteHoogte;
        }
    }
    #positie = {} // Cache van posities (array met x, y, w, h)
    #breedte = 0; // Breedte tot nu toe
    #hoogte = 0; // Hoogte tot nu toe
    //#endregion

    //#region Stel de svg samen
    #MaakSvg() {
        let heeftUitgangssituatie = BGProcesSimulator.This().Uitgangssituatie().JuridischWerkendVanaf() !== undefined;

        this.#MaakProjectBranchKoppen(heeftUitgangssituatie);

        if (heeftUitgangssituatie) {
            this.#VoegUitgangssituatieToe();
        }

        for (let activiteit of Activiteit.Activiteiten()) {
            this.#VoegActiviteitToe(activiteit);
        }
    }

    /**
     * Maak de koppen met de project- en branchnamen
     */
    #MaakProjectBranchKoppen(heeftUitgangssituatie) {
        let projecten = [];
        for (let act of Activiteit.Activiteiten()) {
            if (!projecten.includes(act.Project())) {
                projecten.push(act.Project());
            }
        }

        let xProject = this.#TussenruimteBreedte + this.#TijdstipBreedte + this.#TussenruimteBreedte;
        let yProject = this.#NaamHoogte;
        let hProject = this.#NaamHoogte;
        let yBranch = yProject + hProject + this.#NaamHoogte;
        let hBranch = this.#ElementHoogte;
        let wBranch = this.#NaamBreedte;
        if (heeftUitgangssituatie) {
            let wProject = this.#NaamBreedte;
            this.#Registreer(xProject, yProject, wProject, hProject);
            this.#svg += `<text x="${xProject + wProject / 2}" y="${yProject}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">Uitgangssituatie</text>
                          <path d="M ${xProject} ${yProject + hProject} L ${xProject + wProject} ${yProject + hProject}" class="bgvbd_naam_l"/>`;
            xProject += wProject + this.#TussenruimteBreedte;
        }
        for (let project of projecten) {
            let branches = Branch.Branches(undefined, project);
            if (branches.length == 0) {
                continue;
            }
            let wProject = branches.length * this.#NaamBreedte + (branches.length - 1) * this.#TussenruimteBreedte;
            this.#Registreer(xProject, yProject, wProject, hProject);

            this.#svg += `<text x="${xProject + wProject / 2}" y="${yProject}" data-prj="${project.Index()}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">${project.Naam()}</text>
                          <path d="M ${xProject} ${yProject + hProject} L ${xProject + wProject} ${yProject + hProject}" class="bgvbd_naam_l"/>`;
            let xBranch = xProject;
            for (let branch of branches) {
                this.#Registreer(xBranch, yBranch, wBranch, hBranch, branch.Index());
                this.#svg += `<text x="${xBranch + wBranch / 2}" y="${yBranch}" data-prj="${project.Index()}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">${branch.Naam()}</text>`;
                xBranch += wBranch + this.#TussenruimteBreedte;
            }

            xProject += wProject + this.#TussenruimteBreedte;
        }
    }

    /**
     * Voeg een blokje toe voor de uitgangssituatie
     */
    #VoegUitgangssituatieToe() {
        let x = this.#TussenruimteBreedte + (this.#NaamBreedte - this.#ElementBreedte) / 2;
        let y = this.#hoogte;
        let w = this.#TijdstipBreedte;
        let h = this.#ElementHoogte;
        this.#svg += `<text x="${x}" y="${y + h / 2}" dominant-baseline="middle" text-anchor="start" class="bgvbd_naam">${BGProcesSimulator.This().Uitgangssituatie().Tijdstip().DatumTijdHtml()}</text>`;

        x += w + this.#TussenruimteBreedte;
        w = this.#ElementBreedte;
        this.#Registreer(x, y, w, h, BGProcesSimulator.This().Uitgangssituatie().Index());
        this.#svg += `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="3" ry="3" class="bgvbd_mo_u"></rect>
                      <text x="${x + w / 2}" y="${y + h / 2}" dominant-baseline="middle" text-anchor="middle" class="bgvbd_symbolen">${BGProcesSimulator.Symbool_Inhoud}${BGProcesSimulator.Symbool_Tijdstempel}</text>`;
    }

    /**
     * Voeg de bijdrage van een activiteit toe
     * @param {any} activiteit
     */
    #VoegActiviteitToe(activiteit) {
        // Zoek uit welke branches geraakt worden en hoe ze van elkaar afhangen
        let momentopnamen = activiteit.Momentopnamen();
        momentopnamen.sort((a, b) => Branch.Vergelijk(a.Branch(), b.Branch()));
        if (momentopnamen.length === 0) {
            return;
        }
        let teTekenenOpRij = {}; // key = momentopname, value = rij waarop de mo getekend moet worden
        let aantalRijen = 0;
        let teTekenen = momentopnamen;
        while (teTekenen.length > 0) {
            aantalRijen += 1;
            let gePlaatst = [];
            let tekenenOpVolgendeRij = [];

            for (let mo of teTekenen) {
                if (mo.Index() in teTekenenOpRij) {
                    // Is blijkbaar al eens geplaatst
                    continue;
                }
                if (tekenenOpVolgendeRij.includes(mo)) {
                    // Nu even niet
                    continue;
                }
                if (mo.TegelijkBeheerd() !== undefined && mo.Project() !== activiteit.Project()) {
                    // Gebruik dezelfde rij als de momentopname die voor het project van de activiteit wordt toegewezen.
                    continue;
                }

                let kanGetekendWorden = true;
                for (let v of [mo.VoorgaandeMomentopname(), ...mo.OntvlochtenMet(), ...mo.VervlochtenMet()]) {
                    if (v !== undefined && teTekenen.includes(v)) {
                        // Teken de voorgaande/vervlochten/ontvlochten momentopname eerder/hoger
                        kanGetekendWorden = false;
                        break;
                    }
                }
                if (kanGetekendWorden) {
                    if (mo.TegelijkBeheerd() === undefined) {
                        // Teken op deze rij
                        teTekenenOpRij[mo.Index()] = aantalRijen;
                        gePlaatst.push(mo);
                    } else {
                        // Zet alle tegelijk beheerde op een rij
                        // Komen ze naast elkaar te staan in het diagram zonder andere ertussen?
                        let aansluitend = undefined;
                        let tussenliggend = [];
                        for (let m of momentopnamen) {
                            if (mo.TegelijkBeheerd().includes(m)) {
                                if (aansluitend === undefined) {
                                    // De eerste van het stel
                                    aansluitend = mo.TegelijkBeheerd().length;
                                }
                                if (--aansluitend == 0) {
                                    // De laatste van het stel
                                    break;
                                }
                            } else {
                                // Deze momentopname zit er tussen
                                let rijNummer = teTekenenOpRij[mo.Index()]
                                if (rijNummer === undefined) {
                                    // Niet op deze rij tekenen
                                    tussenliggend.push(m);
                                } else if (rijNummer == aantalRijen) {
                                    // Zet al deze momentopnamen op de volgende rij
                                    tekenenOpVolgendeRij.push(...mo.TegelijkBeheerd());
                                    tussenliggend = [];
                                    kanGetekendWorden = false;
                                    break;
                                } else {
                                    // Zit al op een eerdere rij
                                }
                            }
                        }
                        if (tussenliggend.length > 0) {
                            // Teken de tussenliggende momentopnamen op de volgende rij
                            tekenenOpVolgendeRij.push(...tussenliggend);
                        }
                        if (kanGetekendWorden) {
                            for (let m of mo.TegelijkBeheerd()) {
                                if (teTekenen.includes(m)) {
                                    teTekenenOpRij[m.Index()] = aantalRijen;
                                    gePlaatst.push(m);
                                }
                            }
                        }
                    }
                }
            }
            teTekenen = teTekenen.filter((mo) => !gePlaatst.includes(mo));
        }

        // Teken het tijdstip
        let y = this.#hoogte;
        {
            let x = this.#TussenruimteBreedte;
            let h = aantalRijen * this.#ElementHoogte + (aantalRijen - 1) * this.#TussenruimteHoogte;
            this.#svg += `<text x="${x}" y="${y + h / 2}" data-bga="${activiteit.Index()}" dominant-baseline="middle" text-anchor="start" class="bgvbd_naam">${activiteit.Tijdstip().DatumTijdHtml()}</text>`;
            if (aantalRijen > 1) {
                let xl = x + this.#NaamBreedte + this.#TussenruimteBreedte / 4;
                this.#svg += `<path d="M ${xl} ${y} L ${xl} ${y + h}" class="bgvbd_naam_l"/>`;
            }
        }

        // Teken de momentopnamen
        let mo_css = activiteit.UitgevoerdDoorAdviesbureau() ? 'a' : 'bg';
        let w = this.#ElementBreedte;
        let h = this.#ElementHoogte;
        for (let rijNummer = 1; rijNummer <= aantalRijen; rijNummer++) {
            let getekend = [];
            for (let mo of momentopnamen.filter((m) => teTekenenOpRij[m.Index()] === rijNummer)) {
                if (getekend.includes(mo)) {
                    continue;
                }

                let symbolen = '';
                if (mo.HeeftGewijzigdeInstrumentversie()) {
                    symbolen += BGProcesSimulator.Symbool_Inhoud;
                }
                if (mo.HeeftGewijzigdeTijdstempels()) {
                    symbolen += BGProcesSimulator.Symbool_Tijdstempel;
                }
                if (activiteit.Uitwisselingen().length > 0) {
                    symbolen += BGProcesSimulator.Symbool_Uitwisseling;
                }

                // Teken alle momentopnamen
                let teTekenen = [mo];
                if (mo.TegelijkBeheerd() !== undefined) {
                    teTekenen = momentopnamen.filter((m) => mo.TegelijkBeheerd().includes(m)); // in de juiste volgorde
                }
                let xPerMO = {};
                for (let m of teTekenen) {
                    let branchPositie = this.#positie[m.Branch().Index()];
                    xPerMO[m.Index()] = branchPositie.x + (branchPositie.w - w) / 2;
                }
                if (teTekenen.length > 1) {
                    // Teken een omhullende
                    let xBox = xPerMO[teTekenen[0]];
                    let wBox = xPerMO[teTekenen[teTekenen.length - 1]] = xBox + w;
                    this.#svg += `<rect x="${xBox}" y="${y}" width="${wBox}" height="${h}" rx="3" ry="3" class="bgvbd_mo_tegelijk"></rect>`;
                }

                for (let tekenMO of teTekenen) {
                    // Teken de momentopname
                    getekend.push(tekenMO);
                    let x = xPerMO[tekenMO.Index()];
                    this.#Registreer(x, y, w, h, tekenMO.Index());
                    this.#svg += `<rect x="${x}" y="${y}" width="${w}" height="${h}" data-bga="${activiteit.Index()}" data-prj="${tekenMO.Branch().Project().Index()}" rx="3" ry="3" class="bgvbd_mo_${mo_css}"></rect>
                                  <text x="${x + w / 2}" y="${y + h / 2}" data-bga="${activiteit.Index()}" data-prj="${tekenMO.Branch().Project().Index()}" dominant-baseline="middle" text-anchor="middle" class="bgvbd_symbolen">${symbolen}</text>`;

                    // Teken de lijn vanaf de vorige momentopname
                    if (tekenMO.VoorgaandeMomentopname() !== undefined) {
                        // Dit is de branchlijn
                        let positieVorigeMO = this.#positie[tekenMO.VoorgaandeMomentopname().Index()];
                        if (tekenMO.VoorgaandeMomentopname().Branch() == tekenMO.Branch()) {
                            this.#svg += `<path d="M ${x + w / 2} ${positieVorigeMO.y + positieVorigeMO.h} L ${x + w / 2} ${y}" class="bgvbd_line_branch"/>`;
                        } else {
                            // Basisversie
                            this.#LijnMetPijlpunt(tekenMO.VoorgaandeMomentopname(), tekenMO, 0, 0.5, 0.25, true, 'basis')
                        }
                    }
                    // Ver- en ontvlechtingen
                    for (let v of tekenMO.VervlochtenMet()) {
                        this.#LijnMetPijlpunt(v, tekenMO, 0.5, 0.25, 0.5, false, 'vv')
                    }
                    for (let v of tekenMO.OntvlochtenMet()) {
                        this.#LijnMetPijlpunt(v, tekenMO, -0.5, 0.375, 0.375, false, 'ov')
                    }
                }
            }
            // Volgende rij
            y += h + this.#TussenruimteHoogte;
        }
    }

    /**
     * Teken een lijn met een pijlpunt - dit zijn relaties tussen branches
     * @param {Momentopname} van - Momentopname waar de pijl begint
     * @param {Momentopname} naar - Momentopname waar de pijl eindigt
     * @param {number} dx - Fractie van de elementbreedte, vanaf de branchlijn tot het punt waar de lijn start/eindigt
     * @param {any} dy - Fractie van verticale tussenruimte waar de lijn eerst naar toe gaat
     * @param {any} t_dx - Fractie van horizontale tussenruimte, afstand van element tot de vertikale lijn
     * @param {any} isBasis - Vereenvoudige lijn voor de basisversie
     * @param {any} css - CSS voor weergave
     */
    #LijnMetPijlpunt(van, naar, dx, dy, t_dx, isBasis, css) {
        let vanPositie = this.#positie[van.Index()];
        let naarPositie = this.#positie[naar.Index()];
        dx = Math.round(dx * this.#ElementBreedte / 2);
        dy = Math.round(dy * this.#TussenruimteHoogte);
        t_dx = Math.round(t_dx * this.#TussenruimteHoogte);

        // Lijn:
        // van b(egin) omlaag naar t(ussenpunt)1
        // van t1 naar tussenruimte t1b
        // van t1b omlaag naar t2b (*)
        // van t2b naar branchlijn, naar t2
        // van t2 naar e(eindelement)
        // Als elementen op opeenvolgende rijen liggen, is (*) niet nodig
        let yb = vanPositie.y + vanPositie.h;
        let yt1 = yb + dy; // y van t1 en t1b
        let yt2 = naarPositie.y - this.#TussenruimteHoogte + dy; // y van t2 en t2b
        if (yt2 <= yt1 + 2) {
            yt2 = yt1; // (*) is niet nodig
        }
        let ye = naarPositie.y

        // Horizontaal kan het naar links f rechts gaan
        let xb, xt1, xt2, xe;
        if (vanPositie.x < naarPositie.x) {
            xb = vanPositie.x + vanPositie.w / 2 + dx;
            xt1 = vanPositie.x + vanPositie.w + t_dx;
            xt2 = naarPositie.x - t_dx;
            xe = naarPositie.x + naarPositie.w / 2 - dx;
            if (xt2 <= xt1 + 2) {
                xt2 = xt1;
            }
        } else {
            xb = vanPositie.x + vanPositie.w / 2 - dx;
            xt1 = vanPositie.x - t_dx;
            xt2 = naarPositie.x + naarPositie.w + t_dx;
            xe = naarPositie.x + naarPositie.w / 2 + dx;
            if (xt1 <= xt2 + 2) {
                xt1 = xt2;
            }
        }
        this.#svg += `<path d="M ${xb} ${yb} L ${xb} ${yt1}`;
        if (isBasis) {
            this.#svg += ` L ${xe} ${yt1}`;
        }
        else {
            this.#svg += ` L ${xt1} ${yt1}`;
            if (yt1 != yt2) {
                this.#svg += ` L ${xt1} ${yt2}`;
            }
            if (xt1 != xt2) {
                this.#svg += ` L ${xt2} ${yt2}`;
            }
            this.#svg += ` L ${xe} ${yt2}`;
        }
        this.#svg += ` L ${xe} ${ye}" class="bgvbd_line_${css}"/>
                    <path d="M ${xe} ${ye} L ${xe - this.#Punt_d} ${ye - this.#Punt_1} L ${xe} ${ye - this.#Punt_0} L ${xe + this.#Punt_d} ${ye - this.#Punt_1} Z" class="bgvbd_line_${css}_p"/>`;
    }
    //#endregion
}
//#endregion

//#endregion

//#region Basisklassen voor UI interactie / beheer specificatie
/*==============================================================================
 *
 * Nu volgen een aantal basisklassen voor de manipulatie van de specificatie
 * en het ondersteunen van de invoer. Deze moeten hier staan omdat javascript 
 * geen forward declaration van klassen kent.
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
 *
 * SpecificatieElement is een basisklasse voor een object dat een deel van 
 * de specificatie kan manipuleren. Het maakt HTML invoervelden, handelt 
 * UI events af en zorgen dat de specificatie bijgewerkt wordt. 
 * 
 *----------------------------------------------------------------------------*/
class SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak een specificatie-element aan.
     * @param {any} eigenaarObject - Object of array in de specificatie waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Als eigenaarObject een array is, laat dit dan leeg.
     * @param {any} data - In-memory object voor het element, overschrijft een waarde in het eigenaarobject voor de eigenschap.
     *                     Als data undefined is en zowel eigenaarObject als eigenschap gegeven, dan wordt de huidige waarde 
     *                     van eigenaarObject[eigenschap] als waarde gebruikt.
     * @param {SpecificatieElement} superInvoer - SpecificatieElement waar dit een specificatie-subelement van is
     */
    constructor(eigenaarObject, eigenschap, data, superInvoer) {
        this.#index = SpecificatieElement.#element_idx++;
        SpecificatieElement.#elementen[this.#index] = this;
        this.#superInvoer = superInvoer;
        if (superInvoer !== undefined) {
            superInvoer.#subInvoer[this.#index] = this;
        }
        this.#eigenaarObject = eigenaarObject;
        this.#eigenschap = eigenschap;
        if (data !== undefined) {
            this.#WerkSpecificatieBij(data);
        } else {
            if (eigenaarObject !== undefined && eigenschap !== undefined) {
                this.#data = eigenaarObject[eigenschap];
            }
        }
        SpecificatieElement.#elementen[this.Index()] = this;
    }
    //#endregion

    //#region Te implementeren/aan te passen in afgeleide klassen
    /**
     * Aangeroepen om de HTML voor een read-only weergave te maken van de invoer.
     * Deze wordt gepresenteerd binnen de container die door WeergaveHtml wordt klaargezet 
     * Wordt geïmplementeerd in afgeleide klassen.
     */
    WeergaveInnerHtml() {
        return '';
    }

    /**
     * Aangeroepen om de HTML voor de invoer te maken, zoals die voorkomt in het modal invoerscherm,
     * binnen de container die door InvoerHtml wordt klaargezet.
     * Als al bekend is dat er een volgende stap in de invoer nodig is, dan moet in deze methode 
     * of in InvoerIntroductie de VolgendeStapNodig methode aangeroepen worden.
     * Wordt geïmplementeerd in afgeleide klassen.
     */
    InvoerInnerHtml() {
        return '';
    }

    /**
     * Aangeroepen als er op een element geklikt wordt in de weergave-html. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnWeergaveClick(elt, idSuffix) {
    }

    /**
     * Aangeroepen als er iets in de invoer is gewijzigd. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is; weggelaten als kind-specificatie-element gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnInvoerChange(elt, idSuffix) {
    }

    /**
     * Aangeroepen als er in de invoer geklikt wordt. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnInvoerClick(elt, idSuffix) {
    }

    /**
     * Aangeroepen vlak voordat het modal scherm getoond wordt: prepareer het specificatie-element voor
     * de invoer van een nieuwe waarde.
     */
    BeginInvoer() {
        return true;
    }

    /**
     * Aangeroepen vlak voordat de invoer van de huidige stap afgerond wordt: valideer de gewijzigde invoer.
     * Als er een volgende stap in de invoer nodig is, dan kan in deze methode de VolgendeStapNodig
     * methode aangeroepen worden.
     * @param {boolean} accepteerInvoer - Geeft aan of de invoer geaccepteerd (ipv geannuleerd) wordt.
     * @returns {boolean} Geeft aan of de invoer nog niet beëindigd kan worden. Bij true wordt de invoerstap niet gesloten.
     */
    ValideerInvoer(accepteerInvoer) {
        return false;
    }

    /**
     * Aangeroepen vlak voordat het modal scherm gesloten wordt: verwerk de gewijzigde invoer.
     * Als er een volgende stap in de invoer nodig is, dan kan in deze methode als laatste de VolgendeStapNodig
     * methode aangeroepen worden.
     * @param {boolean} accepteerInvoer - Geeft aan of de invoer geaccepteerd (ipv geannuleerd) wordt.
     */
    EindeInvoer(accepteerInvoer) {
    }

    /**
     * Aangeroepen vlak nadat het modal scherm gesloten is en de niet-modal pagina is bijgewerkt.
     * @param {boolean} accepteerInvoer - Geeft aan of de invoer geaccepteerd (ipv geannuleerd) wordt.
     */
    EindeModal(accepteerInvoer) {
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Geef het specificatie-element waar dit een onderdeel van is
     */
    SuperInvoer() {
        return this.#superInvoer;
    }
    #superInvoer;
    /**
     * Geef de specificatie-elementen die voor een onderdeel van deze specificatie zijn aangemaakt
     */
    SubManagers() {
        return Object.values(this.#subInvoer);
    }
    #subInvoer = {};

    /**
     * Geef de unieke code voor dit specificatie-element
     */
    Index() {
        return this.#index;
    }
    #index = 0;

    /**
     * Geeft het object of array in de specificatie waar dit een eigenschap van is
     */
    EigenaarObject() {
        return this.#eigenaarObject;
    }
    #eigenaarObject;

    /**
     * Geeft de eigenschap waaraan dit element toegekend wordt. Als eigenaarObject een array is, dan is dit indefined.
     */
    Eigenschap() {
        return this.#eigenschap;
    }
    #eigenschap;

    /**
     * Geef het in-memory object voor het element
     */
    Specificatie() {
        return this.#data;
    }
    /**
     * Geef de eigenschap een andere waarde
     */
    SpecificatieWordt(data) {
        this.#WerkSpecificatieBij(data);
    }
    //#endregion

    //#region Status voor de invoer/weergave
    /**
     * Geeft aan of het specificatie-element actief is in het modal scherm (en niet in de weergave van de overzichtspagina)
     * @returns
     */
    IsInvoer() {
        return this.#isInvoer;
    }
    #isInvoer = false;

    /**
     * Geeft aan of het specificatie-element read-only is en niet gewijzigd mag worden.
     * @returns
     */
    IsReadOnly() {
        return this.#isReadOnly;
    }
    #isReadOnly = false;

    /**
     * Geeft de stap in een invoerscherm waarvan de invoer in verschillende stappen uitgevoerd moet worden
     * @returns
     */
    InvoerStap() {
        return this.IsInvoer() ? this.#invoerStap : 0;
    }
    #invoerStap;

    //#endregion

    //#region Hulpfuncties om de html te maken
    /**
     * Geef het ID voor een HTML element gemaakt door het specificatie-element
     * @param {string} idSuffix - Suffix voor de identificatie van het element
     */
    ElementId(idSuffix) {
        let id = `_bgpg_${this.#index}_${(this.IsInvoer() ? 'I' + this.InvoerStap() : 'W')}`;
        if (idSuffix !== undefined && idSuffix !== '') {
            id += '_' + idSuffix;
        }
        return id;
    }
    /**
     * Geef het HTML element gemaakt door het specificatie-element
     * @param {string} idSuffix - Suffix voor de identificatie van het element
     */
    Element(idSuffix) {
        return document.getElementById(this.ElementId(idSuffix));
    }

    /**
     * Geef de dataset declaratie voor het top-level element
     */
    DataSet() {
        return `data-se="${this.#index}"`;
    }

    /**
     * Maakt de HTML voor een voegtoe knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     * @param {string} extraAttributen - Extra attributen voor de knop
     */
    HtmlVoegToe(hint, idSuffix, extraAttributen) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} ${(extraAttributen === undefined ? '' : extraAttributen)} class="voegtoe">&#x271A;</span>`;
    }
    /**
     * Maakt de HTML voor een edit knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     * @param {string} extraAttributen - Extra attributen voor de knop
     */
    HtmlWerkBij(hint, idSuffix, extraAttributen) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} ${(extraAttributen === undefined ? '' : extraAttributen)} class="werkbij">&#x270E;</span>`;
    }
    /**
     * Maakt de HTML voor een verwijder knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     * @param {string} extraAttributen - Extra attributen voor de knop
     */
    HtmlVerwijder(hint, idSuffix, extraAttributen) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} ${(extraAttributen === undefined ? '' : extraAttributen)} class="verwijder">&#x1F5D1;</span>`;
    }
    //#endregion

    //#region Openen van modal invoerscherm
    /**
     * Open een modal invoer scherm voor de invoer van de gegevens waarvoor dit specificatie-element opgezet is.
     * 
     * @param {lambda} onClose - Functie aangeroepen nadat box gesloten is; argument geeft aan of het via ok was (en niet cancel)
     */
    OpenModal(onClose) {
        if (SpecificatieElement.#modalOpener !== undefined) {
            throw Error("Programmeerfout: modal scherm is al open!");
        }
        SpecificatieElement.#modalOpener = this;
        this.#onModalClose = onClose;
        this.#invoerStap = 1;
        this.#volgendeStapNodig = false;
        this.#ModalMode(true);
        document.getElementById('_bgpg_modal_content').innerHTML = this.Html();
        document.getElementById("_bgpg_modal_volgende").style.display = this.#volgendeStapNodig ? '' : 'none';
        document.getElementById("_bgpg_modal_ok").style.display = this.#volgendeStapNodig ? 'none' : '';
        document.getElementById('_bgpg_modal').style.display = 'block';
    }
    static #modalOpener;

    /**
     * Aangeroepen om de HTML voor de weergave te maken. Afhankelijk van de IsInvoer()
     * gaat het om de weergave op (bij false) een overzichtspagina, of (bij true) het
     * modal scherm. Deze methode bepaalt alleen wat de container wordt om de eigenlijke
     * html heen: standaard een span. Kan in afgeleide klassen worden aangepast.
     * @param {string} containerElement - Optioneel: tag/naam van het containerelement om de HTML in te plaatsen
     */
    Html(containerElement = 'span') {
        if (this.#isInvoer) {
            return `<${containerElement} id="${this.ElementId('___M')}" ${this.DataSet()}>${this.InvoerInnerHtml()}</${containerElement}>`
        } else {
            return `<${containerElement} id="${this.ElementId('___W')}" ${this.DataSet()}>${this.WeergaveInnerHtml()}</${containerElement}>`
        }
    }

    /**
     * Vervang de html die eerder door InnerHtml () is gemaakt door een nieuwe versie.
     * Welke versie dat is hangt af van de huidige staat van het specificatie-element
     */
    VervangInnerHtml() {
        if (this.#isInvoer) {
            let elt = document.getElementById(this.ElementId('___M'));
            if (elt) {
                // Verifieer dat de submanagers ook klaar zijn voor de invoer
                this.#ModalMode(true);
                elt.innerHTML = this.InvoerInnerHtml();
            }
        }
        else {
            let elt = document.getElementById(this.ElementId('___W'));
            if (elt) {
                elt.innerHTML = this.WeergaveInnerHtml();
            }
        }
        if (SpecificatieElement.#modalOpener !== undefined) {
            document.getElementById("_bgpg_modal_volgende").style.display = SpecificatieElement.#modalOpener.#volgendeStapNodig ? '' : 'none';
            document.getElementById("_bgpg_modal_ok").style.display = SpecificatieElement.#modalOpener.#volgendeStapNodig ? 'none' : '';
        }
    }

    /**
     * Geeft aan dat een volgende stap nodig is voor de invoer
     */
    static VolgendeStapNodig() {
        SpecificatieElement.#modalOpener.#volgendeStapNodig = true;
    }
    #volgendeStapNodig;
    //#endregion

    //#region Interne functionaliteit: specificatie/verwijderen
    /**
     * Verwijder het element uit de specificatie met alle gerelateerde specificatie-elementen.
     */
    Verwijder() {
        this.#WerkSpecificatieBij(this.#data, undefined);
        this.destructor();
    }

    /**
     * Neem de waarde van Specificatie() over in de specificatie
     */
    #WerkSpecificatieBij(data) {
        if (this.#eigenaarObject !== undefined) {
            if (this.#eigenschap === undefined) {
                let idx = this.#data == undefined ? -1 : this.#eigenaarObject.indexOf(this.#data);
                if (data === undefined) {
                    if (idx >= 0) {
                        delete this.#eigenaarObject[idx];
                    }
                } else {
                    if (idx < 0) {
                        this.#eigenaarObject.push(data);
                    } else {
                        this.#eigenaarObject[idx] = data;
                    }
                }
            }
            else {
                if (data !== undefined) {
                    this.#eigenaarObject[this.#eigenschap] = data;
                } else if (this.#eigenaarObject[this.#eigenschap] !== undefined) {
                    delete this.#eigenaarObject[this.#eigenschap];
                }
            }
        }
        this.#data = data;
    }
    #data;

    /**
     * Verwijder alle actieve specificatie-elementen
     * @param {any} vanafTijdstip - drempelwaarde, indien gegeven worden alleen de specificatie-elementen van activiteiten na dit tijdstip weggegooid.
     */
    static VerwijderElementen(vanafTijdstip) {
        for (let gewijzigd = true; gewijzigd && Object.keys(SpecificatieElement.#elementen).length > 0;) {
            gewijzigd = false;
            for (let se of [...Object.values(SpecificatieElement.#elementen)]) {
                if (vanafTijdstip === undefined || (se.Tijdstip !== undefined && se.Tijdstip().Vergelijk(tijdstip) > 0)) {
                    se.destructor();
                    gewijzigd = true;
                    break;
                }
            }
        }
    }
    static #elementen = {};
    static #element_idx = 0;

    /**
     * Opruimen van dit specificatie-element en de specificatie-elementen die ervan afhangen.
     */
    destructor() {
        if (this.#index !== undefined) {
            let index = this.#index;
            this.#index = undefined;
            delete SpecificatieElement.#elementen[index];
            if (this.#superInvoer !== undefined) {
                delete this.#superInvoer.#subInvoer[index];
                this.#superInvoer = undefined;
            }
            for (let subInvoer of this.SubManagers()) {
                this.#subInvoer.#superInvoer = undefined;
                subInvoer.destructor();
            }
        }
    }

    //#endregion

    //#region Interne functionaliteit: invoer/modal scherm
    /**
     * Omzetten van de #invoer naar aanleiding van het openen/sluiten van het modal scherm
     * @param {boolean} isInvoer Geeft aan of de modal box open is
     */
    #ModalMode(isInvoer) {
        while (true) {
            let numMgr = this.SubManagers().length;

            for (let subInvoer of this.SubManagers()) {
                subInvoer.#ModalMode(isInvoer);
            }
            if (this.#isInvoer !== isInvoer) {
                this.#isInvoer = isInvoer;
                if (isInvoer) {
                    this.BeginInvoer();
                }
            }

            // Er kunnen specificatie-elementen bijgemaakt worden
            if (this.SubManagers().length === numMgr) {
                break;
            }
        }
    }

    /**
     * Sluit de modal invoer box
     * @param {boolean} accepteerInvoer - Geeft aan of het via ok was (en niet cancel)
     */
    static SluitModal(accepteerInvoer) {
        if (SpecificatieElement.#modalOpener === undefined) {
            return;
        }
        let modalOpener = SpecificatieElement.#modalOpener;
        let kanNietSluiten = modalOpener.#ModalVerwerk((im) => im.ValideerInvoer(accepteerInvoer), true);
        if (kanNietSluiten) {
            return;
        }
        modalOpener.#ModalVerwerk((im) => im.EindeInvoer(accepteerInvoer));
        if (modalOpener.#volgendeStapNodig) {
            modalOpener.#volgendeStapNodig = false;
            modalOpener.#invoerStap++;
            modalOpener.VervangInnerHtml();
            return;
        }

        SpecificatieElement.#modalOpener = undefined;
        modalOpener.#ModalMode(false);
        document.getElementById('_bgpg_modal').style.display = 'none';
        document.getElementById('_bgpg_modal_content').innerHTML = '';
        modalOpener.EindeModal(accepteerInvoer);
        modalOpener.VervangInnerHtml();
        BGProcesSimulator.This().ToonGewijzigdeSpecificatie();

        let onClose = modalOpener.#onModalClose;
        modalOpener.#onModalClose = undefined;
        if (onClose !== undefined) {
            onClose(accepteerInvoer);
        }
    }
    #onModalClose;

    /**
     * Aangeroepen om het resultaat van de invoer te verwerken en aan te geven dat het modal scherm gesloten kan worden
     * @param {boolean} todo - Methode die voor elke specificatie-element uitgevoerd moet worden
     * @returns {boolean} Geeft aan of de invoer beëindigd kan worden. Bij false wordt het modal scherm niet gesloten.
     */
    #ModalVerwerk(todo, returnOnTrue = false) {
        // Subinvoer managers kunnen bij het verwerken verwijderd worden
        let subInvoerIndices = [...Object.keys(this.#subInvoer)];
        for (let idx of subInvoerIndices) {
            let subInvoer = this.#subInvoer[idx];
            if (subInvoer !== undefined) {
                if (subInvoer.#ModalVerwerk(todo, returnOnTrue) && returnOnTrue) {
                    return true;
                }
            }
        }
        return todo(this);
    }

    /**
     * Link de specificatie-elementen aan dat deel van de webpagina waar de UI events gegenereerd worden.
     * @param {any} spec_invoer Top-level HTML element van het UI-gebied
     */
    static AddEventListener(spec_invoer) {
        SpecificatieElement.#spec_invoer = spec_invoer
        spec_invoer.addEventListener('change', e => SpecificatieElement.#Invoer_Event(e.target, (se, s, a) => se.#OnChange(a, s)));
        spec_invoer.addEventListener('click', e => SpecificatieElement.#Invoer_Event(e.target, (se, s, a) => se.#OnClick(a, s)));
    }
    static #spec_invoer;
    /**
     * Verwerk een UI event in een van de specificatie elementen
     * @param {HTMLElement} elt_invoer - element waarvoor het change element is gegenereerd
     * @param {lambda} handler - functie die de juiste methode voor het specificatie-element uitvoert
     */
    static #Invoer_Event(elt_invoer, handler) {
        for (let elt = elt_invoer; elt && elt.id !== SpecificatieElement.#spec_invoer.id; elt = elt.parentElement) {
            if (elt.dataset) {
                if (elt.dataset.se) {
                    let se = parseInt(elt.dataset.se);
                    let idPrefix = `_bgpg_${se}_`;
                    let suffix = undefined;
                    if (elt_invoer.id.startsWith(idPrefix)) {
                        suffix = elt_invoer.id.substring(idPrefix.length);
                        suffix = suffix.slice(suffix.indexOf('_') + 1);
                    }
                    else if (elt.id.startsWith(idPrefix)) {
                        suffix = elt.id.substring(idPrefix.length);
                        suffix = suffix.slice(suffix.indexOf('_') + 1);
                    }
                    let specificatieElt = SpecificatieElement.#elementen[se];
                    if (specificatieElt !== undefined) {
                        handler(specificatieElt, suffix, elt_invoer);
                    }
                    return;
                }
            }
        }
    }

    #OnClick(a, s) {
        if (this.IsInvoer()) {
            this.OnInvoerClick(a, s);
        } else {
            this.OnWeergaveClick(a, s);
        }
    }
    #OnChange(a, s) {
        if (this.IsInvoer()) {
            this.OnInvoerChange(a, s);
        }
    }
    //#endregion
}

/*------------------------------------------------------------------------------
 *
 * Tijdstippen worden relatief ten opzichte van de startdatum opgegeven in
 * de specificatie (en in de invoer), maar worden (ook) getoond als 
 * absolute datum.
 * 
 *----------------------------------------------------------------------------*/
class Tijdstip extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak het specificatie-element aan
     * @param {SpecificatieElement} superInvoer - SpecificatieElement waar dit een specificatie-subelement van is
     * @param {any} eigenaarObject - Object of array in de specificatie waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Als eigenaarObject een array is, laat dit dan leeg.
     * @param {bool} isTijdstip - Geeft aan of dit een tijdstip (ipv een datum) is
     * @param {Tijdstip} naTijdstip - Geef de dag/tijd waar het tijdstip na moet vallen
     */
    constructor(superInvoer, eigenaarObject, eigenschap, isTijdstip, naTijdstip) {
        super(eigenaarObject, eigenschap, undefined, superInvoer);
        this.#isTijdstip = isTijdstip;
        if (naTijdstip !== undefined) {
            this.#naDag = naTijdstip.#dag;
            this.#naUur = naTijdstip.#uur;
        }
        this.BeginInvoer();
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Geeft aan dat het tijdstip een waarde heeft
     * @returns
     */
    HeeftWaarde() {
        return this.Specificatie() !== undefined;
    }

    /**
     * Geef de datum/tijdstip als een ISO datum
     */
    DatumTijdHtml() {
        let datum = new Date(Startdatum.Datum());
        datum.setDate(datum.getDate() + this.#dag);
        let yyyMMdd = datum.toJSON().slice(0, 10);
        if (this.#isTijdstip && this.#uur > 0) {
            let HH = ('00' + this.#uur).slice(-2);
            return `${yyyMMdd}T${HH}:00Z`;
        } else {
            return yyyMMdd;
        }
    }
    /**
     * Geef de datum en evt uur als een array van strings
     */
    DagUurHtml() {
        if (this.#isTijdstip) {
            if (this.#uur == 0) {
                return [this.#dag, ''];
            } else {
                let HH = ('00' + this.#uur).slice(-2);
                return [this.#dag, `${HH}:00Z`];
            }
        } else {
            return [this.#dag];
        }
    }

    /**
     * Geeft de startdatum als tijdstip-Tijdstip (want dat is niet in te voeren)
     */
    static StartTijd() {
        if (Tijdstip.#startTijd === undefined) {
            Tijdstip.#startTijd = new Tijdstip(undefined, undefined, undefined, true);
            Tijdstip.#startTijd.#dag = 0;
            Tijdstip.#startTijd.SpecificatieWordt(0);
        }
        return Tijdstip.#startTijd;
    }
    static #startTijd;

    /**
     * Geeft de startdatum als datum-Tijdstip (want dat is niet in te voeren)
     */
    static StartDatum() {
        if (Tijdstip.#startDatum === undefined) {
            Tijdstip.#startDatum = new Tijdstip(undefined, undefined, undefined, false);
            Tijdstip.#startDatum.#dag = 0;
            Tijdstip.#startDatum.SpecificatieWordt(0);
        }
        return Tijdstip.#startDatum;
    }
    static #startDatum;

    /**
     * Geeft aan of dit tijdstip gelijk is aan het andere. Dat is het geval als ze beide
     * geen waarde hebben, of beide wel een waarde en Vergelijk = 0 
     * @param {Tijdstip} tijdstip
     */
    IsGelijk(tijdstip) {
        if (tijdstip === undefined) {
            return !this.HeeftWaarde();
        } else {
            return this.Specificatie() === tijdstip.Specificatie();
        }
    }

    /**
     * Vergelijk dit tijdstip met het andere. 
     * Geeft < 0, = 0, > 0 als dit tijdstip eerder / gelijk / later is dan het opgegeven tijdstip,
     * en undefined als een van de tijdstippen undefined is.
     * @param {Tijdstip} tijdstip
     */
    Vergelijk(tijdstip) {
        if (tijdstip !== undefined && tijdstip.HeeftWaarde() && this.HeeftWaarde()) {
            return this.Specificatie() - tijdstip.Specificatie();
        }
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        if (!this.HeeftWaarde()) {
            return '-';
        }
        else if (this.#isTijdstip && this.#uur > 0) {
            return `dag ${this.#dag} (${this.DatumTijdHtml()})`;
        } else {
            return `dag ${this.#dag} (${this.DatumTijdHtml()})`;
        }
    }
    #isTijdstip;

    BeginInvoer() {
        this.#uur = 0;
        if (!this.HeeftWaarde()) {
            this.#dag = 1;
        } else {
            this.#dag = Math.floor(this.Specificatie())
            if (this.#isTijdstip) {
                this.#uur = Math.round(100 * this.Specificatie() - 100 * this.#dag);
                if (this.#uur < 0) {
                    this.#uur = 0;
                } else if (this.#uur > 23) {
                    this.#uur = 23;
                }
            }
            if (this.#dag < 1) {
                this.#dag = 1;
            }
        }
    }
    #dag;
    #uur = 0;
    #naDag;
    #naUur;

    InvoerInnerHtml() {
        // Tijdstippen worden altijd als eerste gezet en nogen daarna nooit wijzigen
        if (this.Specificatie() !== undefined) {
            return this.WeergaveInnerHtml();
        }
        html = `dag <input type="number" class="number4" id="${this.ElementId('D')}" value="${this.#dag}"/>`
        if (this.#isTijdstip) {
            html += ` om <input type="number" class="number2" min="0" max="23" id="${this.ElementId('T')}" value="${this.#uur}"/>:00`
        }
        html += ` (${this.DatumTijdHtml()})`
    }

    OnInvoerChange(elt, idSuffix) {
        if (idSuffix == 'D' || idSuffix == 'H') {
            let dag = parseInt(document.getElementById(this.ElementId('D')).value);

            if (this.#isTijdstip) {
                let uur = parseInt(document.getElementById(this.ElementId('T')).value);
                if (uur < 0) {
                    uur = 0;
                    document.getElementById(this.ElementId('T')).value = uur;
                } else if (uur > 23) {
                    uur = 23;
                    document.getElementById(this.ElementId('T')).value = uur;
                }
                if (dag <= this.#naDag) {
                    dag = this.#naDag
                    if (uur <= this.#naUur) {
                        uur = this.#naUur + 1;
                        if (uur > 23) {
                            uur = 0;
                            dag += 1;
                        }
                    }
                    document.getElementById(this.ElementId('D')).value = dag;
                    document.getElementById(this.ElementId('T')).value = uur;
                }
            } else {
                if (dag <= this.#naDag) {
                    dag = this.#naDag + 1;
                    document.getElementById(this.ElementId('D')).value = dag;
                }

            }
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            if (this.#isTijdstip) {
                this.SpecificatieWordt(this.#dag + 0.01 * this.#uur);
            } else {
                this.SpecificatieWordt(this.#dag);
            }
        }
    }
    //#endregion
}
//#endregion

//#region BG-intern versiebeheer
/*==============================================================================
 *
 * Simulatie van het interne versiebeheer bij een BG:
 * - Instrumentversie bevat alle informatie die over een instrument wordt
 *   bijgehouden in het interne BG versiebeheer (althans voor deze applicatie).
 * - InstrumentversieWijziging representeert de interactie tussen eindgebruiker
 *   en BG-software; dit heeft een weerslag in de specificatie van het scenario.
 * - Momentopname bevat de informatie die in een branch op een bepaald moment
 *   bekend is, en kan tevens de specificatie daarvan voor het scenario beheren.
 * 
 =============================================================================*/

//#region Intern datamodel voor instrumentversies
/*------------------------------------------------------------------------------
*
* Instrumentversie bevat alle informatie die over een instrument wordt
* bijgehouden in het interne BG versiebeheer (althans voor deze applicatie).
* Voor het bijhouden van annotaties worden aparte klassen gebruikt
* 
*----------------------------------------------------------------------------*/
/**
 * Representatie van een naam + waarde voor een STOP of non-STOP annotatie
 */
class Annotatie {
    //#region Initialisatie
    /**
     * Maak een nieuwe annotatie aan
     * @param {string} naam - Naam van de annotatie; vrij voor een STOP annotatie, een van de 
     *                        BGProcesSimulator.SoortAnnotatie voor STOP annotatie
     * @param {Momentopname} momentopname - Momentopname waarin de versie van de annotatie is aangemaakt
     */
    constructor(naam, momentopname) {
        this.#naam = naam;
        this.#momentopname = momentopname;
        this.#uuid = ++Annotatie.#laatste_uuid;
    }
    //#endregion

    //#region Constanten
    static SoortAnnotatie_Citeertitel = 'Metadata';
    static SoortAnnotatie_Toelichtingrelaties = 'Toelichtingrelaties';
    static SoortAnnotatie_Symbolisatie = 'Symbolisatie';
    static SoortAnnotatie_Gebiedsmarkering = 'Gebiedsmarkering';
    static SoortAnnotatie_NonSTOP = 'NonSTOP';
    //#endregion

    //#region Eigenschappen
    /**
     * Naam van de annotatie
     */
    Naam() {
        return this.#naam;
    }
    #naam;
    /**
     * Geeft een vrije naam voor een non-STOP annotatie
     */
    static VrijeNonStopAnnotatieNaam() {
        let alleNonStop = {};
        Momentopname.VoorAlleMomentopnamen(undefined, undefined, (momentopname) => {
            for (let versie of momentopname.Instrumentversies()) {
                for (let a of versie.Instrumentversie().AnnotatieNamen(false)) {
                    alleNonStop[a] = true;
                }
            }
        });
        return BGProcesSimulator.VrijeNaam(Object.keys(alleNonStop), '#');
    }

    /**
     * Uniek ID voor de combinatie van deze annotatie (naam) + waarde ervan.
     */
    UUID() {
        return this.#uuid;
    }
    #uuid;
    static #laatste_uuid = 0;

    /**
     * Geeft de momentopname waarvoor de annotatie is aangemaakt
     * @returns
     */
    Momentopname() {
        return this.#momentopname
    }
    #momentopname;

    /**
     * Geeft aan of deze annotatie hetzelfde is (naam + waarde) als een andere annotatie
     * @param {Annotatie} annotatie
     */
    IsGelijkAan(annotatie) {
        return annotatie !== undefined && this.Naam() === annotatie.Naam() && this.UUID() === annotatie.UUID();
    }

    /**
     * Geeft aan of twee annotaties gelijk aan elkaar zijn.
     * @param {Annotatie} annotatie1
     * @param {Annotatie} annotatie2
     */
    static ZijnGelijk(annotatie1, annotatie2) {
        if (annotatie1 === undefined) {
            return annotatie2 === undefined;
        } else {
            return annotatie1.IsGelijkAan(annotatie2);
        }
    }
    //#endregion
}

/**
 * Specialisatie van de Annotatie voor de metadata met citeertitel.
 */
class Metadata extends Annotatie {

    //#region Initialisatie
    /**
     * Maak een metadata annotatie aan
     * @param {any} citeertitel - Citeertitel, een van de onderdelen van de metadata
     * @param {Momentopname} momentopname - Momentopname waarin de versie van de annotatie is aangemaakt
     */
    constructor(citeertitel, momentopname) {
        super(Annotatie.SoortAnnotatie_Citeertitel, momentopname);
        this.#citeertitel = citeertitel;
    }
    //#endregion

    //#region Eigenschappen
    /**
     * De citeertitel als onderdeel van de metadata
     * @returns
     */
    Citeertitel() {
        return this.#citeertitel;
    }
    #citeertitel;

    /**
     * Geeft aan of deze annotatie hetzelfde is (naam + waarde) als een andere annotatie
     * @param {Annotatie} annotatie
     */
    IsGelijkAan(annotatie) {
        return annotatie !== undefined && this.Naam() === annotatie.Naam() && this.Citeertitel() === annotatie.Citeertitel();
    }
    //#endregion
}

/**
 * In deze applicatie is geen behoefte aan een modellering van een instrument
 * anders dan de (work-)naam ervan. De Instrumentklasse bevat alleen constanten
 * en configuratie.
 */
class Instrument {

    //#region Constanten
    static SoortInstrument_Besluit = 'b';
    static SoortInstrument_Regeling = 'reg';
    static SoortInstrument_GIO = 'gio';
    static SoortInstrument_PDF = 'pdf';
    static SoortInstrumentNamen = {
        b: 'besluit',
        reg: 'regeling',
        gio: 'GIO',
        pdf: 'PDF'
    };
    static SoortInstrument_Regelgeving = [Instrument.SoortInstrument_Regeling, Instrument.SoortInstrument_GIO, Instrument.SoortInstrument_PDF]

    static SoortAnnotatiesVoorInstrument = {
        b: [
            Annotatie.SoortAnnotatie_Citeertitel,
            Annotatie.SoortAnnotatie_Gebiedsmarkering
        ],
        reg: [
            Annotatie.SoortAnnotatie_Citeertitel,
            Annotatie.SoortAnnotatie_Toelichtingrelaties
        ],
        gio: [
            Annotatie.SoortAnnotatie_Citeertitel,
            Annotatie.SoortAnnotatie_Symbolisatie
        ],
        pdf: [
            Annotatie.SoortAnnotatie_Citeertitel
        ]
    };
    static NonStopAnnotatiesVoorInstrument = ["reg"];
    //#endregion

    //#region Globale gegevens
    /**
     * Geef de instrumentsoort behorend bij de instrumentnaam
     * @param {any} instrumentnaam - Naam van het instrument
     * @param {boolean} alleenRegelgeving - Geeft aan dat alleen naar de instrumenten van de regelgeving gekeken moet worden
     * @returns {string} Soort instrument, of undefined als het niet bepaald kan worden
     */
    static SoortInstrument(instrumentnaam, alleenRegelgeving = true) {
        if (alleenRegelgeving) {
            for (let prefix of Instrument.SoortInstrument_Regelgeving) {
                if (instrumentnaam.startsWith(prefix + '_')) {
                    return prefix;
                }
            }
        } else {
            for (let prefix of Instrument.SoortInstrumentNamen) {
                if (instrumentnaam.startsWith(prefix + '_')) {
                    return prefix;
                }
            }
        }
    }


    /**
     * Geef een (gesorteerde) lijst met bekende instrumentnamen
     */
    static Instrumentnamen(soortInstrument) {
        let alleInstrumenten = {};
        Momentopname.VoorAlleMomentopnamen(undefined, undefined, (momentopname) => {
            for (let versie of momentopname.Instrumentversies()) {
                let naam = versie.Instrument();
                if (soortInstrument === undefined || naam.startsWith(soortInstrument + '_')) {
                    alleInstrumenten[naam] = true;
                }
            }
        });
        return Object.keys(alleInstrumenten);
    }

    /**
     * Geef een vrij te gebruiken naam voor een soort instrument
     * @param {any} soortInstrument
     */
    static VrijeNaam(soortInstrument) {
        let alleInstrumenten = {};
        Momentopname.VoorAlleMomentopnamen(undefined, undefined, (momentopname) => {
            for (let versie of momentopname.Instrumentversies()) {
                let naam = versie.Instrument();
                if (naam.startsWith(soortInstrument + '_')) {
                    alleInstrumenten[naam] = true;
                }
            }
        });
        return BGProcesSimulator.VrijeNaam(Object.keys(alleInstrumenten), soortInstrument + '_');
    }
    //#endregion
}

/**
 * Representatie van een regeling- of informatieobjectversie
 *
 * Het wijzigen van een instrumentversie werkt als volgt:
 * - Maak een nieuwe instrumentversie aan op basis van de ongewijzigde versie en eventueel eerder gewijzigde versie
 * - Pas eventueel de wijzigingen uit de specificatie toe via PasSpecificatieToe
 * - Pas de instrumentversie aan op basis van de "invoer van de eindgebruiker"
 * - Roep MaakSpecificatie aan. Dit heeft een nieuwe specificatie als resultaat.
 */
class Instrumentversie {

    //#region Initialisatie
    /**
     * Maakt een nieuwe instrumentversie.
     * @param {Momentopname} momentopname - De momentopname waarvoor deze instrumentversie wordt gemaakt
     * @param {string} instrument - De naam van het instrument
     * @param {Instrumentversie} basisversie - De ongewijzigde (voorgaande) instrumentversie (optioneel)
     * @param {Instrumentversie} gewijzigd - De eerder gewijzigde versie (optioneel).
     */
    constructor(momentopname, instrument, basisversie, gewijzigd) {
        this.#momentopname = momentopname;
        this.#instrument = instrument;
        this.#soortInstrument = Instrument.SoortInstrument(instrument);
        this.#basisversie = basisversie;
        if (gewijzigd !== undefined) {
            this.#uuidNieuweVersie = gewijzigd.#uuidNieuweVersie;
        }
        this.#Kopieer(gewijzigd === undefined ? basisversie : gewijzigd);
    }
    /**
     * Neem de inhoud over van het origineel
     * @param {any} origineel - Instrumentversie met originele inhoud
     */
    #Kopieer(origineel) {
        if (origineel === undefined) {
            this.#uuid = undefined;
            this.#isIngetrokken = false;
            this.#juridischeInhoud = undefined;
            this.#nonStopAnnotaties = {}
            this.#stopAnnotaties = {}
            this.#isTeruggetrokken = true;
        } else {
            this.#uuid = origineel.#uuid;
            this.#isIngetrokken = origineel.#isIngetrokken;
            this.#juridischeInhoud = origineel.#juridischeInhoud;
            this.#nonStopAnnotaties = Object.assign({}, origineel.#nonStopAnnotaties);
            this.#stopAnnotaties = Object.assign({}, origineel.#stopAnnotaties);
            if (this.Branchnaam() === origineel.Branchnaam()) {
                this.#isTeruggetrokken = origineel.#isTeruggetrokken;
            } else {
                this.#isTeruggetrokken = true;
            }
        }
        this.#isEerdereVersie = undefined;
    }
    //#endregion

    //#region Eigenschappen en wijzigen daarvan
    /**
     * De naam van de branch die deze instrumentversie beheert
     */
    Branchnaam() {
        return this.Momentopname().Branch().Naam();
    }

    /**
     * De momentopname waar deze instrumentversie deel van uitmaakt.
     */
    Momentopname() {
        return this.#momentopname;
    }
    #momentopname;

    /**
     * De naam van het instrument
     */
    Instrument() {
        return this.#instrument;
    }
    #instrument;

    /**
     * Geeft de soort van het instrument waar dit een versie van is
     * @returns
     */
    SoortInstrument() {
        return this.#soortInstrument;
    }
    #soortInstrument;

    /**
     * Uniek ID voor deze instrumentversie.
     */
    UUID() {
        return this.#uuid;
    }
    #uuid;
    #MaakNieuweVersie() {
        if (this.#uuidNieuweVersie === undefined) {
            this.#uuidNieuweVersie = ++Instrumentversie.#laatste_uuid;
        }
        this.#uuid = this.#uuidNieuweVersie;
        this.#isTeruggetrokken = false;
    }
    /**
     * De UUID te gebruiken als dit een nieuwe versie is.
     * Deze wordt bewaard zodat het uuid niet steeds wijzigt 
     * als in deze applicatie de eindgebruiker de versie wijzigt
     * en de wijziging weer terugdraait.
     */
    #uuidNieuweVersie;

    /**
     * Geef een UUID door die al in de specificatie wordt gebruikt
     * @param {int} uuid
     */
    static UUIDGebruiktInSpecificatie(uuid) {
        if (Instrumentversie.#laatste_uuid < uuid) {
            Instrumentversie.#laatste_uuid = uuid;
        }
    }
    static #laatste_uuid = 0;

    /**
     * Geeft aan dat dit een initiële versie is, d.w.z. de eerste
     * instrumentversie op deze branch en op branches waar deze branch
     * van afgeleid is.
     */
    IsInitieleVersie() {
        return this.#basisversie === undefined;
    }

    /**
     * Geeft aan dat dit een nieuwe instrumentversie is, d.w.z. dat het een 
     * andere inhoud heeft als de voorgaande versie op de branch. Dit is nooit 
     * het geval als IsOngewijzigdInBranch = true of IsEerdereVersie !== undefined.
     */
    IsNieuweVersie() {
        if (this.IsOngewijzigdInBranch() || this.IsEerdereVersie() !== undefined) {
            return false;
        }
        return this.#uuidNieuweVersie !== undefined && this.#uuid === this.#uuidNieuweVersie;
    }

    /**
     * Geeft aan of het instrument ongewijzigd is op deze branch, d.w.z de
     * inhoud van het instrument is de instrumentversie bij het ontstaan 
     * van de branch.
     */
    IsOngewijzigdInBranch() {
        return this.#isTeruggetrokken;
    }
    /**
     * Trek het instrument terug, d.w.z. geef aan dat het instrument op deze branch
     * niet wijzigt. De inhoud van het instrument is daarna de instrumentversie bij
     * het ontstaan van de branch.
     */
    MaakOngewijzigdInBranch() {
        if (!this.#isTeruggetrokken) {
            this.#isTeruggetrokken = true;
            // Zoek de eerste instrumentversie via de basisversies die niet in deze branch zit
            for (let voorganger = this.#basisversie; voorganger !== undefined; voorganger = voorganger.#basisversie) {
                if (voorganger.Branchnaam() != this.Branchnaam()) {
                    // Dit is de versie
                    this.#Kopieer(voorganger);
                    return;
                }
            }
            // Geen voorganger blijkbaar
            this.#Kopieer(undefined);
        }
    }
    #isTeruggetrokken;

    /**
     * Geef de ongewijzigde versie waarop deze instrumentversie is gebaseerd
     */
    Basisversie() {
        return this.#basisversie;
    }
    /**
     * Maak alle wijzigingen ongedaan en maak deze versie gelijk aan de ongewijzigde versie
     */
    Undo() {
        this.#Kopieer(this.#basisversie);
    }
    #basisversie;

    /**
     * Geeft aan dat een eerder gemaakte versie gebruikt wordt in plaats van 
     * een wijziging van de voorgaande versie.
     * @param {Instrumentversie} instrumentversie
     */
    IsEerdereVersie(instrumentversie) {
        return this.#isEerdereVersie;
    }
    /**
     * Gebruik een eerder gemaakte versie als volgende instrumentversie op de branch.
     * @param {Instrumentversie} instrumentversie
     */
    GebruikEerdereVersie(instrumentversie) {
        this.#Kopieer(instrumentversie);
        this.#isEerdereVersie = instrumentversie;
    }
    #isEerdereVersie;
    //#endregion

    //#region Inhoud van instrumentversie en wijzigen daarvan
    /**
     * Geeft aan dit een versie is met juridische inhoud (tekst of data). Zo niet,
     * dan is het een placeholder voor iets dat nog komen gaat.
     */
    HeeftJuridischeInhoud() {
        return !this.#isIngetrokken && this.#juridischeInhoud !== undefined;
    }
    /**
     * Geeft aan dat de juridische inhoud van het instrument is gewijzigd.
     * Als dat zo is, dan wordt een eventuele intrekking ongedaan gemaakt.
     */
    SpecificeerNieuweJuridischeInhoud() {
        this.#juridischeInhoud = new Annotatie(undefined, this.Momentopname());
        this.#isIngetrokken = false;
        this.#MaakNieuweVersie();
    }
    /**
     * Tijdstip van laatste wijziging van de juridische inhoud
     * @returns {Momentopname}
     */
    JuridischeInhoudLaatstGewijzigd() {
        return this.#juridischeInhoud === undefined ? undefined : this.#juridischeInhoud.Momentopname().Tijdstip();
    }
    #juridischeInhoud;

    /**
     * Geeft aan of het instrument ingetrokken is
     */
    IsIngetrokken() {
        return this.#isIngetrokken;
    }
    /**
     * Trek het instrument in. Het instrument heeft daarna geen juridische inhoud meer.
     */
    TrekIn() {
        this.#isIngetrokken = true;
        this.#juridischeInhoud = undefined;
        this.#MaakNieuweVersie();
    }
    #isIngetrokken;

    /**
     * Geef de toegestane namen van de annotaties
     * @param {boolean} isStop - Geeft aan of het om de STOP annotaties gaat - undefined voor alle annotaties
     */
    HeeftAnnotaties(isStop) {
        if (isStop === undefined || isStop === true) {
            if (Object.keys(this.#stopAnnotaties).length > 0) {
                return true;
            }
        }
        if (isStop === undefined || isStop === false) {
            if (Object.keys(this.#nonStopAnnotaties).length > 0) {
                return true;
            }
        }
        return false;
    }

    /**
     * Geef de toegestane namen van de annotaties
     * @param {boolean} isStop - Geeft aan of het om de STOP annotaties gaat
     */
    AnnotatieNamen(isStop) {
        if (isStop) {
            if (BGProcesSimulator.Opties.Annotaties) {
                return Instrument.SoortAnnotatiesVoorInstrument[this.#soortInstrument];
            }
            else {
                return [];
            }
        } else {
            let namen = Object.assign({}, this.#nonStopAnnotaties);
            if (this.#basisversie !== undefined) {
                namen = Object.assign(namen, this.#basisversie.#nonStopAnnotaties);
            }
            return Object.keys(namen).sort();
        }
    }
    /**
     * Geeft de huidige waarde voor de annotatie (als Annotatie), 
     * of undefined als die er nog niet is.
     * @param {boolean} isStop - Geeft aan of het om een STOP annotatie gaat
     * @param {string} naam - De naam van de annotatie
     */
    Annotatie(isStop, naam) {
        if (isStop) {
            return this.#stopAnnotaties[naam];
        } else {
            return this.#nonStopAnnotaties[naam];
        }
    }
    /**
     * Vervangt de huidige waarde voor de annotatie. Dit kan in deze
     * simulatie alleen als de juridische inhoud ook wijzigt; dat wordt dan 
     * ook gedaan.
     * @param {boolean} isStop - Geeft aan of het om een STOP annotatie gaat
     * @param {Annotatie} annotatie - De waarde voor de stop annotatie
     * @returns {boolean} - Geeft terug of de annotatie is gewijzigd.
     */
    AnnotatieWordt(isStop, annotatie) {
        if (isStop) {
            if (!this.AnnotatieNamen(isStop).includes(annotatie.Naam())) {
                return false;
            }
        } else {
            if (!BGProcesSimulator.Opties.NonStopAnnotaties) {
                return false;
            }
            if (!Instrument.NonStopAnnotatiesVoorInstrument[this.#soortInstrument] === undefined) {
                return false;
            }
            if (this.AnnotatieNamen(isStop).includes(annotatie.Naam())) {
                return false;
            }
        }
        let annotaties = isStop ? this.#stopAnnotaties : this.#nonStopAnnotaties;
        if (!Annotatie.ZijnGelijk(annotaties[annotatie.Naam()], annotatie)) {
            annotaties[annotatie.Naam()] = annotatie;
            return true;
        }
        return false;
    }
    /**
     * Herstel de voorgaande waarde voor de annotatie. Dit kan in deze
     * simulatie alleen als de juridische inhoud ook wijzigt; dat wordt dan 
     * ook gedaan.
     * @param {boolean} isStop - Geeft aan of het om een STOP annotatie gaat
     * @param {string} naam - De naam van de annotatie
     * @returns {boolean} - Geeft terug of de annotatie is gewijzigd.
     */
    AnnotatieUndo(isStop, naam) {
        if (this.#basisversie === undefined) {
            return this.AnnotatieWeg(isStop, naam);
        }
        let annotaties = isStop ? this.#stopAnnotaties : this.#nonStopAnnotaties;
        let voorgaande = isStop ? this.#basisversie.#stopAnnotaties : this.#basisversie.#nonStopAnnotaties;
        if (!Annotatie.ZijnGelijk(voorgaande[naam], annotaties[naam])) {
            annotaties[naam] = voorgaande[naam];
            return true;
        }
        return false;
    }
    /**
     * Verwijder de waarde voor de STOP annotatie. Dit kan in deze
     * simulatie alleen als de juridische inhoud ook wijzigt; dat wordt dan 
     * ook gedaan.
     * @param {boolean} isStop - Geeft aan of het om een STOP annotatie gaat
     * @param {string} naam - De naam van de annotatie
     * @returns {boolean} - Geeft terug of de annotatie is gewijzigd.
     */
    AnnotatieWeg(isStop, naam) {
        let annotaties = isStop ? this.#stopAnnotaties : this.#nonStopAnnotaties;
        if (annotaties[naam] !== undefined) {
            delete annotaties[naam];
            return true;
        }
        return false;
    }
    #stopAnnotaties;
    #nonStopAnnotaties;
    //#endregion

    //#region Van / naar specificatieToe
    /**
     * Pas de specificatie toe op de ongewijzigde versie
     * @param {any} specificatie
     */
    PasSpecificatieToe(specificatie) {
        this.#Kopieer(this.#basisversie);
        if (specificatie === undefined) {
            // Geen wijziging
        }
        else if (specificatie === null) {
            // Terugtrekking
            this.MaakOngewijzigdInBranch();
        }
        else if (specificatie == false) {
            // Intrekking
            this.TrekIn();
        }
        else if (typeof specificatie == "number") {
            // Verwijzing naar een andere instrumentversie
            let instrumentversie;
            Momentopname.VoorAlleMomentopnamen(this.Momentopname().Tijdstip(), undefined, (mo) => {
                for (let spec of mo.Instrumentversies()) {
                    if (spec.Instrumentversie().UUID() === specificatie) {
                        instrumentversie = spec.Instrumentversie();
                    }

                }
            });
            if (instrumentversie === undefined) {
                BGProcesSimulator.SpecificatieMelding(this.Momentopname().Tijdstip(), `Specificatie bevat verwijzing naar instrumentversie (${specificatie}) die nog niet bestaat op dit moment`);
            } else if (instrumentversie.Instrument() != this.Instrument()) {
                BGProcesSimulator.SpecificatieMelding(this.Momentopname().Tijdstip(), `Specificatie voor instrumentversie van ${this.Instrument()} bevat verwijzing naar instrumentversie (${specificatie}) van een ander instrument ${instrumentversie.Instrument()}`);
            } else if (instrumentversie.IsIngetrokken()) {
                BGProcesSimulator.SpecificatieMelding(this.Momentopname().Tijdstip(), `Specificatie bevat verwijzing naar instrumentversie (${specificatie}) die ingetrokken is`);
            } else if (!instrumentversie.HeeftJuridischeInhoud()) {
                BGProcesSimulator.SpecificatieMelding(this.Momentopname().Tijdstip(), `Specificatie bevat verwijzing naar instrumentversie (${specificatie}) die geen juridische inhoud heeft`);
            } else {
                this.GebruikEerdereVersie(instrumentversie);
            }
        } else {
            // Specificatie van een nieuwe versie
            this.SpecificeerNieuweJuridischeInhoud();
            for (let annotatie in specificatie) {
                if (annotatie === Annotatie.SoortAnnotatie_Citeertitel) {
                    this.AnnotatieWordt(true, new Metadata(specificatie[annotatie], this.Momentopname()))
                } else if (annotatie !== Annotatie.SoortAnnotatie_NonSTOP) {
                    if (specificatie[annotatie] === false) {
                        this.AnnotatieUndo(true, annotatie);
                    } else {
                        this.AnnotatieWordt(true, new Annotatie(annotatie, this.Momentopname()));
                    }
                } else {
                    for (let nonStop in specificatie[annotatie]) {
                        if (specificatie[annotatie][nonStop] === false) {
                            this.AnnotatieUndo(false, nonStop);
                        } else {
                            this.AnnotatieWordt(false, new Annotatie(nonStop, this.Momentopname()));
                        }
                    }
                }
            }
            if (specificatie.uuid === undefined) {
                specificatie.uuid = this.UUID();
            }
        }
    }

    /**
     * Maak de specificatie van de wijziging
     */
    MaakSpecificatie() {
        if (this.IsEerdereVersie() !== undefined) {
            // Verwijzing naar eerdere instrumentversie
            return this.IsEerdereVersie().UUID();
        }
        if (this.IsOngewijzigdInBranch()) {
            if (this.#basisversie === undefined) {
                // Deze instrumentversie bestaat niet
                return undefined;
            } else if (this.Branchnaam() !== this.#basisversie.Branchnaam()) {
                // Eerste ongewijzigde versie op een nieuwe branch - geen wijziging
                return undefined;
            } else if (this.#basisversie.IsOngewijzigdInBranch()) {
                // Geen wijziging in teruggetrokken status
                return undefined;
            } else {
                // Dit is een nieuwe terugtrekking
                return null;
            }
        }
        else if (this.IsNieuweVersie()) {
            if (this.IsIngetrokken()) {
                // Wijziging van de ingetrokken status
                return false;
            }
            else {
                // Nieuwe instrumentversie
                let specificatie = { uuid: this.UUID() }
                // Wijziging in STOP annotaties
                for (let naam of this.AnnotatieNamen(true)) {
                    let origineel = this.#basisversie === undefined ? undefined : this.#basisversie.Annotatie(true, naam);
                    let annotatie = this.Annotatie(true, naam);
                    if (!Annotatie.ZijnGelijk(origineel, annotatie)) {
                        if (annotatie === undefined) {
                            specificatie[naam] = false;
                        }
                        else if (naam === Annotatie.SoortAnnotatie_Citeertitel) {
                            specificatie[naam] = annotatie.Citeertitel();
                        }
                        else {
                            specificatie[naam] = true;
                        }
                    }
                }
                // Wijziging in non-STOP annotaties
                specificatie[Annotatie.SoortAnnotatie_NonSTOP] = {};
                for (let naam of this.AnnotatieNamen(false)) {
                    let origineel = this.#basisversie === undefined ? undefined : this.#basisversie.STOPAnnotatie(false, naam);
                    let annotatie = this.Annotatie(false, naam);
                    if (!Annotatie.ZijnGelijk(origineel, annotatie)) {
                        specificatie[Annotatie.SoortAnnotatie_NonSTOP][annotatie.Naam()] = annotatie !== undefined;
                    }
                }
                return specificatie;
            }
        }
    }
    //#endregion
}

//#endregion

//#region Invoer van instrumentversie en momentopname
/*------------------------------------------------------------------------------
*
* InstrumentversieWijziging is een specificatie-element die de Instrumentversie voor een
* regeling of informatieobject als onderdeel van de inhoud van een branch 
* op een bepaald moment kan vastleggen.
* 
*----------------------------------------------------------------------------*/
class InstrumentversieSpecificatie extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak het specificatie-element aan
     * @param {Momentopname} momentopname - Momentopname waar dit een specificatie-subelement van is
     * @param {string} instrument - Instrument waarvoor de versie gespecificeerd moet worden
     * @param {InstrumentversieSpecificatie} basisversie - De vorige wijziging waarop deze voortbouwt
     * @param {InstrumentversieSpecificatie[]} ontvlochtenversies - De wijzigingen die ontvlochten moeten worden met deze wijziging
     * @param {InstrumentversieSpecificatie[]} vervlochtenversies - De wijzigingen die vervlochten moeten worden met deze wijziging
     */
    constructor(momentopname, instrument, basisversie, ontvlochtenversies, vervlochtenversies) {
        super(momentopname.Specificatie(), instrument, undefined, momentopname);
        this.#ontvlochtenversies = ontvlochtenversies;
        this.#vervlochtenversies = vervlochtenversies;
        this.#actueleversie = new Instrumentversie(momentopname, instrument, basisversie === undefined ? undefined : basisversie.Instrumentversie());
        this.#actueleversie.PasSpecificatieToe(this.Specificatie());
    }
    #ontvlochtenversies;
    #vervlochtenversies;
    //#endregion

    //#region Eigenschappen
    /**
     * Geeft de naam/code van het instrument waar dit een versie van is
     * @returns
     */
    Instrument() {
        return this.Eigenschap();
    }

    /**
     * Geef de naam van het instrument zoals aan de eindgebruiker getoond wordt.
     * Dit is de citeertitel, tenzij die niet gezet is.
     */
    InstrumentInteractienaam() {
        let versie = this.IsInvoer() ? this.#nieuweversie : this.#actueleversie;
        if (versie !== undefined) {
            let citeertitel = versie[Annotatie.SoortAnnotatie_Citeertitel];
            if (citeertitel) {
                return citeertitel;
            }
        }
        return this.Instrument();
    }


    /**
     * Geeft de momentopname waar deze instrumentversie deel van uitmaakt
     * @returns
     */
    Momentopname() {
        return this.SuperInvoer();
    }

    /**
     * Geeft de in-memory representatie van de instrumentversie
     */
    Instrumentversie() {
        return this.IsInvoer() ? this.#nieuweversie : this.#actueleversie;
    }
    #actueleversie;
    #nieuweversie;
    //#endregion

    //#region Statusoverzicht
    /**
      * Het overzicht van de momentopname in het projectoverzicht
      */
    OverzichtHtml() {
        let html = `laatst gewijzigd op ${this.Instrumentversie().JuridischeInhoudLaatstGewijzigd().DatumTijdHtml()}`;
        if (this.Instrumentversie().HeeftAnnotaties()) {
            html = `<table><tr><td colspan="2">${html}</td></tr>`;
            for (let isStop of [true, false]) {
                for (let naam of this.Instrumentversie().AnnotatieNamen(isStop)) {
                    let annotatie = this.Instrumentversie().Annotatie(isStop, naam);
                    if (annotatie !== undefined) {
                        if (naam === Annotatie.SoortAnnotatie_Citeertitel) {
                            html += `<tr><td>${naam}</td><td>d.d. ${annotatie.Momentopname().Tijdstip().DatumTijdHtml()}</td></tr><tr><td>Citeertitel</td><td>${annotatie.Citeertitel()}</td></tr>`;
                        } else {
                            html += `<tr><td>${naam}</td><td>d.d. ${annotatie.Momentopname().Tijdstip().DatumTijdHtml()}</td></tr>`;
                        }
                    }
                }
            }
            html += '</table>';
        }
        return html;
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return this.#InnerHtml(this.#actueleversie, false);
    }

    BeginInvoer() {
        this.#nieuweversie = new Instrumentversie(this.Momentopname(), this.Instrument(), this.#actueleversie.Basisversie(), this.#actueleversie);
    }

    InvoerInnerHtml() {
        return this.#InnerHtml(this.#nieuweversie, true);
    }
    #InnerHtml(instrumentversie, enabled) {
        let disabled = enabled ? '' : ' disabled';
        let html;
        if (instrumentversie.IsInitieleVersie()) {
            // Opties zijn: een (na terugtrekking nieuwe) eerste versie of niet aanwezig in de branch
            html = `<input type="checkbox" id="${this.ElementId('N')}"${(instrumentversie.HeeftJuridischeInhoud() ? ' checked' : '')}${disabled}><label for="${this.ElementId('N')}">Nieuwe initiële versie</label>`
            if (instrumentversie.HeeftJuridischeInhoud()) {
                html += this.#AnnotatiesInnerHtml(instrumentversie, enabled);
            }
        } else {
            // Er is een eerdere versie, geef een keuze voor de status waarin een instrument zich bevindt.
            let html = '<table>';
            let checked = 'B';
            if (instrumentversie.IsIngetrokken()) {
                checked = 'D';
            } else if (instrumentversie.IsOngewijzigdInBranch()) {
                checked = 'T';
            }
            else if (instrumentversie.IsNieuweVersie()) {
                checked = 'W';
            }
            else if (instrumentversie.IsEerdereVersie() !== undefined) {
                checked = 'V';
            }
            html += `<tr><td><input type="radio" id="${this.ElementId('B')}" name="${this.ElementId('R')}"${(checked == 'B' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('B')}">Ongewijzigd laten</label></td></tr>`;
            html += `<tr><td><input type="radio" id="${this.ElementId('W')}" name="${this.ElementId('R')}"${(checked == 'W' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('W')}">Nieuwe versie</label>${(checked == 'W' ? this.#AnnotatiesInnerHtml(instrumentversie, enabled) : '')}</td></tr>`;
            html += `<tr><td><input type="radio" id="${this.ElementId('D')}" name="${this.ElementId('R')}"${(checked == 'D' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('D')}">Intrekken</label></td></tr>`;
            html += `<tr><td><input type="radio" id="${this.ElementId('T')}" name="${this.ElementId('R')}"${(checked == 'T' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('T')}">Ongewijzigd laten voor ${this.Momentopname().Branch().Interactienaam()}</label></td></tr>`;

            if (instrumentversie.SoortInstrument() != Instrument.SoortInstrument_Regeling) {
                // Zoek eerst alle nieuwe instrumentversies die op dit moment bekend zijn
                let versies = {};
                Momentopname.VoorAlleMomentopnamen(this.Momentopname().Tijdstip(), undefined, (mo) => {
                    let versie = mo.Instrumentversie(this.Instrument());
                    if (versie !== undefined && versie !== this && versie.Instrumentversie().IsNieuweVersie()) {
                        //Een andere instrumentversie dan deze die een nieuwe versie specificeert
                        if (instrumentversie.Basisversie() !== undefined && instrumentversie.Basisversie().UUID() == versie.Instrumentversie().UUID()) {
                            // Naar een versie met dezelfde expression-ID als de ongewijzigde versie moet niet verwezen worden, dan moet van de wijziging afgezien worden.
                            return;
                        }
                        versies[`Op ${versie.Momentopname().Tijdstip().DatumTijdHtml()} voor: ${versie.Momentopname().Branch().Interactienaam()}`] = versie.UUID();
                    }
                });
                if (versies.length > 0) {
                    html += `<tr><td><input type="radio" id="${this.ElementId('V')}" name="${this.ElementId('R')}"${(checked == 'V' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('V')}">Gelijk aan een eerder opgestelde versie:<label><br>`;
                    html += `<select id="${this.ElementId('VL')}"${disabled}>`;
                    for (let versie of Object.keys(versies).sort()) {
                        html += `<option value="${versies[versie]}"${(checked == 'V' && versies[versie] === instrumentversie.UUID() ? ' selected' : '')}>${versie}</option>`;
                    }
                    html += '</select></td></tr>';
                }
            }
        }
        return html;
    }

    #AnnotatiesInnerHtml(instrumentversie, enabled) {
        if (!BGProcesSimulator.Opties.Annotaties && !BGProcesSimulator.Opties.NonStopAnnotaties) {
            return '';
        }
        // Maak de invoer voor de annotaties
        let disabled = enabled ? '' : ' disabled';
        let html = '<table>';
        let titel = 'Naast de juridische informatie ook een nieuwe versie van de annotatie(s):';
        let idx = 0;
        for (let isStop of [true, false]) {
            // Zoek uit welke annotaties ingevoerd kunnen worden
            let namen = [...instrumentversie.AnnotatieNamen(isStop)];
            if (isStop) {
                if (!BGProcesSimulator.Opties.Annotaties) {
                    continue;
                }
            } else {
                if (!BGProcesSimulator.Opties.NonStopAnnotaties) {
                    continue;
                }
                if (!Instrument.NonStopAnnotatiesVoorInstrument[instrumentversie.SoortInstrument()] === undefined) {
                    continue;
                }
                namen.push(Annotatie.VrijeNonStopAnnotatieNaam());
            }
            for (let naam of namen) {
                // Voeg de annotatie aan de tabel toe
                if (titel !== '') {
                    html += '<tr><td colspan="3">' + titel + '</tr>';
                    titel = '';
                }
                let versie = instrumentversie.Annotatie(isStop, naam);
                let ongewijzigd = undefined;
                if (instrumentversie.Basisversie() != undefined) {
                    ongewijzigd = instrumentversie.Basisversie().Annotatie(isStop, naam);
                }
                let checked = false;
                idx++;
                if (ongewijzigd === undefined) {
                    checked = versie !== undefined;
                } else {
                    checked = Annotatie.ZijnGelijk(versie, ongewijzigd);
                }
                if (isStop && naam === Annotatie.SoortAnnotatie_Citeertitel) {
                    //Citeertitel
                    html += `<tr><td rowspan="2"><input type="checkbox" id="${this.ElementId('AW' + idx)}" data-a="${naam}" data-s="${(isStop ? 1 : 0)}"${(checked ? ' checked' : '')}${disabled}></td>
                        <td><label for="${this.ElementId('AW' + idx)}">${naam}<label></td>
                    </tr>
                    <tr><td>Citeertitel: <input type="text" id="${this.ElementId('CT')}" value="${(versie === undefined ? '' : versie.Citeertitel())}"${disabled}></td></tr>`;
                }
                else if (enabled && !isStop && ongewijzigd === undefined && versie === undefined) {
                    html += `<tr><td>${this.HtmlVoegToe("Voeg een nieuwe non-STOP annotatie toe", 'NS')}</td><td><input type="text" id="${this.ElementId('NSN')}" value="${naam}"${disabled}></td></tr>`;
                } else {
                    html += `<tr><td><input type="checkbox" id="${this.ElementId('AW' + idx)}" data-a="${naam}" data-s="${(isStop ? 1 : 0)}"${(checked ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('AW' + idx)}">${naam}<label></td></tr>`;
                }
            }
        }
        html += '</table>';
        return html;
    }

    OnInvoerChange(elt, idSuffix) {
        if (idSuffix === 'VL') {
            // Selectie van eerdere instrumentversie is gewijzigd
            this.#GebruikEerdereVersie(elt);
        }
        else if (idSuffix === 'CT') {
            // Wijziging van de citeertitel
            if (this.#nieuweversie.AnnotatieWordt(true, new Metadata(elt.value.trim(), this.Momentopname()))) {
                this.VervangInnerHtml();
            }
        }
    }

    OnInvoerClick(elt, idSuffix) {
        if (idSuffix === undefined) {
            return;
        }
        if (idSuffix.charAt(0) == 'A') {
            //#region Annotaties
            let naam = elt.dataset.a;
            let isStop = elt.dataset.s == '1';
            let annotatie = undefined;
            if (elt.checked) {
                // Nieuwe annotatieversie
                if (isStop && naam === Annotatie.SoortAnnotatie_Citeertitel) {
                    annotatie = new Metadata(document.getElementById(this.ElementId('CT')).value, this.Momentopname());
                } else {
                    annotatie = new Annotatie(naam, this.Momentopname());
                }
                if (this.#nieuweversie.AnnotatieWordt(isStop, annotatie)) {
                    this.VervangInnerHtml();
                }
            } else {
                // Toch geen eerste versie voor de annotatie
                if (this.#nieuweversie.AnnotatieUndo(isStop, naam)) {
                    this.VervangInnerHtml();
                }
            }
            //#endregion
        }
        else if (idSuffix == 'NS') {
            //#region Nieuwe non-STOP annotatie
            let naam = document.getElementById(this.ElementId('NSN')).value.trim();
            if (naam !== '') {
                if (this.#nieuweversie.AnnotatieWordt(false, new Annotatie(naam, this.Momentopname()))) {
                    this.VervangInnerHtml();
                }
            }
            //#endregion
        }
        else {
            //#region Selectie van instrumentversie
            switch (idSuffix) {
                case 'N':
                    if (elt.checked) {
                        // Nieuwe versie
                        this.#nieuweversie.SpecificeerNieuweJuridischeInhoud();
                    } else {
                        // Toch geen initiële versie meer
                        this.#nieuweversie.MaakOngewijzigdInBranch();
                    }
                    this.VervangInnerHtml();
                    break;
                case 'B':
                    if (!elt.checked) {
                        // Toch geen nieuwe versie meer
                        this.#nieuweversie.Undo();
                        this.VervangInnerHtml();
                    }
                    break;
                case 'W':
                    if (elt.checked) {
                        // Nieuwe versie
                        this.#nieuweversie.SpecificeerNieuweJuridischeInhoud();
                        this.VervangInnerHtml();
                    }
                    break;
                case 'D':
                    if (elt.checked) {
                        // Trek het instrument in
                        this.#nieuweversie.TrekIn();
                        this.VervangInnerHtml();
                    }
                    break;
                case 'T':
                    if (!elt.checked) {
                        // Toch geen nieuwe versie meer
                        this.#nieuweversie.MaakOngewijzigdInBranch();
                        this.VervangInnerHtml();
                    }
                    break;
                case 'V':
                    if (!elt.checked) {
                        // Verwijs naar een eerdere versie
                        this.#GebruikEerdereVersie(document.getElementById(this.ElementId('VL')));
                        this.VervangInnerHtml();
                    }
                    break;
            }
            //#endregion
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            this.SpecificatieWordt(this.#nieuweversie.MaakSpecificatie());
            this.#actueleversie = this.#nieuweversie;
        }
    }
    //#endregion

    //#region Interne functionaliteit
    /**
     * Zoek naar een instrumentversie op basis van het UUID
     * @param {HTMLSelectElement} elt - Selectielijst
     */
    #GebruikEerdereVersie(elt) {
        if (elt.selectedIndex >= 0) {
            Momentopname.VoorAlleMomentopnamen(this.Momentopname().Tijdstip(), undefined, (mo) => {
                let versie = mo.Instrumentversie(this.Instrument());
                if (versie !== undefined && versie.Instrumentversie().UUID() === elt.value && versie.Instrumentversie().IsNieuweVersie()) {
                    this.#nieuweversie.GebruikEerdereVersie(versie.Instrumentversie());
                    return true;
                }
            });
            // Als de versie niet gevonden is bestaat die misschien niet meer - maak de lijst opnieuw
            this.VervangInnerHtml();
        }
    }
    //#endregion
}

class TijdstempelSpecificatie extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak het specificatie-element aan
     * @param {Momentopname} momentopname - Momentopname waar dit een specificatie-subelement van is
     * @param {string} tijdstempel - Tijdstempel die gespecificeerd moet worden.
     * @param {Tijdstip} ongewijzigdeDatum - De vorige tijdstempel waarop deze voortbouwt
     * @param {TijdstempelSpecificatie} jwv - Als dit de GeldigVanaf is, dan is jwv de specificatie van JuridischWerkendVanaf
     */
    constructor(momentopname, tijdstempel, ongewijzigdeDatum, jwv) {
        super(momentopname.Specificatie(), tijdstempel, undefined, momentopname);
        this.#ongewijzigd = ongewijzigdeDatum === undefined ? undefined : ongewijzigdeDatum.Specificatie();
        this.#jwv = jwv;

        let waarde;
        if (this.Specificatie() !== undefined && this.Specificatie() !== false) {
            waarde = this.Specificatie();
        }
        else {
            waarde = this.#ongewijzigd;
        }
        this.#actueleversie = new Tijdstip(this, { 'Datum': waarde }, 'Datum', false, momentopname.Tijdstip());
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Geeft de momentopname waar de tijdstempel voor opgegeven wordt
     * @returns {Momentopname}
     */
    Momentopname() {
        return this.SuperInvoer();
    }

    /**
     * Geeft de datum van de tijdstempel terug
     * @returns {Tijdstip}
     */
    Datum() {
        let versie = this.IsInvoer() ? this.#nieuweversie : this.#actueleversie;
        if (this.#jwv === undefined || !this.#jwv.Datum().IsGelijk(versie)) {
            return versie;
        }
    }
    #actueleversie;
    #jwv;
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return this.#actueleversie.WeergaveInnerHtml();
    }

    BeginInvoer() {
        if (this.#nieuweversie !== undefined) {
            this.#nieuweversie.destructor();
        }
        this.#nieuweversie = new Tijdstip(this, { 'Datum': this.#actueleversie.Specificatie() }, 'Datum', false, this.Momentopname().Tijdstip());
    }
    #nieuweversie;

    InvoerInnerHtml() {
        let html = '';
        if (!this.#nieuweversie.HeeftWaarde()) {
            html += this.HtmlVoegToe("Voeg een tijdstempel toe", 'N');
        } else {
            if (this.#ongewijzigd !== undefined) {
                html += this.HtmlVerwijder("Verwijder de tijdstempel", 'D') + ' ';
            }
            html += this.#nieuweversie.InvoerInnerHtml();
        }
        return html;
    }

    OnInvoerClick(elt, idSuffix) {
        let nieuweSpec = this.#nieuweversie.Specificatie();
        switch (idSuffix) {
            case 'B':
                if (!elt.checked) {
                    nieuweSpec = this.#ongewijzigd;
                }
                break;
            case 'N':
                nieuweSpec = this.#ongewijzigd === undefined ? this.Momentopname().Tijdstip() : this.#ongewijzigd;
                break;
        }
        if (nieuweSpec != this.#nieuweversie.Specificatie()) {
            this.#nieuweversie.destructor();
            this.#nieuweversie = new Tijdstip(this, { 'Datum': nieuweSpec }, 'Datum', false, this.Momentopname().Tijdstip());
            this.VervangInnerHtml();
        }
    }
    #ongewijzigd;

    /**
     * Aangeroepen vlak voordat het modal scherm gesloten wordt: verwerk de gewijzigde invoer.
     * @param {boolean} accepteerInvoer - Geeft aan of de invoer geaccepteerd (ipv geannuleerd) wordt.
     * @returns {boolean} Geeft aan of de invoer nog niet beëindigd kan worden. Bij true wordt het modal scherm niet gesloten.
     */
    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            this.#actueleversie.destructor();
            this.#actueleversie = new Tijdstip(this, { 'Datum': this.#nieuweversie.Specificatie() }, 'Datum', false, this.Momentopname().Tijdstip());

            if (this.#jwv !== undefined && this.#actueleversie.Vergelijk(this.#jwv.Datum()) == 0) {
                // Doorgeven van JWV is voldoende
                this.SpecificatieWordt(undefined);
            }
            else if (this.#actueleversie.Specificatie() === this.#ongewijzigd) {
                // Ongewijzigd
                this.SpecificatieWordt(undefined);
            } else if (!this.#actueleversie.HeeftWaarde()) {
                // Tijdstempel vervalt
                this.SpecificatieWordt(false);
            } else {
                // Tijstempel heeft nieuwe waarde
                this.SpecificatieWordt(this.#actueleversie.Specificatie());
            }
        }
    }
    //#endregion
}

/*------------------------------------------------------------------------------
*
* Momentopname is een basisklasse/specificatie-subelement die de invoer van de
* inhoud van een branch op een bepaald moment kan vastleggen. Het gaat dan
* om de instrumenten en annotaties, en evt om de tijdstempels.
* 
*----------------------------------------------------------------------------*/
class Momentopname extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak het specificatie-element aan
     * @param {SpecificatieElement} superInvoer - SpecificatieElement waar dit een specificatie-subelement van is
     * @param {any} eigenaarObject - Object of array in de specificatie waar dit een eigenschap van is
     * @param {Branch} branch - De branch waarvoor dit een momentopname is
     * @param {bool} tijdstempelsToegestaan - Geeft aan of ook tijdstippen ingevoerd mogen worden
     * @param {bool} werkUitgangssituatieBij - Geeft aan of de uitgangssituatie bijgewerkt moet worden
     * @param {Momentopname[]} ontvlochtenversies - De wijzigingen die ontvlochten moeten worden met deze wijziging
     * @param {Momentopname[]} vervlochtenversies - De wijzigingen die vervlochten moeten worden met deze wijziging
     */
    constructor(superInvoer, eigenaarObject, branch, tijdstempelsToegestaan, werkUitgangssituatieBij = false, ontvlochtenversies, vervlochtenversies) {
        super(eigenaarObject, branch.Naam(), undefined, superInvoer);
        this.#branch = branch;
        this.#tijdstempelsToegestaan = tijdstempelsToegestaan;
        this.#ontvlochtenMet = ontvlochtenversies === undefined ? [] : ontvlochtenversies;
        this.#vervlochtenMet = vervlochtenversies === undefined ? [] : vervlochtenversies;

        // Zoek de voorgaande momentopname waar deze momentopname op doorgaat
        let voorgaandeMomentopnameDezeBranch;
        if (!(this instanceof Uitgangssituatie)) {
            Momentopname.VoorAlleMomentopnamen(this.Tijdstip(), this.Branch(), (mo) => {
                if (mo != this) {
                    voorgaandeMomentopnameDezeBranch = mo;
                }
            });
        }

        if (voorgaandeMomentopnameDezeBranch !== undefined) {
            // Neem informatie van voorgaande momentopname over
            this.#tegelijkBeheerd = voorgaandeMomentopnameDezeBranch.#tegelijkBeheerd;
            this.#doorAdviesbureau = voorgaandeMomentopnameDezeBranch.#doorAdviesbureau;

            if (voorgaandeMomentopnameDezeBranch.#isOnderdeelVanPublicatie) {
                // De vorige momentopname is nu de uitgangssituatie
                this.#uitgangssituatie = [voorgaandeMomentopnameDezeBranch];
                this.#inhoudVorigeMOIsGewijzigd = false;
            } else {
                // Neem uitgangssituatie over
                this.#uitgangssituatie = voorgaandeMomentopnameDezeBranch.#uitgangssituatie;
                this.#inhoudVorigeMOIsGewijzigd = voorgaandeMomentopnameDezeBranch.IsInhoudGewijzigd();
            }
            this.#isVastgesteld = voorgaandeMomentopnameDezeBranch.#isOnderdeelVanPublicatie || voorgaandeMomentopnameDezeBranch.#isVastgesteld;
        }

        let voorgaandeMomentopname = voorgaandeMomentopnameDezeBranch;
        let uitgangssituatie;
        if (werkUitgangssituatieBij || voorgaandeMomentopnameDezeBranch === undefined) {
            // Zoek de laatste momentopname op van de uitgangssituatie waar de branch van uitgaat.
            if (this.Branch().Soort() === Branch.Soort_GeldendeRegelgeving) {
                if (!(this instanceof Uitgangssituatie)) {
                    // De uitgangssituatie (en tevens basisversie) is de geldende regelgeving.
                    let status = this.Activiteit().VoorgaandeConsolidatiestatus();
                    status = status === undefined ? undefined : status.NuGeldend(this.Tijdstip());
                    if (status !== undefined && !status.IsVoltooid()) {
                        BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `branch '${this.Branch().Naam()}': consolidatie van nu geldende regelgeving is incompleet.`);
                    }
                    if (status !== undefined) {
                        uitgangssituatie = status.IWTMoment().LaatsteBijdrage(status.IWTMoment().Inwerkingtredingbranchnamen()[0]);
                    }
                }
            } else {
                // De uitgangssituatie is de laatste momentopname van de branch waar deze branch op volgt
                uitgangssituatie = this.Branch().VolgtOpBranch().LaatsteMomentopname(this.Tijdstip());
                if (this.Branch().Soort() === Branch.Soort_OplossingSamenloop) {
                    // De andere branches werken als een vervlechting
                    for (let andereBranch of this.Branch().TreedtConditioneelInWerkingMet()) {
                        if (andereBranch != this.Branch().VolgtOpBranch()) {
                            this.#vervlochtenMet.push(andereBranch.LaatsteMomentopname(this.Tijdstip()));
                        }
                    }
                }
            }
            if (uitgangssituatie !== undefined) {

                if (voorgaandeMomentopnameDezeBranch === undefined) {
                    // Dit is de eerste momentopname van de branch en bepaalt dus de basisversie van de branch
                    voorgaandeMomentopname = uitgangssituatie;
                    this.#uitgangssituatie = [uitgangssituatie];

                } else {
                    if (this.#isVastgesteld) {
                        // De uitgangssituatie blijft de voorgaande publicatie
                        if (this.#uitgangssituatie[0] == voorgaandeMomentopnameDezeBranch) {
                            // ... en dat is de voorgaande momentopname.
                            // Die wordt nu bijgewerkt, dus deze momentopname wordt het nieuwe uitgangspunt
                            this.#uitgangssituatie = [this];
                        } else {
                            // Er zijn tussentijdse wijzigingen, voeg de nieuwe uitgangssituatie toe aan de lijst
                            this.#uitgangssituatie.push(uitgangssituatie);
                        }
                    } else {
                        // Nog niet vastgesteld, dus de uitgangssituatie wijzigt.
                        this.#uitgangssituatie = uitgangssituatie !== undefined ? [uitgangssituatie] : voorgaandeMomentopnameDezeBranch.uitgangssituatie;
                    }
                    // Dit werkt hetzelfde als een vervlechting in versiebeheer
                    this.#vervlochtenMet.push(uitgangssituatie);
                }
            }
        }

        // Bepaal de collectieve bijdragen van alle branches tbv consolidatie
        this.#voorgaandeMomentopname = voorgaandeMomentopname;
        this.#BepaalBijdragen();

        // Maak alle specificatie-elementen

        if (!tijdstempelsToegestaan && this.Specificatie() !== undefined) {
            if (this.Specificatie().JuridischWerkendVanaf !== undefined || this.Specificatie().GeldigVanaf) {
                BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `branch '${this.Branch().Naam()}': specificatie van tijdstempels is niet toegestaan')).`);
                delete this.Specificatie().JuridischWerkendVanaf;
                delete this.Specificatie().GeldigVanaf;
            }
        }
        // Maak specificatie-elementen voor de tijstempels
        this.#juridischWerkendVanaf = new TijdstempelSpecificatie(this, 'JuridischWerkendVanaf', voorgaandeMomentopnameDezeBranch === undefined ? undefined : voorgaandeMomentopnameDezeBranch.JuridischWerkendVanaf());
        this.#geldigVanaf = new TijdstempelSpecificatie(this, 'GeldigVanaf', voorgaandeMomentopnameDezeBranch === undefined ? undefined : voorgaandeMomentopnameDezeBranch.GeldigVanaf(), this.#juridischWerkendVanaf);

        // Zoek uit welke instrumenten aanwezig zijn in deze momentopname
        if (voorgaandeMomentopname !== undefined) {
            // Alle instrumenten van de basisversie moeten overgenomen worden
            for (let instr in voorgaandeMomentopname.#actueleInstrumenten) {
                this.#actueleInstrumenten[instr] = undefined;
            }
        }
        // Alle instrumenten van de vervlochten versies zijn aanwezig
        for (let v of this.#vervlochtenMet) {
            // Alle instrumenten van de vervlochten versie moeten overgenomen worden
            for (let instr in v.#actueleInstrumenten) {
                this.#actueleInstrumenten[instr] = undefined;
            }
        }
        if (this.Specificatie() != undefined) {
            // Alle instrumenten uit de specificatie zijn aanwezig
            for (let instr in this.Specificatie()) {
                if (Instrument.SoortInstrument(instr) !== undefined) {
                    this.#actueleInstrumenten[instr] = undefined;
                }
            }
        }

        // Maak specificatie-elementen voor alle instrumenten
        for (let instr in this.#actueleInstrumenten) {
            let ontvl = [];
            for (let v of this.#ontvlochtenMet) {
                if (instr in v.#actueleInstrumenten) {
                    ontvl.push(v.#actueleInstrumenten[instr])
                }
            }
            let vervl = [];
            for (let v of this.#vervlochtenMet) {
                if (instr in v.#actueleInstrumenten) {
                    vervl.push(v.#actueleInstrumenten[instr])
                }
            }
            this.#actueleInstrumenten[instr] = new InstrumentversieSpecificatie(this, instr, (this.#voorgaandeMomentopname === undefined ? undefined : this.#voorgaandeMomentopname.#actueleInstrumenten[instr]), ontvl, vervl);
        }
    }
    //#endregion

    //#region Eigenschappen tbv deze simulatie
    /**
     * Geeft de branch waar deze instrumentversie deel van uitmaakt
     * @returns
     */
    Branch() {
        return this.#branch;
    }
    #branch;

    /**
     * Geeft het tijdstip van de activiteit waarvoor de momentopname gespecificeerd wordt
     */
    Tijdstip() {
        if (this.Eigenschap() == this.#branch.Naam()) {
            return this.SuperInvoer().Tijdstip();
        }
        // else: Uitgangssituatie
        return Tijdstip.StartTijd();
    }

    /**
     * Geeft de activiteit waarvoor de momentopname gespecificeerd wordt
     */
    Activiteit() {
        if (this.Eigenschap() == this.#branch.Naam()) {
            return this.SuperInvoer();
        }
        // else: Uitgangssituatie
    }

    /**
     * Geeft aan dat de momentopname door een adviesbureau is aangemaakt
     * @returns
     */
    UitgevoerdDoorAdviesbureau() {
        return this.#doorAdviesbureau;
    }
    UitgevoerdDoorAdviesbureauWordt(inderdaad) {
        this.#doorAdviesbureau = inderdaad;
    }
    #doorAdviesbureau = false;

    /**
     * Geeft aan of het vaststellingsbesluit is gepubliceerd. ALleen nodig voor de 
     * weergave in deze applicatie (want dan zijn rectificaties mogelijk)
     */
    IsVaststellingsbesluitGepubliceerd() {
        return this.#isVastgesteld;
    }
    #isVastgesteld = false;
    //#endregion

    //#region Eigenschappen - Inhoud van de branch
    /**
     * Geeft de juridische uitgangssituatie, de momentopname die gebruikt moet worden om 
     * de was-wordt versie van de (tekst-/geo-)renvooi te maken. Dit is een lijst
     * als de uitgangssituatie later is bijgewerkt met wijzigen uit de tweede en latere
     * momentopname.
     * @returns {Momentopname[]}
     */
    JuridischeUitgangssituaties() {
        return this.#uitgangssituatie;
    }
    #uitgangssituatie;

    /**
     * Geeft aan of de inhoud van de branch is gewijzigd ten opzichte van de eerste van 
     * de JuridischeUitgangssituatie. In deze applicatie alleen nodig voor weergave.
     */
    IsInhoudGewijzigd() {
        if (this.#inhoudVorigeMOIsGewijzigd) {
            return true;
        }
        for (let versie of this.Instrumentversies()) {
            if (this.Tijdstip().IsGelijk(versie.Instrumentversie().JuridischeInhoudLaatstGewijzigd())) {
                return true;
            }
        }
        return false;
    }
    #inhoudVorigeMOIsGewijzigd;

    /**
     * Geeft aan of de inwerkingtreding is toegevoegd ten opzichte van de eerste van 
     * de JuridischeUitgangssituatie. In deze applicatie alleen nodig voor weergave.
     */
    IsInwerkingtredingToegevoegd() {
        if (!this.JuridischWerkendVanaf().HeeftWaarde()) {
            return false;
        }
        if (this.JuridischeUitgangssituaties() === undefined) {
            return false;
        }
        let uitgangssituatie = this.JuridischeUitgangssituaties()[0];
        return !uitgangssituatie.JuridischWerkendVanaf().HeeftWaarde();
    }

    /**
     * Geeft aan of deze momentopname onderdeel is van een besluit, rectificatie of
     * mededeling die (eerder) vastgestelde inhoud betreft (dus geen ontwerp).
     * Als dat zo is, dan is deze momentopname de JuridischeUitgangssituatie van 
     * de volgende momentopname.
     */
    IsOnderdeelVanPublicatieVastgesteldeInhoud() {
        return this.#isOnderdeelVanPublicatie;
    }
    IsOnderdeelVanPublicatieVastgesteldeInhoudWordt() {
        this.#isOnderdeelVanPublicatie = true;
    }
    #isOnderdeelVanPublicatie = false;

    /**
     * Geeft de versies van de instrumenten (als InstrumentversieSpecificatie) op deze branch in deze momentopname
     */
    Instrumentversies() {
        let versies = this.IsInvoer() ? this.#nieuweInstrumenten : this.#actueleInstrumenten;
        return Object.values(versies);
    }
    /**
     * Geeft de versie van het instrument (als InstrumentversieSpecificatie of undefined) in deze momentopname
     */
    Instrumentversie(instrument) {
        let versies = this.IsInvoer() ? this.#nieuweInstrumenten : this.#actueleInstrumenten;
        return versies[instrument];
    }
    #actueleInstrumenten = {};
    #nieuweInstrumenten = {};

    /**
     * Geeft aan dat de inhoud van tenminste een van de instrumentversies is gewijzigd 
     * in deze momentopname
     */
    HeeftGewijzigdeInstrumentversie() {
        for (let versie of this.Instrumentversies()) {
            if (this.Tijdstip().IsGelijk(versie.Instrumentversie().JuridischeInhoudLaatstGewijzigd())) {
                return true;
            }
        }
        return false;
    }

    /**
     * Geef de datum van inwerkingtreding, indien bekend
     * @returns {Tijdstip}
     */
    JuridischWerkendVanaf() {
        return this.#juridischWerkendVanaf.Datum();
    }
    #juridischWerkendVanaf;
    #tijdstempelsToegestaan;

    /**
     * Geef de datum van start geldigheid, indien bekend en indien afwijkend van JuridischWerkendVanaf
     * @returns {Tijdstip}
     */
    GeldigVanaf() {
        return this.#geldigVanaf.Datum();
    }
    #geldigVanaf;

    /**
     * Geeft aan of de tijdstempels gewijzigd zijn in deze momentopname
     */
    HeeftGewijzigdeTijdstempels() {
        if (this.VoorgaandeMomentopname().Branch() == this.Branch()) {
            if (!this.JuridischWerkendVanaf().IsGelijk(this.VoorgaandeMomentopname().JuridischWerkendVanaf())) {
                return true;
            }
            if (this.GeldigVanaf() === undefined) {
                return this.VoorgaandeMomentopname().GeldigVanaf() !== undefined;
            } else {
                return !this.GeldigVanaf.IsGelijk(this.VoorgaandeMomentopname().GeldigVanaf());
            }
        } else {
            return this.JuridischWerkendVanaf().HeeftWaarde();
        }
        return false;
    }

    //#endregion

    //#region Eigenschappen - relatie met andere branches/momentopnamen

    /**
     * Geeft de voorgaande momentopname op dezelfde of een andere branch
     * @returns {Momentopname}
     */
    VoorgaandeMomentopname() {
        return this.#voorgaandeMomentopname;
    }
    #voorgaandeMomentopname;


    /**
     * Geeft aan dat een aantal branches dezelfde inhoud hebben en altijd tegelijk beheerd
     * worden. Als dit niet undefined is, dan is deze branch onderdeel van de lijst.
     * @returns {Momentopname[]}
     */
    TegelijkBeheerd() {
        return this.#tegelijkBeheerd;
    }
    #tegelijkBeheerd;

    /**
     * Geeft de momentopnamen van de branches waarmee ontvlochten is
     * @returns {Momentopname[]}
     */
    OntvlochtenMet() {
        return this.#ontvlochtenMet;
    }
    #ontvlochtenMet;

    /**
     * Geeft de momentopnamen van de branches waarmee vervlochten is
     * @returns {Momentopname[]}
     */
    VervlochtenMet() {
        return this.#vervlochtenMet;
    }
    #vervlochtenMet;

    /**
     * Geeft de namen van de braches waarvan de inhoud is verwerkt in de
     * inhoud van deze momentopname. Dat is inclusief de branch van deze
     * momentopname.
     */
    HeeftBijdragenVan() {
        return Object.keys(this.#bijdragen);
    }
    /**
     * Geeft de momentopname van de laatste bijdrage van een branch die in deze 
     * momentopname is verwerkt
     * @param {string} branchNaam - Een van de namen uit HeeftBijdragenVan
     * @returns {Tijdstip}
     */
    LaatsteBijdrage(branchNaam) {
        return this.#bijdragen[branchNaam];
    }

    /**
     * Per branch het tijdstip van laatste tijdstip van bijdragen
     */
    #bijdragen = {};
    /**
     * Bepaal welke branches (en tot welk tijdstip) verwerkt zijn in deze momentopname
     */
    #BepaalBijdragen() {
        this.#bijdragen = {};

        // Verzamel eerst alle bijdragen
        if (this.#voorgaandeMomentopname !== undefined) {
            this.#bijdragen = Object.assign({}, this.#voorgaandeMomentopname.#bijdragen);
        }
        this.#bijdragen[this.Branch().Naam()] = this;
        for (let v of this.#vervlochtenMet) {
            let bijdrage = this.#bijdragen[v.Branch().Naam()];
            if (bijdrage === undefined || bijdrage.Activiteit().Tijdstip().Vergelijk(v.Activiteit().Tijdstip()) < 0) {
                this.#bijdragen[v.Branch().Naam()] = v;
            }
        }
        // Haal de bijdragen van ontvlochten branches weg
        for (let v of this.#ontvlochtenMet) {
            delete this.#bijdragen[v.Branch().Naam()];
        }
    }
    //#endregion

    //#region Hulppfuncties
    /**
     * Itereer over alle momentopnamen voor alle projecten
     * @param {Tijdstip} tijdstip - Optioneel: tijdstip waarop de momentopname uiterlijk gemaakt moet zijn - undefined voor alle momentopnamen
     * @param {Branch} branch - Optioneel : branch waarvoor de momentopname gemaakt is - undefined voor alle branches en uitgangssituatie
     * @param {any} todo - methode die als argument een (momentopname krijgt; geef true terug om te stoppen
     */
    static VoorAlleMomentopnamen(tijdstip, branch, todo) {
        if (branch === undefined && BGProcesSimulator.This().Uitgangssituatie() !== undefined) {
            if (tijdstip === undefined || 0 <= tijdstip.Specificatie()) {
                if (todo(BGProcesSimulator.This().Uitgangssituatie())) {
                    return true;
                }
            }
        }
        for (let activiteit of Activiteit.Activiteiten(tijdstip)) {
            for (let momentopname of activiteit.Momentopnamen()) {
                if (branch === undefined || momentopname.Branch() == branch) {
                    if (todo(momentopname)) {
                        return true;
                    }
                }
            }
        };
    }
    //#endregion

    //#region Statusoverzicht
    /**
     * Het overzicht van de momentopname in het projectoverzicht
     */
    OverzichtHtml() {
        let meerdereInstrumentenMogelijk = BGProcesSimulator.Opties.MeerdereRegelingen || BGProcesSimulator.Opties.InformatieObjecten;
        let html = '<table>';
        for (let soortInstrument of Instrument.SoortInstrument_Regelgeving) {
            let soortnaam = Instrument.SoortInstrumentNamen[soortInstrument];
            soortnaam = soortnaam.charAt(0).toUpperCase() + soortnaam.slice(1)

            for (let instr of Object.keys(this.#actueleInstrumenten).sort()) {
                let instrument = this.#actueleInstrumenten[instr];
                if (instrument.Instrumentversie().HeeftJuridischeInhoud() && instrument.Instrumentversie().SoortInstrument() === soortInstrument) {
                    html += '<tr>';
                    if (meerdereInstrumentenMogelijk) {
                        html += `<td class="nw">${soortnaam}</td><td class="nw">${instrument.Instrument()}</td>`;
                    }
                    html += `<td class="w100">${instrument.OverzichtHtml()}</td></tr>`;
                }
            }
        }
        if (this.JuridischWerkendVanaf().HeeftWaarde()) {
            if (meerdereInstrumentenMogelijk) {
                html += `<tr><td colspan="2" class="nw">In werking vanaf</td><td>${this.JuridischWerkendVanaf().DatumTijdHtml()}</td></tr>`;
            } else {
                html += `<tr><td>In werking vanaf: ${this.JuridischWerkendVanaf().DatumTijdHtml()}</td></tr>`;
            }
            if (this.GeldigVanaf() !== undefined && this.GeldigVanaf().HeeftWaarde()) {
                if (meerdereInstrumentenMogelijk) {
                    html += `<tr><td colspan="2" class="nw">Terugwerkend tot</td><td>${this.GeldigVanaf().DatumTijdHtml()}</td></tr>`;
                } else {
                    html += `<tr><td>Terugwerkend tot: ${this.GeldigVanaf().DatumTijdHtml()}</td></tr>`;
                }
            }
        }

        if (this.JuridischeUitgangssituaties() === undefined || this.JuridischeUitgangssituaties()[0] !== this) {
            let heeftIWTWijzigingen = false;
            let heeftInhoudWijzigingen = false;
            if (this.Activiteit().Publicatiebron() === undefined) {
                heeftInhoudWijzigingen = true;
            } else {
                heeftInhoudWijzigingen = this.IsInhoudGewijzigd();
                if (!heeftInhoudWijzigingen) {
                    heeftIWTWijzigingen = this.IsInwerkingtredingToegevoegd();
                }
            }

            html += `<tr><td colspan="${(meerdereInstrumentenMogelijk ? 3 : 1)}">`;
            if (this.Activiteit().Publicatiebron() !== undefined) {
                html += `In ${this.Activiteit().Publicatiebron()} wordt `;
            } else {
                html += `Indien aanwezig wordt in een ${BGProcesSimulator.This().MogelijkePublicatie(this.IsVaststellingsbesluitGepubliceerd())} `;
            }
            if (heeftInhoudWijzigingen) {
                if (this.JuridischeUitgangssituaties() === undefined) {
                    html += 'een integrale versie van de tekst/informatieobjecten opgenomen.';
                } else {
                    html += `de wijziging ten opzichte van ${this.JuridischeUitgangssituaties()[0].Branch().Interactienaam()} d.d. ${this.JuridischeUitgangssituaties()[0].Tijdstip().DatumTijdHtml()}`;
                    if (this.JuridischeUitgangssituaties().length > 1) {
                        html += ', bijgewerkt met wijzigingen uit ';
                        for (let i = 1; i < this.JuridischeUitgangssituaties().length; i++) {
                            if (i > 1) {
                                html += ', ';
                            }
                            html += `${this.JuridischeUitgangssituaties()[i].Branch().Interactienaam()} d.d. ${this.JuridischeUitgangssituaties()[i].Tijdstip().DatumTijdHtml()}`;
                        }
                    }
                    html += ' beschreven.';
                }
            } else if (heeftIWTWijzigingen) {
                html += `de inwerkingtreding van het resultaat van ${this.JuridischeUitgangssituaties()[0].Branch().Interactienaam()} d.d. ${this.JuridischeUitgangssituaties()[0].Tijdstip().DatumTijdHtml()} beschreven.`;
            } else {
                html += 'geen wijziging in deze regelgeving beschreven.';
            }
            html += '</td></tr>';
        }
        if (this.#tegelijkBeheerd !== undefined) {
            let namen = [];
            for (let mo in this.#tegelijkBeheerd) {
                if (mo.Branch() != this.Branch()) {
                    namen.push(mo.Branch().Interactienaam());
                }
            }
            html += `<tr><td colspan="${(meerdereInstrumentenMogelijk ? 3 : 1)}">(De inhoud wordt gelijkgehouden met de inhoud van ${namen.join(', ')})</td></tr>`;
        }

        html += '</table>';
        return html;
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        // De opmaak verschilt tussen 1-instrument en meer-instrument scenario's.
        let meerdereInstrumentenMogelijk = BGProcesSimulator.Opties.MeerdereRegelingen || BGProcesSimulator.Opties.InformatieObjecten;

        let html = '<table>';

        for (let soortInstrument of Instrument.SoortInstrument_Regelgeving) {
            let soortnaam = Instrument.SoortInstrumentNamen[soortInstrument];
            soortnaam = soortnaam.charAt(0).toUpperCase() + soortnaam.slice(1)

            for (let instr of Object.keys(this.#actueleInstrumenten).sort()) {
                let instrument = this.#actueleInstrumenten[instr];
                if (instrument.Instrumentversie().SoortInstrument() === soortInstrument) {
                    html += '<tr>';
                    if (meerdereInstrumentenMogelijk) {
                        html += `<td>${soortnaam}</td><td>${(instrument.InstrumentInteractienaam())}</td>`;
                    }
                    html += `<td>${instrument.Html()}</td></tr>`;
                }
            }
        }

        html += '</table>';
        return html;
    }

    BeginInvoer() {
        this.#nieuweInstrumenten = Object.assign({}, this.#actueleInstrumenten);
        if (!BGProcesSimulator.Opties.MeerdereRegelingen && Object.keys(this.#nieuweInstrumenten).length == 0) {
            this.#MaakInstrument(Instrument.VrijeNaam(Instrument.SoortInstrument_Regeling, "Enige regeling"));
        }
    }

    InvoerInnerHtml() {
        // De opmaak is anders voor een wijziging of een initiële stand.
        let isWijzigig = this.#voorgaandeMomentopname !== undefined;

        // De opmaak verschilt tussen 1-instrument en meer-instrument scenario's.
        let meerdereInstrumentenMogelijk = BGProcesSimulator.Opties.MeerdereRegelingen || BGProcesSimulator.Opties.InformatieObjecten;
        let instrumentenAndereProjecten = {};
        if (meerdereInstrumentenMogelijk) {
            for (let instr of Instrument.Instrumentnamen()) {
                if (!(instr in this.#nieuweInstrumenten)) {
                    let soort = Instrument.SoortInstrument(instr);
                    if (instrumentenAndereProjecten[soort] === undefined) {
                        instrumentenAndereProjecten[soort] = [instr];
                    } else {
                        instrumentenAndereProjecten[soort].push(instr);
                    }
                }
            }
        }

        let html = '<table>';

        // Eerst de instrumenten die al op de branch aanwezig zijn
        for (let soortInstrument of Instrument.SoortInstrument_Regelgeving) {
            let soortnaam = Instrument.SoortInstrumentNamen[soortInstrument];
            soortnaam = soortnaam.charAt(0).toUpperCase() + soortnaam.slice(1)

            for (let instr of Object.keys(this.#nieuweInstrumenten).sort()) {
                let instrument = this.#nieuweInstrumenten[instr];
                if (instrument.Instrumentversie().SoortInstrument() === soortInstrument) {
                    html += '<tr>';
                    if (meerdereInstrumentenMogelijk) {
                        html += `<td>${soortnaam}</td><td>${(instrument.InstrumentInteractienaam())}</td>`;
                    }
                    html += `<td>${instrument.Html()}</td></tr>`;
                }
            }

            if (soortInstrument != Instrument.SoortInstrument_Regeling || BGProcesSimulator.Opties.MeerdereRegelingen) {
                if (instrumentenAndereProjecten[soortInstrument] !== undefined) {
                    // Toevoegen van een instrument uit een ander project
                    let opties = []
                    for (let instr of instrumentenAndereProjecten[soortInstrument]) {
                        // Zoek de laatste citeertitel voor het instrument op
                        let tijdstip;
                        let interactienaam = undefined;
                        Momentopname.VoorAlleMomentopnamen(this.Tijdstip(), undefined, (mo) => {
                            if (tijdstip === undefined || tijdstip.Vergelijk(mo.Tijdstip()) < 0) {
                                let versie = mo.Instrumentversie(instr);
                                if (versie !== undefined && versie.Instrumentversie().IsNieuweVersie()) {
                                    let metadata = versie.Instrumentversie().Annotatie(true, Annotatie.SoortAnnotatie_Citeertitel);
                                    if (metadata !== undefined && metadata.Citeertitel() !== '') {
                                        interactienaam = metadata.Citeertitel();
                                        tijdstip = mo.Tijdstip().Specificatie();
                                    }
                                }
                            }
                        });
                        opties.push({ id: instr, naam: (interactienaam === undefined ? instr : interactienaam), citeertitel: (interactienaam === undefined ? '' : interactienaam) });
                    }
                    if (opties.length > 0) {
                        opties.sort((x, y) => x.naam.localeCompare(y.naam));

                        html += `<tr><td>${soortnaam}</td><td>${this.HtmlVoegToe("Voeg een initiële versie toe", 'P_' + soortInstrument)}</td>
                                <td><label for="${this.ElementId('P_' + soortInstrument)}">Instrument uit een ander project:<br/>
                                <select id="${this.ElementId('IP_' + soortInstrument)}">`;
                        for (let optie of opties) {
                            html += `<option value="${optie.id}" data-ct="${optie.citeertitel}">${optie.naam}</option>`;
                        }
                        html += `</select></td></tr>`;
                    }
                }

                if (soortInstrument === Instrument.SoortInstrument_Regeling || BGProcesSimulator.Opties.InformatieObjecten) {
                    // Toevoegen nieuw instrument
                    html += `<tr><td>${soortnaam}</td><td>${this.HtmlVoegToe("Voeg een nieuw instrument toe", 'N_' + soortInstrument, ` data-soort="${soortInstrument}"`)}</td>
                            <td><label for="${this.ElementId('N_' + soortInstrument)}">Nieuw instrument</td></tr>`;
                }
            }
        }

        html += '</table>';
        return html;
    }

    OnInvoerClick(elt, idSuffix) {
        if (idSuffix === undefined) {
            return;
        }
        switch (idSuffix.charAt(0)) {
            case 'P':
                // Uit een ander project
                let select = document.getElementById(this.ElementId('I' + idSuffix));
                if (select.selectedIndex >= 0) {
                    let citeertitel = undefined;
                    let ct = select.options[select.selectedIndex].dataset.ct;
                    if (ct) {
                        citeertitel = ct;
                    }
                    this.#MaakInstrument(select.value, ct);
                    this.VervangInnerHtml();
                }
                break;
            case 'N':
                // Nieuw instrument
                this.#MaakInstrument(Instrument.VrijeNaam(elt.dataset.soort));
                this.VervangInnerHtml();
                break;
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            // OK
            let specificatie = this.Specificatie();
            // Haal specificatie en specificatie-elementen weg die geen basisversie en geen juridische inhoud hebben
            for (let instrument of [...Object.keys(this.#nieuweInstrumenten)]) {
                let versie = this.#nieuweInstrumenten[instrument];
                if (versie.Instrumentversie().Basisversie() === undefined && !versie.Instrumentversie().HeeftJuridischeInhoud()) {
                    this.#nieuweInstrumenten[instrument].Verwijder();
                    delete this.#nieuweInstrumenten[instrument];
                    delete specificatie[instrument];
                }
            }
            this.#actueleInstrumenten = this.#nieuweInstrumenten;
        } else {
            // Annuleren
            let specificatie = this.Specificatie();
            // Haal specificatie en nieuwe specificatie-elementen weg voor instrumenten die nog niet bestonden in de vorig gewijzigde versie
            for (let instrument in this.#nieuweInstrumenten) {
                let vorigeVersie = this.#actueleInstrumenten[instrument];
                if (vorigeVersie === undefined) {
                    this.#nieuweInstrumenten[instrument].Verwijder();
                    delete specificatie[instrument];
                } else {
                    specificatie[instrument] = vorigeVersie.Instrumentversie().MaakSpecificatie();
                }
            }
        }
    }
    //#endregion

    //#region Interne functionaliteit
    /**
     * Maak een nieuw instrument
     * @param {string} naam - Naam van het instrument
     * @param {string} citeertitel - Optioneel: citeertitel
     */
    #MaakInstrument(naam, citeertitel) {
        let instrument = new InstrumentversieSpecificatie(this, naam);
        this.#nieuweInstrumenten[naam] = instrument;
        instrument.Instrumentversie().SpecificeerNieuweJuridischeInhoud();
        if (citeertitel !== undefined) {
            instrument.Instrumentversie().Annotatie(new Metadata(citeertitel, this));
        }
    }
    //#endregion
}
//#endregion

//#region Branch informatie en invoer/selectie
/*------------------------------------------------------------------------------
*
* Branch bevat de globale informatie over de branch en beheert de specificatie
* die bij het aanmaken van de branch gegeven moet worden.
* 
*----------------------------------------------------------------------------*/
class Branch extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak een specificatie-element voor een branch
     * @param {Activiteit} activiteit - Activiteit die de branch aanmaakt
     * @param {string} naam - korte naam van de branch, te gebruiken in de specificatie.
     * @param {Branch[]} moAndereBranches - de branch (Soort_VolgtOpAndereBranch) of branches (Soort_OplossingSamenloop)
     *                                      waar deze branch op voortbouwt.
     */
    constructor(activiteit, naam, moAndereBranches) {
        super(activiteit.Specificatie(), naam, undefined, activiteit);
        if (this.Soort() === Branch.Soort_VolgtOpAndereBranch) {
            this.#volgtOpBranch = moAndereBranches;
        } else if (this.Soort() === Branch.Soort_OplossingSamenloop) {
            this.#volgtOpBranch = moAndereBranches[0];
            this.#inWerkingMet = moAndereBranches;
        }
        this.#volgorde = ++Branch.#volgende_volgorde;
        Branch.#branches[this.Index()] = this;
    }

    destructor() {
        if (this.Index() !== undefined) {
            delete Branch.#branches[this.Index()];
        }
        super.destructor();
    }
    //#endregion

    //#region Constanten
    /**
     * Branch is afgeleid van de (op een bepaald moment) geldende regelgeving
     */
    static Soort_GeldendeRegelgeving = "Regulier";
    /**
     * Branch bouwt voort op een andere branch
     */
    static Soort_VolgtOpAndereBranch = "VolgendOp";
    /**
     * Branch bevat de oplossing van samenloop tussen andere branches
     */
    static Soort_OplossingSamenloop = "TegelijkMet";
    //#endregion

    //#region Eigenschappen
    /**
     * Geef de branches die in het scenario bekend zijn, gesorteerd op volgorde van aanmaken / onderlinge afhankelijkheid
     * Een branch die afhangt van een andere branch komt dus later in het resultaat.
     * @param {Tijdstip} tijdstip - Optioneel: tijdstip waarop de branch uiterlijk aangemaakt moet zijn - undefined voor alle branches
     * @param {Project} project - Optioneel: project waar de branch bij hoort - undefined voor branches van alle projecten
     */
    static Branches(tijdstip, project) {
        let branches = [];
        for (let branch of Object.values(Branch.#branches)) {
            if (project === undefined || branch.Project() === project) {
                if (tijdstip === undefined || branch.OntstaanIn().Tijdstip().Vergelijk(tijdstip) <= 0) {
                    branches.push(branch);
                }
            }
        }
        branches.sort(Branch.Vergelijk);
        return branches;
    }
    static #branches = {};
    #volgorde;
    static #volgende_volgorde = 0;

    /**
     * Vergelijkingsfunctie om branches te sorteren
     */
    static Vergelijk(a, b) {
        let diff = a.OntstaanIn().Tijdstip().Vergelijk(b.OntstaanIn().Tijdstip());
        if (diff === 0) {
            diff = a.#volgorde - b.#volgorde;
        }
        return diff;
    }

    /**
     * Geef de branch met de gegeven naam
     * @param {string} branchnaam - Naam van de branch
     */
    static Branch(branchnaam) {
        for (let branch of Object.values(Branch.#branches)) {
            if (branch.Naam() === branchnaam) {
                return branch;
            }
        }
    }

    /**
     * Geeft de activiteit waarin de branch is ontstaan
     */
    OntstaanIn() {
        return this.SuperInvoer();
    }

    /**
     * Geeft de naam van de branch zoals die in de specificatie voorkomt
     */
    Project() {
        return this.OntstaanIn().Project();
    }

    /**
     * Geeft de naam van de branch zoals die in de specificatie voorkomt
     */
    Naam() {
        return this.Eigenschap();
    }

    /**
     * Geeft de naam van de branch zoals die aan de eindgebruiker getoond moet worden.
     */
    Interactienaam() {
        if (Branch.Branches(undefined, this.Project()).length == 1) {
            return this.Project().Naam();
        }
        let idx = 0;
        for (let branch of Branch.Branches(undefined, this.Project())) {
            idx++;
            if (branch === this) {
                return `IWT-moment #${idx} van ${this.Project().Naam()}`;
            }
        }
        return `Programmeerfout? ${this.Naam()}`
    }

    /**
     * Geeft een toelichting op de aard van de branch, voor weergave
     */
    InteractieToelichting() {
        if (this.Soort() == Branch.Soort_VolgtOpAndereBranch) {
            return `Volgt op ${this.VolgtOpBranch().Interactienaam()}`;
        } else if (this.Soort() == Branch.Soort_OplossingSamenloop) {
            let namen = [];
            for (let branch of this.TreedtConditioneelInWerkingMet().sort((a, b) => {
                let diff = a.Project().Naam().localeCompare(b.Project().Naam());
                if (diff == 0) {
                    diff = a.#volgorde - b.#volgorde;
                }
                return diff;
            })) {
                namen.push(branch.Interactienaam());
            }
            return `Lost samenloop op van ${namen.join(', ')}`;
        }
    }

    /**
     * Geeft de soort waartoe de branch behoort.
     */
    Soort() {
        return this.Specificatie().Soort;
    }

    /**
     * Geeft de branch die als voorganger dient van deze branch (niet voor Soort_GeldendeRegelgeving).
     */
    VolgtOpBranch() {
        return this.#volgtOpBranch;
    }
    #volgtOpBranch;

    /**
     * Geeft de branches die eerst in werking moeten treden; deze branch 
     * treedt dan ook in werking. Als deze waarde niet undefined is,
     * dan behoort VolgtOpBranch tot hetzelfde project.
     */
    TreedtConditioneelInWerkingMet() {
        return this.#inWerkingMet;
    }
    #inWerkingMet;

    /**
     * Geeft de laatste momentopname voor deze branch
     * @param {Tijdstip} tijdstip - Optioneel: tijdstip waarop de activiteit uiterlijk uitgevoerd moet zijn - undefined voor alle activiteiten
     */
    LaatsteMomentopname(tijdstip) {
        let resultaat;
        Momentopname.VoorAlleMomentopnamen(tijdstip, this, (mo) => resultaat = mo);
        return resultaat;
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return this.Interactienaam();
    }

    InvoerInnerHtml() {
        return '';
    }

    /**
     * Aangeroepen als er op een element geklikt wordt in de weergave-html. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnWeergaveClick(elt, idSuffix) {
    }

    /**
     * Aangeroepen als er iets in de invoer is gewijzigd. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is; weggelaten als kind-specificatie-element gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnInvoerChange(elt, idSuffix) {
    }

    /**
     * Aangeroepen als er in de invoer geklikt wordt. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnInvoerClick(elt, idSuffix) {
    }

    /**
     * Aangeroepen vlak voordat het modal scherm getoond wordt: prepareer het specificatie-element voor
     * de invoer van een nieuwe waarde.
     */
    BeginInvoer() {
        return true;
    }

    /**
     * Aangeroepen vlak voordat het modal scherm gesloten wordt: verwerk de gewijzigde invoer.
     * @param {boolean} accepteerInvoer - Geeft aan of de invoer geaccepteerd (ipv geannuleerd) wordt.
     * @returns {boolean} Geeft aan of de invoer nog niet beëindigd kan worden. Bij true wordt het modal scherm niet gesloten.
     */
    EindeInvoer(accepteerInvoer) {
        return false;
    }
    //#endregion
}
//#endregion

//#endregion

//#region Consolidatie en besluitstatus
/*==============================================================================
 *
 * De BG software moet ook bijhouden of er consolidatieproblemen optreden, dus
 * of er onopgeloste samenloop is. Daarnaast moet een eventuele beroepsprocedure
 * gevolgd worden en de uitkomsten ervan verwerkt worden.
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
*
* IWTMoment houdt bij welke inwerkingtredingsmomenten er inmiddels (bij BG) 
* bekend zijn. Dit gaat op datum: er kunnen meerdere branches zijn met dezelfde
* JuridischWerkendVanaf. De GeldigVanaf is voor de consolidatie bij BG niet 
* van belang. 
* 
*----------------------------------------------------------------------------*/
class IWTMoment {
    //#region Initialisatie
    /**
     * Maak een nieuw IWT-moment aan
     * @param {Tijdstip} datum
     */
    constructor(datum) {
        this.#datum = datum;
    }

    /**
     * Maak een kloon van dit object om bij te kunnen werken
     */
    #Kloon() {
        let kloon = new IWTMoment(this.#datum);
        kloon.#bijdragen = Object.assign({}, this.#bijdragen);
        return kloon;
    }
    //#endregion

    //#region Eigenschappen
    /**
     * De datum van iwt
     */
    Datum() {
        return this.#datum;
    }
    #datum;

    /**
     * De namen van de branches die leiden tot het ontstaan
     * van dit iwt-moment
     */
    Inwerkingtredingbranchnamen() {
        return Object.keys(this.#bijdragen);
    }
    /**
     * De momentopname van de branch die als laatste bijgedraagt
     * aan de versie die in werking treedt.
     * @returns {Momentopname}
     */
    LaatsteBijdrage(branchnaam) {
        return this.#bijdragen[branchnaam];
    }
    #bijdragen = {};
    //#endregion

    //#region Bijwerken
    /**
     * Geef een branch door als bijdragend aan een IWT-moment
     * @param {any} perBranch - Collectie met IWTMoment per branch
     * @param {any} perDatum - Collectie met IWTMoment per datum
     * @param {string} branchnaam - Naam van de branch
     * @param {Momentopname} momentopname - laatste momentopname voor de branch
     * @param {Tijdstip} iwtDatum - Nieuwe datum van inwerkingtreding
     */
    static WerkBij(perBranch, perDatum, branchnaam, momentopname, iwtDatum) {
        let iwtMoment = perBranch[branchnaam];
        if (iwtMoment !== undefined) {
            if (!iwtMoment.Datum().IsGelijk(iwtDatum)) {
                iwtMoment.#VerwijderBranch(perBranch, perDatum, branchnaam);
                if (iwtDatum === undefined) {
                    return;
                }
                iwtMoment = undefined;
            }
        }
        if (iwtDatum !== undefined && iwtDatum.HeeftWaarde()) {
            iwtMoment = iwtMoment === undefined ? new IWTMoment(iwtDatum) : iwtMoment.#Kloon();
            iwtMoment.#bijdragen[branchnaam] = momentopname; // Nieuwe momentopname is altijd recenter dan eerder verwerkte
            iwtMoment.#WerkCollectieBij(perBranch, perDatum);
        }
    }

    /**
     * Verwijder een branch als bijdragend aan een IWT-moment
     * @param {any} perBranch - Collectie met IWTMoment per branch
     * @param {any} perDatum - Collectie met IWTMoment per datum
     * @param {string} branchnaam - Naam van de branch
     */
    #VerwijderBranch(perBranch, perDatum, branchnaam) {
        delete perBranch[branchnaam];
        if (this.Branchnamen().length == 1) {
            delete perDatum[this.#datum.Specificatie()];
            return;
        }

        let kloon = this.#Kloon();
        delete kloon.#bijdragen[branchnaam];
        kloon.#WerkCollectieBij(perBranch, perDatum);
    }

    /**
     * Voeg deze instantie toe aan de collectie
     * @param {any} perBranch - Collectie met IWTMoment per branch
     * @param {any} perDatum - Collectie met IWTMoment per datum
     */
    #WerkCollectieBij(perBranch, perDatum) {
        perDatum[this.#datum.Specificatie()] = this;
        for (let branchnaam of this.Inwerkingtredingbranchnamen()) {
            perBranch[branchnaam] = this;
        }
    }
    //#endregion
}

/*------------------------------------------------------------------------------
*
* IWTMomentConsolidatiestatus geeft de status van het consolidatieproces
* voor een iwt-moment. Het heeft ook informatie over wat er fout is, en 
* hoe BG dat moet herstellen.
* 
*----------------------------------------------------------------------------*/
class IWTMomentConsolidatiestatus {
    //#region Initialisatie
    /**
     * Maak een nieuwe consolidatiestatus voor een IWT-moment aan
     * @param {IWTMoment} iwtMoment - IWT moment waar dit de status van is.
     * @param {any} cumulatieveIWTBijdragen - Bijdragen aan de IWT-versie van alle branches die in werking zijn.
     */
    constructor(iwtMoment, cumulatieveIWTBijdragen) {
        this.#iwtMoment = iwtMoment;

        // Als er sprake is van gelijktijdige iwt, dan moet elke branch als
        // laatste bijdrage de laatste momentopname van de andere branches hebben.
        this.#samenloopBijIWT = false;
        for (let branchnaam of iwtMoment.Inwerkingtredingbranchnamen()) {
            for (let andereBranchnaam of iwtMoment.Inwerkingtredingbranchnamen()) {
                if (branchnaam != andereBranchnaam) {
                    if (cumulatieveIWTBijdragen[branchnaam].LaatsteBijdrage(andereBranchnaam) != cumulatieveIWTBijdragen[andereBranchnaam]) {
                        samenloopBijIWT = true;
                        break;
                    }
                }
            }
        }

        // Bepaal de laatste bijdragen van andere branches aan de versie die voor IWT is klaargezet op deze branch
        // Bij gelijktijdige iwt is de aanname dat de bijdragenViaBranches een goede weergave is van de bijdragen 
        // als de samenloop - bij - IWT is opgelost.
        let bijdragenViaBranches = {}
        for (let branchnaam of iwtMoment.Inwerkingtredingbranchnamen()) {
            for (let bijdragendeBranch of cumulatieveIWTBijdragen[branchnaam].HeeftBijdragenVan()) {
                let laatste = bijdragenViaBranches[bijdragendeBranch];
                let mo = cumulatieveIWTBijdragen[branchnaam].LaatsteBijdrage(bijdragendeBranch);
                if (laatste === undefined || laatste.Activiteit.Tijdstip().Vergelijk(mo.Activiteit.Tijdstip()) < 0) {
                    bijdragenViaBranches[bijdragendeBranch] = mo;
                }
            }
        }

        // Er is geen sprake van samenloop als elke laatste bijdrage aan het IWT-moment tevens de laatste bijdrage aan de instrumentversies
        // die voor het IWT-moment zijn klaargezet, dus de bijdragen in bijdragenViaBranches.
        this.#teVervlechten = [];
        for (let vereisteBranchnaam in cumulatieveIWTBijdragen) {
            let bijdrage = bijdragenViaBranches[vereisteBranchnaam];
            if (bijdrage === undefined || bijdrage != cumulatieveIWTBijdragen[vereisteBranchnaam]) {
                this.#teVervlechten.push(cumulatieveIWTBijdragen[vereisteBranchnaam]);
            }
        }

        // Via de bijdragen van de instrumentversies mogen er geen branches zijn die niet in werking zijn
        this.#teOntvlechten = [];
        for (let bijdragendeBranchnaam in bijdragenViaBranches) {
            if (cumulatieveIWTBijdragen[bijdragendeBranchnaam] === undefined) {
                this.#teOntvlechten.push(bijdragenViaBranches[bijdragendeBranchnaam]);
            }
        }
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Het IWT moment waar dit de status van is
     */
    IWTMoment() {
        return this.#iwtMoment;
    }
    #iwtMoment;

    /**
     * Geeft aan dat de consolidatie voltooid is
     */
    IsVoltooid() {
        return !this.#samenloopBijIWT && this.#teVervlechten.length == 0 && this.#teOntvlechten.length == 0;
    }

    /**
     * Geeft aan dat er samenloop is tussen de verschillende branches die tegelijk in werking treden
     */
    HeeftSamenloopBijIWT() {
        return this.#samenloopBijIWT;
    }
    #samenloopBijIWT;

    /**
     * De momentopnamen (uit andere branches dan de iwt-branches) die vervlochten moeten worden
     * om tot een geconsolideerde versie voor het IWT moment te komen
     */
    TeVervlechten() {
        return this.#teVervlechten;
    }
    #teVervlechten;

    /**
     * De momentopnamen (uit andere branches dan de iwt-branches) die vervlochten moeten worden
     * om tot een geconsolideerde versie voor het IWT moment te komen
     */
    TeOntvlechten() {
        return this.#teOntvlechten;
    }
    #teOntvlechten;
    //#endregion
}

/*------------------------------------------------------------------------------
*
* Consolidatiestatus houdt bij hoe ver de consolidatie is gevorderd. Elke activiteit
* heeft in deze simulator een eigen kopie van de status na afronding van de
* activiteit. In BG-software zal het een actuele status zijn die steeds
* bijgewerkt wordt (of opvraagbaar is).
* 
*----------------------------------------------------------------------------*/
class Consolidatiestatus {

    //#region Initialisatie
    /**
     * Maak een nieuwe instantie van de consolidatiestatus
     */
    constructor() {
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Geeft de op dit moment geldende regeling (waarvan de consolidatie niet afgerond kan zijn)
     * @param {Tijdstip} tijdstip - Tijdstip waarop om de geldende regeling gevraagd wordt
     * @returns {IWTMomentConsolidatiestatus}
     */
    NuGeldend(tijdstip) {
        let resultaat;
        for (let geldend of this.#geldend) {
            if (geldend.IWTMoment().Datum().Vergelijk(tijdstip) <= 0) {
                resultaat = geldend;
            } else {
                break;
            }
        }
        return resultaat;
    }
    #geldend = [];

    /**
     * Geef de toekomstige IWT-momenten en de status ervan, voor zover bepaald
     * @returns {IWTMomentConsolidatiestatus[]}
     */
    Bepaald() {
        return this.#geldend;
    }

    /**
     * Werk de consolidatiestatus bij. Deze moet aangeroepen worden nadat de 
     * specificatie gewijzigd is.
     */
    static WerkBij() {
        let voorgaandeConsolidatie = BGProcesSimulator.This().Uitgangssituatie().Consolidatiestatus();
        if (voorgaandeConsolidatie !== undefined) {
            voorgaandeConsolidatie.#WerkBij(undefined, BGProcesSimulator.This().Uitgangssituatie());
        }
        for (let activiteit of Activiteit.Activiteiten()) {
            activiteit.Consolidatiestatus().#WerkBij(voorgaandeConsolidatie, activiteit);
            voorgaandeConsolidatie = activiteit.Consolidatiestatus();
        }
    }
    //#endregion

    //#region Interne functionaliteit
    /**
     * Werk de consolidatie-informatie bij
     * @param {Consolidatiestatus} voorgaandeConsolidatie
     * @param {Activiteit} activiteit - Activiteit of Uitgangssituatie
     */
    #WerkBij(voorgaandeConsolidatie, activiteit) {
        // Werk de relatie tussen IWT-momenten en branches bij
        this.#iwtPerBranch = Object.assign({}, voorgaandeConsolidatie === undefined ? undefined : voorgaandeConsolidatie.#iwtPerBranch)
        this.#iwtPerDatum = Object.assign({}, voorgaandeConsolidatie === undefined ? undefined : voorgaandeConsolidatie.#iwtPerDatum)
        if (activiteit instanceof Uitgangssituatie) {
            IWTMoment.WerkBij(this.#iwtPerBranch, this.#iwtPerDatum, activiteit.Branch().Naam(), activiteit, activiteit.JuridischWerkendVanaf());
        } else {
            for (let mo of activiteit.Momentopnamen()) {
                if (mo.Activiteit() !== activiteit) {
                    // Ongewijzigde momentopname
                    continue;
                }
                IWTMoment.WerkBij(this.#iwtPerBranch, this.#iwtPerDatum, mo.Branch().Naam(), mo, mo.JuridischWerkendVanaf());
            }
        }

        this.#geldend = [];

        // Deze simulator bouwt de volledige consolidatie op. Dat zal in de praktijk na een enkele
        // activiteit niet nodig zijn, dan kan het oude deel ongemoeid gelaten worden. Maar omdat het
        // hier over bijzonder weinig gegevens gaat, wordt (qua codering) de meest eenvoudige oplossing
        // gekozen.
        let iwtDatums = Object.keys(this.#iwtPerDatum).sort();
        if (iwtDatums.length == 0) {
            // Niets te consolideren
            return;
        }

        // We zijn niet geïnteresseerd in consolidatie in het verleden, daar heeft
        // BG geen consolidatieplicht voor.
        let teConsoliderenVanaf = iwtDatums[0];
        for (let iwtDatum of iwtDatums) {
            if (this.#iwtPerDatum[iwtDatum].Datum().Vergelijk(activiteit.Tijdstip()) < 0) {
                teConsoliderenVanaf = iwtDatum;
            } else {
                break;
            }
        }

        let cumulatieveIWTBijdragen = {}
        for (let iwtDatum of iwtDatums) {
            let iwtMoment = this.#iwtPerDatum[iwtDatum];
            for (let branchnaam of iwtMoment.Inwerkingtredingbranchnamen()) {
                cumulatieveIWTBijdragen[branchnaam] = iwtMoment.LaatsteBijdrage(branchnaam);
            }
            if (iwtDatum < teConsoliderenVanaf) {
                continue;
            }

            // Bepaal de status van de consolidatie
            let status = new IWTMomentConsolidatiestatus(iwtMoment, cumulatieveIWTBijdragen);
            this.#geldend.push(status);
            if (!status.IsVoltooid()) {
                // Verder gaan heeft geen zin, de volgende zullen incompleet worden als dit IWT-moment wordt opgelost
                break;
            }
        }
    }
    #iwtPerBranch = {};
    #iwtPerDatum = {};

    //#endregion
}
//#endregion

//#region In te vullen door scenario-schrijver
/*==============================================================================
 *
 * Onderdelen van de specificatie die niet door een gesimuleerde eindgebruiker
 * maar door de schrijver van het scenario worden ingevuld: 
 * Specificatie als geheel, Beschrijving, Startdatum, Uitgangssituatie.
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
 *
 * Beschrijving
 * 
 *----------------------------------------------------------------------------*/
class Beschrijving extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak het specificatie-element aan voor de beschrijving van het scenario (of van een activiteit)
     * @param {any} specificatie - Volledige specificatie
     * @param {Activiteit} activiteit - Optioneel: activiteit waar dit een beschrijving van is
     */
    constructor(specificatie, activiteit) {
        super(specificatie, 'Beschrijving', undefined, activiteit);
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        if (this.Specificatie() === undefined) {
            return this.HtmlVoegToe("Voeg een beschrijving toe", 'M');
        } else {
            return `<table><tr><td>${this.HtmlWerkBij("Wijzig de beschrijving", 'M')}</td><td>${this.Specificatie()}</td></tr></table>`;
        }
    }

    InvoerInnerHtml() {
        return `<textarea class="beschrijving" id="${this.ElementId('T')}">${(this.Specificatie() === undefined ? '' : this.Specificatie())}</textarea>`;
    }

    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix == 'M') {
            this.OpenModal();
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            this.SpecificatieWordt(document.getElementById(this.ElementId('T')).value);
        }
    }
    //#endregion
}

/*------------------------------------------------------------------------------
 *
 * Startdatum
 * 
 *----------------------------------------------------------------------------*/
class Startdatum extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak het specificatie-element aan voor de startdatum van het scenario
     * @param {any} specificatie - Volledige specificatie
     */
    constructor(specificatie) {
        super(specificatie, 'Startdatum');
        if (this.Specificatie() === undefined) {
            let datum = new Date(Date.now());
            datum.setHours(0, 0, 0, 0);
            this.#WerkSpecificatieBij(datum);
        } else {
            let spec = this.Specificatie();
            this.#WerkSpecificatieBij(new Date(Date.UTC(parseInt(spec.substr(0, 4)), parseInt(spec.substr(5, 2)) - 1, parseInt(spec.substr(8, 2)))))
        }
    }
    //#endregion

    //#region Eigenschappen
    static Datum() {
        return Startdatum.#startdatum;
    }
    static #startdatum;
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return `${this.HtmlWerkBij("Pas de startdatum van het scenario aan", 'M')}${this.Specificatie()}`;
    }

    InvoerInnerHtml() {
        return `<p>
Geef de startdatum van het scenario. Alle tijdstippen en datums worden ten opzichte van deze datum gerekend.
Het werken met dagen-sinds-start maakt het rekenwerk met termijnen eenvoudiger.
</p>
<div>
    <input type="number" class="number2" min="1" max="31" id="${this.ElementId('D')}" value="${this.Specificatie().substr(8, 2)}"/> -
    <input type="number" class="number2" min="1" max="12" id="${this.ElementId('M')}" value="${this.Specificatie().substr(5, 2)}"/> -
    <input type="number" class="number4" min="2020" id="${this.ElementId('J')}" value="${this.Specificatie().substr(0, 4)}"/>
</div>`;
    }

    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix == 'M') {
            this.OpenModal();
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            let dag = parseInt(this.Element('D').value);
            let maand = parseInt(this.Element('M').value);
            let jaar = parseInt(this.Element('J').value);
            let datum = new Date(Date.UTC(jaar, maand - 1, dag));
            this.#WerkSpecificatieBij(datum);
        }
    }
    //#endregion

    //#region Interne functionaliteit
    #WerkSpecificatieBij(datum) {
        Startdatum.#startdatum = datum;
        this.SpecificatieWordt(datum.toJSON().substr(0, 10));
    }
    //#endregion
}

/*------------------------------------------------------------------------------
*
* Uitgangssituatie
* 
*----------------------------------------------------------------------------*/
class Uitgangssituatie extends Momentopname {

    //#region Initialisatie
    /**
     * Maak het specificatie-element aan
     * @param {any} specificatie - Volledige specificatie
     */
    constructor(specificatie) {
        let branchImitator = {
            Naam: () => 'Uitgangssituatie',
            Interactienaam: () => 'Uitgangssituatie',
            Soort: () => Branch.Soort_GeldendeRegelgeving
        };
        super(undefined, specificatie, branchImitator, false);
    }
    #momentopname;
    //#endregion

    //#region Eigenschappen
    Tijdstip() {
        return Tijdstip.StartTijd();
    }

    /**
     * De uitgangssituatie is in werking 
     */
    JuridischWerkendVanaf() {
        if (this.Instrumentversies().length > 0) {
            return Tijdstip.StartDatum();
        }
    }

    /**
     * Geef de datum van start geldigheid (als undefined)
     */
    GeldigVanaf() {
    }

    /**
     * Geef een overzicht van de status van het consolidatieproces na de uitgangssituatie
    */
    Consolidatiestatus() {
        return this.#consolidatiestatus;
    }
    #consolidatiestatus = new Consolidatiestatus();
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        if (this.IsReadOnly()) {
            if (this.Specificatie() === undefined) {
                return '';
            } else {
                return super.WeergaveInnerHtml();
            }
        } else {
            let html = '';
            if (this.Specificatie() === undefined) {
                if (BGProcesSimulator.Opties.MeerdereRegelingen || BGProcesSimulator.Opties.InformatieObjecten) {
                    html += 'Geef aan welke regelgeving al in werking is bij de start van het scenario.'
                }
                else {
                    html += 'Geef aan of er al een versie van de regeling in werking is bij de start van het scenario.'
                }
                html += this.HtmlVoegToe("Voeg een uitgangssituatie toe", 'M');
            } else {
                html += `<table><tr><td>${this.HtmlWerkBij("Wijzig de uitgangssituatie", 'M')}</td><td>${super.WeergaveInnerHtml()}</td></tr></table>`;
            }
            return html;
        }
    }

    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix == 'M') {
            this.OpenModal();
        }
    }

    InvoerInnerHtml() {
        let html = '<p>';
        if (BGProcesSimulator.Opties.MeerdereRegelingen || BGProcesSimulator.Opties.InformatieObjecten) {
            html += 'Geef aan welke regelgeving al in werking is bij de start van het scenario.'
        }
        else {
            html += 'Geef aan of er al een versie van de regeling in werking is bij de start van het scenario.'
        }
        html += `</p>
${super.InvoerInnerHtml()}`;
        return html;
    }
    //#endregion
}

//#endregion

//#region Activiteit en projecten
/*==============================================================================
 *
 * Vastleggen wat de eindgebruiker uitvoert: Activiteit en Project
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
*
* Project beheert de informatie over een project.
* 
*----------------------------------------------------------------------------*/
class Project extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Create a new project
     * @param {string} naam Naam van het project
     */
    constructor(naam) {
        super(BGProcesSimulator.This().Specificatie().Projecten, naam);
        Project.#projecten[naam] = this;
    }

    destructor() {
        delete Project.#projecten[this.Naam()];
        super.destructor();
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Een lijst met alle projecten in het scenario
     */
    static Projecten() {
        return this.#projecten;
    }
    static #projecten = {};

    /**
     * Naam van het project
     */
    Naam() {
        return this.Eigenschap()
    }
    /**
     * Geef een beschikbare naam voor een nieuw project
     */
    static VrijeNaam() {
        return BGProcesSimulator.VrijeNaam(Object.keys(BGProcesSimulator.This().Specificatie().Projecten), "Project #");
    }

    /**
     * De unieke code van dit project waarmee de namen van de branches gemaakt worden
     * @returns
     */
    BranchPrefix() {
        return `p${this.#index}_`;
    }
    #index;
    //#endregion
}

/*------------------------------------------------------------------------------
*
* Activiteit is een basisklasse/specificatie-subelement die de basisfunctionaliteit
* biedt voor de invoer van een activiteit.
* 
*----------------------------------------------------------------------------*/
class Activiteit extends SpecificatieElement {

    //#region Initialisatie / lees specificatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {Project} project - Naam van het project waar de activiteit bijhoort
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(project, specificatie) {
        super(BGProcesSimulator.This().Specificatie().Projecten[project.Naam()], undefined, specificatie);
        this.#project = project;
        this.#naam = this.Specificatie().Soort;
        this.#soort = Activiteit.SoortActiviteit[this.Specificatie().Soort];
        this.#tijdstip = new Tijdstip(this, this.Specificatie(), 'Tijdstip', true);
        this.#beschrijving = new Beschrijving(this.Specificatie(), this);
        Activiteit.#activiteiten[this.Index()] = this;
    }

    /**
     * Aangeroepen als een activiteit verwijderd wordt
     */
    destructor() {
        if (this.Index() !== undefined) {
            delete Activiteit.#activiteiten[this.Index()];
        }
        super.destructor();
    }

    /**
     * Zet de specificatie om in een in-memory activiteit
     * @param {Project} project - Naam van het project waar de activiteit bijhoort (als het om een projectactiviteit gaat)
     * @param {any} specificatie - Specificatie van de activiteit
     * @returns {Activiteit} - De activiteit, of undefined als de activiteit niet gemaakt kan worden
     */
    static LeesSpecificatie(project, specificatie) {
        let soort = Activiteit.SoortActiviteit[specificatie.Soort];
        if (soort.Constructor === undefined) {
            BGProcesSimulator.SpecificatieMelding(new Tijdstip(undefined, specificatie, 'Tijdstip', true), `Geen in-memory representatie beschikbaar voor activiteit ${specificatie.Soort}`);
            return;
        }
        try {
            let activiteit = soort.Constructor(project, specificatie);
            let namen = [];
            if (activiteit.#soort.IsWijziging) {
                // Maak de momentopnamen aan
                let activiteitProps = ['Soort', 'Tijdstip', 'Beschrijving'];
                activiteitProps.push(...activiteit.#soort.Props);
                for (let prop in specificatie) {
                    if (!activiteitProps.includes(prop)) {
                        namen.push(prop);
                    }
                }
            }
            activiteit.LeesMomentopnameSpecificaties(namen);
            activiteit.PasSpecificatieToe();
            return activiteit;
        } catch (e) {
            BGProcesSimulator.SpecificatieMelding(new Tijdstip(undefined, specificatie, 'Tijdstip', true), `Kan in-memory representatie activiteit ${specificatie.Soort} niet aanmaken: ${e}`);
        }
    }

    /**
     * Lees de specificatie van een momentopname voor een branch
     * @param {string} branchnaam - Naam van de branch. De branch moet bestaan als onderdeel van het project waar deze activiteit bij hoort.
     */
    LeesMomentopnameSpecificatie(branchnaam) {
        // Zoek de branch op
        let branch = Branch.Branch(branchnaam);
        if (branch === undefined) {
            BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `branch '${branchnaam}' bestaat nog niet`);
            branch = new Branch(this, branchnaam);
        }
        new Momentopname(this, this.Specificatie(), branch, this.Soort().MomentopnameTijdstempels);
    }
    //#endregion

    //#region Constanten
    static SoortActiviteit = {
        'Maak branch': {
            KanVolgenOp: true,
            KanNietVolgenOp: false,
            IsWijziging: true,
            Props: [],
            MomentopnameTijdstempels: false,
            MomentopnameProps: ['Soort', 'Branch', 'Branches'],
            Constructor: (project, specificatie) => {
                if (Activiteit.Activiteiten(undefined, project).length === 0) {
                    return new Activiteit_MaakProject(project, specificatie);
                } else {
                    return new Activiteit_MaakBranch(project, specificatie);
                }
            }
        },
        'Download': {
            KanVolgenOp: [],
            IsWijziging: false,
            Props: ['Branch'],
            Constructor: (project, specificatie) => new Activiteit_Download(project, specificatie)
        },
        'Wijziging': {
            KanVolgenOp: ['Maak branch', 'Download'],
            KanNietVolgenOp: false,
            IsWijziging: true,
            Props: [],
            MomentopnameTijdstempels: false,
            MomentopnameProps: [],
            Constructor: (project, specificatie) => new Activiteit(project, specificatie)
        },
        'Uitwisseling': {
            KanVolgenOp: ['Download', 'Uitwisseling'],
            KanNietVolgenOp: false,
            IsWijziging: false,
            Props: [],
            Constructor: (project, specificatie) => new Activiteit_Uitwisseling(project, specificatie)
        },
        'Bijwerken uitgangssituatie': {
            KanVolgenOp: ['Maak branch', 'Uitwisseling'],
            KanNietVolgenOp: false,
            IsWijziging: true,
            Props: [],
            MomentopnameTijdstempels: false,
            MomentopnameProps: [],
            Constructor: (project, specificatie) => new Activiteit_BijwerkenUitgangssituatie(project, specificatie)
        },
        'Ontwerpbesluit': {
            KanVolgenOp: ['Maak branch', 'Uitwisseling'],
            KanNietVolgenOp: ['Concept-vaststellingsbesluit', 'Vaststellingsbesluit'],
            IsWijziging: true,
            Props: ['Begin inzagetermijn', 'Einde inzagetermijn'],
            MomentopnameTijdstempels: false,
            MomentopnameProps: [],
            Constructor: (project, specificatie) => new Activiteit_Ontwerpbesluit(project, specificatie)
        },
        'Concept-vaststellingsbesluit': {
            KanVolgenOp: ['Maak branch', 'Uitwisseling'],
            KanNietVolgenOp: ['Vaststellingsbesluit'],
            IsWijziging: true,
            Props: [],
            MomentopnameTijdstempels: true,
            MomentopnameProps: [],
            Constructor: (project, specificatie) => new Activiteit_Vaststellingsbesluit(project, specificatie)
        },
        'Vaststellingsbesluit': {
            KanVolgenOp: ['Maak branch', 'Uitwisseling'],
            KanNietVolgenOp: false,
            IsWijziging: true,
            Props: ['Einde beroepstermijn'],
            MomentopnameTijdstempels: true,
            MomentopnameProps: [],
            Constructor: (project, specificatie) => new Activiteit_Vaststellingsbesluit(project, specificatie)
        }
    };
    //#endregion

    //#region Eigenschappen
    /**
     * Geef alle gespecificeerde activiteiten, gesorteerd op tijdstip
     * @param {Tijdstip} tijdstip - Optioneel: tijdstip waarop de activiteit uiterlijk uitgevoerd moet zijn - undefined voor alle activiteiten
     * @param {Project} project - Optioneel: project waarbij de activiteiten getoond moeten worden.
     */
    static Activiteiten(tijdstip, project) {

        return Object.values(Activiteit.#activiteiten).filter(
            (activiteit) => {
                if (project === undefined || activiteit.ToonInProject(project)) {
                    if (tijdstip === undefined || activiteit.Tijdstip().Vergelijk(tijdstip) <= 0) {
                        return true;
                    }
                }
                return false;
            }
        ).sort((a, b) => a.Tijdstip().Vergelijk(b.Tijdstip()));
    }
    static #activiteiten = {};

    /**
     * Geeft de naam van het project waarvoor deze activiteit is gespecificeerd.
     * Voor de niet-projectgebonden activiteiten is dit het project waarop de
     * wijzigingen aan regelgeving worden uitgevoerd voordat ze naar de andere
     * projecten worden gebruikt.
     */
    Project() {
        return this.#project;
    }
    #project;

    /**
     * Geeft de naam van de branch waar deze instrumentversie deel van uitmaakt zoals die aan de eindgebruiker getoond moet worden.
     * @returns
     */
    Tijdstip() {
        return this.#tijdstip;
    }
    #tijdstip;

    /**
     * Geeft de beschrijving van de soort activiteit uit SoortActiviteit
     */
    Soort() {
        return this.#soort;
    }
    #soort;

    /**
     * Een toelichting op het waarom van de activiteit, de rol die de activiteit speelt in het scenario
     * @returns {Beschrijving}
     */
    Beschrijving() {
        return this.#beschrijving;
    }
    #beschrijving;

    /**
     * Geef de momentopnamen waarvoor inmiddels specificatie-elementen zijn aangemaakt, ongesorteerd
     */
    Momentopnamen() {
        let momentopnamen = [];
        for (let im of this.SubManagers()) {
            if (im instanceof Momentopname) {
                momentopnamen.push(im);
            }
        }
        return momentopnamen;
    }
    //#endregion

    //#region Te implementeren/overschrijven in afgeleide klassen
    /**
     * De naam van de activiteit voor weergave in de overzichten
     */
    Naam() {
        return this.#naam;
    }
    #naam;

    /**
     * Geeft aan of de activiteit vermeld moet worden in het overzicht van het project
     * @param {Project} project - Het project waarvoor het overzicht gemaakt wordt
     */
    ToonInProject(project) {
        if (project === null) {
            return false;
        }
        return this.#project === project
    }

    /**
     * Geeft aan dat de momentopname door een adviesbureau is aangemaakt
     */
    UitgevoerdDoorAdviesbureau() {
        for (let mo of this.Momentopnamen()) {
            return mo.UitgevoerdDoorAdviesbureau();
        }
    }

    /**
     * Als de activiteit leidt tot een publicatie of revisie: de naam van de bron ervan
     * met lidwoord.
     */
    Publicatiebron() {

    }

    /**
     * Weergave van de status van een project kort na het uitvoeren van een activiteit.
     * Het overzicht wordt samengesteld voor de laatst uitgevoerde activiteit voor het project,
     * @param {Activiteit} naActiviteit - De activiteit die zojuist is uitgevoerd.
     * @param {Project} project - Project waarvan de status weergegeven moet worden.
     * @returns {string} - Html
     */
    ProjectstatusHtml(naActiviteit, project) {
        let html = this.ProjectActiviteitOverzichtHtml(naActiviteit, project);
        html += this.VersiebeheerOverzichtHtml(project);
        return html;
    }

    /**
     * Lees de specificaties van de momentopnamen voor deze activiteit
     * @param {string[]} branchnamen - De namen van de branches.
     */
    LeesMomentopnameSpecificaties(branchnamen) {
        // Maak momentopnamen aan op basis van de branches in de specificatie
        for (let branchnaam of branchnamen) {
            this.LeesMomentopnameSpecificatie(branchnaam);
        }
        // Voeg ook momentopnamen toe voor de overige momentopnamen uit het project
        for (let branch of Branch.Branches(this.Tijdstip(), this.Project())) {
            if (!branchnamen.includes(branch.Naam())) {
                this.LeesMomentopnameSpecificatie(branch.Naam());
            }
        }
    }

    /**
     * Pas de specificatie toe voor de activiteit, nadat alle (gespecificeerde) momentopnamen
     * zijn ingelezen.
     */
    PasSpecificatieToe() {

    }
    //#endregion

    //#region Verslag van de activiteit
    /**
     * Weergave van het verslag van de activiteit, gericht op wat er in de user interface gebeurt
     * @returns {string} - Html
     */
    ActiviteitUIVerslagHtml() {
        let html = this.ActiviteitOverzichtHtml(naActiviteit, project);
        html += this.VersiebeheerOverzichtHtml(project);
        return html;
    }
    #uiVerslag = [];

    /**
     * Weergave van het verslag van de activiteit, gericht op wat er in de software gebeurt
     * @returns {string} - Html
     */
    ActiviteitSoftwareVerslagHtml() {
        let html = this.ActiviteitOverzichtHtml(naActiviteit, project);
        html += this.VersiebeheerOverzichtHtml(project);
        return html;
    }
    #softwareVerslag = [];

    Uitwisselingen() {
        return this.#uitwisselingen;
    }
    VoegUitwisselingToe(uitwisseling) {
        this.#uitwisselingen.push(uitwisseling);
    }
    #uitwisselingen = [];
    //#endregion

    //#region Statusoverzichten
    /**
     * Overzicht van de uitvoering van de laatste activiteit die voor het project
     * is uitgevoerd.
     * @param {Activiteit} naActiviteit - De activiteit die zojuist is uitgevoerd.
     * @param {Project} project - Project waarvan de status weergegeven moet worden.
     */
    ProjectActiviteitOverzichtHtml(naActiviteit, project) {
        let html = '';
        if (naActiviteit === this) {
            html += `<p><div class="entry_detail">Aan dit project is zojuist gewerkt.</div>De rol van deze activiteit in het scenario: ${this.Beschrijving().Html()}</p>`;
        } else {
            html += `<p class="entry_detail">Aan dit project is voor het laatst op ${this.Tijdstip().DatumTijdHtml()} gewerkt.</p>`;
        }
        return html;
    }
    /**
     * Weergave van de status van het versiebeheer, te tonen als onderdeel van ProjectstatusHtml.
     * @param {Project} - Project waarvan de status na deze activiteit weergegeven moet worden.
     *                    De activiteit wijzigt daadwerkelijk iets voor dit project.
     * @returns {string} - Html
     */
    VersiebeheerOverzichtHtml(project) {
        let momentopnamen = this.Momentopnamen().filter((mo) => mo.Branch().Project() === project);
        momentopnamen.sort((a, b) => Branch.Vergelijk(a.Branch(), b.Branch()));

        let html = '<div><b>Versie van de regelgeving</b></div>';
        if (this.UitgevoerdDoorAdviesbureau()) {
            html += '<div>(Wordt aan gewerkt door een adviesbureau)</div>';
        }
        html += '<table>';
        for (let mo of momentopnamen) {
            let soortToelichting = mo.Branch().InteractieToelichting();
            html += '<tr>';
            if (momentopnamen.length > 1) {
                soortToelichting = soortToelichting === undefined ? '' : `<br>(${soortToelichting})`;
                html += `<td>${mo.Branch().Interactienaam()}${soortToelichting}</td>`;
            }
            else if (soortToelichting !== undefined) {
                html += `<td>${soortToelichting}</td></tr><tr>`;
            }
            html += `<td>${mo.OverzichtHtml()}</td></tr>`;
        }
        html += '</table>';
        return html;
    }

    /**
     * Geef een overzicht van de status van het consolidatieproces na deze activiteit
     */
    Consolidatiestatus() {
        return this.#consolidatiestatus;
    }
    #consolidatiestatus = new Consolidatiestatus();

    /**
     * De wwergave van de status van het consolidatieproces
     * @returns
     */
    ConsolidatiestatusHtml() {
        if (this.Consolidatiestatus().Bepaald().length == 0) {
            return 'Consolidatie voltooid';
        }
        let html = `<table ${this.DataSet()}><tr><td>Inwerkingtreding</td><td>Status</td></tr>`;
        for (let bepaald of this.Consolidatiestatus().Bepaald()) {
            html += `<tr><td class="nw">${bepaald.IWTMoment().Datum().DatumTijdHtml()}</td><td class="nw">`;
            if (bepaald.IsVoltooid()) {
                html += 'Voltooid';
            } else {
                html += `Incompleet ${this.HtmlVoegToe("Voer consolidatie uit", 'VC')}`;
            }
            html += '</td></tr>';
        }
        html += '</table>';
        return html;
    }

    /**
     * Geef een overzicht van de status van het consolidatieproces voorafgaand aan deze activiteit
     */
    VoorgaandeConsolidatiestatus() {
        let activiteiten = Activiteit.Activiteiten(this.Tijdstip());
        if (activiteiten.length == 1) {
            // De laatste activiteit is deze activiteit
            return BGProcesSimulator.This().Uitgangssituatie().Consolidatiestatus();
        }
        else {
            return activiteiten[activiteiten.length - 2].Consolidatiestatus();
        }
    }

    /**
     * Geef een overzicht van de status van de besluiten na deze activiteit
     */
    BesluitStatus() {
        return { Html: () => 'TODO' };
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return ``;
    }

    InvoerInnerHtml() {
        return '';
    }

    /**
     * Aangeroepen als er op een element geklikt wordt in de weergave-html. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix === 'VC') {
            // TODO: oplossen consolidatie
        }
    }

    /**
     * Aangeroepen als er iets in de invoer is gewijzigd. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is; weggelaten als kind-specificatie-element gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnInvoerChange(elt, idSuffix) {
    }

    /**
     * Aangeroepen als er in de invoer geklikt wordt. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnInvoerClick(elt, idSuffix) {
    }

    /**
     * Aangeroepen vlak voordat het modal scherm getoond wordt: prepareer het specificatie-element voor
     * de invoer van een nieuwe waarde.
     */
    BeginInvoer() {
        return true;
    }

    /**
     * Aangeroepen vlak voordat het modal scherm gesloten wordt: verwerk de gewijzigde invoer.
     * @param {boolean} accepteerInvoer - Geeft aan of de invoer geaccepteerd (ipv geannuleerd) wordt.
     * @returns {boolean} Geeft aan of de invoer nog niet beëindigd kan worden. Bij true wordt het modal scherm niet gesloten.
     */
    EindeInvoer(accepteerInvoer) {
        return false;
    }
    //#endregion
}
//#endregion

//#region Implementatie van de activiteiten

//#region MaakBranch / MaakProject

class Activiteit_MaakBranch extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {Project} project - Naam van het project waar de activiteit bijhoort (als het om een projectactiviteit gaat)
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(project, specificatie) {
        super(project, specificatie);
    }
    //#endregion

    //#region Implementatie van de activiteit
    LeesMomentopnameSpecificaties(branchnamen) {

        // Maak een lijst van alle bekende branches
        let alleBranches = {};
        for (let branch of Branch.Branches(this.Tijdstip())) {
            alleBranches[branch.Naam()] = branch;
        }

        // Controleer op dubbele namen
        let nogAanmaken = branchnamen;
        let nogSteedsAanmaken = [];
        branchnamen = [];
        for (let branchnaam of nogAanmaken) {
            if (branchnaam in alleBranches) {
                BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `branch '${branchnaam}' bestaat al`);
            } else {
                nogSteedsAanmaken.push(branchnaam);
            }
        }

        // Maak eerst de branches aan op basis van de geldende regelgeving
        nogAanmaken = nogSteedsAanmaken;
        nogSteedsAanmaken = [];
        for (let branchnaam of nogAanmaken) {
            if (this.Specificatie()[branchnaam].Soort === Branch.Soort_GeldendeRegelgeving) {
                alleBranches[branchnaam] = new Branch(this, branchnaam);
                branchnamen.push(branchnaam);
            } else {
                nogSteedsAanmaken.push(branchnaam);
            }
        }

        while (nogSteedsAanmaken.length > 0) {
            nogAanmaken = nogSteedsAanmaken;
            nogSteedsAanmaken = [];
            let isGemaakt = false;

            // Vervolgens branches gebaseerd op andere branches
            for (let branchnaam of nogAanmaken) {
                if (this.Specificatie()[branchnaam].Soort === Branch.Soort_VolgtOpAndereBranch) {
                    let andereBranchnaam = this.Specificatie()[branchnaam].Branch;
                    if (andereBranchnaam === undefined) {
                        BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `Branch='${andereBranchnaam}' van branch '${branchnaam}' ontbreekt`);
                    } else if (andereBranchnaam in alleBranches) {
                        alleBranches[branchnaam] = new Branch(this, branchnaam, alleBranches[andereBranchnaam]);
                        branchnamen.push(branchnaam);
                        isGemaakt = true
                    } else {
                        BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `branch '${andereBranchNaam}' als basis voor branch '${branchnaam}' bestaat (nog) niet`);
                    }
                } else {
                    nogSteedsAanmaken.push(branchnaam);
                }
            }
            if (isGemaakt) {
                // Probeer eerst alle van de voorgaande soort aan te maken
                continue;
            }
            nogAanmaken = nogSteedsAanmaken;
            nogSteedsAanmaken = [];

            // Tot slot de samenloop-oplossingen
            for (let branchnaam of nogAanmaken) {
                if (this.Specificatie()[branchnaam].Soort === Branch.Soort_OplossingSamenloop) {
                    let andereBranchnamen = this.Specificatie()[branchnaam].Branches;
                    if (andereBranchnamen === undefined) {
                        BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `Branches ontbreekt in branch '${branchnaam}'"`);
                    } else {
                        let andereBranches = [];
                        let branchDitProject;
                        let ok = true;
                        for (let andereBranchNaam of andereBranchnamen) {
                            let andereBranch = alleBranches[andereBranchNaam];
                            if (andereBranch === undefined) {
                                BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `branch '${andereBranchNaam}' als basis voor branch '${branchnaam}' bestaat (nog) niet`);
                                ok = false;
                            } else {
                                andereBranches.push(andereBranch);
                                if (branchDitProject === undefined) {
                                    branchDitProject = andereBranch;
                                    if (branchDitProject.Project() !== this.Project()) {
                                        BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `branch '${andereBranchNaam}' als basis voor branch '${branchnaam}' moet bij hetzelfde project horen`);
                                    }
                                }
                            }
                        }
                        if (ok) {
                            alleBranches[branchnaam] = new Branch(this, branchnaam, andereBranches);
                            branchnamen.push(branchnaam);
                            isGemaakt = true;
                        }
                    }
                } else {
                    nogSteedsAanmaken.push(branchnaam);
                }
            }
            if (!isGemaakt) {
                BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `branches '${nogSteedsAanmaken.join("', '")}' kunnen niet aangemaakt worden`);
                break;
            }
        }
        // Lees nu de branches in
        super.LeesMomentopnameSpecificaties(branchnamen);
    }
    //#endregion
}

class Activiteit_MaakProject extends Activiteit_MaakBranch {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {Project} project - Naam van het project waar de activiteit bijhoort (als het om een projectactiviteit gaat)
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(project, specificatie) {
        super(project, specificatie);
    }
    //#endregion

    //#region Implementatie van de activiteit
    Naam() {
        return "Maak project";
    }
    //#endregion
}


//#endregion

//#region Download en Uitwisseling

class Adviesbureau_Branch extends Branch {

    constructor(activiteit, naam) {
        super(activiteit, naam);
    }

    Soort() {
        return Branch.Soort_GeldendeRegelgeving;
    }
}

class Activiteit_Download extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {Project} project - Naam van het project waar de activiteit bijhoort (als het om een projectactiviteit gaat)
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(project, specificatie) {
        super(project, specificatie);
        this.VoegUitwisselingToe(undefined); // TODO
    }
    //#endregion

    //#region Implementatie van de activiteit
    UitgevoerdDoorAdviesbureau() {
        return true;
    }

    LeesMomentopnameSpecificaties(branchnamen) {
        // Maak de nieuwe branch
        let branchnaam = this.Specificatie()['Branch'];
        if (branchnaam === undefined) {
            BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `Branch ontbreekt`);
        } else if (Branch.Branch(branchnaam) !== undefined) {
            BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `branch '${branchnaam}' bestaat al`);
        } else {
            new Adviesbureau_Branch(this, branchnaam);
        }
        // Lees nu de branches in
        super.LeesMomentopnameSpecificaties([branchnaam]);
    }

    PasSpecificatieToe() {
        for (let mo of this.Momentopnamen()) {
            // Zou maar om één momentopname moeten gaan...
            mo.UitgevoerdDoorAdviesbureauWordt(true);
        }
    }
    //#endregion
}

class Activiteit_Uitwisseling extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {Project} project - Naam van het project waar de activiteit bijhoort (als het om een projectactiviteit gaat)
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(project, specificatie) {
        super(project, specificatie);
        this.VoegUitwisselingToe(undefined); // TODO
    }
    //#endregion

    //#region Implementatie van de activiteit

    Naam() {
        if (this.#ontvangenDoorAdviesbureau) {
            return "Levering aan adviesbureau";
        } else {
            return "Levering aan bevoegd gezag";
        }
    }

    UitgevoerdDoorAdviesbureau() {
        return !this.#ontvangenDoorAdviesbureau;
    }
    #ontvangenDoorAdviesbureau;

    PasSpecificatieToe() {
        if (this.Momentopnamen().length !== 1) {
            BGProcesSimulator.SpecificatieMelding(this.Tijdstip(), `Een uitwisseling kan alleen gedaan worden voor een project met één branch.`);
        }
        for (let mo of this.Momentopnamen()) {
            this.#ontvangenDoorAdviesbureau = !mo.UitgevoerdDoorAdviesbureau();
            mo.UitgevoerdDoorAdviesbureauWordt(this.#ontvangenDoorAdviesbureau);
        }
    }
    //#endregion
}

//#endregion

//#region Bijwerken uitgangssituatie

class Activiteit_BijwerkenUitgangssituatie extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {Project} project - Naam van het project waar de activiteit bijhoort (als het om een projectactiviteit gaat)
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(project, specificatie) {
        super(project, specificatie);
    }
    //#endregion

    //#region Implementatie van de activiteit

    LeesMomentopnameSpecificaties(branchnamen) {
        for (let branch of Branch.Branches(this.Tijdstip(), this.Project())) {
            new Momentopname(this, this.Specificatie(), branch, this.Soort().MomentopnameTijdstempels, true);
        }
    }
    //#endregion
}



//#endregion

//#region Ontwerp- en vaststellingsbesluit

class Activiteit_Ontwerpbesluit extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {Project} project - Naam van het project waar de activiteit bijhoort (als het om een projectactiviteit gaat)
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(project, specificatie) {
        super(project, specificatie);
        this.VoegUitwisselingToe(undefined); // TODO
    }
    //#endregion

    //#region Implementatie van de Activiteit
    Publicatiebron() {
        return 'het ontwerpbesluit';
    }
    //#endregion
}

class Activiteit_Vaststellingsbesluit extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {Project} project - Naam van het project waar de activiteit bijhoort (als het om een projectactiviteit gaat)
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(project, specificatie) {
        super(project, specificatie);
        this.#isConcept = this.Naam() === 'Concept-vaststellingsbesluit';
        if (!this.#isConcept) {
            this.VoegUitwisselingToe(undefined); // TODO
        }
    }
    //#endregion

    //#region Implementatie van de Activiteit
    Publicatiebron() {
        return `het ${(this.#isConcept ? 'concept-' : '')}${this.#publicatiebron}`;
    }
    #publicatiebron = 'vaststellingsbesluit';
    #isConcept;

    PasSpecificatieToe() {
        // De inhoud van alle branches is nu vastgesteld.
        // Althans in deze applicatie, waarin het niet mogelijk is 
        // branches in aparte besluiten onder te brengen
        for (let mo of this.Momentopnamen()) {
            mo.IsOnderdeelVanPublicatieVastgesteldeInhoudWordt();
        }

        // Voor weergave: kan de naam van het besluit accurater?
        // Kijk of er al eerder een vaststellingsbesluit is geweest
        let eerderBesluit;
        for (let activiteit of Activiteit.Activiteiten(this.Tijdstip(), this.Project())) {
            if (activiteit != this && activiteit instanceof Activiteit_Vaststellingsbesluit) {
                eerderBesluit = activiteit;
            }
        }
        if (eerderBesluit !== undefined) {
            this.#publicatiebron = 'vervolgbesluit';
            for (let mo of this.Momentopnamen()) {
                if (mo.IsInwerkingtredingToegevoegd()) {
                    this.#publicatiebron = 'inwerkingtredingsbesluit';
                    break;
                }
            }
        }
    }

    //#endregion
}

//#endregion

//#endregion

