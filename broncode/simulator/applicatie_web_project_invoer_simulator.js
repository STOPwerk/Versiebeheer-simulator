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
 *============================================================================*/

//#region Simulator applicatie
/*==============================================================================
 *
 * BGProcesSimulator - Leest een bg_proces.json specificatie voor de simulator,
 * en bevat de algehele aansturing van de simulator.
 * 
 *------------------------------------------------------------------------------
 * De applicatie werkt als volgt:
 * - Een BGProcesSimulator instantie wordt aangemaakt en eventuele specificatie 
 *   wordt ingelezen.
 * - BGProcesSimulator maakt de opzet van de UI en vangt events af.
 * - Een gebruiker (scenari-schrijver) kan iets aan het scenario wijzigen.
 *   De invoer wordt direct vastgelegd in de specificatie van het scenario.
 * - Als de invoer de uitgangssituatie of een activiteit betreft: alle in-memory
 *   objecten daarvoor en voor latere activiteiten worden verwijderd en vanuit
 *   de specificatie opnieuw aangemaakt.
 * - De UI wordt ververst.
 * 
 *============================================================================*/
class BGProcesSimulator {

    //#region Initialisatie en start van applicatie
    /*--------------------------------------------------------------------------
     *
     * Initialisatie van de generator
     *
     -------------------------------------------------------------------------*/
    /**
     * Maak de generator aan
     * @param {HTMLElement} elt_simulator - Element waarin de simulator getoond wordt
     * @param {string} soortBG - Soort van het bevoegd gezag
     */
    constructor(elt_simulator, soortBG) {
        BGProcesSimulator.#This = this;
        this.#elt_simulator = elt_simulator;
        this.#data.BevoegdGezag = soortBG;
        this.#data.BGCode = soortBG == BGProcesSimulator.SoortBG_Gemeente ? "gm9999" : "mnre9999";
        this.#data.Naam = this.#MaakValideTitel();
    }
    #elt_simulator;

    /**
     * Maak een nieuwe specificatie op basis van het type bevoegd gezag
     * @param {HTMLElement} elt_simulator - Element waarin de simulator getoond wordt
     * @param {string} soortBG - Gemeente of Rijk
     * @returns De generator voor het bevoegd gezag
     */
    static Selecteer(elt_simulator, soortBG) {
        return new BGProcesSimulator(elt_simulator, soortBG);
    }

    /*--------------------------------------------------------------------------
     *
     * Maken van de invoerpagina
     *
     -------------------------------------------------------------------------*/
    /**
     * Start met de invoer van de specificatie
     * @param {HTMLElement} elt_lvbb_form - form om de specificatie voor de LVBB simulator in op te nemen
     * @param {HTMLElement} elt_lvbb_startknop - element waarin de start knop staat van de LVBB simulator
     * @param {HTMLAnchorElement} elt_lvbb_download - element met de downloadlink voor de invoerbestanden van de LVBB simulator
     * @param {HTMLAnchorElement} elt_spec_download - element met de downloadlink voor de specificatie
     */
    Start(elt_lvbb_form, elt_lvbb_startknop, elt_lvbb_download, elt_spec_download) {
        SpecificatieElement.AddEventListener(this.#elt_simulator)
        this.#elt_lvbb_form = elt_lvbb_form;
        this.#elt_lvbb_startknop = elt_lvbb_startknop;
        this.#elt_lvbb_download = elt_lvbb_download;
        this.#elt_spec_download = elt_spec_download;

        // Maak de eerste versie van de pagina.
        this.#MaakPagina();
    }
    //#endregion

    //#region Constanten
    static SoortBG_Gemeente = 'Gemeente';
    static SoortBG_Rijksoverheid = 'Rijksoverheid';
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
        SpecificatieVersie: '2023-06',
        start: {},
        Activiteiten: []
    };

    /**
     * Geeft het soort bevoegd gezag dat gesimuleerd wordt.
     * @returns {string}
     */
    BevoegdGezag() {
        return this.#data.BevoegdGezag;
    }

    /**
     * Geeft de unieke code voor het bevoegd gezag dat gesimuleerd wordt.
     * @returns {string}
     */
    BGCode() {
        return this.#data.BGCode;
    }

    /**
     * Geeft de naam van het scenario
     * @returns {string}
     */
    Naam() {
        return this.#data.Naam;
    }

    /**
     * Geeft de beschrijving van het scenario
     * @returns {string}
     */
    Beschrijving() {
        return this.#data.Beschrijving;
    }

    Startdatum() {
        return this.#startdatum.Datum();
    }
    #startdatum;

    /**
     * De uitgangssituatie van het scenario
     */
    Uitgangssituatie() {
        return this.#uitgangssituatie;
    }
    #uitgangssituatie;

    /**
     * Verzamelbak voor singletons voor andere klassen
     * @param {string} naam - Naam van de singleton; weglaten om alle singletons te zien
     * @param {string} defaultWaarde - Optioneel; default waarde van de singleton in het geval die nog niet bestaat
     */
    static Singletons(naam, defaultWaarde) {
        if (naam === undefined) {
            return BGProcesSimulator.#This.#singletons;
        } else {
            let data = BGProcesSimulator.#This.#singletons[naam];
            if (data === undefined) {
                BGProcesSimulator.#This.#singletons[naam] = data = defaultWaarde;
            }
            return data;
        }
    }
    #singletons = {};
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
        let simulator = undefined;
        let data = JSON.parse(json);
        if (data.BevoegdGezag) {
            if (data.BevoegdGezag === BGProcesSimulator.SoortBG_Gemeente || data.BevoegdGezag === BGProcesSimulator.SoortBG_Rijksoverheid) {
                simulator = new BGProcesSimulator(elt_invoer, data.BevoegdGezag);
            }
            else {
                throw new Error('Invalide specificatie - onbekend bevoegd gezag');
            }
        } else {
            throw new Error('Invalide specificatie - bevoegd gezag ontbreekt');
        }
        if (data.BGCode) {
            simulator.#data.BGCode = data.BGCode;
        }
        if (data.Naam !== undefined) {
            simulator.#data.Naam = data.Naam;
        }
        if (data.Beschrijving !== undefined) {
            simulator.#data.Beschrijving = data.Beschrijving;
        }
        if (data.Startdatum !== undefined) {
            simulator.#data.Startdatum = data.Startdatum;
        }
        new Startdatum(simulator.#data);

        let regelingen = {};
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
                                                //`Onbekende wijziging specificatie genegeerd voor non-STOP annotatie "${ns}" van ${onderdeel}, instrument ${instr}.`
                                            }
                                        }
                                        if (Object.keys(valide).length > 0) {
                                            BGProcesSimulator.Opties.NonStopAnnotaties = true;
                                            target[instr][annotatie] = valide;
                                        }
                                    } else {
                                        //`Onbekende wijziging specificatie genegeerd voor non-STOP annotaties van ${onderdeel}, instrument ${instr}.`
                                    }
                                } else if (annotatie == Annotatie.SoortAnnotatie_Citeertitel) {
                                    // Toegestaan: "..."
                                    if (typeof value === 'string') {
                                        BGProcesSimulator.Opties.Annotaties = true;
                                        target[instr][annotatie] = value;
                                    } else {
                                        //`Onbekende specificatie genegeerd voor STOP annotatie ${annotatie} van ${onderdeel}, instrument ${instr}.`
                                    }
                                } else {
                                    // Toegestaan: true | false
                                    if (typeof value === 'boolean') {
                                        BGProcesSimulator.Opties.Annotaties = true;
                                        target[instr][annotatie] = value;
                                    } else {
                                        //`Onbekende specificatie genegeerd voor STOP annotatie ${annotatie} van ${onderdeel}, instrument ${instr}.`
                                    }
                                }
                            }
                        }
                        for (let prop in src[instr]) {
                            if (!herkend.includes(prop)) {
                                //`Onbekende eigenschap "${prop}" genegeerd van ${onderdeel}, instrument ${instr}.`
                            }
                        }
                    }
                }
                else {
                    //`Onbekende eigenschap "${instr}" genegeerd van ${onderdeel}.`
                }
            }
        }

        let tijdstippen = [];
        function copyActiviteiten(project, target, src) {
            for (let activiteit of src) {
                if (activiteit.Soort === undefined) {
                    throw new Error('Elke activiteit moet een eigenschap "Soort" hebben.')
                }
                let spec = MogelijkeActiviteit.SoortActiviteit[activiteit.Soort];
                if (spec === undefined) {
                    throw new Error(`Onbekende activiteit: "Soort": "${activiteit.Soort}".`)
                }
                if (activiteit.Tijdstip === undefined) {
                    throw new Error(`Elke activiteit moet een eigenschap "Tijdstip" hebben ("Soort": "${activiteit.Soort}").`)
                }
                let tijdstip = new Tijdstip(undefined, { Tijdstip: activiteit.Tijdstip }, 'Tijdstip', true);
                if (tijdstippen.includes(tijdstip.Specificatie())) {
                    throw new Error(`Elk "Tijdstip" moet een unieke waarde hebben ("Tijdstip": ${activiteit.Tijdstip}).`)
                }

                let targetActiviteit = {};
                target.push(targetActiviteit);
                for (let prop in activiteit) {
                    if (['Soort', 'Tijdstip', 'Beschrijving', 'Project'].includes(prop) || spec.Props.includes(prop)) {
                        targetActiviteit[prop] = activiteit[prop];
                    } else if (spec.IsWijziging) {
                        // Moet een branch zijn
                        targetActiviteit[prop] = {};
                        let mprops = spec.MomentopnameTijdstempels ? ['JuridischWerkendVanaf', 'GeldigVanaf'] : [];
                        mprops.push(...spec.MomentopnameProps);
                        copyWijziging(tijdstip, `activiteit "${activiteit.Soort}", branch "${prop}"`, targetActiviteit[prop], activiteit[prop], mprops);
                    } else {
                        // Geen branch maar iets anders
                        targetActiviteit[prop] = activiteit[prop];
                    }
                }
            }
        }

        copyWijziging(new Tijdstip(undefined, Tijdstip.StartTijd(), 'Tijdstip', false), 'Uitgangssituatie', simulator.#data.Uitgangssituatie, data.Uitgangssituatie, []);
        if (data.Activiteiten !== undefined) {
            copyActiviteiten(project, simulator.#data.Activiteiten, data.Activiteiten);
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
        simulator.#singletons = {};

        simulator.#MaakValideTitel(simulator.#data.Naam, true);

        // Maak het interne datamodel aan
        simulator.#VertaalSpecificatie();
        return simulator;
    }

    /**
     * Maak de JSON specificatie
     */
    #MaakSpecificatie() {
        if (this.Specificatie().Beschrijving || this.Uitgangssituatie().Instrumentversies().length > 0 || this.Specificatie().Activiteiten.length > 0) {
            this.Specificatie().Activiteiten.sort((x, y) => x.Tijdstip - y.Tijdstip);
            return JSON.stringify(this.Specificatie(), BGProcesSimulator.#ObjectFilter, 4).trim();
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

    #MaakValideTitel(titel, isNieuweVersie) {
        if (titel === undefined || titel.length === 0) {
            titel = `Scenario voor ${this.#data.BevoegdGezag === BGProcesSimulator.SoortBG_Gemeente ? "een gemeente" : "de rijksoverheid"}`;
        }
        if (isNieuweVersie) {
            document.title = 'Simulator - ' + titel;
        }
        return titel;
    }
    //#endregion

    //#region Van specificatie naar intern datamodel
    /**
     * Gebruik de ingelezen of ingevoerde specificatie om het interne datamodel
     * bij te werken dat voor elk tijdstip de actuele stand van zaken beschrijft.
     * @param {float} tijdstip - Tijdstip waarop de activiteit is uitgevoerd die zojuist is aangemaakt/gewijzigd/verwijderd.
     */
    WerkScenarioUit(tijdstip) {
        // Maak een kopie van de activiteitspecificaties en verwijder alle activiteiten
        // vanaf (en inclusief) de gewijzigdeActiviteit uit het interne datamodel
        this.#data.Activiteiten.sort((x, y) => x.Tijdstip - y.Tijdstip);
        let activiteitSpecificatie = [...this.#data.Activiteiten.filter(spec => spec.Tijdstip >= tijdstip)];

        for (let activiteit of [...Activiteit.Activiteiten().filter(act => act.Tijdstip().Specificatie() >= tijdstip)]) {
            activiteit.Verwijder();
        }

        // Vertaal de activiteiten opnieuw naar het interne datamodel
        this.#VertaalActiviteiten(tijdstip === 0, activiteitSpecificatie);

        // Ververs de UI
        if (tijdstip !== 0) {
            this.#huidigeActiviteit = undefined;
            this.#huidigeActiviteitTijdstip = tijdstip;
        }
        this.#ToonGewijzigdScenario();
    }

    /**
     * Zet de ingelezen specificatie om naar het interne datamodel
     * dat voor elk tijdstip de actuele stand van zaken beschrijft.
     */
    #VertaalSpecificatie() {
        this.#startdatum = new Startdatum(this.#data);

        // Maak de uitgangssituatie aan
        this.#uitgangssituatie = new Uitgangssituatie(this.#data);
        let voorgaandeConsolidatie = this.#uitgangssituatie.Consolidatiestatus();
        if (voorgaandeConsolidatie !== undefined) {
            voorgaandeConsolidatie.WerkBij(undefined, this.#uitgangssituatie);
        }

        // Verwijder de specificatie van de activiteiten
        this.#data.Activiteiten.sort((x, y) => x.Tijdstip - y.Tijdstip);
        let activiteitSpecificatie = [...this.#data.Activiteiten]
        this.#data.Activiteiten = [];
        // Vertaal de activiteiten
        this.#VertaalActiviteiten(true, activiteitSpecificatie);
    }

    /**
     * Gebruik de ingelezen of ingevoerde specificatie om het interne datamodel
     * bij te werken dat voor elk tijdstip de actuele stand van zaken beschrijft.
     */
    #VertaalActiviteiten(werkUitgangssituatieBij, activiteitenSpecificatie) {
        // Vind de laatst beschikbare consolidatie
        let voorgaandeConsolidatie = this.#uitgangssituatie.Consolidatiestatus();
        if (werkUitgangssituatieBij) {
            // Uitgangssituatie is gewijzigd, bepaal de consolidatie opnieuw
            if (voorgaandeConsolidatie !== undefined) {
                voorgaandeConsolidatie.WerkBij(undefined, this.#uitgangssituatie);
            }
        } else {
            let activiteiten = Activiteit.Activiteiten();
            if (activiteiten.length > 0) {
                voorgaandeConsolidatie = activiteiten[activiteiten.length - 1].Consolidatiestatus();
            }
        }

        // Maak het interne datamodel voor activiteiten aan
        for (let activiteitSpecificatie of activiteitenSpecificatie) {
            let activiteit = Activiteit.LeesSpecificatie(activiteitSpecificatie);
            if (activiteit === undefined) {
                break;
            }
            activiteit.Consolidatiestatus().WerkBij(voorgaandeConsolidatie, activiteit);
            voorgaandeConsolidatie = activiteit.Consolidatiestatus();
        }
    }
    //#endregion

    //#region Specificatie voor LVBB simulator
    /**
     * Maak de specificatie voor de LVBB simulator
     */
    #MaakSimulatorSpecificatie() {
        let numBestanden = 0;
        let zipData = {}

        // Neem de STOP XML bestanden op in de form
        for (let activiteit of [this.#uitgangssituatie, ...Activiteit.Activiteiten()]) {
            for (let module of activiteit.ModulesVoorLVBBSimulator()) {
                let elt = this.#elt_lvbb_form.elements[`onlineInvoer${++numBestanden}`];
                if (elt === undefined || elt === null) {
                    elt = document.createElement('textarea');
                    elt.name = `onlineInvoer${numBestanden}`;
                    elt.classList.add('verborgenInvoer');
                    this.#elt_lvbb_form.appendChild(elt);
                }
                elt.value = module.STOPXml;
                zipData[`${numBestanden.toString().padStart(2, '0')}_${module.ModuleNaam}.xml`] = module.STOPXml;
            }
        }

        let beschrijving = {
            Beschrijving: this.#data.Beschrijving,
            Uitwisselingen: []
        };
        for (let activiteit of Activiteit.Activiteiten()) {
            if (activiteit.HeeftUitwisselingen() && activiteit.Publicatiebron() !== undefined) {
                beschrijving.Uitwisselingen.push({
                    naam: `${activiteit.Project().Naam()}: ${activiteit.Naam()}`,
                    gemaaktOp: activiteit.Tijdstip().STOPDatumTijd(),
                    beschrijving: activiteit.Specificatie().Beschrijving,
                    revisie: activiteit.Publicatiebron().endsWith('revisie')
                });
            }
            if (this.Uitgangssituatie().Instrumentversies().length > 0) {
                beschrijving.Uitwisselingen.push({
                    naam: 'Uitgangssituatie',
                    gemaaktOp: this.Uitgangssituatie().Tijdstip().STOPDatumTijd(),
                    beschrijving: 'De regelgeving die in werking is bij de start van het scenario.',
                    revisie: true
                });
            }
        }
        let json = JSON.stringify(beschrijving, BGProcesSimulator.#ObjectFilter, 4).trim();
        if (json !== '{}') {
            let elt = this.#elt_lvbb_form.elements[`onlineInvoer${++numBestanden}`];
            if (elt === undefined || elt === null) {
                elt = document.createElement('textarea');
                elt.name = `onlineInvoer${numBestanden}`;
                elt.classList.add('verborgenInvoer');
                this.#elt_lvbb_form.appendChild(elt);
            }
            elt.value = json;
            zipData['00_beschrijving.json'] = json;
        }

        // Haal overige form-velden voor bestanden weg
        while (true) {
            let elt = this.#elt_lvbb_form.elements[`onlineInvoer${++numBestanden}`];
            if (elt === undefined || elt === null) {
                break;
            }
            elt.parentNode.removeChild(elt);
        }

        // Neem de zip file op in de download link
        this.#CreateZip(zipData);
    }
    #elt_lvbb_form;

    async #CreateZip(zipData) {
        this.#elt_lvbb_download.href = "#";
        const zipWriter = new zip.ZipWriter(new zip.Data64URIWriter("application/zip"));
        for (let file in zipData) {
            await zipWriter.add(file, new zip.TextReader(zipData[file]));
        }
        this.#elt_lvbb_download.href = await zipWriter.close();
    }
    #elt_lvbb_download;
    //#endregion

    //#region Webpagina voor applicatie
    #MaakPagina() {
        this.#nieuweactiviteit = new NieuweActiviteit();

        let html = `
<div id="_bgps_modal" class="modal">
  <div class="modal-content">
    <span class="modal-close"><span id="_bgps_modal_volgende">&#x276F;&#x276F;</span> <span id="_bgps_modal_ok">&#x2714;</span> <span id="_bgps_modal_cancel">&#x2716;</span></span>
    <p id="_bgps_modal_content"></p>
  </div>
</div>
<button data-accordion="_bgps_s1" class="accordion_h active">Over het scenario</button>
<div data-accordion-paneel="_bgps_s1" class="accordion_h_paneel" style = "display: block">
<p>
<b>Naam/titel van het scenario</b><br>
${new Naam(this.Specificatie(), undefined, (n, a) => this.#MaakValideTitel(n, a)).Html()}
</p>
<p>
<b>Beschrijving van het scenario</b><br>
Geef een korte beschrijving van het scenario waarvoor deze specificatie is opgesteld (optioneel)
${new Beschrijving(this.#data).Html('div')}
</p>
<p>
<b>Uitgangssituatie</b> per ${this.#startdatum.Html()}<br>
${this.#uitgangssituatie.Html()}
</p>
</div>
<button data-accordion="_bgps_s2" class="accordion_h active"><h3>Simulatie - User interface</h3></button>
<div data-accordion-paneel="_bgps_s2" class="accordion_h_paneel" style = "display: block" data-bh="0">
<table>
    <tr><td rowspan="2" class="nw" id="_bgps_activiteiten"></td>
    <th id="_bgps_projecten" style="height: 1px" ></th>
    <th rowspan="2"></th>
    <th></th>
    </tr>
    <tr>
        <td class="w100" id="_bgps_activiteit_detail"></td>
        <td rowspan="2" id="_bgps_tijdstip_detail">
            <table>
                <tr><th style="height: 1px" class="nw">Status consolidatie</th></tr>
                <tr><td class="nw" style="height: 1px" id="_bgps_consolidatie_status">TODO</td></tr>
                <tr><th class="nw" style="height: 1px">Status besluiten</th></tr>
                <tr><td class="nw" id="_bgps_besluit_status">TODO</td></tr>
            </table>
        </td>
    </tr>
</table>
</div>
<div id="_bgps_intern">
<button data-accordion="_bgps_s3" class="accordion_h active"><h3>Simulatie - Software intern</h3></button>
<div data-accordion-paneel="_bgps_s3" class="accordion_h_paneel" style = "display: block" data-bh="0">
<div id="_bgps_software">
TODO
</div>
</div>
</div>
<div id="_bgps_stop">
<button data-accordion="_bgps_s4" class="accordion_h active"><h3>Simulatie - Uitwisseling via STOP</h3></button>
<div data-accordion-paneel="_bgps_s4" class="accordion_h_paneel" style = "display: block">
<table class="w100" style="table-layout: fixed">
    <tr><th class="c w50">Versiebeheer door de simulator</th><th class="c w50">Uitwisseling via STOP</th></tr>
    <tr>
        <td>
            <table>
                <tr><td class="nw" style="height: 1px; width: 1px;">${BGProcesSimulator.Symbool_Inhoud}</td><td>Wijziging van regeling/informatieobject</td></tr>
                <tr><td style="height: 1px">${BGProcesSimulator.Symbool_Tijdstempel}</td><td>Wijziging van inwerkingtreding</td></tr>
                <tr><td style="height: 1px">${BGProcesSimulator.Symbool_Uitwisseling}</td><td>Uitwisseling via STOP</td></tr>
            </table>
        </td>
        <td rowspan="2" id="_bgps_uitwisseling"></td>
    </tr>
    <tr>
        <td><div id="_bgps_versiebeheer"></div></td>
    </tr>
</table> 
</div>
</div>
`
        this.#elt_simulator.insertAdjacentHTML('beforeend', html);
        this.#ToonGewijzigdScenario();

        document.getElementById("_bgps_modal_volgende").addEventListener('click', () => SpecificatieElement.SluitModal(true));
        document.getElementById("_bgps_modal_ok").addEventListener('click', () => SpecificatieElement.SluitModal(true));
        document.getElementById("_bgps_modal_cancel").addEventListener('click', () => SpecificatieElement.SluitModal(false));
        window.dispatchEvent(new CustomEvent('init_accordion', {
            cancelable: true
        }));
    }

    /**
     * Aangeroepen als de specificatie wijzigt
     */
    #ToonGewijzigdScenario() {
        // Maak specificatie van dit scenario downloadbaar
        let json = this.#MaakSpecificatie();
        if (json !== undefined) {
            this.#elt_spec_download.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(json);
            this.#elt_spec_download.style.visibility = 'visible';
        } else {
            this.#elt_spec_download.href = '#';
            this.#elt_spec_download.style.visibility = 'hidden';
        }

        // Maak LVBB specificatie
        if (this.Specificatie().Activiteiten.length > 0) {
            this.#MaakSimulatorSpecificatie();
            this.#elt_lvbb_startknop.style.display = '';
            this.#elt_lvbb_download.style.display = '';
        } else {
            this.#elt_lvbb_startknop.style.display = 'none';
            this.#elt_lvbb_download.style.display = 'none';
        }

        // Software-interne informatie alleen laten zien als er activiteiten zijn
        if (this.Specificatie().Activiteiten.length > 0) {
            document.getElementById('_bgps_intern').style.display = '';
            document.getElementById('_bgps_stop').style.display = '';
        } else {
            document.getElementById('_bgps_intern').style.display = 'none';
            document.getElementById('_bgps_stop').style.display = 'none';
        }
        this.#MaakActiviteitenOverzicht();
    }
    #elt_spec_download;
    #elt_lvbb_startknop;

    #MaakActiviteitenOverzicht() {
        let activiteiten = Activiteit.Activiteiten();

        // Maak een lijst van projecten op volgorde van aanmaken
        let html = ''
        if (activiteiten.length > 0) {
            // Maak eerst de headers en tabs voor de projecten
            html += '<table class="activiteiten_overzicht"><tr><th colspan="3"></th><th colspan="5" class="c nw">Activiteiten eindgebruikers</th><th>&nbsp;&nbsp;&nbsp;</th></tr>';

            // Toon de activiteiten
            for (let activiteit of activiteiten) {
                let daguur = activiteit.Tijdstip().DagUurHtml();
                html += `<tr data-bga="${activiteit.Index()}"><td>${activiteit.HtmlWerkBij("Wijzig de activiteit", 'AM')}</td><td>${activiteit.KanVerwijderdWorden() ? ' ' + activiteit.HtmlVerwijder("Verwijder de activiteit", 'AD') : ''}</td><td>`;
                if (activiteit.HeeftSpecificatieMeldingen()) {
                    html += activiteit.HtmlWaarschuwing("De specificatie van de activiteit past niet meer in het scenario", 'AW');
                }
                html += `</td><td class="td0">Dag</td><td class="td1">${daguur[0]}</td><td class="tu">${daguur[1]}</td><td class="tz">${activiteit.Tijdstip().DatumTijdHtml()}</td>`;
                html += `<td class="nw">${activiteit.Naam()}</td><td class="ac"></td></tr>`;
            }
            html += '</table>';
        }
        html += this.#nieuweactiviteit.Html();
        document.getElementById('_bgps_activiteiten').innerHTML = html;
        new VersiebeheerDiagram('_bgps_versiebeheer').Teken();
        this.#LuisterNaarEvents();
        this.#SelecteerActiviteit(-1);
    }
    #nieuweactiviteit;

    #ToonActiviteit() {
        if (this.#huidigeActiviteit === undefined) {
            ['_bgps_projecten', '_bgps_consolidatie_status', '_bgps_software', '_bgps_uitwisseling'].forEach(eltNaam => {
                document.getElementById(eltNaam).innerHTML = '';
            });
        } else {
            let html = `<span class="p_tab${(this.#huidigProject === undefined ? ' huidige-prj' : '')} huidige-act" data-prj="*"">User interface</span>`;
            for (let project of Project.Projecten(this.#huidigeActiviteit.Tijdstip())) {
                html += `<span class="p_tab${(project === this.#huidigProject ? ' huidige-prj' : '')}${(this.#huidigeActiviteit !== undefined && this.#huidigeActiviteit.ToonInProject(project) ? ' huidige-act' : '')}" data-prj=${project.Index()}>${project.Naam()}</span>`;
            }
            document.getElementById('_bgps_projecten').innerHTML = html;

            // Update de consolidatie en besluitstatus
            document.getElementById('_bgps_consolidatie_status').innerHTML = this.#huidigeActiviteit.Consolidatiestatus().Html();

            // TODO besluitstatus

            // Update het verwerkingsverslag en de uitwisselingen
            document.getElementById('_bgps_software').innerHTML = this.#huidigeActiviteit.UitvoeringsverslagHtml();
            this.#huidigeActiviteit.ToonUitwisselingen('_bgps_uitwisseling');
        }

        // Werk de weergave bij
        ['_bgps_tijdstip_detail', '_bgps_activiteit_detail', '_bgps_software', '_bgps_uitwisseling'].forEach(eltNaam => {
            let elt_status = document.getElementById(eltNaam);
            if (elt_status !== null) {
                if (this.#huidigeActiviteit === undefined) {
                    elt_status.classList.remove('active');
                } else {
                    elt_status.classList.add('active');
                }
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
    #huidigeActiviteitTijdstip;

    /**
     * Toon het verslag van de uitvoering van de activiteit
     */
    #ToonActiviteitUitvoering() {
        let elt = document.getElementById('_bgps_activiteit_detail');
        if (this.#huidigeActiviteit === undefined) {
            elt.innerHTML = '';
        } else {
            elt.innerHTML = this.#huidigeActiviteit.Html();
        }
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
        let elt = document.getElementById('_bgps_activiteit_detail');
        if (voorActiviteit !== undefined) {
            elt.innerHTML = voorActiviteit.ProjectstatusHtml(this.#huidigeActiviteit, this.#huidigProject);
        } else {
            elt.innerHTML = '';
        }

        this.#ToonGerelateerdeActiviteitenProjecten(this.#huidigProject.Index())
    }
    #huidigProject;
    #huidigeProjectcode;

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
        let projectIndex;
        if (e.currentTarget.dataset.prj === "*") {
            projectIndex = -1;
        }
        else if (e.currentTarget.dataset.prj !== undefined) {
            projectIndex = parseInt(e.currentTarget.dataset.prj);
        }
        if (e.currentTarget.dataset.bga !== undefined) {
            BGProcesSimulator.This().#SelecteerActiviteit(parseInt(e.currentTarget.dataset.bga), projectIndex);
        }
        else if (projectIndex !== undefined) {
            BGProcesSimulator.This().#SelecteerProject(projectIndex);
        }
    }

    /**
     * Selecteer eerst de activiteit
     * @param {int} activiteitIndex - Index() van de activiteit
     * @param {int} projectIndex - Index() van het project
     */
    #SelecteerActiviteit(activiteitIndex, projectIndex) {
        // Zoek uit welke activiteit geselecteerd is
        let activiteit = this.#ActiviteitViaIndex(activiteitIndex);
        if (activiteit === undefined) {
            // Kunnen we de huidig geselecteerde activiteit blijven gebruiken?
            // Zo niet, kies dan degene die ervoor zit
            for (let act of Activiteit.Activiteiten()) {
                if (act.Tijdstip().Specificatie() <= this.#huidigeActiviteitTijdstip) {
                    activiteit = act;
                }
                else {
                    break;
                }
            }
        }
        this.#huidigeActiviteit = activiteit;
        this.#huidigeActiviteitTijdstip = activiteit === undefined ? 0 : activiteit.Tijdstip().Specificatie();

        // Zoek uit of het huidige project daarbij getoond kan worden
        let project = undefined;
        if (projectIndex === undefined) {
            if (this.#huidigeActiviteit !== undefined) {
                // Kijk of het geselecteerde project al bestaat op dit tijdstip
                if (this.#huidigeProjectcode !== undefined) {
                    project = Project.Project(this.#huidigeProjectcode);
                    if (project !== undefined) {
                        if (project.OntstaanIn().Tijdstip().Vergelijk(this.#huidigeActiviteit.Tijdstip()) > 0) {
                            // Project bestaat nog niet
                            project = undefined;
                        }
                    }
                }
            }
            this.#huidigProject = project;
            this.#huidigeProjectcode = project === undefined ? undefined : project.Code();
        }

        // Pas de UI aan
        this.#ToonActiviteit();
        if (projectIndex !== undefined) {
            this.#SelecteerProject(projectIndex);
        }
        else if (project === undefined) {
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
            for (let project of Project.Projecten(this.#huidigeActiviteit.Tijdstip())) {
                if (project.Index() === projectIndex) {
                    this.#huidigProject = project;
                    break;
                }
            }
        }
        if (this.#huidigProject === undefined) {
            this.#huidigeProjectcode = undefined;
            projectIndex = "*";
        } else {
            this.#huidigeProjectcode = this.#huidigProject.Code();
        }

        // Pas UI status aan
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
            let start = BGProcesSimulator.This().Uitgangssituatie();
            let wProject = this.#NaamBreedte;
            this.#Registreer(xProject, yProject, wProject, hProject);
            this.#svg += `<text x="${xProject + wProject / 2}" y="${yProject}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">${start.Branch().Project().Naam()}</text>
                          <path d="M ${xProject} ${yProject + hProject} L ${xProject + wProject} ${yProject + hProject}" class="bgvbd_naam_l"/>`;
            let xBranch = xProject;
            this.#Registreer(xBranch, yBranch, wBranch, hBranch);
            this.#svg += `<text x="${xBranch + wBranch / 2}" y="${yBranch}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">${start.Branch().Code()}</text>`;
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
                this.#svg += `<text x="${xBranch + wBranch / 2}" y="${yBranch}" data-prj="${project.Index()}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">${branch.Code()}</text>`;
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
                if (activiteit.HeeftUitwisselingen()) {
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
     * @param {any} defaultData - Specificatie voor het object, te gebruiken als data undefined is en er ook geen specificatie in het eigenaarObject zit.
     */
    constructor(eigenaarObject, eigenschap, data, superInvoer, defaultData) {
        this.#index = SpecificatieElement.#element_idx++;
        BGProcesSimulator.Singletons('Elementen', {})[this.#index] = this;
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
            if (this.#data === undefined && defaultData !== undefined) {
                this.#WerkSpecificatieBij(defaultData);
            }
        }
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
     * Aangeroepen als er op een element geklikt wordt in de weergave-html. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnWeergaveClick(elt, idSuffix) {
    }

    /**
     * Aangeroepen vlak voordat het modal scherm getoond wordt: prepareer het specificatie-element voor
     * de invoer van een nieuwe waarde.
     */
    BeginInvoer() {
        return true;
    }

    /**
     * Aangeroepen om de HTML voor de invoer te maken, zoals die voorkomt in het modal invoerscherm,
     * binnen de container die door InvoerHtml wordt klaargezet.
     * Als al bekend is dat er een volgende stap in de invoer nodig is, dan moet in deze methode 
     * of in InvoerIntroductie de VolgendeStapNodig methode aangeroepen worden.
     * Wordt geïmplementeerd in afgeleide klassen.
     */
    InvoerInnerHtml() {
        return this.WeergaveInnerHtml();
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
    static #element_idx = 0; // Absolute waarde is niet relevant

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
     * @returns {boolean}
     */
    IsReadOnly() {
        return this.#isReadOnly;
    }
    /**
     * Geef aan dat dit element niet gewijzigd mag worden
     * @param {boolean} readOnly
     */
    ReadOnlyWordt(readOnly) {
        this.#isReadOnly = readOnly;
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
        let id = `_bgps_${this.#index}_${(this.IsInvoer() ? 'I' : 'W')}`;
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
    /**
     * Maakt de HTML voor een waarschuwingsicoon aan
     * @param {string} hint - Mouseover hint voor het icoon
     * @param {string} idSuffix - Suffix voor de identificatie van het icoon
     * @param {string} extraAttributen - Extra attributen voor het icoon
     */
    HtmlWaarschuwing(hint, idSuffix, extraAttributen) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} ${(extraAttributen === undefined ? '' : extraAttributen)} class="specmelding">&#x26A0;</span>`;
    }
    //#endregion

    //#region Openen van modal invoerscherm
    /**
     * Open een modal invoer scherm voor de invoer van de gegevens waarvoor dit specificatie-element opgezet is.
     */
    OpenModal() {
        if (BGProcesSimulator.Singletons('UI', {}).ModalOpener !== undefined) {
            throw Error("Programmeerfout: modal scherm is al open!");
        }
        BGProcesSimulator.Singletons('UI').ModalOpener = this;
        this.#invoerStap = 1;
        this.#volgendeStapNodig = false;
        this.#ModalMode(true);
        document.getElementById('_bgps_modal_content').innerHTML = this.Html();
        document.getElementById("_bgps_modal_volgende").style.display = this.#volgendeStapNodig ? '' : 'none';
        document.getElementById("_bgps_modal_ok").style.display = this.#volgendeStapNodig ? 'none' : '';
        document.getElementById('_bgps_modal').style.display = 'block';
    }

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
        if (BGProcesSimulator.Singletons('UI').ModalOpener !== undefined) {
            document.getElementById("_bgps_modal_volgende").style.display = BGProcesSimulator.Singletons('UI').ModalOpener.#volgendeStapNodig ? '' : 'none';
            document.getElementById("_bgps_modal_ok").style.display = BGProcesSimulator.Singletons('UI').ModalOpener.#volgendeStapNodig ? 'none' : '';
        }
    }

    /**
     * Geeft aan dat een volgende stap nodig is voor de invoer
     */
    VolgendeStapNodig() {
        BGProcesSimulator.Singletons('UI').ModalOpener.#volgendeStapNodig = true;
    }
    #volgendeStapNodig;
    //#endregion

    //#region Interne functionaliteit: specificatie/verwijderen
    /**
     * Verwijder het element uit de specificatie met alle gerelateerde specificatie-elementen.
     */
    Verwijder() {
        this.#WerkSpecificatieBij(undefined);
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
                        this.#eigenaarObject.splice(idx, 1);
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
        for (let gewijzigd = true; gewijzigd && Object.keys(BGProcesSimulator.Singletons('Elementen', {})).length > 0;) {
            gewijzigd = false;
            for (let se of [...Object.values(BGProcesSimulator.Singletons('Elementen'))]) {
                if (vanafTijdstip === undefined || (se.Tijdstip !== undefined && se.Tijdstip().Vergelijk(tijdstip) > 0)) {
                    se.destructor();
                    gewijzigd = true;
                    break;
                }
            }
        }
    }

    /**
     * Opruimen van dit specificatie-element en de specificatie-elementen die ervan afhangen.
     */
    destructor() {
        if (this.#index !== undefined) {
            let index = this.#index;
            this.#index = undefined;
            delete BGProcesSimulator.Singletons('Elementen')[index];
            if (this.#superInvoer !== undefined) {
                delete this.#superInvoer.#subInvoer[index];
                this.#superInvoer = undefined;
            }
            for (let subInvoer of this.SubManagers()) {
                subInvoer.#superInvoer = undefined;
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
        if (BGProcesSimulator.Singletons('UI', {}).ModalOpener === undefined) {
            return;
        }
        let modalOpener = BGProcesSimulator.Singletons('UI').ModalOpener;
        let kanNietSluiten = modalOpener.#ModalVerwerk((im) => im.ValideerInvoer(accepteerInvoer), true);
        if (kanNietSluiten) {
            return;
        }
        modalOpener.#ModalVerwerk((im) => im.EindeInvoer(accepteerInvoer));
        if (accepteerInvoer && modalOpener.#volgendeStapNodig) {
            modalOpener.#volgendeStapNodig = false;
            modalOpener.#invoerStap++;
            modalOpener.VervangInnerHtml();
            return;
        }

        BGProcesSimulator.Singletons('UI').ModalOpener = undefined;
        modalOpener.#ModalMode(false);
        document.getElementById('_bgps_modal').style.display = 'none';
        document.getElementById('_bgps_modal_content').innerHTML = '';
        modalOpener.VervangInnerHtml();
        modalOpener.EindeModal(accepteerInvoer);
    }

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
        if (!this.IsReadOnly()) {
            return todo(this);

        }
    }

    /**
     * Link de specificatie-elementen aan dat deel van de webpagina waar de UI events gegenereerd worden.
     * @param {any} spec_invoer Top-level HTML element van het UI-gebied
     */
    static AddEventListener(spec_invoer) {
        BGProcesSimulator.Singletons('UI', {}).Container = spec_invoer
        spec_invoer.addEventListener('change', e => SpecificatieElement.#Invoer_Event(e.target, (se, s, a) => se.#OnChange(a, s)));
        spec_invoer.addEventListener('click', e => SpecificatieElement.#Invoer_Event(e.target, (se, s, a) => se.#OnClick(a, s)));
    }
    /**
     * Verwerk een UI event in een van de specificatie elementen
     * @param {HTMLElement} elt_invoer - element waarvoor het change element is gegenereerd
     * @param {lambda} handler - functie die de juiste methode voor het specificatie-element uitvoert
     */
    static #Invoer_Event(elt_invoer, handler) {
        for (let elt = elt_invoer; elt && elt.id !== BGProcesSimulator.Singletons('UI', {}).Container.id; elt = elt.parentElement) {
            if (elt.dataset) {
                if (elt.dataset.se) {
                    let se = parseInt(elt.dataset.se);
                    let idPrefix = `_bgps_${se}_`;
                    let suffix = undefined;
                    if (elt_invoer.id.startsWith(idPrefix)) {
                        suffix = elt_invoer.id.substring(idPrefix.length);
                        suffix = suffix.slice(suffix.indexOf('_') + 1);
                    }
                    else if (elt.id.startsWith(idPrefix)) {
                        suffix = elt.id.substring(idPrefix.length);
                        suffix = suffix.slice(suffix.indexOf('_') + 1);
                    }
                    let specificatieElt = BGProcesSimulator.Singletons('Elementen')[se];
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
    Specificatie() {
        if (this.IsInvoer()) {
            if (this.#isTijdstip) {
                return this.#dag + 0.01 * this.#uur;
            } else {
                return this.#dag;
            }
        } else {
            return super.Specificatie();
        }
    }

    /**
     * Geeft aan dat het tijdstip een waarde heeft
     * @returns
     */
    HeeftWaarde() {
        return this.Specificatie() !== undefined;
    }

    /**
     * Geef de datum/tijdstip als een ISO datum voor gebruik in STOP modules
     */
    STOPDatumTijd() {
        let datum = new Date(BGProcesSimulator.This().Startdatum());
        let dag = Math.floor(this.Specificatie());
        let uur = Math.round(100 * (this.Specificatie() - dag));
        datum.setDate(datum.getDate() + dag);
        let yyyMMdd = datum.toJSON().slice(0, 10);
        if (this.#isTijdstip) {
            let HH = ('00' + uur).slice(-2);
            return `${yyyMMdd}T${HH}:00:00Z`;
        } else {
            return yyyMMdd;
        }
    }
    /**
     * Geef het jaar van deze datum/tijdstip
     */
    Jaar() {
        let datum = new Date(BGProcesSimulator.This().Startdatum());
        let dag = Math.floor(this.Specificatie());
        datum.setDate(datum.getDate() + dag);
        return datum.getFullYear();
    }

    /**
     * Geef de datum/tijdstip als een ISO datum
     */
    DatumTijdHtml() {
        let datum = new Date(BGProcesSimulator.This().Startdatum());
        let dag = Math.floor(this.Specificatie());
        let uur = Math.round(100 * (this.Specificatie() - dag));
        datum.setDate(datum.getDate() + dag);
        let yyyMMdd = datum.toJSON().slice(0, 10);
        if (this.#isTijdstip && uur > 0) {
            let HH = ('00' + uur).slice(-2);
            return `${yyyMMdd}T${HH}:00Z`;
        } else {
            return yyyMMdd;
        }
    }
    /**
     * Geef de datum en evt uur als een array van strings
     */
    DagUurHtml() {
        let dag = Math.floor(this.Specificatie());
        if (this.#isTijdstip) {
            let uur = Math.round(100 * (this.Specificatie() - dag));
            if (uur == 0) {
                return [dag, ''];
            } else {
                let HH = ('00' + uur).slice(-2);
                return [dag, `${HH}:00Z`];
            }
        } else {
            return [dag];
        }
    }

    /**
     * Geeft de startdatum als tijdstip-Tijdstip (want dat is niet in te voeren)
     */
    static StartTijd() {
        let singletons = BGProcesSimulator.Singletons('Tijdstip', {});
        if (singletons.StartTijd === undefined) {
            singletons.StartTijd = new Tijdstip(undefined, undefined, undefined, true);
            singletons.StartTijd.SpecificatieWordt(0);
        }
        return singletons.StartTijd;
    }

    /**
     * Geeft de startdatum als datum-Tijdstip (want dat is niet in te voeren)
     */
    static StartDatum() {
        let singletons = BGProcesSimulator.Singletons('Tijdstip', {});
        if (singletons.StartDatum === undefined) {
            singletons.StartDatum = new Tijdstip(undefined, undefined, undefined, false);
            singletons.StartDatum.SpecificatieWordt(0);
        }
        return singletons.StartDatum;
    }

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
        let dag = Math.floor(this.Specificatie());
        if (this.#isTijdstip) {
            //let uur = Math.round(100 * (this.Specificatie() - dag));
            return `dag ${dag} (${this.DatumTijdHtml()})`;
        } else {
            return `dag ${dag} (${this.DatumTijdHtml()})`;
        }
    }
    #isTijdstip;

    BeginInvoer() {
        let data = super.Specificatie();
        this.#uur = 0;
        if (data === undefined) {
            this.#dag = 1;
        } else {
            this.#dag = Math.floor(data)
            if (this.#isTijdstip) {
                this.#uur = Math.round(100 * data - 100 * this.#dag);
                if (this.#uur < 0) {
                    this.#uur = 0;
                } else if (this.#uur > 23) {
                    this.#uur = 23;
                    this.#dag++;
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
        let html = `dag <input type="number" class="number4" id="${this.ElementId('D')}" value="${this.#dag}"/>`
        if (this.#isTijdstip) {
            html += ` om <input type="number" class="number2" min="0" max="23" id="${this.ElementId('T')}" value="${this.#uur}"/>:00`
        }
        html += ` (${this.DatumTijdHtml()})`
        return html;
    }

    OnInvoerChange(elt, idSuffix) {
        if (idSuffix == 'D' || idSuffix == 'H') {
            let dag = parseInt(document.getElementById(this.ElementId('D')).value);
            let uur = this.#uur;

            if (this.#isTijdstip) {
                uur = parseInt(document.getElementById(this.ElementId('T')).value);
                if (uur < 0) {
                    uur = 0;
                } else if (uur > 23) {
                    uur = 23;
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
                }
            } else {
                if (dag <= this.#naDag) {
                    dag = this.#naDag + 1;
                }

            }
            if (dag != this.#dag || uur != thus.#uur) {
                this.#dag = dag;
                this.#uur = uur;
                this.VervangInnerHtml();
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
    static #laatste_uuid = 0; // Absolute waarde is niet relevant, alleen gebruikt @runtime

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

    /**
     * Geef het work-ID voor een instrument
     * @param {string} instrument - Naam van het instrument
     * @param {Activiteit} activiteit - Activiteit waarin het instrument aangemaakt wordt (niet voor regelgeving)
     */
    static Work(instrument, activiteit) {
        let soort = Instrument.SoortInstrument(instrument);
        if (soort === 'b') {
            return `/akn/nl/bill/${BGProcesSimulator.This().BGCode()}/${activiteit.Tijdstip().Jaar()}/${instrument}`;
        }
        let jaar;
        Momentopname.VoorAlleMomentopnamen(undefined, undefined, (momentopname) => {
            for (let versie of momentopname.Instrumentversies()) {
                if (versie.Instrument() === instrument) {
                    jaar = momentopname.Tijdstip().Jaar();
                    return true;
                }
            }
        });
        if (jaar !== undefined) {
            switch (Instrument.SoortInstrument(instrument)) {
                case 'reg':
                    return `/akn/nl/act/${BGProcesSimulator.This().BGCode()}/${jaar}/${instrument}`;
                default:
                    return `/join/id/regdata/${BGProcesSimulator.This().BGCode()}/${jaar}/${instrument}`;
            }
        }
        return Object.keys(alleInstrumenten);
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
        this.#onbekendeVersie = false;
        if (origineel === undefined) {
            this.#uuid = undefined;
            this.#isIngetrokken = false;
            this.#juridischeInhoud = undefined;
            this.#nonStopAnnotaties = {}
            this.#stopAnnotaties = {}
            this.#isTeruggetrokken = true;
        } else {
            this.#uuid = origineel.#uuid;
            this.#work = origineel.#work;
            this.#isIngetrokken = origineel.#isIngetrokken;
            this.#juridischeInhoud = origineel.#juridischeInhoud;
            this.#nonStopAnnotaties = Object.assign({}, origineel.#nonStopAnnotaties);
            this.#stopAnnotaties = Object.assign({}, origineel.#stopAnnotaties);
            if (this.Branch() === origineel.Branch()) {
                this.#isTeruggetrokken = origineel.#isTeruggetrokken;
                this.#onbekendeVersie = origineel.#onbekendeVersie;
            } else {
                this.#isTeruggetrokken = true;
            }
        }
        this.#isEerdereVersie = undefined;
    }
    //#endregion

    //#region Eigenschappen en wijzigen daarvan
    /**
     * De branch die deze instrumentversie beheert
     */
    Branch() {
        return this.Momentopname().Branch();
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
     * @returns {string}
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
            this.#uuidNieuweVersie = BGProcesSimulator.Singletons('UUID', 0);
            BGProcesSimulator.Singletons().UUID++;
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
        if (BGProcesSimulator.Singletons('UUID', 0) < uuid) {
            BGProcesSimulator.Singletons().UUID = uuid;
        }
    }

    /**
     * Geeft de AKN/JOIN identificatie van deze instrumentversie
     * @returns
     */
    ExpressionIdentificatie() {
        if (this.IsEerdereVersie()) {
            return this.IsEerdereVersie().ExpressionIdentificatie();
        } else if (this.IsNieuweVersie()) {
            let work = this.WorkIdentificatie();
            if (this.#soortInstrument === 'reg') {
                return `${work}/nld@${this.Momentopname().Tijdstip().Jaar()};${this.UUID()};${this.Momentopname().Branch().Code()}`;
            } else {
                return `${work}/@${this.Momentopname().Tijdstip().Jaar()};${this.UUID()};${this.Momentopname().Branch().Code()}`;
            }
        } else if (this.HeeftJuridischeInhoud()) {
            return this.#basisversie.ExpressionIdentificatie();
        }
    }
    WorkIdentificatie() {
        if (this.#work === undefined) {
            this.#work = Instrument.Work(this.Instrument());
        }
        return this.#work;
    }
    #work;

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
                if (voorganger.Branch() != this.Branch()) {
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
     */
    IsEerdereVersie() {
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

    /**
     * Geeft aan dat de instrumentversie voor de consolidatie als onbekende versie beschouwd moet worden.
     * @returns {boolean}
     */
    IsOnbekendeVersieVoorConsolidatie() {
        return this.#onbekendeVersie;
    }
    #onbekendeVersie;

    /**
     * Geeft aan dat de instrumentversie voor de consolidatie vanaf nu als onbekende versie beschouwd moet worden.
     */
    BeschouwOnbekendeVersieVoorConsolidatie() {
        this.#onbekendeVersie = true;
    }
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
                this.Momentopname().Activiteit().SpecificatieMelding(`Specificatie bevat verwijzing naar instrumentversie (${specificatie}) die nog niet bestaat op dit moment`);
            } else if (instrumentversie.Instrument() != this.Instrument()) {
                this.Momentopname().Activiteit().SpecificatieMelding(`Specificatie voor instrumentversie van ${this.Instrument()} bevat verwijzing naar instrumentversie (${specificatie}) van een ander instrument ${instrumentversie.Instrument()}`);
            } else if (instrumentversie.IsIngetrokken()) {
                this.Momentopname().Activiteit().SpecificatieMelding(`Specificatie bevat verwijzing naar instrumentversie (${specificatie}) die ingetrokken is`);
            } else if (!instrumentversie.HeeftJuridischeInhoud()) {
                this.Momentopname().Activiteit().SpecificatieMelding(`Specificatie bevat verwijzing naar instrumentversie (${specificatie}) die geen juridische inhoud heeft`);
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
            } else if (this.Branch() !== this.#basisversie.Branch()) {
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
     * @returns {Momentopname}
     */
    Momentopname() {
        return this.SuperInvoer();
    }

    /**
     * Geeft de activiteit waar deze instrumentversie deel van uitmaakt
     * @returns {Activiteit}
     */
    Activiteit() {
        return this.Momentopname().Activiteit();
    }

    /**
     * Geeft de branch waar deze instrumentversie deel van uitmaakt
     * @returns {Branch}
     */
    Branch() {
        return this.Momentopname().Branch();
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

    /**
     * HTML van de bijdrage aan het intern datamodel van de momentopname
     */
    MeldInternDatamodelHtml() {
        if (this.Instrumentversie().IsOngewijzigdInBranch()) {
            return `${this.Instrumentversie().WorkIdentificatie()} is niet gewijzigd in deze branch.`;
        } else if (this.Instrumentversie().IsIngetrokken()) {
            return `${this.Instrumentversie().WorkIdentificatie()} is juridisch niet (meer) in werking.`;
        } else {
            let html = `${this.Instrumentversie().ExpressionIdentificatie()}<br>(`;
            if (this.Instrumentversie().IsEerdereVersie() !== undefined) {
                html += 'Verwijzing naar eerder gepubliceerde versie';
            } else if (this.Instrumentversie().IsInitieleVersie()) {
                html += 'Initiële versie';
            } else {
                html += 'Gewijzigd in deze branch';
            }
            if (this.Instrumentversie().IsOnbekendeVersieVoorConsolidatie()) {
                html += '; dit is niet de correcte versie om voor de consolidatie te gebruiken, die is onbekend';
            }
            html += ')';
            return html;
        }
    }
    //#endregion

    //#region Uitwisseling met LVBB
    /**
     * Voeg de informatie voor deze instrumentversie toe aan de ConsolidatieInformatie module
     * @param {any} module - ConsolidatieInformatie module waaraan de informatie toegevoegd moet worden
     * @param {boolean} isRevisie - Geeft aan of de momentopname deel is van een revisie en geen verwijzing naar de tekst kan hebben
     */
    VoegToeAanConsolidatieInformatie(module, isRevisie) {
        // Zoek de laatste uitwisseling voor dit instrument
        let vorigeSpec = this.#LaatsteUitwisseling();

        let toegevoegd;
        if (this.Instrumentversie().IsOngewijzigdInBranch()) {
            // Hoeft alleen gemeld te worden als de vorigeSpec ook uit deze branch komt
            if (vorigeSpec !== undefined && vorigeSpec.Branch() === this.Branch() && !vorigeSpec.Instrumentversie().IsOngewijzigdInBranch()) {
                this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Branch ${this.Branch().Code()}: instrument ${this.Instrument()} is teruggetrokken.`)
                if (module.Terugtrekkingen === undefined) {
                    module.Terugtrekkingen = [];
                }
                if (this.Instrumentversie().SoortInstrument() === 'reg') {
                    toegevoegd = {
                        doel: this.Branch().Doel(),
                        instrument: this.Instrumentversie().WorkIdentificatie(),
                        eId: isRevisie ? undefined : "eId_terugtrekking"
                    };
                    module.Terugtrekkingen.push({
                        TerugtrekkingRegeling: toegevoegd
                    });
                } else {
                    toegevoegd = {
                        doel: this.Branch().Doel(),
                        instrument: this.Instrumentversie().WorkIdentificatie(),
                        eId: isRevisie ? undefined : "eId_bijlage_IO"
                    };
                    module.Terugtrekkingen.push({
                        TerugtrekkingInformatieobject: toegevoegd
                    });
                }
                module.Terugtrekkingen.push(toegevoegd);
            }
        } else if (this.Instrumentversie().IsIngetrokken()) {
            if (vorigeSpec === undefined || (vorigeSpec.Branch() !== this.Branch() || !vorigeSpec.Instrumentversie().IsIngetrokken())) {
                // Ingetrokken op deze branch, of sinds de laatste uitwisseling
                this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Branch ${this.Branch().Code()}: instrument ${this.Instrument()} is ingetrokken.`)
                if (this.Instrumentversie().SoortInstrument() === 'reg') {
                    toegevoegd = {
                        doel: this.Branch().Doel(),
                        instrument: Instrument.WorkIdentificatie(this.Instrument()),
                        eId: isRevisie ? undefined : "eId_intrekking"
                    };
                } else {
                    toegevoegd = {
                        doel: this.Branch().Doel(),
                        instrument: Instrument.WorkIdentificatie(this.Instrument()),
                        eId: isRevisie ? undefined : "eId_bijlage_IO"
                    };
                }
                if (module.Intrekkingen === undefined) {
                    module.Intrekkingen = [];
                }
                module.Intrekkingen.push({ Intrekking: toegevoegd });
                this.#instrumentversieUitgewisseld = true;
            }
        } else {
            // Alleen doorgeven als het echt om een andere versie gaat
            if (vorigeSpec === undefined || vorigeSpec.Instrumentversie().UUID() !== this.Instrumentversie().UUID()) {
                this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Branch ${this.Branch().Code()}: instrument ${this.Instrument()} is gewijzigd.`)

                if (module.BeoogdeRegelgeving === undefined) {
                    module.BeoogdeRegelgeving = [];
                }
                if (this.Instrumentversie().SoortInstrument() === 'reg') {
                    toegevoegd = {
                        doelen: [
                            { doel: this.Branch().Doel() }
                        ],
                        instrumentVersie: this.Instrumentversie().ExpressionIdentificatie(),
                        eId: isRevisie ? undefined : "eId_intrekking"
                    };
                    module.BeoogdeRegelgeving.push({
                        BeoogdeRegeling: toegevoegd
                    });
                } else {
                    toegevoegd = {
                        doelen: [
                            { doel: this.Branch().Doel() }
                        ],
                        instrumentVersie: this.Instrumentversie().ExpressionIdentificatie(),
                        eId: isRevisie ? undefined : "eId_bijlage_IO"
                    };
                    module.BeoogdeRegelgeving.push({
                        BeoogdInformatieobject: toegevoegd
                    });
                }
            }
        }
        if (toegevoegd !== undefined) {
            this.#instrumentversieUitgewisseld = true;

            toegevoegd.gemaaktOpBasisVan = [];
            if (vorigeSpec !== undefined) {
                if (vorigeSpec.Branch() !== this.Branch()) {
                    this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Branch ${this.Branch().Code()}: instrument ${this.Instrument()} is 
                    voor het laatst uitgewisseld voor branch ${vorigeSpec.Momentopname().Branch()}, dus dat is voor STOP de voorgaande branch voor dit instrument.`)
                }
                toegevoegd.gemaaktOpBasisVan.push({
                    Basisversie: {
                        doel: vorigeSpec.Branch().Doel(),
                        gemaaktOp: vorigeSpec.Momentopname().Tijdstip().STOPDatumTijd()
                    }
                });
            }
        }
    }
    /**
     * Zoek de laatste momentopname waar dit instrument is uitgewisseld
     * @returns {InstrumentversieSpecificatie}
     */
    #LaatsteUitwisseling() {
        if (this.#instrumentversieUitgewisseld) {
            return this;
        }
        for (let mo = this.Momentopname().VoorgaandeMomentopname(); mo !== undefined; mo = mo.VoorgaandeMomentopname()) {
            let spec = mo.Instrumentversie(this.Instrument());
            if (spec === undefined) {
                break;
            }
            if (spec.#instrumentversieUitgewisseld) {
                return spec;
            }
        }
    }
    #instrumentversieUitgewisseld = false;
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
            html += `<tr><td><input type="radio" id="${this.ElementId('T')}" name="${this.ElementId('R')}"${(checked == 'T' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('T')}">Ongewijzigd laten voor ${this.Momentopname().Branch().InteractieNaam()}</label></td></tr>`;

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
                        versies[`Op ${versie.Momentopname().Tijdstip().DatumTijdHtml()} voor: ${versie.Momentopname().Branch().InteractieNaam()}`] = versie.UUID();
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

    /**
     * Geeft aan of deze specificatie dezelfde waarde heeft als de andere
     * @param {TijdstempelSpecificatie} specificatie
     * @returns {boolean}
     */
    IsGelijk(specificatie) {
        let deze = this.Datum();
        let andere = specificatie.Datum();
        if (deze === undefined) {
            return andere === undefined;
        } else {
            return deze.IsGelijk(andere);
        }
    }
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
     * @param {bool/Tijdstip/Momentopname} werkUitgangssituatieBij - Geeft aan of de uitgangssituatie bijgewerkt moet worden,
     *                                              en evt voor welk tijdstip de geconsolideerde regelgeving gebruikt moet worden
     *                                              c.q. welke momentopname. 
     * @param {Momentopname[]} ontvlochtenversies - De wijzigingen die ontvlochten moeten worden met deze wijziging
     * @param {Momentopname[]} vervlochtenversies - De wijzigingen die vervlochten moeten worden met deze wijziging
     */
    constructor(superInvoer, eigenaarObject, branch, tijdstempelsToegestaan, werkUitgangssituatieBij = false, ontvlochtenversies, vervlochtenversies) {
        super(eigenaarObject, branch.Code(), undefined, superInvoer);
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
        if (werkUitgangssituatieBij !== false || voorgaandeMomentopnameDezeBranch === undefined) {
            // Zoek de laatste momentopname op van de uitgangssituatie waar de branch van uitgaat.
            if (this.Branch().Soort() === Branch.Soort_GeldendeRegelgeving) {
                if (!(this instanceof Uitgangssituatie)) {
                    // De uitgangssituatie (en tevens basisversie) is de geldende regelgeving.
                    let status = this.Activiteit().VoorgaandeConsolidatiestatus();
                    if (status === undefined || status.Bepaald().length === 0) {
                        this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Er is nog geen geldende regelgeving bekend; deze branch leidt tot nieuwe regelingen.`);
                    } else {
                        let tijdstip = werkUitgangssituatieBij instanceof Tijdstip ? werkUitgangssituatieBij : this.Tijdstip();
                        this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De uitgangssituatie van de regelgeving van deze branch wordt bijgewerkt naar de regelgeving die geldig is op ${tijdstip.DatumTijdHtml()}`);
                        status = status.NuGeldend(tijdstip);
                        uitgangssituatie = status.IWTMoment().LaatsteBijdrage(status.IWTMoment().Inwerkingtredingbranchcodes()[0]);
                        if (!status.IsVoltooid()) {
                            this.Activiteit().SpecificatieMelding(`Consolidatie van nu geldende regelgeving is incompleet; scenario gebruikt de regelgeving van de branch ${uitgangssituatie.Branch().Code()} per ${uitgangssituatie.Tijdstip().DatumTijdHtml()}.`);
                        }
                    }
                }
            } else {
                // De uitgangssituatie is de laatste momentopname van de branch waar deze branch op volgt
                uitgangssituatie = werkUitgangssituatieBij instanceof Momentopname ? werkUitgangssituatieBij : this.Branch().VolgtOpBranch().LaatsteMomentopname(this.Tijdstip());
                this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De uitgangssituatie van de regelgeving van deze branch wordt bijgewerkt naar de regelgeving van de branch ${uitgangssituatie.Branch().Code()} per ${uitgangssituatie.Tijdstip().DatumTijdHtml()}.`);
                if (this.Branch().Soort() === Branch.Soort_OplossingSamenloop) {
                    // De andere branches werken als een vervlechting
                    for (let andereBranch of this.Branch().TreedtConditioneelInWerkingMet()) {
                        if (andereBranch != this.Branch().VolgtOpBranch()) {
                            let andereMO = andereBranch.LaatsteMomentopname(this.Tijdstip());
                            this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Tevens worden de wijzigingen van de regelgeving van de branch ${andereMO.Branch().Code()} (waarmee de samenloop opgelost moet worden) per ${andereMO.Tijdstip().DatumTijdHtml()} in deze momentopname vervlochten.`);
                            this.#vervlochtenMet.push(andereMO);
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
                this.Activiteit().SpecificatieMelding(`Specificatie van tijdstempels is niet toegestaan - de tijdstempels worden genegeerd.')).`);
                delete this.Specificatie().JuridischWerkendVanaf;
                delete this.Specificatie().GeldigVanaf;
            }
        }
        // Maak specificatie-elementen voor de tijstempels
        this.#juridischWerkendVanaf = new TijdstempelSpecificatie(this, 'JuridischWerkendVanaf', voorgaandeMomentopnameDezeBranch === undefined ? undefined : voorgaandeMomentopnameDezeBranch.JuridischWerkendVanaf());
        this.#geldigVanaf = new TijdstempelSpecificatie(this, 'GeldigVanaf', voorgaandeMomentopnameDezeBranch === undefined ? undefined : voorgaandeMomentopnameDezeBranch.GeldigVanaf(), this.#juridischWerkendVanaf);
        if (!tijdstempelsToegestaan) {
            this.#juridischWerkendVanaf.ReadOnlyWordt(true);
            this.#geldigVanaf.ReadOnlyWordt(true);
        }

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
        return this.SuperInvoer().Tijdstip();
    }

    /**
     * Geeft de activiteit waarvoor de momentopname gespecificeerd wordt
     */
    Activiteit() {
        return this.SuperInvoer();
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
     * Geeft aan of de regelgeving van de branch is gewijzigd ten opzichte van de eerste van 
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
     * Geeft aan of het vaststellingsbesluit is gepubliceerd. ALleen nodig voor de 
     * weergave in deze applicatie (want dan zijn rectificaties mogelijk)
     */
    IsVaststellingsbesluitGepubliceerd() {
        return this.#isVastgesteld;
    }
    #isVastgesteld = false;

    /**
     * Geeft de versies van de instrumenten (als InstrumentversieSpecificatie) op deze branch in deze momentopname
     * @returns {InstrumentversieSpecificatie[]}
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
        if (this.VoorgaandeMomentopname() !== undefined && this.VoorgaandeMomentopname().Branch() == this.Branch()) {
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
        this.#bijdragen[this.Branch().Code()] = this;
        for (let v of this.#vervlochtenMet) {
            let bijdrage = this.#bijdragen[v.Branch().Code()];
            if (bijdrage === undefined || bijdrage.Activiteit().Tijdstip().Vergelijk(v.Activiteit().Tijdstip()) < 0) {
                this.#bijdragen[v.Branch().Code()] = v;
            }
        }
        // Haal de bijdragen van ontvlochten branches weg
        for (let v of this.#ontvlochtenMet) {
            delete this.#bijdragen[v.Branch().Code()];
        }
    }
    //#endregion

    //#region Uitwisseling met LVBB
    /**
     * Voeg de informatie in deze momentopname toe aan de ConsolidatieInformatie module
     * @param {any} module - ConsolidatieInformatie module waaraan de informatie toegevoegd moet worden
     * @param {boolean} isRevisie - Geeft aan of de momentopname deel is van een revisie en geen verwijzing naar de tekst kan hebben
     */
    VoegToeAanConsolidatieInformatie(module, isRevisie) {
        // Voeg de instrumentversie-informatie toe
        for (let instrumentversie of this.Instrumentversies()) {
            instrumentversie.VoegToeAanConsolidatieInformatie(module, isRevisie)
        }

        // Voeg de tijdstempels toe
        let tijdstempelsEerderUitgewisseld = false;
        for (let mo = this.VoorgaandeMomentopname(); mo !== undefined && mo.Branch() === this.Branch(); mo = mo.VoorgaandeMomentopname()) {
            if (mo.tijdstempelsUitgewisseld) {
                if (this.#juridischWerkendVanaf.IsGelijk(mo.#juridischWerkendVanaf) && this.#geldigVanaf.IsGelijk(mo.#geldigVanaf)) {
                    // Waarde is niet gewijzigd
                    return;
                }
                if (logVerwerking) {
                    this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Branch ${this.Branch().Code()}: Tijdstempels zijn gewijzigd sinds laatste uitwisseling (gemaaktOp = ${this.Activiteit().Tijdstip().STOPDatumTijd()}).`)
                }
                tijdstempelsEerderUitgewisseld = true;
                break;
            }
        }
        if (!tijdstempelsEerderUitgewisseld) {
            this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Branch ${this.Branch().Code()}: Tijdstempels zijn nog niet eerder uitgewisseld.`)
        }

        // Neem de tijdstempel op in de module
        if (this.JuridischWerkendVanaf().HeeftWaarde()) {
            if (module.Tijdstempels === undefined) {
                module.Tijdstempels = [];
            }
            module.Tijdstempels.push({
                Tijdstempel: {
                    doel: this.Branch().Doel(),
                    soortTijdstempel: 'juridischWerkendVanaf',
                    datum: this.JuridischWerkendVanaf().STOPDatumTijd(),
                    eId: isRevisie ? undefined : 'eId_tijdstempels'
                }
            });
            if (this.GeldigVanaf() !== undefined) {
                module.Tijdstempels.push({
                    Tijdstempel: {
                        doel: this.Branch().Doel(),
                        soortTijdstempel: 'geldigVanaf',
                        datum: this.GeldigVanaf().STOPDatumTijd(),
                        eId: isRevisie ? undefined : 'eId_tijdstempels'
                    }
                });
            }
            this.#tijdstempelsUitgewisseld = true;
        } else if (tijdstempelsEerderUitgewisseld) {
            if (module.Terugtrekkingen === undefined) {
                module.Terugtrekkingen = [];
            }
            module.Terugtrekkingen.push({
                TerugtrekkingTijdstempel: {
                    doel: this.Branch().Doel(),
                    soortTijdstempel: 'juridischWerkendVanaf',
                    eId: isRevisie ? undefined : 'eId_tijdstempels'
                }
            });
            this.#tijdstempelsUitgewisseld = true;
        }
    }
    #tijdstempelsUitgewisseld = false;
    //#endregion

    //#region Statusoverzicht
    /**
     * Het overzicht van de momentopname in het projectoverzicht
     */
    OverzichtHtml() {
        let meerdereInstrumentenMogelijk = BGProcesSimulator.Opties.MeerdereRegelingen || BGProcesSimulator.Opties.InformatieObjecten;
        let html = '<table>';
        let heeftInstrumentversies = false;
        for (let soortInstrument of Instrument.SoortInstrument_Regelgeving) {
            let soortnaam = Instrument.SoortInstrumentNamen[soortInstrument];
            soortnaam = soortnaam.charAt(0).toUpperCase() + soortnaam.slice(1)

            let heeftVersiesVanDezeSoort = false;
            for (let instr of Object.keys(this.#actueleInstrumenten).sort()) {
                let instrument = this.#actueleInstrumenten[instr];
                if (instrument.Instrumentversie().HeeftJuridischeInhoud() && instrument.Instrumentversie().SoortInstrument() === soortInstrument) {
                    html += `<tr><td class="nw">${soortnaam}</td>`;
                    if (meerdereInstrumentenMogelijk) {
                        html += `<td class="nw">${instrument.Instrument()}</td>`;
                    }
                    html += `<td class="w100">${instrument.OverzichtHtml()}</td></tr>`;
                    heeftVersiesVanDezeSoort = true;
                    heeftInstrumentversies = true;
                }
            }
            if (soortInstrument == Instrument.SoortInstrument_Regeling && !heeftVersiesVanDezeSoort) {
                html += `<tr><td class="nw">${soortnaam}</td>`;
                if (meerdereInstrumentenMogelijk) {
                    html += `<td class="nw" colspan="2">`;
                } else {
                    html += '<td>';
                }
                html += '(nog) niet opgesteld</td></tr>';
            }
        }
        if (this.JuridischWerkendVanaf().HeeftWaarde()) {
            html += `<tr><td colspan="${meerdereInstrumentenMogelijk ? 2 : 1}" class="nw">In werking vanaf</td><td>${this.JuridischWerkendVanaf().DatumTijdHtml()}</td></tr>`;
            if (this.GeldigVanaf() !== undefined && this.GeldigVanaf().HeeftWaarde()) {
                html += `<tr><td colspan="${meerdereInstrumentenMogelijk ? 2 : 1}" class="nw">Terugwerkend tot</td><td>${this.GeldigVanaf().DatumTijdHtml()}</td></tr>`;
            }
        }

        if (heeftInstrumentversies && (this.JuridischeUitgangssituaties() === undefined || this.JuridischeUitgangssituaties()[0] !== this)) {
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

            html += `<tr><td colspan="${(meerdereInstrumentenMogelijk ? 3 : 2)}">`;
            if (this.Activiteit().Publicatiebron() !== undefined) {
                html += `In ${this.Activiteit().Publicatiebron()} wordt `;
            } else {
                html += `Indien aanwezig wordt in een ${this.#MogelijkePublicatie(this.IsVaststellingsbesluitGepubliceerd())} `;
            }
            if (heeftInhoudWijzigingen) {
                if (this.JuridischeUitgangssituaties() === undefined) {
                    html += 'een integrale versie van de tekst/informatieobjecten opgenomen.';
                } else {
                    html += `de wijziging ten opzichte van ${this.JuridischeUitgangssituaties()[0].Branch().InteractieNaam()} d.d. ${this.JuridischeUitgangssituaties()[0].Tijdstip().DatumTijdHtml()}`;
                    if (this.JuridischeUitgangssituaties().length > 1) {
                        html += ', bijgewerkt met wijzigingen uit ';
                        for (let i = 1; i < this.JuridischeUitgangssituaties().length; i++) {
                            if (i > 1) {
                                html += ', ';
                            }
                            html += `${this.JuridischeUitgangssituaties()[i].Branch().InteractieNaam()} d.d. ${this.JuridischeUitgangssituaties()[i].Tijdstip().DatumTijdHtml()}`;
                        }
                    }
                    html += ' beschreven.';
                }
            } else if (heeftIWTWijzigingen) {
                html += `de inwerkingtreding van het resultaat van ${this.JuridischeUitgangssituaties()[0].Branch().InteractieNaam()} d.d. ${this.JuridischeUitgangssituaties()[0].Tijdstip().DatumTijdHtml()} beschreven.`;
            } else {
                html += 'geen wijziging in deze regelgeving beschreven.';
            }
            html += '</td></tr>';
        }
        html += '</table>';
        return html;
    }

    /**
     * Genereer UitvoeringMeldingen die de stand van het interne datamodel rapporteren.
     * Standaard is een overzicht van de momentopnamen.
     */
    MeldInternDatamodel() {
        let html = `<table>
            <tr><th>Momentopname</td><td>Branch <code>${this.Branch().Code()}</code> @ ${this.Tijdstip().DatumTijdHtml()}</td></tr>
            <tr><td>Naam branch</td><td>${this.Branch().InteractieNaam()}</td></tr>
            <tr><td>Regelgeving gepubliceerd in vaststellingsbesluit?</td><td>${this.IsVaststellingsbesluitGepubliceerd() ? 'Ja; juridische uitgangssituatie is eerdere momentopname van deze branch' : 'Nee; juridische uitgangssituatie afkomstig van andere branch'}</td></tr>
            <tr><td>Juridische uitgangssituatie</td><td>`;
        if (this.JuridischeUitgangssituaties() === undefined) {
            html += '-';
        } else if (this.JuridischeUitgangssituaties().length === 1) {
            let mo = this.JuridischeUitgangssituaties()[0];
            html += `Branch <code>${mo.Branch().Code()}</code> @ ${mo.Tijdstip().DatumTijdHtml()}`
        } else {
            html += '<ul>' + this.JuridischeUitgangssituaties().map(mo => `<li>Branch <code>${mo.Branch().Code()}</code> @ ${mo.Tijdstip().DatumTijdHtml()}</li>`).join('') + '</ul>';
        }
        html += `</td></tr>
            <tr><td>Instrumentversies</td><td><ul>${this.Instrumentversies().sort((a, b) => a.Instrumentversie().WorkIdentificatie().localeCompare(b.Instrumentversie().WorkIdentificatie())).map(iv => `<li>${iv.MeldInternDatamodelHtml()}</li>`).join('')}</ul></td></tr>
            <tr><td>Juridisch werkend vanaf</td><td>${this.JuridischWerkendVanaf() === undefined || !this.JuridischWerkendVanaf().HeeftWaarde() ? '-' : this.JuridischWerkendVanaf().DatumTijdHtml()}</td></tr>
            <tr><td>Geldig vanaf</td><td>${this.GeldigVanaf() === undefined || !this.GeldigVanaf().HeeftWaarde() ? '-' : this.GeldigVanaf().DatumTijdHtml()}</td></tr>
            <tr><td>Bevat wijzigingen van</td><td><ul>${Object.values(this.#bijdragen).sort((a, b) => -Branch.Vergelijk(a.Branch(), b.Branch())).map(mo => `<li>Branch <code>${mo.Branch().Code()}</code> @ ${mo.Tijdstip().DatumTijdHtml()}</li>`).join('')}</ul></td></tr>
        </table>`;
        if (this.TegelijkBeheerd() !== undefined) {
            html += 'De regelgeving voor deze branch treedt tegelijk in werking met die van andere branches. Dezelfde instrumentversies zijn te vinden in: <ul>'
                + this.TegelijkBeheerd().map(mo => `<li>Branch <code>${mo.Branch().Code()}</code> @ ${mo.Tijdstip().DatumTijdHtml()}</li>`).join('') + '</ul>';
        }
        this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_InternDatamodel, html);
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

    /**
     * Geef aan welke publicaties mogelijk zijn
     * @param {boolean} isVaststellingsbesluitGepubliceerd - Geeft aan of er al een vaststellingsbesluit is gepubliceerd
     * @returns {string}
     */
    #MogelijkePublicatie(isVaststellingsbesluitGepubliceerd) {
        if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente) {
            if (isVaststellingsbesluitGepubliceerd) {
                return '(concept-)rectificatie';
            } else {
                return '(concept-)besluit';
            }
        }
        if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Rijksoverheid) {
            if (isVaststellingsbesluitGepubliceerd) {
                return '(concept-)vervolgbesluit of rectificatie';
            } else {
                return '(concept-)besluit';
            }
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
     * @param {Project} project - Project waarvoor de branch wordt aangemaakt
     * @param {string} code - Unieke code voor de branch
     */
    constructor(activiteit, project, code) {
        super(activiteit.Specificatie(), code, undefined, activiteit, {});
        if (code !== Branch.Code_Uitgangssituatie) {
            let branches = BGProcesSimulator.Singletons('Branches', {});
            if (code in branches) {
                throw new Error(`Branch met code ${code} bestaat al`);
            }
            branches[code] = this;
        } else {
            this.Specificatie().Soort = Branch.Soort_GeldendeRegelgeving;
            this.Specificatie().Naam = 'Uitgangssituatie';
        }

        this.#project = project;
        if (this.Soort() === Branch.Soort_VolgtOpAndereBranch) {
            this.#volgtOpBranch = Branch.Branch(this.Specificatie().Branch);
            if (this.#volgtOpBranch === undefined || this.#volgtOpBranch.OntstaanIn().Tijdstip().Vergelijk(this.OntstaanIn().Tijdstip()) > 0) {
                throw new Error(`Branch met code ${this.Specificatie().Branch} bestaat (nog) niet`);
            }
        } else if (this.Soort() === Branch.Soort_OplossingSamenloop) {
            this.#inWerkingMet = this.Specificatie().Branches.map(bc => {
                let b = Branch.Branch(bc);
                if (b === undefined || b.OntstaanIn().Tijdstip().Vergelijk(this.OntstaanIn().Tijdstip()) > 0) {
                    throw new Error(`Branch met code ${bc} bestaat (nog) niet`);
                }
                return b;
            });
            this.#volgtOpBranch = this.#inWerkingMet[0];
        }
        this.#volgorde = ++Branch.#volgende_volgorde;
        this.#naam = new Naam(this.Specificatie(), this, n => n);
        this.#beschrijving = new Beschrijving(this.Specificatie(), this);
    }

    /**
     * Maak een nieuwe branch
     * @param {Activiteit} activiteit - Activiteit die de branch aanmaakt
     * @param {Project} project - Project waarvoor de branch wordt aangemaakt
     * @param {string} code - Code voor de branch
     * @param {string} naam - Naam van de branch
     * @param {string} beschrijving - Beschrijving van de branch
     * @param {string} soort - Soort branch
     * @param {Branch/Branch[]} moAndereBranches - Optioneel: branch (Soort_VolgtOpAndereBranch)
     *                                             / branches (Soort_OplossingSamenloop)
     */
    static MaakBranch(activiteit, project, code, naam, beschrijving, soort, moAndereBranches) {
        if (code === undefined) {
            code = BGProcesSimulator.VrijeNaam(Branch.Branches(undefined, project).map(b => b.Code()), `${project.Code()}_`);
        }
        activiteit.Specificatie()[code] = {
            Soort: soort,
            Naam: naam,
            Beschrijving: beschrijving
        };
        if (soort === Branch.Soort_VolgtOpAndereBranch) {
            activiteit.Specificatie()[code].Branch = moAndereBranches.Code();
        } else if (soort === Branch.Soort_OplossingSamenloop) {
            activiteit.Specificatie()[code].Branch = moAndereBranches;
        }
        return new Branch(activiteit, project, code);
    }

    destructor() {
        if (this.Specificatie() !== undefined) {
            delete BGProcesSimulator.Singletons('Branches')[this.Code()];
        }
        super.destructor();
    }
    //#endregion

    //#region Constanten
    static Code_Uitgangssituatie = 'start';

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
        for (let branch of Object.values(BGProcesSimulator.Singletons('Branches', {}))) {
            if (project === undefined || branch.Project() === project) {
                if (tijdstip === undefined || branch.OntstaanIn().Tijdstip().Vergelijk(tijdstip) <= 0) {
                    branches.push(branch);
                }
            }
        }
        branches.sort(Branch.Vergelijk);
        return branches;
    }
    #volgorde;
    static #volgende_volgorde = 0; // Absolute waarde is niet relevant

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
     * @param {string} branchcode - Naam van de branch
     */
    static Branch(branchcode) {
        return BGProcesSimulator.Singletons('Branches', {})[branchcode];
    }

    /**
     * Geeft de activiteit waarin de branch is ontstaan
     */
    OntstaanIn() {
        return this.SuperInvoer();
    }

    /**
     * Geeft het project waarvoor de branch is aangemaakt
     */
    Project() {
        return this.#project;
    }
    #project;

    /**
     * Geeft de code van de branch zoals die in de specificatie voorkomt
     */
    Code() {
        return this.Eigenschap();
    }

    /**
     * Geeft de naam van de branch zoals die in de specificatie voorkomt
     */
    Naam() {
        return this.#naam.Specificatie();
    }
    #naam;

    /**
     * Geeft de naam van de branch zoals die in de user interface gebruikt moet worden
     */
    InteractieNaam() {
        if (Branch.Branches(undefined, this.Project()).length <= 1) {
            return this.Project().Naam();
        } else {
            return `${this.Naam()} (${this.Project().Naam()})`;
        }
    }

    /**
     * Geeft een toelichting op de aard van de branch, voor weergave
     */
    Beschrijving() {
        return this.#beschrijving.Specificatie();
    }
    #beschrijving;

    /**
     * Geeft de soort waartoe de branch behoort.
     */
    Soort() {
        return this.Specificatie().Soort;
    }

    /**
     * Geeft de branch die als voorganger dient van deze branch (niet voor Soort_GeldendeRegelgeving).
     * @returns {Branch}
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

    /**
     * Geeft het doel dat in STOP modules voor deze branch gebruikt moet worden
     * @returns {string}
     */
    Doel() {
        return `/join/id/proces/${this.OntstaanIn().Tijdstip().Jaar()}/${this.Code()}`;
    }
    //#endregion

    //#region Statusoverzicht
    /**
     * Maak de uitvoeringmeldingen voor het maken van de branch
     */
    MeldUitvoering() {
        let html = `<table>
                        <tr><th>Branch</th><td>${this.Code()}</td></tr>
                        <tr><td>Naam</td><td>${this.InteractieNaam()}</td></tr>`;
        if (this.Beschrijving() !== undefined) {
            html += `<tr><td>Beschrijving</td><td>${this.Beschrijving()}</td></tr>`;
        }
        html += `<tr><td>Doel</td><td>${this.Doel()}</td></tr>
                        <tr><td class="nw">Juridische uitgangssituatie</td><td>`;
        switch (this.Soort()) {
            case Branch.Soort_GeldendeRegelgeving:
                html += 'Regelgeving die op enig moment geldig was.';
                break;
            case Branch.Soort_VolgtOpAndereBranch:
                html += `Regelgeving van de branch <code>${this.VolgtOpBranch().Code()}</code> van project "${this.VolgtOpBranch().Project().Naam()}"`;
                break;
            case Branch.Soort_OplossingSamenloop:
                html += `Regelgeving van de branch <code>${this.VolgtOpBranch().Code()}</code>`;
                break;
        }
        html += '</td></tr></table>';
        if (this.Soort() === Branch.Soort_OplossingSamenloop) {
            html += `De branch is gemaakt om in een besluit de oplossing te beschrijven van de samenloop van 
                ${this.TreedtConditioneelInWerkingMet(), map((b) => `branch <code>${b.Code()}</code> van project ${b.Project().Naam()}`).join(', ')}. 
                De juridische uitgangssituatie is in deze simulator een branch van dit project; dat had ook een van de andere branches mogen zijn.`;
        }
        this.OntstaanIn().UitvoeringMelding(Activiteit.Onderwerp_InternDatamodel, html);
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return this.InteractieNaam();
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
    Inwerkingtredingbranchcodes() {
        return Object.keys(this.#bijdragen);
    }
    /**
     * De momentopname van de branch die als laatste bijgedraagt
     * aan de versie die in werking treedt.
     * @param {string} branchcode - Code van de branch
     * @returns {Momentopname}
     */
    LaatsteBijdrage(branchcode) {
        return this.#bijdragen[branchcode];
    }
    #bijdragen = {};
    //#endregion

    //#region Bijwerken
    /**
     * Geef een branch door als bijdragend aan een IWT-moment
     * @param {any} perBranch - Collectie met IWTMoment per branch
     * @param {any} perDatum - Collectie met IWTMoment per datum
     * @param {string} branchcode - Naam van de branch
     * @param {Momentopname} momentopname - laatste momentopname voor de branch
     * @param {Tijdstip} iwtDatum - Nieuwe datum van inwerkingtreding
     */
    static WerkBij(perBranch, perDatum, branchcode, momentopname, iwtDatum) {
        let iwtMoment = perBranch[branchcode];
        if (iwtMoment !== undefined) {
            if (!iwtMoment.Datum().IsGelijk(iwtDatum)) {
                iwtMoment.#VerwijderBranch(perBranch, perDatum, branchcode);
                if (iwtDatum === undefined) {
                    return;
                }
                iwtMoment = undefined;
            }
        }
        if (iwtDatum !== undefined && iwtDatum.HeeftWaarde()) {
            iwtMoment = iwtMoment === undefined ? new IWTMoment(iwtDatum) : iwtMoment.#Kloon();
            iwtMoment.#bijdragen[branchcode] = momentopname; // Nieuwe momentopname is altijd recenter dan eerder verwerkte
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
        for (let branchnaam of this.Inwerkingtredingbranchcodes()) {
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
     * @param {Activiteit} activiteit - Activiteit waar de consolidatiestatus bij hoort, of undefined voor de uitgangssituatie
     * @param {IWTMoment} iwtMoment - IWT moment waar dit de status van is.
     * @param {any} cumulatieveIWTBijdragen - Bijdragen aan de IWT-versie van alle branches die in werking zijn.
     */
    constructor(activiteit, iwtMoment, cumulatieveIWTBijdragen) {
        this.#iwtMoment = iwtMoment;

        // Als er sprake is van gelijktijdige iwt, dan moet elke branch als
        // laatste bijdrage de laatste momentopname van de andere branches hebben.
        this.#samenloopBijIWT = false;
        for (let branchcode of iwtMoment.Inwerkingtredingbranchcodes()) {
            for (let andereBranchcode of iwtMoment.Inwerkingtredingbranchcodes()) {
                if (branchcode != andereBranchcode) {
                    if (cumulatieveIWTBijdragen[branchcode].LaatsteBijdrage(andereBranchcode) != cumulatieveIWTBijdragen[andereBranchcode]) {
                        this.#samenloopBijIWT = true;
                        break;
                    }
                }
            }
        }

        // Bepaal de laatste bijdragen van andere branches aan de versie die voor IWT is klaargezet op deze branch
        // Bij gelijktijdige iwt is de aanname dat de bijdragenViaBranches een goede weergave is van de bijdragen 
        // als de samenloop - bij - IWT is opgelost.
        let bijdragenViaBranches = {}
        for (let branchcode of iwtMoment.Inwerkingtredingbranchcodes()) {
            for (let bijdragendeBranch of cumulatieveIWTBijdragen[branchcode].HeeftBijdragenVan()) {
                let laatste = bijdragenViaBranches[bijdragendeBranch];
                let mo = cumulatieveIWTBijdragen[branchcode].LaatsteBijdrage(bijdragendeBranch);
                if (laatste === undefined || laatste.Activiteit.Tijdstip().Vergelijk(mo.Activiteit.Tijdstip()) < 0) {
                    bijdragenViaBranches[bijdragendeBranch] = mo;
                }
            }
        }

        // Er is geen sprake van samenloop als elke laatste bijdrage aan het IWT-moment tevens de laatste bijdrage aan de instrumentversies
        // die voor het IWT-moment zijn klaargezet, dus de bijdragen in bijdragenViaBranches.
        this.#teVervlechten = [];
        for (let vereisteBranchcode in cumulatieveIWTBijdragen) {
            let bijdrage = bijdragenViaBranches[vereisteBranchcode];
            if (bijdrage === undefined || bijdrage != cumulatieveIWTBijdragen[vereisteBranchcode]) {
                this.#teVervlechten.push(cumulatieveIWTBijdragen[vereisteBranchcode]);
            }
        }

        // Via de bijdragen van de instrumentversies mogen er geen branches zijn die niet in werking zijn
        this.#teOntvlechten = [];
        for (let bijdragendeBranchcode in bijdragenViaBranches) {
            if (cumulatieveIWTBijdragen[bijdragendeBranchcode] === undefined) {
                this.#teOntvlechten.push(bijdragenViaBranches[bijdragendeBranchcode]);
            }
        }

        if (activiteit !== undefined) {
            let html = `<table>
                <tr><th class="nw">Geconsolideerde regelgeving</th><td>inwerkingtredingsmoment ${this.#iwtMoment.Datum().DatumTijdHtml()}</td><tr>
                <tr><td class="mw">Status consolidatie</td><td>${this.IsVoltooid() ? 'Voltooid' : 'Nog niet afgerond'}</td></tr>
                <tr><td class="nw">Bevat wijzigingen uit</td><td><ul>${Object.keys(cumulatieveIWTBijdragen).map(bc => `<li>Branch <code>${bc}</code> @ ${cumulatieveIWTBijdragen[bc].Tijdstip().DatumTijdHtml()}</li>`).join('')}</ul></td></tr>
                <tr><td class="nw">In werking treedt</td><td>Branch <code>`;
            if (iwtMoment.Inwerkingtredingbranchcodes().length === 1) {
                html += iwtMoment.Inwerkingtredingbranchcodes()[0];
            } else {
                html += iwtMoment.Inwerkingtredingbranchcodes().join('</code>, branch <code>');
            }
            html += `</code></td></tr>`;
            if (iwtMoment.Inwerkingtredingbranchcodes().length > 1) {
                html += `<tr><td class="nw">Samenloop bij iwt?</td><td>${this.#samenloopBijIWT ? 'Ja, in werking tredende branches specificeren verschillende regelgeving' : 'Nee, in werking tredende branches specificeren dezelfde regelgeving'}</td></tr>`;
            }
            if (Object.keys(cumulatieveIWTBijdragen).length > iwtMoment.Inwerkingtredingbranchcodes().length) {
                html += `<tr><td class="nw">Alle eerdere wijzigingen meegenomen?</td><td>${this.#teOntvlechten.length > 0 || this.#teVervlechten.length > 0 ? 'Nee.<br>' : 'Ja'}</td></tr>`;
                if (this.#teVervlechten.length > 0) {
                    html += `<p>Nog te vervlechten:<ul>${this.#teVervlechten.map(mo => `<li>Branch <code>${mo.Branch().Code()}, wijzigingen na ${mo.Tijdstip().DatumTijdHtml()} niet meegenomen</li>`).join('')}</ul></p>`
                }
                if (this.#teOntvlechten.length > 0) {
                    html += `<p>Nog te ontvlechten:<ul>${this.#teOntvlechten.map(mo => `<li>Branch <code>${mo.Branch().Code()}, wijzigingen t/m ${mo.Tijdstip().DatumTijdHtml()} onterecht meegenomen</li>`).join('')}</ul></p>`
                }
                html += '</td></tr>';
            }
            html += '</table>';
            activiteit.UitvoeringMelding(Activiteit.Onderwerp_InternDatamodel, html);
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
class Consolidatiestatus extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak een nieuwe instantie van de consolidatiestatus
     */
    constructor() {
        // Er wordt geen specificatie gewijzigd, wel wordt de invoersystematiek gebruikt
        super();
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Geeft aan dat er nog geen enkele geldende regelgeving bekend is
     */
    static GeenConsolidatieAanwezig() {
        if (BGProcesSimulator.This().Uitgangssituatie().JuridischWerkendVanaf() !== undefined) {
            return false;
        }
        for (let activiteit of Activiteit.Activiteiten()) {
            if (activiteit.Consolidatiestatus().Bepaald().length > 0) {
                return true;
            }
        }
        return false;
    }

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
    //#endregion

    //#region Implementatie van SpecificatieElement
    WeergaveInnerHtml() {
        if (this.Bepaald().length == 0) {
            return 'Consolidatie voltooid';
        }
        let html = `<table ${this.DataSet()}><tr><td>Inwerkingtreding</td><td>Status</td></tr>`;
        for (let bepaald of this.Bepaald()) {
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
     * Aangeroepen als er op een element geklikt wordt in de weergave-html. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix === 'VC') {
            // TODO: oplossen consolidatie
        }
    }
    //#endregion

    //#region Bijwerken van de consolidatie
    /**
     * Werk de consolidatie-informatie bij
     * @param {Consolidatiestatus} voorgaandeConsolidatie - Consolidatie van voorgaande activiteit of van de Uitgangssituatie
     * @param {Activiteit} activiteit - Activiteit of Uitgangssituatie waar de consolidatiestatus bij hoort
     */
    WerkBij(voorgaandeConsolidatie, activiteit) {
        // Werk de relatie tussen IWT-momenten en branches bij
        this.#iwtPerBranch = Object.assign({}, voorgaandeConsolidatie === undefined ? undefined : voorgaandeConsolidatie.#iwtPerBranch)
        this.#iwtPerDatum = Object.assign({}, voorgaandeConsolidatie === undefined ? undefined : voorgaandeConsolidatie.#iwtPerDatum)
        if (activiteit instanceof Uitgangssituatie) {
            IWTMoment.WerkBij(this.#iwtPerBranch, this.#iwtPerDatum, activiteit.Branch().Code(), activiteit, activiteit.JuridischWerkendVanaf());
        } else {
            for (let mo of activiteit.Momentopnamen()) {
                if (mo.Activiteit() !== activiteit) {
                    // Ongewijzigde momentopname
                    continue;
                }
                IWTMoment.WerkBij(this.#iwtPerBranch, this.#iwtPerDatum, mo.Branch().Code(), mo, mo.JuridischWerkendVanaf());
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
        if (!(activiteit instanceof Uitgangssituatie)) {
            activiteit.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, 'Controleer of de consolidatie van de regelgeving voor de nu en in de toekomst geldende regelgeving is afgerond.');
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
            for (let branchnaam of iwtMoment.Inwerkingtredingbranchcodes()) {
                cumulatieveIWTBijdragen[branchnaam] = iwtMoment.LaatsteBijdrage(branchnaam);
            }
            if (iwtDatum < teConsoliderenVanaf) {
                continue;
            }

            // Bepaal de status van de consolidatie
            let status = new IWTMomentConsolidatiestatus(activiteit instanceof Uitgangssituatie ? undefined : activiteit, iwtMoment, cumulatieveIWTBijdragen);
            this.#geldend.push(status);
            if (!status.IsVoltooid()) {
                // Verder gaan heeft geen zin, de volgende zullen incompleet worden als dit IWT-moment wordt opgelost
                if (iwtDatum !== iwtDatums[iwtDatums.length - 1]) {
                    activiteit.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Controle van status van consolideren gestopt; de consolidatie voor latere inwerkingtredingsmomenten
                    zal nog niet afgerond zijn omdat het voltooien van de consolidatie voor ${iwtDatum} tot aanvullende consolidatiewerkzaamheden voor latere datums zal leiden.`);
                }
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
     * Maak het specificatie-element aan voor de beschrijving van het scenario (of van een activiteit,
     * project of branch)
     * @param {any} specificatie - Volledige specificatie
     * @param {any} superInvoer - Optioneel: activiteit/project/branch waar dit een beschrijving van is
     */
    constructor(specificatie, superInvoer) {
        super(specificatie, 'Beschrijving', undefined, superInvoer);
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        if (this.SuperInvoer() === undefined) {
            if (this.Specificatie() === undefined) {
                return this.HtmlVoegToe("Voeg een beschrijving toe", 'M');
            } else {
                return `<table><tr><td>${this.HtmlWerkBij("Wijzig de beschrijving", 'M')}</td><td>${this.Specificatie()}</td></tr></table>`;
            }
        } else {
            return this.Specificatie() === undefined ? '' : this.Specificatie();
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
 * Naam
 * 
 *----------------------------------------------------------------------------*/
class Naam extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak het specificatie-element aan voor een naam (van een project of branch)
     * @param {any} specificatie - Volledige specificatie
     * @param {any} superInvoer - Project/branch waar dit een beschrijving van is
     * @param {lambda} maakValideNaam - Methode die een ingevoerde naam accepteert (en optioneel een indicatie of het de geaccepteerde naam is) en een valide naam teruggeeft
     */
    constructor(specificatie, superInvoer, maakValideNaam) {
        super(specificatie, 'Naam', undefined, superInvoer);
        this.#maakValideNaam = maakValideNaam;
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return this.Specificatie();
    }

    InvoerInnerHtml() {
        return `<input type="text" class="naam" id="${this.ElementId('T')}" value="${(this.Specificatie() === undefined ? '' : this.Specificatie())}">`;
    }

    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix === 'M') {
            this.OpenModal();
        }
    }

    OnInvoerChange(elt, idSuffix) {
        if (idSuffix === 'T') {
            this.#MaakValideNaam(false);
        }
    }

    ValideerInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            return this.#MaakValideNaam(true);
        }
    }
    #MaakValideNaam(isNieuweVersie) {
        let elt = document.getElementById(this.ElementId('T'));
        let valide = this.#maakValideNaam(elt.value, isNieuweVersie);
        if (valide !== elt.value) {
            elt.value = valide;
            return true;
        }
    }
    #maakValideNaam;

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
    /**
     * Geeft de startdatum als Date.
     * @returns {Date}
     */
    Datum() {
        return this.#datum;
    }
    #datum;
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
        this.#datum = datum;
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
        let activiteit = new Activiteit({ Tijdstip: 0, Soort: MogelijkeActiviteit.SoortActiviteit_Uitgangssituatie });
        let branch = new Branch(activiteit, activiteit.Project(), 'start');
        super(activiteit, specificatie, branch, false);
    }
    #momentopname;
    //#endregion

    //#region Eigenschappen
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
            if (this.Instrumentversies().length == 0) {
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

    EindeModal(accepteerInvoer) {
        super.EindeModal(accepteerInvoer);
        if (accepteerInvoer) {
            BGProcesSimulator.This().WerkScenarioUit(0);
        }
    }
    //#endregion

    //#region LVBB simulator
    /**
     * Geeft de STOP module 
     */
    ModulesVoorLVBBSimulator() {
        if (this.Instrumentversies().length == 0) {
            return [];
        }
        let module = {
            _ns: Activiteit.STOP_Data,
            gemaaktOp: Tijdstip.StartTijd().STOPDatumTijd()
        }
        this.VoegToeAanConsolidatieInformatie(module, false);
        return [{ ModuleNaam: 'ConsolidatieInformatie', STOPXml: Activiteit.ModuleToXml('ConsolidatieInformatie', module) }];
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
     * @param {Activiteit} activiteit De activiteit waarin het project aangemaakt wordt
     * @param {string} code Unieke code voor het project
     */
    constructor(activiteit, code) {
        if (code === undefined) {
            code = BGProcesSimulator.VrijeNaam(Object.keys(BGProcesSimulator.Singletons('Projecten', {})), 'p');
        }
        super(activiteit.Specificatie(), code, undefined, activiteit, {});
        if (code === Project.Code_Uitgangssituatie) {
            this.Specificatie().Naam = Project.Code_Uitgangssituatie
        } else {
            let projecten = BGProcesSimulator.Singletons('Projecten', {});
            if (code in projecten) {
                throw new Error(`Project met code ${code} bestaat al`);
            }
            projecten[code] = this;
            this.Specificatie().Naam = this.#MaakValideNaam(this.Naam());
        }
        this.#naam = new Naam(this.Specificatie(), this, (n, a) => this.#MaakValideNaam(n, a));
        this.#beschrijving = new Beschrijving(this.Specificatie(), this);
    }

    destructor() {
        delete BGProcesSimulator.Singletons('Projecten', {})[this.Code()];
        super.destructor();
    }
    //#endregion

    //#region Constanten
    static Code_Uitgangssituatie = 'Uitgangssituatie';
    //#endregion

    //#region Eigenschappen
    /**
     * Een lijst met alle projecten in het scenario, gesorteerd op de naam van het project.
     * @param {Tijdstip} tijdstip - Optioneel: tijdstip waarop het project al bekend moet zijn
     */
    static Projecten(tijdstip) {
        return Object.values(BGProcesSimulator.Singletons('Projecten', {})).filter((p) => tijdstip === undefined || p.OntstaanIn().Tijdstip().Vergelijk(tijdstip) <= 0).sort((a, b) => a.Naam().localeCompare(b.Naam()));
    }

    /**
     * Geeft het project op basis van de code
     * @param {string} code
     * @returns {Project}
     */
    static Project(code) {
        return BGProcesSimulator.Singletons('Projecten', {})[code];
    }

    /**
     * De unieke code voor dit project
     * @returns
     */
    Code() {
        return this.Eigenschap();
    }

    /**
     * Naam van het project
     */
    Naam() {
        return this.Specificatie().Naam;
    }

    /**
     * Geeft de activiteit waarin de branch is ontstaan
     */
    OntstaanIn() {
        return this.SuperInvoer();
    }
    //#endregion

    //#region Implementatie van SpecificatieElement
    WeergaveInnerHtml() {
        return `<table>
                    <tr><td>Naam</td><td>${this.#naam.Html()}</td></tr>
                    <tr><td>Beschrijving</td><td class="w100">${this.#beschrijving.Html()}</td></tr>
                </table>`;
    }
    #naam;
    #beschrijving;

    #MaakValideNaam(naam) {
        let namen = [];
        for (let project of Object.values(BGProcesSimulator.Singletons('Projecten', {}))) {
            if (project !== this) {
                namen.push(project.Naam());
            }
        }
        if (naam === undefined || namen.includes(naam)) {
            return BGProcesSimulator.VrijeNaam(namen, 'Project #');
        }
        return naam;
    }
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
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(specificatie) {
        let isUitgangssituatie = specificatie.Soort === MogelijkeActiviteit.SoortActiviteit_Uitgangssituatie;
        super(isUitgangssituatie ? [] : BGProcesSimulator.This().Specificatie().Activiteiten, undefined, specificatie);
        this.#naam = this.Specificatie().Soort;
        this.#soort = MogelijkeActiviteit.SoortActiviteit[this.Specificatie().Soort];
        this.#soort.Naam = this.Specificatie().Soort;
        this.#tijdstip = new Tijdstip(this, this.Specificatie(), 'Tijdstip', true);
        this.#beschrijving = new Beschrijving(this.Specificatie(), this);
        if (isUitgangssituatie) {
            this.#project = new Project(this, Project.Code_Uitgangssituatie);
        } else {
            BGProcesSimulator.Singletons('Activiteiten', {})[this.Index()] = this;
            if (this.Specificatie().Project !== undefined) {
                this.#project = Project.Project(this.Specificatie().Project);
                if (this.#project === undefined) {
                    this.SpecificatieMelding(`Activiteit is onderdeel van een onbekend project met code "${this.Specificatie().Project}"`);
                }
            }
        }
    }

    /**
     * Aangeroepen als een activiteit verwijderd wordt
     */
    destructor() {
        if (this.Index() !== undefined) {
            delete BGProcesSimulator.Singletons('Activiteiten')[this.Index()];
            for (let activiteit of this.#blokkeertActiviteit) {
                delete activiteit.#blokkerendeActiviteiten[activiteit.#blokkerendeActiviteiten.indexOf(this)];
            }
            this.#blokkeertActiviteit = [];
        }
        super.destructor();
    }

    /**
     * Zet de specificatie om in een in-memory activiteit
     * @param {any} specificatie - Specificatie van de activiteit
     * @returns {Activiteit} - De activiteit, of undefined als de activiteit niet gemaakt kan worden
     */
    static LeesSpecificatie(specificatie) {
        let soort = MogelijkeActiviteit.SoortActiviteit[specificatie.Soort];
        if (soort.Constructor === undefined) {
            throw new Error(`Geen in-memory representatie beschikbaar voor activiteit ${specificatie.Soort}`);
        }
        let activiteit = undefined;
        try {
            activiteit = soort.Constructor(specificatie);
            activiteit.#isNieuw = false;
            activiteit.PasSpecificatieToe();
            activiteit.MeldInternDatamodel();
            return activiteit;
        } catch (e) {
            throw new Error(`Kan in-memory representatie activiteit "${specificatie.Soort}" niet aanmaken: ${e}`);
        }
    }
    //#endregion

    //#region Constanten
    static Systeem_Adviesbureau = "Software van het adviesbureau";
    static Systeem_BG = "Software van het bevoegd gezag";
    static Systeem_LVBB = "Bronhouderkoppelvlak LVBB";

    static Onderwerp_ScenarioFout = "Scenario";
    static Onderwerp_InternDatamodel = "Intern datamodel";
    static Onderwerp_Invoer = "Eindgebruiker";
    static Onderwerp_Procesbegeleiding = "Procesbegeleiding";
    static Onderwerp_Uitwisseling = "Uitwisseling";
    static Onderwerp_Verwerking_Invoer = "Verwerking invoer";

    static STOP_Data = "https://standaarden.overheid.nl/stop/imop/data/";
    static STOP_Consolidatie = "https://standaarden.overheid.nl/stop/imop/consolidatie/";
    //#endregion

    //#region Eigenschappen
    /**
     * Geef alle gespecificeerde activiteiten, gesorteerd op tijdstip
     * @param {Tijdstip} tijdstip - Optioneel: tijdstip waarop de activiteit uiterlijk uitgevoerd moet zijn - undefined voor alle activiteiten
     * @param {Project} project - Optioneel: project waarbij de activiteiten getoond moeten worden.
     */
    static Activiteiten(tijdstip, project) {

        return Object.values(BGProcesSimulator.Singletons('Activiteiten', {})).filter(
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

    /**
     * Geeft het project waarvoor deze activiteit is gespecificeerd.
     * Voor de niet-projectgebonden activiteiten is dit het project waarop de
     * wijzigingen aan regelgeving worden uitgevoerd voordat ze naar de andere
     * projecten worden gebruikt.
     * @returns {Project}
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
     * Geeft aan dat de activiteit verwijderd kan worden door de opsteller van het scenario.
     * Dit is niet mogelijk als het resultaat van deze activiteit gebruikt is in de specificatie
     * van een latere activiteit.
     * @returns
     */
    KanVerwijderdWorden() {
        return this.#blokkerendeActiviteiten.length === 0;
    }
    #blokkerendeActiviteiten = [];

    /**
     * Geeft aan dat het resultaat van de andere activiteit gebruikt is in de specificatie
     * van deze activiteit.
     * @param {Activiteit} activiteit
     */
    BlokkeerVerwijdering(activiteit) {
        this.#blokkeertActiviteit.push(activiteit);
        activiteit.#blokkerendeActiviteiten.push(this);
    }
    #blokkeertActiviteit = [];

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
     * @returns {string}
     */
    Naam() {
        return this.#naam;
    }
    #naam;

    /**
     * Geeft aan dat de activiteit de inhoud van een of meer branches wijzigt.
     * @returns {boolean}
     */
    IsWijziging() {
        return this.#soort.IsWijziging;
    }

    /**
     * Geeft aan of de activiteit vermeld moet worden in het overzicht van het project
     * @param {Project} project - Het project waarvoor het overzicht gemaakt wordt
     */
    ToonInProject(project) {
        if (project === null) {
            return false;
        }
        return this.Project() === project
    }

    /**
     * Geeft aan dat de momentopname door een adviesbureau is aangemaakt
     * @returns {boolean}
     */
    UitgevoerdDoorAdviesbureau() {
        for (let mo of this.Momentopnamen()) {
            return mo.UitgevoerdDoorAdviesbureau();
        }
    }

    /**
     * Als de activiteit leidt tot een publicatie of revisie: de naam van de bron ervan
     * met lidwoord.
     * @returns {string}
     */
    Publicatiebron() {

    }

    /**
     * Pas de specificatie toe voor de activiteit die zojuist is aangemaakt op basis van de specificatie.
     * Maakt standaard de momentopnamen bij als het een wijziging-activiteit betreft.
     */
    PasSpecificatieToe() {
        if (this.IsWijziging()) {
            this.VerwerkMomentopnameSpecificaties();
        }
    }

    /**
     * Als deze activiteit verwijderd wordt, dan moet VerwijderGerelateerdeActiviteiten alle activiteiten
     * verwijderen die niet kunnen bestaan zonder deze activiteit.
     */
    VerwijderGerelateerdeActiviteiten() {

    }

    /**
     * Genereer UitvoeringMeldingen die de stand van het interne datamodel rapporteren.
     * Standaard is een overzicht van de momentopnamen.
     */
    MeldInternDatamodel() {
        for (let momentopname of [...this.Momentopnamen()]) {
            momentopname.MeldInternDatamodel();
        }
    }
    //#endregion

    //#region Hulpfuncties voor de interpretatie van de specificatie
    /**
     * Registreer een melding over een probleem bij de toepassing van de specificatie
     * @param {string} melding - Te tonen melding
     */
    SpecificatieMelding(melding) {
        this.#heeftSpecificatieMeldingen = true;
        this.UitvoeringMelding(Activiteit.Onderwerp_ScenarioFout, melding);
    }
    #specificatieMeldingen = [];

    /**
     * Geeft aan of er meldingen over de specificatie zijn. Deze kunnen zowel bij het inlezen 
     * van de specificatie aangevuld worden als bij het wijzigen ervan, als een nieuwe activiteit
     * voor een eerdere datum leidt tot inconsistenties bij latere activiteiten.
     * @returns
     */
    HeeftSpecificatieMeldingen() {
        return this.#heeftSpecificatieMeldingen;
    }
    #heeftSpecificatieMeldingen = false;

    /**
     * Lees de specificaties van de momentopnamen voor deze activiteit 
     * @param {string} projectcode - De naam van het project waarvoor de momentopnamen worden aangemaakt
     *                               Alleen opgeven als de activiteit "Maak project" is en het project afwijkt van this.Project().
     */
    VerwerkMomentopnameSpecificaties(projectcode) {
        let specificatie = projectcode === undefined ? this.Specificatie() : this.Specificatie()[projectcode];
        let project = projectcode === undefined ? this.Project() : Project.Project(projectcode);

        bestaandeBranches = []
        if (this.IsWijziging()) {
            // Maak momentopnamen aan op basis van de branches in de specificatie
            let activiteitProps = ['Soort', 'Tijdstip', 'Beschrijving', 'Project'];
            activiteitProps.push(...activiteit.#soort.Props);
            for (let branchcode in specificatie) {
                if (!activiteitProps.includes(branchcode)) {
                    this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Maak een nieuwe momentopname voor de branch ${branchcode}.`);
                    this.VerwerkMomentopnameSpecificatie(branchcode, specificatie);
                    bestaandeBranches.push(branchcode);
                }
            }
        }

        // Voeg ook momentopnamen toe voor de overige momentopnamen uit het project
        for (let branch of Branch.Branches(this.Tijdstip(), project)) {
            if (!bestaandeBranches.includes(branch.Code())) {
                this.VerwerkMomentopnameSpecificatie(branch.Code(), specificatie);
                bestaandeBranches.push(branch.Code());
            }
        }

        // Verwijder momentopnamen die niet meer relevant zijn
        for (let momentopname of [...this.Momentopnamen()]) {
            if (!bestaandeBranches.include(momentopname.Branch().Code())) {
                momentopname.Verwijder();
            }
        }
    }


    /**
     * Maak een momentopname voor een branch als onderdeel van de specificatie
     * @param {string} branchcode - Code van de branch. De branch moet bestaan.
     * @param {any} specificatie - De specificatie voor zover die anders is dan de specificatie van deze activiteit
     * @param {bool/Tijdstip/Momentopname} werkUitgangssituatieBij - Geeft aan of de uitgangssituatie bijgewerkt moet worden,
     *                                              en evt voor welk tijdstip de geconsolideerde regelgeving gebruikt moet worden
     *                                              c.q. welke momentopname. 
     * @param {Momentopname[]} ontvlochtenversies - De wijzigingen die ontvlochten moeten worden met deze wijziging
     * @param {Momentopname[]} vervlochtenversies - De wijzigingen die vervlochten moeten worden met deze wijziging
     */
    VerwerkMomentopnameSpecificatie(branchcode, specificatie, werkUitgangssituatieBij = false, ontvlochtenversies, vervlochtenversies) {
        // Kijk of de momentopname al bestaat
        for (let momentopname of this.Momentopnamen()) {
            if (momentopname.Branch().Code() === branchcode) {
                return;
            }
        }
        // Zoek de branch op
        let branch = Branch.Branch(branchcode);
        if (branch === undefined) {
            this.SpecificatieMelding(this.Tijdstip(), `branch <code>${branchcode}</code> bestaat (nog) niet`);
            branch = new Branch(this, this.Project(), branchcode);
        }
        new Momentopname(this, specificatie === undefined ? this.Specificatie() : specificatie, branch, this.Soort().MomentopnameTijdstempels, werkUitgangssituatieBij, ontvlochtenversies, vervlochtenversies);
    }
    //#endregion

    //#region Resultaat van de activiteit
    /**
     * Vermeld een stap in de uitvoering van de activiteit
     * @param {any} onderwerp - Onderwerp waar de melding betrekking op heeft
     * @param {any} melding - Melding (HTML) van de stap in de uitvoering
     */
    UitvoeringMelding(onderwerp, melding) {
        if (this.#uitvoeringMeldingen.length === 0) {
            this.#uitvoeringMeldingen.push({
                Onderwerp: Activiteit.Onderwerp_Invoer,
                Melding: `De medewerker${BGProcesSimulator.This().BevoegdGezag() !== BGProcesSimulator.SoortBG_Gemeente ? '' : this.UitgevoerdDoorAdviesbureau() ? ' van het adviesbureau' : ' van het bevoegd gezag'} voert uit: ${this.Naam()}`
            });
        }
        this.#uitvoeringMeldingen.push({
            Onderwerp: onderwerp,
            Melding: melding
        });
    }
    #uitvoeringMeldingen = [];

    /**
     * Geeft de HTML voor het verslag van de uitvoering van de geselecteerde activiteit
     */
    UitvoeringsverslagHtml() {
        let html = '';
        if (this.#beschrijving.Specificatie()) {
            html += `<div class="scenario">Rol van deze activiteit in het scenario:${this.#beschrijving.Html('div')}</div>`;
        }
        if (this.#uitvoeringMeldingen.length === 0) {
            html += 'Er is geen verslag beschikbaar van de uitvoering van de activiteit.';
        } else {
            html += '<table>';

            let onderwerp;
            let trStart;
            let rows = []
            for (let melding of this.#uitvoeringMeldingen) {
                if (melding.Onderwerp !== onderwerp) {
                    if (rows.length > 0) {
                        html += `<tr${onderwerp === Activiteit.Onderwerp_ScenarioFout ? ' class="specmelding"' : ''}>
                                    <td rowspan="${rows.length}">${onderwerp === Activiteit.Onderwerp_ScenarioFout ? '<span class="specmelding">&#x26A0;</span>' : ''}</td>
                                    <td class="nw" rowspan="${rows.length}">${onderwerp}</td>
                                    <td>${rows.join('</td></tr><tr><td>')}</td>
                                 </tr>`;
                    }
                    onderwerp = melding.Onderwerp;
                    rows = [];
                }
                rows.push(melding.Melding);
            }
            if (rows.length > 0) {
                html += `<tr${onderwerp === Activiteit.Onderwerp_ScenarioFout ? ' class="specmelding"' : ''}>
                            <td rowspan="${rows.length}">${onderwerp === Activiteit.Onderwerp_ScenarioFout ? '<span class="specmelding">&#x26A0;</span>' : ''}</td>
                            <td class="nw" rowspan="${rows.length}">${onderwerp}</td>
                            <td>${rows.join('</td></tr><tr><td>')}</td>
                        </tr>`;
            }
            html += '</table>';
        }
        return html;
    }

    /**
     * Geeft aan of er STOP modules uitgewisseld zijn bij de uitvoering van de activiteit
     * @returns
     */
    HeeftUitwisselingen() {
        return this.#uitwisselingen.length > 0;
    }

    /**
     * Geeft de STOP modules benodigd als invoer voor de LVBB simulator
     * @returns {any[]} STOP-XML modules die tijdens de uitvoering van deze activiteit naar de LVBB gestuurd worden.
     */
    ModulesVoorLVBBSimulator() {
        return this.#uitwisselingen.filter(u => u.Ontvanger == Activiteit.Systeem_LVBB).map(u => new { ModuleNaam: u.ModuleNaam, STOPXml: u.STOPXml });
    }

    /**
     * Geef de uitwisselingen weer in HTML
     * @param {string} containerEltNaam - Naam van het element dat de HTML van de uitwisselingen ontvangt
     */
    ToonUitwisselingen(containerEltNaam) {
        if (this.#uitwisselingen.length == 0) {
            document.getElementById(containerEltNaam).innerHTML = 'Geen STOP modules uitgewisseld tijdens deze activiteit.'
            return;
        }
        let html = '';

        let systeemAfzender;
        let systeemOntvanger;
        let idx = 0;
        for (let uitwisseling of this.#uitwisselingen) {
            if (systeemAfzender != uitwisseling.Afzender || systeemOntvanger != uitwisseling.Ontvanger) {
                systeemAfzender = uitwisseling.Afzender;
                systeemOntvanger = uitwisseling.Ontvanger;
                html += `<p>${systeemAfzender} &#x21e8; ${systeemOntvanger}</p>`;
            }
            idx++;
            html += `<button data-accordion="_bgps_uitwisseling_${idx}_t" class="accordion_h active">${uitwisseling.ModuleNaam}</button>
    <div data-accordion-paneel="_bgps_uitwisseling_${idx}_t" class="accordion_h_paneel" style="display: block">
        <pre><code class="language-xml">
${uitwisseling.STOPXml.replace(/&/g, '&amp').replace(/</g, '&lt;').replace(/>/g, '&gt;')}
        </code></pre>
    </div>`
        }
        document.getElementById(containerEltNaam).innerHTML = html;
        document.querySelectorAll(`#${containerEltNaam} pre code`).forEach((elt) => {
            hljs.highlightElement(elt);
        });
        window.dispatchEvent(new CustomEvent('init_accordion', {
            cancelable: true
        }));
    }
    #uitwisselingen = [];

    /**
     * Voeg een STOP module toe die tijdens de uitvoering van deze activiteit uitgewisseld wordt.
     * @param {string} systeemAfzender - Systeem dat de XML verzendt
     * @param {string} systeemOntvanger - Systeem dat de XML ontvangt
     * @param {any} modules - Object dat de inhoud van de STOP XML module(s) reflecteert
     */
    VoegUitwisselingToe(systeemAfzender, systeemOntvanger, modules) {
        for (let moduleNaam in modules) {
            this.#uitwisselingen.push({
                Afzender: systeemAfzender,
                Ontvanger: systeemOntvanger,
                ModuleNaam: moduleNaam,
                STOPXml: Activiteit.ModuleToXml(moduleNaam, modules[moduleNaam])
            });
        }
    }

    /**
     * Vertaal een module naar STOP XML
     * @param {string} moduleNaam - Naam van de module
     * @param {any} module - Inhoud van de module
     */
    static ModuleToXml(moduleNaam, module) {
        let xml = `<${moduleNaam} xmlns="${module._ns}">`;
        xml = Activiteit.#ModuleToXml(xml, '  ', module);
        xml += `
</${moduleNaam}>`;
        return xml;
    }

    static #ModuleToXml(xml, indent, data) {
        if (data._comment) {
            xml += `
${indent}<!-- ${data._comment} -->`
        }
        for (let tag in data) {
            if (!tag.startsWith('_')) {
                let value = data[tag];
                if (typeof value !== "string" && Array.isArray(value)) {
                    for (let elt of value) {
                        xml += `
${indent}<${tag}>`;
                        xml = Activiteit.#ModuleToXml(xml, indent + '  ', elt);
                        xml += `
${indent}</${tag}>`;
                    }
                } else if (typeof value === "object") {
                    if (Object.keys(value).length > 0) {
                        xml += `
${indent}<${tag}>`;
                        xml = Activiteit.#ModuleToXml(xml, indent + '  ', value);
                        xml += `
${indent}</${tag}>`;
                    }
                } else {
                    xml += `
${indent}<${tag}>${value}</${tag}>`
                }
            }
        }
        return xml;
    }

    /**
     * Geef een overzicht van de status van het consolidatieproces na deze activiteit
     */
    Consolidatiestatus() {
        return this.#consolidatiestatus;
    }
    #consolidatiestatus = new Consolidatiestatus();

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
    //#endregion

    //#region Statusoverzichten
    /**
     * Weergave van de status van een project kort na het uitvoeren van een activiteit.
     * Het overzicht wordt samengesteld voor de laatst uitgevoerde activiteit voor het project,
     * @param {Activiteit} naActiviteit - De activiteit die zojuist is uitgevoerd.
     * @param {Project} project - Project waarvan de status weergegeven moet worden.
     * @returns {string} - Html
     */
    ProjectstatusHtml(naActiviteit, project) {
        let html = '';
        let uitvoerder = this.UitgevoerdDoorAdviesbureau() ? ' door een adviesbureau' : '';
        if (naActiviteit === this) {
            html += `<p class="entry_detail">Aan dit project is zojuist gewerkt${uitvoerder}.</p>`;
        } else {
            html += `<p class="entry_detail">Aan dit project is voor het laatst op ${this.Tijdstip().DatumTijdHtml()} gewerkt${uitvoerder}.</p>`;
        }

        let momentopnamen = this.Momentopnamen().filter((mo) => mo.Branch().Project() === project);
        momentopnamen.sort((a, b) => Branch.Vergelijk(a.Branch(), b.Branch()));

        html += '<table>';
        for (let mo of momentopnamen) {
            html += '<tr>';
            if (momentopnamen.length > 1) {
                html += `<td><b>${mo.Branch().InteractieNaam()}</b></td>`;
            }
            html += `<td>${mo.OverzichtHtml()}</td></tr>`;
        }
        html += '</table>';
        return html;
    }

    /**
     * Geef een overzicht van de status van de besluiten na deze activiteit
     */
    BesluitStatus() {
        return { Html: () => 'TODO' };
    }
    //#endregion

    //#region Ondersteuning implementatie specificatie-element
    /**
     * Geeft de HTML die opgenomen moet worden aan het begin van de WeergaveInnerHtml/InvoerInnerHtml
     */
    StartInnerHtml() {
        return `<h3>${this.Naam()}</h3>`;
    }

    /**
     * Geeft de HTML die opgenomen moet worden aan het einde van de WeergaveInnerHtml/InvoerInnerHtml
     */
    EindeInnerHtml() {
        let html = '';
        if (this.IsInvoer()) {
            html += `<div class="scenario">Geef een beschrijving van de rol van deze activiteit in het scenario (optioneel)${this.#beschrijving.Html()}</div>`;
        }
        return html;
    }
    #beschrijving;

    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix === 'AM' || idSuffix === 'AW') {
            // Wijzig activiteit
            this.OpenModal();
        }
        else if (idSuffix === 'AD') {
            // Verwijder de activiteit
            new VerwijderActiviteit(this).OpenModal();
        }
    }

    EindeModal(accepteerInvoer) {
        super.EindeModal(accepteerInvoer);
        if (accepteerInvoer) {
            this.#isNieuw = false;
            BGProcesSimulator.This().WerkScenarioUit(this.Tijdstip().Specificatie());
        } else if (this.#isNieuw) {
            // Activiteit is zojuist aangemaakt
            this.Verwijder();
        }
    }
    #isNieuw = true;
    //#endregion
}

/*------------------------------------------------------------------------------
*
* MogelijkeActiviteit bevat de logica voor de opvolging van de activiteiten
* 
*----------------------------------------------------------------------------*/
class MogelijkeActiviteit {

    //#region Initialisatie/toepassing logica
    /**
     * Bepaal welke activiteiten mogelijk zijn
     * @param {Tijdstip} tijdstip - Tijdstip waarop de activiteit uitgevoerd moet worden
     */
    constructor(tijdstip) {
        for (let project of Project.Projecten(tijdstip)) {
            let activiteiten = Activiteit.Activiteiten(tijdstip, project);
            let laatste = activiteiten[activiteiten.length - 1];
            if (laatste.UitgevoerdDoorAdviesbureau()) {
                switch (laatste.Soort().Naam) {
                    case MogelijkeActiviteit.SoortActiviteit_Uitwisseling:
                        // Laatste is levering van adviesbureau aan BG
                        activiteiten = [laatste];
                        break;
                    case MogelijkeActiviteit.SoortActiviteit_Download:
                        this.#bijAdviesbureau[project.Code()] = [MogelijkeActiviteit.SoortActiviteit_Wijziging];
                        continue;
                    default:
                        this.#bijAdviesbureau[project.Code()] = [MogelijkeActiviteit.SoortActiviteit_Wijziging, MogelijkeActiviteit.SoortActiviteit_Uitwisseling];
                        continue;
                }
            } else if (laatste.Soort().Naam == MogelijkeActiviteit.SoortActiviteit_Uitwisseling) {
                // Laatste is levering van BG aan adviesbureau
                this.#bijAdviesbureau[project.Code()] = [MogelijkeActiviteit.SoortActiviteit_Wijziging];
                continue;
            }
            // Bevoegd gezag gaat verder
            let mogelijk = [];
            for (let soort in MogelijkeActiviteit.SoortActiviteit) {
                if (soort === MogelijkeActiviteit.SoortActiviteit_Uitwisseling) {
                    if (Branch.Branches(tijdstip, project).length > 1) {
                        // Geen uitwisseling mogelijk bij meerdere branches
                        continue;
                    }
                }
                let kan = false;
                for (let act of activiteiten) {
                    if (MogelijkeActiviteit.SoortActiviteit[soort].KanVolgenOp.includes(act.Soort().Naam)) {
                        kan = true;
                        break;
                    }
                }
                if (kan && MogelijkeActiviteit.SoortActiviteit[soort].KanNietVolgenOp !== false) {
                    for (let act of activiteiten) {
                        if (MogelijkeActiviteit.SoortActiviteit[soort].KanNietVolgenOp.includes(act.Soort().Naam)) {
                            kan = false;
                            break;
                        }
                    }
                }
                if (kan) {
                    mogelijk.push(soort);
                }
            }
            if (mogelijk.length > 0) {
                this.#bijBevoegdGezag[project.Code()] = mogelijk;
            }
        }
    }
    //#endregion

    //#region Constanten
    static SoortActiviteit_Uitgangssituatie = 'Uitgangssituatie';
    static SoortActiviteit_MaakProject = 'Maak project';
    static SoortActiviteit_Download = 'Download';
    static SoortActiviteit_Uitwisseling = 'Uitwisseling';
    static SoortActiviteit_Wijziging = 'Wijziging';

    static SoortActiviteit = {
        'Uitgangssituatie': {
            KanVolgenOp: [],
            IsWijziging: false,
            Props: []
        },
        'Maak project': {
            KanVolgenOp: [],
            IsWijziging: false,
            Props: ['Invoer'],
            Constructor: (specificatie) => {
                if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente) {
                    return new Activiteit_MaakProject_Gemeente(specificatie);
                } else if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Rijksoverheid) {
                    return new Activiteit_MaakProject_Rijksoverheid(specificatie);
                }
            }
        },
        'Download': {
            KanVolgenOp: [],
            IsWijziging: false,
            Props: ['Invoer'],
            Constructor: (specificatie) => new Activiteit_Download(specificatie)
        },
        'Wijziging': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Download],
            KanNietVolgenOp: false,
            IsWijziging: true,
            Props: [],
            MomentopnameTijdstempels: false,
            MomentopnameProps: [],
            Constructor: (specificatie) => new Activiteit(specificatie),
            Beschrijving: 'Werk aan de volgende versie van regelingen en/of informatieobjecten.'
        },
        'Uitwisseling': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_Download, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: false,
            IsWijziging: false,
            Props: [],
            Constructor: (specificatie) => new Activiteit_Uitwisseling(specificatie),
            Beschrijving: 'Wissel een versie van de regelgeving uit tussen bevoegd gezag en adviesbureau.'
        },
        'Bijwerken uitgangssituatie': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: false,
            IsWijziging: true,
            Props: [],
            MomentopnameTijdstempels: false,
            MomentopnameProps: [],
            Constructor: (specificatie) => new Activiteit_BijwerkenUitgangssituatie(specificatie),
            Beschrijving: 'Neem de wijzigingen over die zijn aangebrancht in de uitgangssituatie voor dit project sinds de start van het project (of sinds de vorige keer dat de uitgangssituatie is bijgewerkt).'
        },
        'Maak branch': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: false,
            IsWijziging: true,
            Props: [],
            MomentopnameTijdstempels: false,
            MomentopnameProps: ['Soort', 'Branch', 'Branches'],
            Constructor: (specificatie) => new Activiteit_MaakBranch(specificatie),
            Beschrijving: ''
        },
        'Ontwerpbesluit': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: ['Concept-vaststellingsbesluit', 'Vaststellingsbesluit'],
            IsWijziging: true,
            Props: ['Begin inzagetermijn', 'Einde inzagetermijn'],
            MomentopnameTijdstempels: false,
            MomentopnameProps: [],
            Constructor: (specificatie) => new Activiteit_Ontwerpbesluit(specificatie),
            Beschrijving: 'Stel het ontwerpbesluit op en publiceer het.'
        },
        'Concept-vaststellingsbesluit': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: ['Vaststellingsbesluit'],
            IsWijziging: true,
            Props: [],
            MomentopnameTijdstempels: true,
            MomentopnameProps: [],
            Constructor: (specificatie) => new Activiteit_Vaststellingsbesluit(specificatie),
            Beschrijving: 'Stel het vaststellingsbesluit op; deze versie wordt gebruikt voor de interne besluitvorming binnen het bevoegd gezag.'
        },
        'Vaststellingsbesluit': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: false,
            IsWijziging: true,
            Props: ['Einde beroepstermijn'],
            MomentopnameTijdstempels: true,
            MomentopnameProps: [],
            Constructor: (specificatie) => new Activiteit_Vaststellingsbesluit(specificatie),
            Beschrijving: 'Finaliseer het vaststellingsbesluit en maak het bekend.'
        }
    };
    //#endregion

    //#region Eigenschappen
    /**
     * Geef een lijst van projecten waaraan door een adviesbureau gewerkt kan worden
     * @param {boolean} voorBevoegdGezag - Geeft aan of de projecten voor het bevoegd gezag zijn (in plaats van voor een adviesbureau)
     * @returns {Project[]}
     */
    ActiviteitenMogelijk(voorBevoegdGezag) {
        return Object.keys(voorBevoegdGezag ? this.#bijBevoegdGezag : this.#bijAdviesbureau).length > 0;
    }

    /**
     * Geef een lijst van projecten waaraan door een adviesbureau gewerkt kan worden
     * @param {boolean} voorBevoegdGezag - Geeft aan of de projecten voor het bevoegd gezag zijn (in plaats van voor een adviesbureau)
     * @returns {Project[]}
     */
    Projecten(voorBevoegdGezag) {
        let projecten = [];
        for (let code of Object.keys(voorBevoegdGezag ? this.#bijBevoegdGezag : this.#bijAdviesbureau)) {
            projecten.push(Project.Project(code));
        }
        projecten.sort((a, b) => a.Naam().localeCompare(b.Naam()));
        return projecten;
    }
    #bijAdviesbureau = {};
    #bijBevoegdGezag = {};

    /**
     * Geef de soort activiteiten die voor een project uitgevoerd kunnen worden
     */
    ProjectActiviteiten(projectcode) {
        let soorten = this.#bijBevoegdGezag[projectcode];
        if (soorten === undefined) {
            soorten = this.#bijAdviesbureau[projectcode];
        }
        return soorten;
    }
    //#endregion
}

/*------------------------------------------------------------------------------
*
* NieuweActiviteit is een hulpklasse om een nieuwe activiteit toe te voegen.
* 
*----------------------------------------------------------------------------*/
class NieuweActiviteit extends SpecificatieElement {

    //#region Initialisatie
    constructor() {
        // Niet direct gerelateerd aan een specificatie, gebruik alleen de invoermogelijkheden
        super();
        this.#tijdstip = new Tijdstip(this, { Tijdstip: 1 }, 'Tijdstip', true);
    }
    //#endregion

    //#region Implementatie van SpecificatieElement
    WeergaveInnerHtml() {
        return `${this.HtmlVoegToe("Voeg een nieuwe activiteit toe", "N")} Nieuwe activiteit`;
    }

    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix === 'N') {
            let inTeVoeren = this;
            if (Project.Projecten().length == 0) {
                if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente) {
                    if (Consolidatiestatus.GeenConsolidatieAanwezig()) {
                        // Er zijn nog geen projecten en er is ook nog geen geldende regelgeving te downloaden. Het maken van een nieuw project door het bevoegd gezag is de enig mogelijke activiteit.
                        inTeVoeren = this.#MaakActiviteit(MogelijkeActiviteit.SoortActiviteit_MaakProject, 1);
                    }
                } else {
                    // Er zijn nog geen projecten. Het maken van een nieuw project is de enig mogelijke activiteit.
                    inTeVoeren = this.#MaakActiviteit(MogelijkeActiviteit.SoortActiviteit_MaakProject, 1);
                }
            } else if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente && !Consolidatiestatus.GeenConsolidatieAanwezig()) {
                // Er is nog geen geldende regelgeving te downloaden; alleen het bevoegd gezag kan activiteiten ontplooien.'
                this.#adviesbureau = false;
            }
            inTeVoeren.OpenModal();
        }
    }

    BeginInvoer() {
        this.#mogelijkeActiviteit = undefined;
        this.#soortActiviteit = undefined;
        let activiteiten = Activiteit.Activiteiten();
        if (activiteiten.length > 0) {
            this.#tijdstip.SpecificatieWordt(Math.floor(activiteiten[activiteiten.length - 1].Tijdstip().Specificatie()) + 1);
            this.#tijdstip.BeginInvoer();
        }
    }

    InvoerInnerHtml() {
        if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente && Consolidatiestatus.GeenConsolidatieAanwezig()) {
            switch (this.InvoerStap()) {
                case 1: return this.#SelecteerWieWanneer();
                case 2: if (this.#adviesbureau) {
                    return this.#SelecteerActiviteit(false);
                } else {
                    return this.#SelecteerActiviteit(true);
                }
            }
        } else {
            return this.#SelecteerActiviteit(true);
        }
    }

    #SelecteerWieWanneer() {
        this.VolgendeStapNodig();
        return `<table>
            <tr><td>Wie is de eindgebruiker?</td><td>Medewerker van <input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('BG')}"${this.#adviesbureau ? '' : ' checked'}> <label for="${this.ElementId('BG')}">bevoegd gezag</label>
                                                        / <input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('AB')}"${this.#adviesbureau ? ' checked' : ''}> <label for="${this.ElementId('AB')}">adviesbureau</label></td></tr>
            <tr><td>Tijdstip van uitvoering</td><td>${this.#tijdstip.Html()}</td></tr>
            </table>`;
    }
    #adviesbureau;
    #tijdstip;

    #SelecteerActiviteit(voorBevoegdGezag) {
        if (this.#mogelijkeActiviteit === undefined) {
            this.#mogelijkeActiviteit = new MogelijkeActiviteit(this.#tijdstip);
        }
        let heeftProjecten = this.#mogelijkeActiviteit.ActiviteitenMogelijk(voorBevoegdGezag);
        let html = `Welke activiteit voert de medewerker van het ${voorBevoegdGezag ? 'bevoegd gezag' : 'adviesbureau'} uit?
        <dl>
        <dt><input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('N')}"${this.#projectcode === undefined || !heeftProjecten ? ' checked' : ''}> <label for="${this.ElementId('N')}">Maak een nieuw project${voorBevoegdGezag ? '' : ' via download uit de LVBB'}</label></dt>
        <dt><input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('B')}"${this.#projectcode !== undefined && heeftProjecten ? ' checked' : ''}${heeftProjecten ? '' : ' disabled'}> <label for="${this.ElementId('B')}">Voor het project:</label> `;
        if (heeftProjecten) {

            html += `<select id="${this.ElementId('P')}">`;
            if (this.#projectcode === undefined) {
                html += `<option value="" selected></option>`;
            }
            for (let project of this.#mogelijkeActiviteit.Projecten(voorBevoegdGezag)) {
                html += `<option value="${project.Code()}"${this.#projectcode === project.Code() ? ' selected' : ''}>${project.Naam()}</option>`;
            }
            html += '</select>';

            if (this.#projectcode === undefined) {
                html += '</dt>';
            } else {
                html += `: <select id="${this.ElementId('A')}">`;
                if (this.#soortActiviteit === undefined) {
                    html += `<option value="" selected></option>`
                }
                for (let soort of this.#mogelijkeActiviteit.ProjectActiviteiten(this.#projectcode)) {
                    html += `<option value="${soort}"${this.#soortActiviteit === soort ? ' selected' : ''}>${soort}</option>`
                }
                html += '</select></dt>';
                if (this.#soortActiviteit !== undefined) {
                    html += `<dd>(${MogelijkeActiviteit.SoortActiviteit[this.#soortActiviteit].Beschrijving})</dd>`;
                }
            }
        } else {
            html += ' (geen projecten beschikbaar)</dt>';
        }
        html += `</dl>`;
        return html;
    }
    #mogelijkeActiviteit;
    #projectcode;
    #soortActiviteit;

    OnInvoerChange(elt, idSuffix) {
        switch (idSuffix) {
            case 'P':
                if (elt.selectedIndex < 0 || elt.value === '') {
                    this.#projectcode = undefined;
                } else {
                    this.#projectcode = elt.value;
                    this.#soortActiviteit = undefined;
                    if (elt.options[0].value === '') {
                        elt.remove(0);
                    }
                }
                this.VervangInnerHtml();
                break;
            case 'A':
                if (elt.selectedIndex < 0) {
                    this.#soortActiviteit = undefined;
                } else {
                    this.#soortActiviteit = elt.value;
                    if (elt.options[0].value === '') {
                        elt.remove(0);
                    }
                }
                this.VervangInnerHtml();
                break;
        }
    }

    OnInvoerClick(elt, idSuffix) {
        switch (idSuffix) {
            case 'AB':
                this.#adviesbureau = true;
                return;
            case 'BG':
                this.#adviesbureau = false;
                return;
            case 'N':
                if (elt.checked) {
                    this.#projectcode = undefined;
                    this.VervangInnerHtml();
                }
                return;
        }
    }

    ValideerInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            switch (this.InvoerStap()) {
                case 1:
                    let ok = true;
                    while (true) {
                        let activiteiten = Activiteit.Activiteiten(this.#tijdstip);
                        if (activiteiten.length > 0 && this.#tijdstip.IsGelijk(activiteiten[activiteiten.length - 1].Tijdstip())) {
                            this.#tijdstip.SpecificatieWordt(this.#tijdstip.Specificatie() + 0.01);
                            ok = false;
                        } else {
                            break;
                        }
                    }
                    if (!ok) {
                        this.VervangInnerHtml();
                        return true;
                    }
                case 2:
                    if (this.#projectcode !== undefined && this.#soortActiviteit === undefined) {
                        return true;
                    }
                    break;
            }
        }
    }

    EindeModal(accepteerInvoer) {
        if (accepteerInvoer) {
            let activiteit;
            if (this.#projectcode === undefined) {
                activiteit = this.#MaakActiviteit(this.#adviesbureau ? MogelijkeActiviteit.SoortActiviteit_Download : MogelijkeActiviteit.SoortActiviteit_MaakProject, this.#tijdstip.Specificatie());
            } else {
                activiteit = this.#MaakActiviteit(this.#soortActiviteit, this.#tijdstip.Specificatie(), this.#projectcode);
            }
            activiteit.UitvoeringMelding(Activiteit.Onderwerp_Simulator, `Door het ${this.#adviesbureau ? 'adviesbureau' : 'bevoegd gezag'} uit te voeren activiteit: ${activiteit.Naam()}`);
            activiteit.OpenModal();
        }
    }
    //#endregion

    //#region Interne functionaliteit
    /**
     * Maak een nieuwe activiteit aan
     * @param {string} soort - Soort activiteit
     * @param {float} tijdstip - Tijdstip van de activiteit
     * @param {string} projectcode - Optioneel: project waar de activiteit onderdeel van is
     * @returns {Activiteit}
     */
    #MaakActiviteit(soort, tijdstip, projectcode) {
        let definitie = MogelijkeActiviteit.SoortActiviteit[soort];
        let specificatie = {
            Soort: soort,
            Tijdstip: tijdstip
        };
        if (projectcode !== undefined) {
            specificatie.Project = projectcode;
        }
        return definitie.Constructor(specificatie);
    }
    //#endregion
}

/*------------------------------------------------------------------------------
*
* NieuweActiviteit is een hulpklasse om een activiteit te verwijderen.
* 
*----------------------------------------------------------------------------*/
class VerwijderActiviteit extends SpecificatieElement {

    //#region Initialisatie
    /**
     * Maak een verwijder-actie aan voor de activiteit
     * @param {Activiteit} activiteit
     */
    constructor(activiteit) {
        // Niet direct gerelateerd aan een specificatie, gebruik alleen de invoermogelijkheden
        super();
        this.#activiteit = activiteit
    }
    //#endregion

    //#region Implementatie van SpecificatieElement
    /**
     * Aangeroepen om de HTML voor een read-only weergave te maken van de invoer.
     * Deze wordt gepresenteerd binnen de container die door WeergaveHtml wordt klaargezet 
     * Wordt geïmplementeerd in afgeleide klassen.
     */
    WeergaveInnerHtml() {
        return `<p>De volgende activiteit wordt verwijderd:</p>
<table>
<tr><th>Activiteit</th><td>${this.#activiteit.Naam()}</td></tr>
<tr><th>Tijdstip</th><td>${this.#activiteit.Tijdstip().Html()}</td></tr>
</table>`;
    }
    #activiteit;

    EindeModal(accepteerInvoer) {
        if (accepteerInvoer) {
            this.Verwijder();

            let tijdstip = this.#activiteit.Tijdstip().Specificatie();
            this.#activiteit.VerwijderGerelateerdeActiviteiten();
            this.#activiteit.Verwijder();

            BGProcesSimulator.This().WerkScenarioUit(tijdstip);
        }
    }
    #nieuweActiviteit;
    //#endregion
}
//#endregion

//#region Implementatie van de activiteiten

//#region MaakProject

class Activiteit_MaakProject_Gemeente extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(specificatie) {
        super(specificatie);
        if (this.Specificatie().Invoer !== undefined) {
            this.#project = new Project(this, this.Specificatie().Invoer.Project);
            this.#branch = new Branch(this, this.#project, this.Specificatie().Invoer.Branch);
        } else {
            this.#project = new Project(this);
            this.Specificatie().Invoer = {
                Project: this.#project.Code()
            };
        }
        this.#InterpreteerInvoer();
    }
    //#endregion

    //#region Implementatie van de activiteit
    Naam() {
        return "Maak nieuw project";
    }

    Project() {
        return this.#project;
    }
    #project;

    PasSpecificatieToe() {
        if (this.#branch === undefined) {
            throw new Error(`Geen branch opgegeven voor nieuw project (Tijdstip = ${this.Tijdstip().Specificatie})`);
        }
        this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker voert de gegevens van het nieuwe project in.');
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Het project wordt aangemaakt.`);
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Voor het project wordt één nieuwe branch aangemaakt.`);
        this.#branch.MeldUitvoering();
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Maak een eerste momentopname voor de branch ${this.#branch.Code()}.`);
        this.VerwerkMomentopnameSpecificatie(this.#branch.Code());
    }

    VerwijderGerelateerdeActiviteiten() {
        for (let activiteit of Activiteit.Activiteiten(undefined, this.#project)) {
            activiteit.Verwijder();
        }
    }
    //#endregion

    //#region Implementatie specificatie-element
    BeginInvoer() {
        if (this.#isOnafhankelijk === undefined) {
            let andereProjecten = Project.Projecten(this.Tijdstip()).filter((p) => p !== this.#project);
            if (andereProjecten.length === 0) {
                this.#isOnafhankelijk = true;
            }
        }
    }
    #InterpreteerInvoer() {
        this.#isOnafhankelijk = undefined;
        this.#volgtOpProject = undefined;
        this.#volgtOpBranch = undefined;
        if (this.#branch !== undefined) {
            this.#isOnafhankelijk = this.#branch.Soort() == Branch.Soort_GeldendeRegelgeving;
            if (this.#branch.Soort() == Branch.Soort_VolgtOpAndereBranch) {
                this.#volgtOpBranch = this.#branch.VolgtOpBranch();
                this.#volgtOpProject = this.#volgtOpBranch.Project();
            }
        }
    }
    #branch;
    #isOnafhankelijk;
    #volgtOpProject;
    #volgtOpBranch;

    WeergaveInnerHtml() {
        let disabled = !this.IsInvoer() || this.IsReadOnly() ? ' disabled' : '';
        let andereProjecten = Project.Projecten(this.Tijdstip()).filter((p) => p !== this.#project);

        let html = `${this.StartInnerHtml()}<p>Welk soort project moet aangemaakt worden?</p>
        <dl>
        <dt><input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('O')}"${this.#isOnafhankelijk === true ? ' checked' : ''}${disabled}> <label for="${this.ElementId('O')}">Onafhankelijk project</label></dt>
        <dd>Een nieuw project waarin regelgeving onafhankelijk van andere projecten aangepast wordt.</dd>
        <dt><input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('V')}"${this.#isOnafhankelijk === false ? ' checked' : ''}${andereProjecten.length === 0 ? ' disabled' : disabled}> <label for="${this.ElementId('V')}">Vervolgproject</label></dt>
        <dd>Een nieuw project dat voortbouwt op de regelgeving die in een ander (nog lopend) project wordt voorbereid`;
        if (andereProjecten.length === 0) {
            html += '. Op dit moment lopen er geen andere projecten.';
        } else {
            html += `, namelijk:<br><select id="${this.ElementId('P')}">`;
            if (this.#volgtOpProject === undefined) {
                html += '<option value="" selected></option>';
            }
            for (let prj of andereProjecten) {
                html += `<option value="${prj.Code()}"${this.#volgtOpProject === prj ? ' selected' : ''}>${prj.Naam()}</option>`;
            }
            html += '</select>';
            if (this.#volgtOpProject !== undefined) {
                let projectBranches = Branch.Branches(this.Tijdstip(), this.#volgtOpProject);
                if (projectBranches.length > 1) {
                    html += `<select id="${this.ElementId('B')}">`;
                    if (this.#volgtOpBranch === undefined) {
                        html += '<option value="" selected></option>';
                    }
                    for (let branch of projectBranches) {
                        html += `<option value="${branch.Code()}"${this.#volgtOpBranch === branch ? ' selected' : ''}>${branch.InteractieNaam()}</option>`;
                    }
                    html += '</select>';
                }
            }
        }
        html += `</dd>
        </dl>
        ${this.#project.Html()}
        ${this.EindeInnerHtml()}`;

        return html;
    }

    OnInvoerChange(elt, idSuffix) {
        switch (idSuffix) {
            case 'P':
                if (elt.selectedIndex < 0 || elt.value === '') {
                    this.#volgtOpProject = undefined;
                    this.#volgtOpBranch = undefined;
                } else {
                    this.#isOnafhankelijk = false;
                    this.#volgtOpProject = Project.Project(elt.value);
                    let projectBranches = Branch.Branches(this.Tijdstip(), this.#volgtOpProject);
                    this.#volgtOpBranch = projectBranches.length == 1 ? projectBranches[0] : undefined;
                    if (elt.options[0].value === '') {
                        elt.remove(0);
                    }
                }
                this.VervangInnerHtml();
                break;
            case 'B':
                if (elt.selectedIndex < 0 || elt.value === '') {
                    this.#volgtOpBranch = undefined;
                } else {
                    this.#volgtOpBranch = Branch.Branch(elt.value);
                    if (elt.options[0].value === '') {
                        elt.remove(0);
                    }
                }
                this.VervangInnerHtml();
                break;
        }
    }

    OnInvoerClick(elt, idSuffix) {
        switch (idSuffix) {
            case 'O':
                this.#isOnafhankelijk = true;
                this.#volgtOpProject = undefined;
                this.#volgtOpBranch = undefined;
                this.VervangInnerHtml();
                break;
            case 'V':
                this.#isOnafhankelijk = false;
                this.VervangInnerHtml();
                break;
        }
    }

    ValideerInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            if (!this.#isOnafhankelijk && this.#volgtOpBranch === undefined) {
                return true;
            }
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            let naam = this.#branch !== undefined ? this.#branch.Naam() : 'Regelgeving waarvoor het project is ingericht';
            let beschrijving = this.#branch !== undefined ? this.#branch.Beschrijving() : 'De regelgeving waaraan binnen het project gewerkt wordt/is. Als er meerdere branches in het project zijn, dan is dit de regelgeving voor het eerste inwerkingtredingmoment.';
            if (this.#branch !== undefined) {
                this.#branch.Verwijder();
            }
            if (this.#isOnafhankelijk) {
                this.#branch = Branch.MaakBranch(this, this.#project, this.Specificatie().Invoer.Branch, naam, beschrijving, Branch.Soort_GeldendeRegelgeving);
            } else {
                this.#branch = Branch.MaakBranch(this, this.#project, this.Specificatie().Invoer.Branch, naam, beschrijving, Branch.Soort_VolgtOpAndereBranch, this.#volgtOpBranch);
            }
            this.Specificatie().Invoer.Branch = this.#branch.Code();
        }
        this.#InterpreteerInvoer();
    }
    //#endregion
}


//#endregion

//#region MaakBranch
class Activiteit_MaakBranch extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(specificatie) {
        super(specificatie);
    }
    //#endregion

    //#region Implementatie van de activiteit
    LeesMomentopnameSpecificaties(branchnamen) {

        // Maak een lijst van alle bekende branches
        let alleBranches = {};
        for (let branch of Branch.Branches(this.Tijdstip())) {
            alleBranches[branch.Code()] = branch;
        }

        // Controleer op dubbele namen
        let nogAanmaken = branchnamen;
        let nogSteedsAanmaken = [];
        branchnamen = [];
        for (let branchnaam of nogAanmaken) {
            if (branchnaam in alleBranches) {
                this.SpecificatieMelding(`Branch '${branchnaam}' bestaat al`);
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
                        this.SpecificatieMelding(`Branch='${andereBranchnaam}' van branch '${branchnaam}' ontbreekt`);
                    } else if (andereBranchnaam in alleBranches) {
                        alleBranches[branchnaam] = new Branch(this, branchnaam, alleBranches[andereBranchnaam]);
                        branchnamen.push(branchnaam);
                        isGemaakt = true
                    } else {
                        this.SpecificatieMelding(`Branch '${andereBranchNaam}' als basis voor branch '${branchnaam}' bestaat (nog) niet`);
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
                        this.SpecificatieMelding(`Branches ontbreekt in branch '${branchnaam}'"`);
                    } else {
                        let andereBranches = [];
                        let branchDitProject;
                        let ok = true;
                        for (let andereBranchNaam of andereBranchnamen) {
                            let andereBranch = alleBranches[andereBranchNaam];
                            if (andereBranch === undefined) {
                                this.SpecificatieMelding(`Branch '${andereBranchNaam}' als basis voor branch '${branchnaam}' bestaat (nog) niet`);
                                ok = false;
                            } else {
                                andereBranches.push(andereBranch);
                                if (branchDitProject === undefined) {
                                    branchDitProject = andereBranch;
                                    if (branchDitProject.Project() !== this.Project()) {
                                        this.SpecificatieMelding(`Branch '${andereBranchNaam}' als basis voor branch '${branchnaam}' moet bij hetzelfde project horen`);
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
                this.SpecificatieMelding(`Branches '${nogSteedsAanmaken.join("', '")}' kunnen niet aangemaakt worden`);
                break;
            }
        }
        // Lees nu de branches in
        super.LeesMomentopnameSpecificaties(branchnamen);
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
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(specificatie) {
        super(specificatie);
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
            this.SpecificatieMelding(`Branch ontbreekt`);
        } else if (Branch.Branch(branchnaam) !== undefined) {
            this.SpecificatieMelding(`Branch '${branchnaam}' bestaat al`);
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
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(specificatie) {
        super(specificatie);
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
            this.SpecificatieMelding(`Een uitwisseling kan alleen gedaan worden voor een project met één branch.`);
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
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(specificatie) {
        super(specificatie);
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
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(specificatie) {
        super(specificatie);
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
     * @param {any} specificatie - Specificatie van de activiteit
     */
    constructor(specificatie) {
        super(specificatie);
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

