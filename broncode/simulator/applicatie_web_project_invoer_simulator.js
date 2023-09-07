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
        let simulator = new BGProcesSimulator(elt_simulator, soortBG);
        simulator.#VertaalSpecificatie()
        return simulator;
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
        if (BGProcesSimulator.Opties.AnnotatiesViaUitgangssituatie) {
            // Maak de vertaling opnieuw
            this.WerkScenarioUit(0);
        }
    }
    //#endregion

    //#region Constanten
    static SoortBG_Gemeente = 'Gemeente';
    static SoortBG_Rijksoverheid = 'Rijksoverheid';
    static STOP_Versie = '2.0.0' === '@@@IMOP' + '_Versie@@@' ? '2.0.0' : '2.0.0';
    //#endregion

    //#region Eigenschappen
    /**
     * Instantie van de generator voor het huidige scenario
     * @returns {BGProcesSimulator}
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
        NonStopAnnotaties: false,
        /**
         * Geeft aan dat voor de overerving van ongewijzigde annotaties de juridische
         * uitgangssituatie gebruikt wordt in plaats van de basisversie.
         */
        AnnotatiesViaUitgangssituatie: false
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
    #isNieuw = true;

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
        return this.#data.BGCode ?? this.BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente ? "gm9999" : "mnre9999";
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
    /** @type {Startdatum} */
    #startdatum;

    /**
     * De uitgangssituatie van het scenario
     * @returns {Uitgangssituatie}
     */
    Uitgangssituatie() {
        return this.#uitgangssituatie;
    }
    /** @type {Uitgangssituatie} */
    #uitgangssituatie;

    /**
     * Verzamelbak voor singletons voor andere klassen
     * @param {string} naam - Naam van de singleton; weglaten om alle singletons te zien
     * @param {any} defaultWaarde - Optioneel; default waarde van de singleton in het geval die nog niet bestaat
     */
    static Singletons(naam, defaultWaarde) {
        if (!naam) {
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
        for (let idx = 1; true; idx++) {
            let naam = (prefix ?? '') + ('00' + idx).slice(-2);
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
                simulator.#isNieuw = false;
            }
            else {
                throw new Error('Invalide specificatie - onbekend bevoegd gezag');
            }
        } else {
            throw new Error('Invalide specificatie - bevoegd gezag ontbreekt');
        }
        if (data.BGCode && data.BGCode !== simulator.BGCode()) {
            simulator.#data.BGCode = data.BGCode;
        }
        if (data.Naam) {
            simulator.#data.Naam = data.Naam;
        }
        if (data.Beschrijving) {
            simulator.#data.Beschrijving = data.Beschrijving;
        }
        if (data.Startdatum) {
            simulator.#data.Startdatum = new Startdatum(simulator.#data).Specificatie();
        }

        let regelingen = {};
        let uuidAanwezig = {};
        function copyWijziging(onderdeel, target, src, extraProps) {
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
        function copyActiviteiten(target, src) {
            for (let activiteit of src) {
                if (!activiteit.Soort) {
                    throw new Error('Elke activiteit moet een eigenschap "Soort" hebben.')
                }
                let spec = MogelijkeActiviteit.SoortActiviteit[activiteit.Soort];
                if (!spec) {
                    throw new Error(`Onbekende activiteit: "Soort": "${activiteit.Soort}".`)
                }
                if (!activiteit.Tijdstip) {
                    throw new Error(`Elke activiteit moet een eigenschap "Tijdstip" hebben ("Soort": "${activiteit.Soort}").`)
                }
                let tijdstip = Tijdstip.Maak(activiteit.Tijdstip);
                if (tijdstippen.includes(tijdstip.Specificatie())) {
                    throw new Error(`Elk "Tijdstip" moet een unieke waarde hebben ("Tijdstip": ${activiteit.Tijdstip}).`)
                }

                let targetActiviteit = {};
                target.push(targetActiviteit);
                for (let prop in activiteit) {
                    if (['Soort', 'Tijdstip', 'Beschrijving', 'Project'].includes(prop) || spec.Props.includes(prop)) {
                        targetActiviteit[prop] = activiteit[prop];
                    } else if (prop.includes('_')) {
                        // Moet een branch zijn
                        targetActiviteit[prop] = {};
                        let mprops = spec.MomentopnameTijdstempels ? ['JuridischWerkendVanaf', 'GeldigVanaf'] : [];
                        mprops.push(...spec.MomentopnameProps);
                        copyWijziging(`activiteit "${activiteit.Soort}", branch "${prop}"`, targetActiviteit[prop], activiteit[prop], mprops);
                    } else {
                        // Geen branch maar iets anders, zoals een project
                        targetActiviteit[prop] = activiteit[prop];
                    }
                }
            }
        }

        copyWijziging('start', simulator.#data.start, data.start, []);
        if (data.Activiteiten) {
            copyActiviteiten(simulator.#data.Activiteiten, data.Activiteiten);
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
        this.#startdatum = new Startdatum(this.#data.Startdatum ? this.#data : {});

        // Maak de uitgangssituatie aan
        this.#uitgangssituatie = new Uitgangssituatie(this.#data);
        this.#uitgangssituatie.PasSpecificatieToe();
        this.#uitgangssituatie.Consolidatiestatus()?.WerkBij(undefined, this.#uitgangssituatie);

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
            voorgaandeConsolidatie?.WerkBij(undefined, this.#uitgangssituatie);
        } else {
            let activiteiten = Activiteit.Activiteiten();
            if (activiteiten.length > 0) {
                voorgaandeConsolidatie = activiteiten[activiteiten.length - 1].Consolidatiestatus();
            }
        }

        // Maak het interne datamodel voor activiteiten aan
        for (let activiteitSpecificatie of activiteitenSpecificatie) {
            let activiteit = Activiteit.LeesSpecificatie(activiteitSpecificatie);
            if (!activiteit) {
                break;
            }
            voorgaandeConsolidatie = activiteit.Consolidatiestatus().WerkBij(voorgaandeConsolidatie, activiteit);
        }
    }
    //#endregion

    //#region Specificatie voor simulatoren maken
    /**
     * Werk de downloadbare specificaties bij
     */
    WerkSpecificatiesBij() {
        // Maak specificatie van dit scenario downloadbaar
        let json = this.#MaakSpecificatie();
        if (json) {
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
    }

    /**
     * Maak de downloadbare JSON specificatie voor deze simulator
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
        if (value === null) {
            return false;
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
        if (!titel) {
            titel = `Scenario voor ${this.#data.BevoegdGezag === BGProcesSimulator.SoortBG_Gemeente ? "een gemeente" : "de rijksoverheid"}`;
        }
        if (isNieuweVersie) {
            document.title = 'Simulator - ' + titel;
        }
        return titel;
    }

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
                if (!elt) {
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
            Titel: this.#data.Naam,
            Beschrijving: this.#data.Beschrijving,
            Uitwisselingen: []
        };
        for (let activiteit of Activiteit.Activiteiten()) {
            if (activiteit.HeeftUitwisselingen() && (activiteit.IsOfficielePublicatie() || activiteit.IsRevisie())) {
                beschrijving.Uitwisselingen.push({
                    naam: `${activiteit.Project().Naam()}: ${activiteit.Naam()}`,
                    gemaaktOp: activiteit.Tijdstip().STOPDatumTijd(),
                    beschrijving: activiteit.Specificatie().Beschrijving,
                    revisie: activiteit.IsRevisie()
                });
            }
        }
        if (this.Uitgangssituatie().Instrumentversies().length > 0) {
            beschrijving.Uitwisselingen.push({
                naam: 'Uitgangssituatie',
                gemaaktOp: this.Uitgangssituatie().Tijdstip().STOPDatumTijd(),
                beschrijving: 'De regelgeving die in werking is bij de start van het scenario.',
                revisie: true
            });
        }
        let json = JSON.stringify(beschrijving, BGProcesSimulator.#ObjectFilter, 4)?.trim();
        if (json) {
            let elt = this.#elt_lvbb_form.elements[`onlineInvoer${++numBestanden}`];
            if (!elt) {
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
            if (!elt) {
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
        this.#diagram = new VersiebeheerDiagram();
        let html = `
<div id="_bgps_modal" class="modal">
  <div class="modal-content">
    <span class="modal-close"><span id="_bgps_modal_volgende">&#x276F;&#x276F;</span> <span id="_bgps_modal_ok">&#x2714;</span> <span id="_bgps_modal_cancel">&#x2716;</span></span>
    <p id="_bgps_modal_content"></p>
  </div>
</div>
<button data-accordion="_bgps_s1" class="accordion_h${this.#isNieuw ? ' active' : ''}">Over het scenario</button>
<div data-accordion-paneel="_bgps_s1" class="accordion_h_paneel"${this.#isNieuw ? ' style = "display: block"' : ''}>
<p>
<b>Naam/titel van het scenario</b><br>
${new Naam(this.#data, undefined, (n, a) => this.#MaakValideTitel(n, a)).Html()}
</p>
<p>
<b>Beschrijving van het scenario</b><br>
Geef een korte beschrijving van het scenario waarvoor deze specificatie is opgesteld (optioneel)
${new Beschrijving(this.#data).Html()}
</p>
<p>
<b>Uitgangssituatie</b> per ${this.#startdatum.Html()}<br>
${this.#uitgangssituatie.Html()}
</p>
</div>
<div class="sectie_op" data-bh="0"><h1>Simulatie - User interface</h1>
<table>
    <tr><td rowspan="3" class="nw" id="_bgps_activiteiten"></td>
    <th id="_bgps_projecten" style="height: 1px" ></th>
    <th rowspan="3"></th>
    <th></th>
    </tr>
    <tr>
        <td class="w100" id="_bgps_activiteit_detail"></td>
        <td id="_bgps_tijdstip_detail">
            <table>
                <tr><th style="height: 1px" class="nw">Status consolidatie</th></tr>
                <tr><td class="nw" style="height: 1px" id="_bgps_consolidatie_status">TODO</td></tr>
                <tr><th class="nw" style="height: 1px">Status besluiten</th></tr>
                <tr><td class="nw" id="_bgps_besluit_status">TODO</td></tr>
            </table>
        </td>
    </tr>
    <tr>
        <td id="_bgps_activiteit_beschrijving" colspan="3"></td>
    </tr>
</table>
<p>&nbsp;</p>
</div>

</div>

<div id="_bgps_intern" class="sectie_lv"><h1>Simulatie - Software</h1>

<button data-accordion="_bgps_s3" class="accordion_h active">Invoer en verwerking daarvan</button>
<div data-accordion-paneel="_bgps_s3" class="accordion_h_paneel" style = "display: block" data-bh="0" id="_bgps_software">
</div>

<button data-accordion="_bgps_s4" class="accordion_h active">Versiebeheer</button>
<div data-accordion-paneel="_bgps_s4" class="accordion_h_paneel" style = "display: block">
${this.#diagram.Html()}
</div>

</div>

<div id="_bgps_stop" class="sectie_uw"><h1>Simulatie - Uitwisselingen via STOP</h1>

<button data-accordion="_bgps_s2" class="accordion_h active">Overzicht van STOP modules</button>
<div data-accordion-paneel="_bgps_s2" class="accordion_h_paneel" style = "display: block" id="_bgps_uitwisseling">
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
        this.WerkSpecificatiesBij();

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
        this.#uitgangssituatie.VervangInnerHtml(); // Kan wijzigen vanwege nieuwe activiteiten
        let activiteiten = Activiteit.Activiteiten();

        // Maak een lijst van projecten op volgorde van aanmaken
        let html = ''
        if (activiteiten.length > 0) {
            // Maak eerst de headers en tabs voor de projecten
            html += '<table class="activiteiten_overzicht"><tr><th colspan="3"></th><th colspan="5" class="c nw">Activiteiten eindgebruikers</th><th>&nbsp;&nbsp;&nbsp;</th></tr>';

            // Toon de activiteiten
            for (let activiteit of activiteiten) {
                let daguur = activiteit.Tijdstip().DagUurHtml();
                html += `<tr data-bga="${activiteit.Index()}"><td>${activiteit.IsReadOnly() ? '' : activiteit.HtmlWerkBij("Wijzig de activiteit", 'AM')}</td ><td>${activiteit.KanVerwijderdWorden() ? ' ' + activiteit.HtmlVerwijder("Verwijder de activiteit", 'AD') : ''}</td><td>`;
                if (activiteit.HeeftSpecificatieMeldingen()) {
                    html += activiteit.HtmlWaarschuwing("De specificatie van de activiteit past niet meer in het scenario", 'AW');
                }
                html += `</td><td class="td0">Dag</td><td class="td1">${daguur[0]}</td><td class="tu">${daguur[1]}</td><td class="tz">${activiteit.Tijdstip().DatumHtml()} ${daguur[1]}</td>`;
                html += `<td class="nw">${activiteit.Naam()}</td><td class="ac"></td></tr>`;
            }
            html += '</table>';
        }
        html += this.#nieuweactiviteit.Html();
        document.getElementById('_bgps_activiteiten').innerHTML = html;
        this.#diagram.Herteken();
        BGProcesSimulator.LuisterNaarEvents();
        this.#SelecteerActiviteit(-1);
    }
    /** @type {NieuweActiviteit} */
    #nieuweactiviteit;
    /** @type {VersiebeheerDiagram} */
    #diagram;

    #ToonActiviteit() {
        if (!this.#huidigeActiviteit) {
            ['_bgps_projecten', '_bgps_consolidatie_status', '_bgps_activiteit_beschrijving', '_bgps_software', '_bgps_uitwisseling'].forEach(eltNaam => {
                document.getElementById(eltNaam).innerHTML = '';
            });
        } else {
            let html = `<span class="p_tab${(this.#huidigProject ? '' : ' huidige-prj')} huidige-act" data-prj="*"">User interface</span>`;
            for (let project of Project.Projecten(this.#huidigeActiviteit.Tijdstip())) {
                html += `<span class="p_tab${(project === this.#huidigProject ? ' huidige-prj' : '')}${(this.#huidigeActiviteit && this.#huidigeActiviteit.ToonInProject(project) ? ' huidige-act' : '')}" data-prj=${project.Index()}>${project.Naam()}</span>`;
            }
            document.getElementById('_bgps_projecten').innerHTML = html;

            // Update de consolidatie en besluitstatus
            document.getElementById('_bgps_consolidatie_status').innerHTML = this.#huidigeActiviteit.Consolidatiestatus().Html();

            // TODO besluitstatus

            // Beschrijving van de activiteit
            document.getElementById('_bgps_activiteit_beschrijving').innerHTML = this.#huidigeActiviteit.Beschrijving().Specificatie()
                ? `<div class="scenario">Rol van deze activiteit in het scenario:${this.#huidigeActiviteit.Beschrijving().Html()}</div>`
                : '';

            // Update het verwerkingsverslag en de uitwisselingen
            document.getElementById('_bgps_software').innerHTML = this.#huidigeActiviteit.UitvoeringsverslagHtml();
            this.#huidigeActiviteit.ToonUitwisselingen('_bgps_uitwisseling');
        }

        // Werk de weergave bij
        ['_bgps_tijdstip_detail', '_bgps_activiteit_detail', '_bgps_software', '_bgps_uitwisseling'].forEach(eltNaam => {
            let elt_status = document.getElementById(eltNaam);
            if (elt_status !== null) {
                if (this.#huidigeActiviteit) {
                    elt_status.classList.add('active');
                } else {
                    elt_status.classList.remove('active');
                }
            }
        });

        // Pas de selectie van activiteiten aan
        let activiteitIndex = this.#huidigeActiviteit?.Index() ?? '-';
        document.querySelectorAll('[data-bga]').forEach((elt) => {
            if (elt.dataset.bga == activiteitIndex) {
                elt.classList.add('huidige-act');
            } else {
                elt.classList.remove('huidige-act');
            }
            let act = this.#ActiviteitViaIndex(elt.dataset.bga);
            if (act && act.ToonInProject(this.#huidigProject)) {
                elt.classList.add('huidige-prj');
            } else {
                elt.classList.remove('huidige-prj');
            }
        });
        BGProcesSimulator.LuisterNaarEvents();
    }
    /** @type {Activiteit} */
    #huidigeActiviteit;
    /** @type {number} */
    #huidigeActiviteitTijdstip;

    /**
     * Toon het verslag van de uitvoering van de activiteit
     */
    #ToonActiviteitUitvoering() {
        let elt = document.getElementById('_bgps_activiteit_detail');
        elt.innerHTML = this.#huidigeActiviteit?.Html() ?? '';
        this.#ToonGerelateerdeActiviteitenProjecten("*");
    }

    /**
     * Toon het project voor het geselecteerde tijdstip
     */
    #ToonProject() {
        // Zoek de activiteit met de laatste wijziging voor dit project op
        let voorActiviteit = this.#huidigeActiviteit;
        if (voorActiviteit && !voorActiviteit.ToonInProject(this.#huidigProject)) {
            for (let activiteit of Activiteit.Activiteiten(this.#huidigeActiviteit.Tijdstip())) {
                if (activiteit.ToonInProject(this.#huidigProject)) {
                    voorActiviteit = activiteit;
                }
            }
        }

        // Toon de detailinformatie
        let elt = document.getElementById('_bgps_activiteit_detail');
        elt.innerHTML = voorActiviteit?.ProjectstatusHtml(this.#huidigeActiviteit, this.#huidigProject) ?? '';

        this.#ToonGerelateerdeActiviteitenProjecten(this.#huidigProject.Index())
    }
    /** @type {Project} */
    #huidigProject;
    /** @type {string} */
    #huidigeProjectcode;

    /**
     * Past de opmaak aan van activiteiten die bij een project horen,
     * en projecten bij een activiteit
     * @param {number} projectIndex
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
            if (act?.ToonInProject(this.#huidigProject)) {
                elt.classList.add('huidige-prj');
            } else {
                elt.classList.remove('huidige-prj');
            }
        });
    }
    //#endregion

    //#region UI events
    /**
     * Methode om event handlers te maken voor klikbare onderdelen van de UI
     */
    static LuisterNaarEvents() {
        document.querySelectorAll('[data-bga]').forEach((elt) => {
            if (!elt.dataset.lne) {
                elt.dataset.lne = true;
                elt.addEventListener('click', (e) => BGProcesSimulator.#BehandelEvent(e));
            }
        });
        document.querySelectorAll('[data-prj]').forEach((elt) => {
            if (!elt.dataset.lne) {
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
        else if (e.currentTarget.dataset.prj) {
            projectIndex = parseInt(e.currentTarget.dataset.prj);
        }
        if (e.currentTarget.dataset.bga) {
            BGProcesSimulator.This().#SelecteerActiviteit(parseInt(e.currentTarget.dataset.bga), projectIndex);
        }
        else if (projectIndex) {
            BGProcesSimulator.This().#SelecteerProject(projectIndex);
        }
    }

    /**
     * Selecteer eerst de activiteit
     * @param {number} activiteitIndex - Index() van de activiteit
     * @param {number} projectIndex - Index() van het project
     */
    #SelecteerActiviteit(activiteitIndex, projectIndex) {
        // Zoek uit welke activiteit geselecteerd is
        let activiteit = this.#ActiviteitViaIndex(activiteitIndex);
        if (!activiteit) {
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
        if (!activiteit) {
            // Kies de eerste activiteit
            for (let act of Activiteit.Activiteiten()) {
                activiteit = act;
                break;
            }
        }
        this.#huidigeActiviteit = activiteit;
        this.#huidigeActiviteitTijdstip = activiteit?.Tijdstip().Specificatie() ?? 0;

        // Zoek uit of het huidige project daarbij getoond kan worden
        let project = undefined;
        if (!projectIndex) {
            if (this.#huidigeActiviteit) {
                // Kijk of het geselecteerde project al bestaat op dit tijdstip
                if (this.#huidigeProjectcode) {
                    project = Project.Project(this.#huidigeProjectcode);
                    if (project) {
                        if (project.OntstaanIn().Tijdstip().Vergelijk(this.#huidigeActiviteit.Tijdstip()) > 0) {
                            // Project bestaat nog niet
                            project = undefined;
                        }
                    }
                }
            }
            this.#huidigProject = project;
            this.#huidigeProjectcode = project?.Code();
        }

        // Pas de UI aan
        this.#ToonActiviteit();
        if (projectIndex) {
            this.#SelecteerProject(projectIndex);
        }
        else if (project) {
            this.#ToonProject();
        } else {
            this.#ToonActiviteitUitvoering();
        }
    }

    /**
     * Zoek een activiteit op aan de hand van de index
     * @param {number} activiteitIndex
     * @returns {Activiteit}
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
     * @param {number} projectIndex - Index() van het project
     */
    #SelecteerProject(projectIndex) {
        if (!this.#huidigeActiviteit) {
            // Kies eerst een activiteit
            return;
        }
        this.#huidigProject = undefined;
        if (projectIndex) {
            for (let project of Project.Projecten(this.#huidigeActiviteit.Tijdstip())) {
                if (project.Index() === projectIndex) {
                    this.#huidigProject = project;
                    break;
                }
            }
        }
        if (this.#huidigProject) {
            this.#huidigeProjectcode = this.#huidigProject.Code();
        } else {
            this.#huidigeProjectcode = undefined;
            projectIndex = "*";
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
            if (act?.ToonInProject(this.#huidigProject)) {
                elt.classList.add('huidige-prj');
            } else {
                elt.classList.remove('huidige-prj');
            }
        });
        if (this.#huidigProject) {
            this.#ToonProject();
        } else {
            this.#ToonActiviteitUitvoering();
        }
    }
    //#endregion

}
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
        if (superInvoer) {
            superInvoer.#subInvoer[this.#index] = this;
        }
        this.#eigenaarObject = eigenaarObject;
        this.#eigenschap = eigenschap;
        if (data !== undefined) {
            this.#WerkSpecificatieBij(data);
        } else {
            if (eigenaarObject && eigenschap) {
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
     * De tag-naam van het container-element dat voor de HTML-weergave gebruikt wordt
     * @returns {string}
     */
    ContainerElement() {
        return 'span';
    }

    /**
     * Aangeroepen om de HTML voor een read-only weergave te maken van de invoer.
     * Deze wordt gepresenteerd binnen de container die door WeergaveHtml wordt klaargezet 
     * Wordt geïmplementeerd in afgeleide klassen.
     * @returns {string}
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
     * Geeft aan of het specificatie-element read-only is en niet gewijzigd mag worden.
     * @returns {boolean} - Standaard false
     */
    IsReadOnly() {
        return false;
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
     * @returns {string}
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
     * @returns {SpecificatieElement}
     */
    SuperInvoer() {
        return this.#superInvoer;
    }
    #superInvoer;
    /**
     * Geef de specificatie-elementen die voor een onderdeel van deze specificatie zijn aangemaakt
     * @returns {SpecificatieElement[]}
     */
    SubManagers() {
        return Object.values(this.#subInvoer);
    }
    #subInvoer = {};

    /**
     * Geef de unieke code voor dit specificatie-element
     * @returns {number}
     */
    Index() {
        return this.#index;
    }
    #index = 0;
    static #element_idx = 1; // Absolute waarde is niet relevant maar moet wel > 0 zijn

    /**
     * Geeft het object of array in de specificatie waar dit een eigenschap van is
     * @returns {any}
     */
    EigenaarObject() {
        return this.#eigenaarObject;
    }
    #eigenaarObject;

    /**
     * Geeft de eigenschap waaraan dit element toegekend wordt. Als eigenaarObject een array is, dan is dit indefined.
     * @returns {string}
     */
    Eigenschap() {
        return this.#eigenschap;
    }
    #eigenschap;

    /**
     * Geef het in-memory object voor het element
     * @returns {any}
     */
    Specificatie() {
        return this.#data;
    }
    /**
     * Geef de eigenschap een andere waarde
     * @param {any} data
     */
    SpecificatieWordt(data) {
        this.#WerkSpecificatieBij(data);
    }
    //#endregion

    //#region Status voor de invoer/weergave
    /**
     * Geeft aan of het specificatie-element actief is in het modal scherm (en niet in de weergave van de overzichtspagina)
     * @returns {boolean}
     */
    IsInvoer() {
        return this.#isInvoer;
    }
    #isInvoer = false;

    /**
     * Geeft de stap in een invoerscherm waarvan de invoer in verschillende stappen uitgevoerd moet worden
     * @returns {number}
     */
    InvoerStap() {
        return this.IsInvoer() ? this.#invoerStap : 0;
    }
    /** @type {number} */
    #invoerStap;

    //#endregion

    //#region Hulpfuncties om de html te maken
    /**
     * Geef het ID voor een HTML element gemaakt door het specificatie-element
     * @param {string} idSuffix - Suffix voor de identificatie van het element
     * @returns {string}
     */
    ElementId(idSuffix) {
        let id = `_bgps_${this.#index}_${(this.IsInvoer() ? 'I' : 'W')}`;
        if (idSuffix) {
            id += '_' + idSuffix;
        }
        return id;
    }
    /**
     * Geef het HTML element gemaakt door het specificatie-element
     * @param {string} idSuffix - Suffix voor de identificatie van het element
     * @returns {HTMLElement}
     */
    Element(idSuffix) {
        return document.getElementById(this.ElementId(idSuffix));
    }

    /**
     * Geef de dataset declaratie voor het top-level element
     * @returns {string}
     */
    DataSet() {
        return `data-se="${this.#index}"`;
    }

    /**
     * Maakt de HTML voor een voegtoe knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     * @param {string} extraAttributen - Extra attributen voor de knop
     * @returns {string}
     */
    HtmlVoegToe(hint, idSuffix, extraAttributen) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} ${(extraAttributen ?? '')} class="voegtoe">&#x271A;</span>`;
    }
    /**
     * Maakt de HTML voor een edit knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     * @param {string} extraAttributen - Extra attributen voor de knop
     * @returns {string}
     */
    HtmlWerkBij(hint, idSuffix, extraAttributen) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} ${(extraAttributen ?? '')} class="werkbij">&#x270E;</span>`;
    }
    /**
     * Maakt de HTML voor een verwijder knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     * @param {string} extraAttributen - Extra attributen voor de knop
     * @returns {string}
     */
    HtmlVerwijder(hint, idSuffix, extraAttributen) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} ${(extraAttributen ?? '')} class="verwijder">&#x1F5D1;</span>`;
    }
    /**
     * Maakt de HTML voor een waarschuwingsicoon aan
     * @param {string} hint - Mouseover hint voor het icoon
     * @param {string} idSuffix - Suffix voor de identificatie van het icoon
     * @param {string} extraAttributen - Extra attributen voor het icoon
     * @returns {string}
     */
    HtmlWaarschuwing(hint, idSuffix, extraAttributen) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} ${(extraAttributen ?? '')} class="specmelding">&#x26A0;</span>`;
    }
    //#endregion

    //#region Openen van modal invoerscherm
    /**
     * Open een modal invoer scherm voor de invoer van de gegevens waarvoor dit specificatie-element opgezet is.
     */
    OpenModal() {
        if (BGProcesSimulator.Singletons('UI', {}).ModalOpener) {
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
     * @returns {string}
     */
    Html() {
        let containerElement = this.ContainerElement();
        return `<${containerElement} id="${this.ElementId(this.IsInvoer() ? '___M' : '___W')}" ${this.DataSet()}>${this.IsInvoer() ? this.InvoerInnerHtml() : this.WeergaveInnerHtml()}</${containerElement}>`
    }

    /**
     * Vervang de html die eerder door InnerHtml () is gemaakt door een nieuwe versie.
     * Welke versie dat is hangt af van de huidige staat van het specificatie-element
     */
    VervangInnerHtml() {
        if (this.#isInvoer) {
            let elt = this.Element('___M');
            if (elt) {
                // Verifieer dat de submanagers ook klaar zijn voor de invoer
                this.#ModalMode(true);
                elt.innerHTML = this.InvoerInnerHtml();
            }
        }
        else {
            let elt = this.Element('___W');
            if (elt) {
                elt.innerHTML = this.WeergaveInnerHtml();
            }
        }
        if (BGProcesSimulator.Singletons('UI').ModalOpener) {
            document.getElementById("_bgps_modal_volgende").style.display = BGProcesSimulator.Singletons('UI').ModalOpener.#volgendeStapNodig ? '' : 'none';
            document.getElementById("_bgps_modal_ok").style.display = BGProcesSimulator.Singletons('UI').ModalOpener.#volgendeStapNodig ? 'none' : '';
        }
    }

    /**
     * Geeft aan dat een volgende stap nodig is voor de invoer
     * @returns {boolean}
     */
    VolgendeStapNodig() {
        BGProcesSimulator.Singletons('UI').ModalOpener.#volgendeStapNodig = true;
    }
    /** @type {boolean} */
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
        if (this.#eigenaarObject) {
            if (this.#eigenschap) {
                if (data !== undefined) {
                    this.#eigenaarObject[this.#eigenschap] = data;
                } else if (this.#eigenaarObject[this.#eigenschap] !== undefined) {
                    delete this.#eigenaarObject[this.#eigenschap];
                }
            }
            else {
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
        }
        this.#data = data;
    }
    #data;

    /**
     * Verwijder alle actieve specificatie-elementen
     * @param {Tijdstip} vanafTijdstip - drempelwaarde, indien gegeven worden alleen de specificatie-elementen van activiteiten na dit tijdstip weggegooid.
     */
    static VerwijderElementen(vanafTijdstip) {
        for (let gewijzigd = true; gewijzigd && Object.keys(BGProcesSimulator.Singletons('Elementen', {})).length > 0;) {
            gewijzigd = false;
            for (let se of [...Object.values(BGProcesSimulator.Singletons('Elementen'))]) {
                if (!vanafTijdstip || (se.Tijdstip && se.Tijdstip().Vergelijk(vanafTijdstip) > 0)) {
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
        if (this.#index) {
            let index = this.#index;
            this.#index = undefined;
            delete BGProcesSimulator.Singletons('Elementen')[index];
            if (this.#superInvoer) {
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
        if (!BGProcesSimulator.Singletons('UI', {}).ModalOpener) {
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
            if (subInvoer) {
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
                    } else {
                        continue;
                    }
                    let specificatieElt = BGProcesSimulator.Singletons('Elementen')[se];
                    if (specificatieElt) {
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
     * @param {boolean} isTijdstip - Geeft aan of dit een tijdstip (ipv een datum) is
     * @param {Tijdstip} naTijdstip - Geef de dag/tijd waar het tijdstip na moet vallen
     * @param {boolean/function} isReadOnly - Optioneel: een boolean of een methode die teruggeeft of het tijdstip gewijzigd kan worden
     */
    constructor(superInvoer, eigenaarObject, eigenschap, isTijdstip, naTijdstip, isReadOnly) {
        super(eigenaarObject, eigenschap, undefined, superInvoer);
        this.#isTijdstip = isTijdstip;
        if (naTijdstip) {
            this.#naDag = naTijdstip.#dag;
            this.#naUur = naTijdstip.#uur;
        }
        this.#isReadOnly = isReadOnly;
        this.#InterpreteerSpecificatie(super.Specificatie());
    }

    /**
     * Maak een Tijdstip dat de opgegeven waarde representeert
     * @param {number} specificatie - Het tijdstip als getal (aantal dagen + 0.01 * uur)
     * @param {boolean} isTijdstip - Geeft aan of dit een tijdstip (ipv een datum) is
     * @returns {Tijdstip}
     */
    static Maak(specificatie, isTijdstip) {
        return new Tijdstip(undefined, { t: specificatie }, 't', isTijdstip, undefined, true);
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
     * @returns {boolean}
     */
    HeeftWaarde() {
        return this.Specificatie() !== undefined;
    }

    /**
     * Geef de datum/tijdstip als een ISO datum voor gebruik in STOP modules
     * @returns {string}
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
     * @returns {number}
     */
    Jaar() {
        let datum = new Date(BGProcesSimulator.This().Startdatum());
        let dag = Math.floor(this.Specificatie());
        datum.setDate(datum.getDate() + dag);
        return datum.getFullYear();
    }

    /**
     * Geef het nummer van de dag
     * @returns {number}
     */
    Dag() {
        if (this.Specificatie()) {
            return Math.floor(this.Specificatie());
        }
    }

    /**
     * Geef de datum als yyyy-mm-dd
     * @returns {string}
     */
    DatumHtml() {
        let datum = new Date(BGProcesSimulator.This().Startdatum());
        let dag = Math.floor(this.Specificatie());
        let uur = Math.round(100 * (this.Specificatie() - dag));
        datum.setDate(datum.getDate() + dag);
        return datum.toJSON().slice(0, 10);
    }
    /**
     * Geef de datum/tijdstip als een ISO datum
     * @returns {string}
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
     * @returns {string[]} - array met dag en, voor een tijdstip, uur.
     */
    DagUurHtml() {
        let dag = Math.floor(this.Specificatie());
        if (this.#isTijdstip) {
            let uur = Math.round(100 * (this.Specificatie() - dag));
            if (uur == 0) {
                return [dag, ''];
            } else {
                let HH = ('00' + uur).slice(-2);
                return [dag, `${HH}u`];
            }
        } else {
            return [dag];
        }
    }

    /**
     * Geeft de startdatum als tijdstip-Tijdstip (want dat is niet in te voeren)
     * @returns {Tijdstip}
     */
    static StartTijd() {
        let singletons = BGProcesSimulator.Singletons('Tijdstip', {});
        if (!singletons.StartTijd) {
            singletons.StartTijd = Tijdstip.Maak(0, true);
        }
        return singletons.StartTijd;
    }

    /**
     * Geeft de startdatum als datum-Tijdstip (want dat is niet in te voeren)
     * @returns {Tijdstip}
     */
    static StartDatum() {
        let singletons = BGProcesSimulator.Singletons('Tijdstip', {});
        if (!singletons.StartDatum) {
            singletons.StartDatum = Tijdstip.Maak(0, false);
        }
        return singletons.StartDatum;
    }

    /**
     * Geeft aan of dit tijdstip gelijk is aan het andere. Dat is het geval als ze beide
     * geen waarde hebben, of beide wel een waarde en Vergelijk = 0 
     * @param {Tijdstip} tijdstip
     * @returns {boolean}
     */
    IsGelijk(tijdstip) {
        return this.Specificatie() === tijdstip?.Specificatie();
    }

    /**
     * Vergelijk dit tijdstip met het andere. 
     * Geeft < 0, = 0, > 0 als dit tijdstip eerder / gelijk / later is dan het opgegeven tijdstip,
     * en undefined als een van de tijdstippen undefined is.
     * @param {Tijdstip} tijdstip
     * @returns {boolean}
     */
    Vergelijk(tijdstip) {
        if (tijdstip?.HeeftWaarde() && this.HeeftWaarde()) {
            return this.Specificatie() - tijdstip.Specificatie();
        }
    }
    //#endregion

    //#region Implementatie specificatie-element
    IsReadOnly() {
        if (typeof this.#isReadOnly === "boolean") {
            return this.#isReadOnly;
        }
        if (typeof this.#isReadOnly === "function") {
            return this.#isReadOnly();
        }
        return Boolean(this.#isReadOnly);
    }
    /** @type {boolean} */
    #isReadOnly;

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
    /** @type {boolean} */
    #isTijdstip;

    BeginInvoer() {
        this.#InterpreteerSpecificatie(super.Specificatie());
    }
    #InterpreteerSpecificatie(data) {
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
            if (this.#dag < 0) {
                this.#dag = 0;
            }
            if (this.#naDag !== undefined) {
                if (this.#isTijdstip) {
                    if (this.#dag < this.#naDag || (this.#dag == this.#naDag && this.#uur <= this.#naUur)) {
                        this.#dag = this.#naDag;
                        this.#uur = this.#naUur + 1;
                    }
                } else {
                    if (this.#dag <= this.#naDag) {
                        this.#dag = this.#naDag + 1;
                    }
                }
                if (this.#uur > 23) {
                    this.#uur = 0;
                    this.#dag += 1;
                }
            }
        }
    }
    /** @type {number} */
    #dag;
    /** @type {number} */
    #uur = 0;
    /** @type {number} */
    #naDag;
    /** @type {number} */
    #naUur;

    InvoerInnerHtml() {
        let disabled = this.IsReadOnly() ? ' disabled' : '';
        let html = `dag <input type="number" class="number4" id="${this.ElementId('D')}" value="${this.#dag}"${disabled}>`
        if (this.#isTijdstip) {
            html += ` om <input type="number" class="number2" min="0" max="23" id="${this.ElementId('T')}" value="${this.#uur}"${disabled}>:00`
        }
        html += ` (${this.DatumTijdHtml()})`
        return html;
    }

    OnInvoerChange(elt, idSuffix) {
        if (idSuffix == 'D' || idSuffix == 'T') {
            let dag = parseInt(this.Element('D').value);
            let uur = this.#isTijdstip ? parseInt(this.Element('T').value) : 0;
            this.#InterpreteerSpecificatie(dag + 0.01 * uur);
            this.VervangInnerHtml();
            if (this.SuperInvoer()?.TijdstipGewijzigd) {
                this.SuperInvoer().TijdstipGewijzigd(this);
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

//#region Weergave van het versiebeheer
/*------------------------------------------------------------------------------
 *
 * Het versiebeheerdiagram geeft een overzicht van het interne BG-versiebeheer
 * zoals dat in de simulator opgezet is. Het kan ook de STOP-versie tonen voor
 * een instrument. Vanwege de UI interactie is het als een specificatie-element
 * gecodeerd.
 * 
 *----------------------------------------------------------------------------*/
class VersiebeheerDiagram extends SpecificatieElement {

    //#region Publieke interface
    /**
     * Maakt een generator voor het versiebeheerdiagram aan
     */
    constructor() {
        super();
    }

    /**
     * Tekent het diagram opnieuw
     */
    Herteken() {
        this.#svg = '';
        this.#instrumentnamen = Instrument.Instrumentnamen().sort(Instrument.VergelijkInstrumentnamen);
        if (this.#instrumentnamen.length == 0) {
            return;
        }
        if (this.#voorInstrument && !this.#instrumentnamen.includes(this.#voorInstrument)) {
            this.#voorInstrument = undefined;
        }
        this.#MaakSvg();
        for (let instrument of this.#instrumentnamen) {
            this.#MaakInstrumentSvg(instrument);
        }
        this.VervangInnerHtml();
    }
    //#endregion

    //#region Implementatie van SpecificatieElement
    WeergaveInnerHtml() {
        if (!this.#svg) {
            return '';
        }
        this.#idx++;
        let html = `<table class="bgvbd_tabel">
                    <tr>
                        <td>
                            <table>
                                <tr>
                                    <td><input type="radio" name="${this.ElementId('T')}" id="${this.ElementId('BG')}"${this.#voorInstrument ? '' : ' checked'}></td>
                                    <th><label for="${this.ElementId('BG')}">Toon intern versiebeheer</label></th>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool bgvbd_BG_I">&nbsp;</td><td>${BGProcesSimulator.This().BevoegdGezag()}</td>
                                </tr>${BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente ? `
                                <tr>
                                    <td class="bgvbd_legenda_symbool bgvbd_BG_A">&nbsp;</td><td>Adviesbureau</td>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool bgvbd_BG_P">&nbsp;</td><td>Provincie</td>
                                </tr>` : ''}
                                <tr>
                                    <td class="bgvbd_legenda_symbool"><svg xmlns="http://www.w3.org/2000/svg" class="bgvbd_legenda_svg" viewBox="0 0 10 10" version="1.1"><path d="M 0 4 L 10 4" class="bgvbd_line_branch"></svg></td>
                                    <td>Branch</td>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool"><svg xmlns="http://www.w3.org/2000/svg" class="bgvbd_legenda_svg" viewBox="0 0 10 10" version="1.1"><path d="M 0 4 L 10 4" class="bgvbd_line_bg"></svg></td>
                                    <td>Basisversie / merge</td>
                                </tr>
                            </table>
                        </td>
                        <td>
                            <table>`;
        let stop_legenda_html = `<tr>
                                    <td class="bgvbd_legenda_symbool bgvbd_STOP_P">&nbsp;</td><td>Publicatie</td>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool bgvbd_STOP_R">&nbsp;</td><td>Intern of revisie</td>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool bgvbd_STOP_nvt">&nbsp;</td><td>N.v.t.</td>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool"><svg xmlns="http://www.w3.org/2000/svg" class="bgvbd_legenda_svg" viewBox="0 0 10 10" version="1.1"><path d="M 0 4 L 10 4" class="bgvbd_line_basis"></svg></td>
                                    <td>Basisversie</td>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool"><svg xmlns="http://www.w3.org/2000/svg" class="bgvbd_legenda_svg" viewBox="0 0 10 10" version="1.1"><path d="M 0 4 L 10 4" class="bgvbd_line_vv"></svg></td>
                                    <td>Vervlechting</td>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool"><svg xmlns="http://www.w3.org/2000/svg" class="bgvbd_legenda_svg" viewBox="0 0 10 10" version="1.1"><path d="M 0 4 L 10 4" class="bgvbd_line_ov"></svg></td>
                                    <td>Ontvlechting</td>
                                </tr>
`
        if (this.#instrumentnamen.length > 1) {
            html += `
                                <tr>
                                    <th colspan="2">Toon STOP versiebeheer voor:</th>
                                </tr>
                                <tr><td><table>`;
            for (let instrument of this.#instrumentnamen) {
                html += `
                                    <tr>
                                        <td><input type="radio" name="${this.ElementId('T')}" id="${this.ElementId(`VI_${instrument}`)}"${this.#voorInstrument === instrument ? ' checked' : ''} value="${instrument}"></td><td><label for="${this.ElementId(`VI_${instrument}`)}">${Instrument.SoortInstrumentNamen[Instrument.SoortInstrument(instrument)]} ${instrument}</label></td>
                                    </tr>`;
            }
            html += `
                                    </table></td>
                                    <td><table>${stop_legenda_html}</table></td>
                                </tr>`;
        } else {
            html += `
                                <tr>
                                    <td><input type="radio" name="${this.ElementId('T')}" id="${this.ElementId('VI')}"${this.#voorInstrument ? ' checked' : ''} value="${this.#instrumentnamen[0]}"></td>
                                    <th><label for="${this.ElementId('VI')}">Toon STOP versiebeheer</label></th>
                                </tr>
                                ${stop_legenda_html}`;
        }
        html += `           </table>
                        </td>
                        <td>
                            <table>
                                <tr>
                                    <th colspan="2">Symbolen</th>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool">${VersiebeheerDiagram.#Symbool_Inhoud}</td><td>Wijziging van regeling/informatieobject</td>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool">${VersiebeheerDiagram.#Symbool_Tijdstempel}</td><td>(Wijziging van) inwerkingtreding</td>
                                </tr>
                                <tr>
                                    <td class="bgvbd_legenda_symbool">${VersiebeheerDiagram.#Symbool_Uitwisseling}</td><td>Uitwisseling via STOP</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="3">
                            <div class="bgvbd_diagram"><svg id="${this.ElementId(`svg_${this.#idx}`)}" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: 100%; height: 100%;" viewBox="0 0 ${this.#breedte} ${this.#hoogte}" version="1.1">
                            ${this.#svg}
                            Deze browser ondersteunt geen SVG en dat is erg jammer.
                            </svg></div>
                        </td>
                    </tr>
                </table>`;
        return html;
    }
    #idx = 0;
    /** @type {string[]} */
    #instrumentnamen;
    /** @type {string} */
    #voorInstrument;
    /** @type {number} */
    #breedte; // Breedte tot nu toe
    /** @type {number} */
    #hoogte; // Hoogte tot nu toe
    #svg = ''; // SVG voor het BG-interne versiebeheer

    OnWeergaveClick(elt, idSuffix) {
        let updateDiagram = false;
        if (idSuffix === 'BG') {
            if (elt.checked) {
                this.#voorInstrument = undefined;
                updateDiagram = true;
            }
        } else if (idSuffix && idSuffix.startsWith('VI')) {
            if (elt.checked) {
                this.#voorInstrument = elt.value;
                updateDiagram = true;
            }
        }
        if (updateDiagram) {
            document.querySelectorAll('[data-bgvbd]').forEach((elt) => {
                if (elt.dataset.bgvbd == this.#voorInstrument) {
                    elt.classList.add('bgvbd_active');
                    elt.classList.remove('bgvbd_hidden');
                } else {
                    elt.classList.add('bgvbd_hidden');
                    elt.classList.remove('bgvbd_active');
                }
            });
        }
    }

    VervangInnerHtml() {
        super.VervangInnerHtml();

        // svgPanZoom werkt niet als de SVG hidden is
        // Wacht daarom totdat het diagram in beeld komt
        let svg_elt = this.Element(`svg_${this.#idx}`);
        if (svg_elt) {
            new IntersectionObserver(function (entries, observer) {
                if (entries[0].isIntersecting) {
                    observer.unobserve(svg_elt);

                    svgPanZoom('#' + svg_elt.id, {
                        zoomEnabled: true,
                        controlIconsEnabled: true,
                        fit: true,
                        center: true
                    })
                }
            }, {
                threshold: 0
            }).observe(svg_elt);

            // Event handlers voor klikken op SVG elementen
            BGProcesSimulator.LuisterNaarEvents();
        }
    }
    //#endregion

    //#region Stel de svg samen - BG-intern versiebeheer
    #MaakSvg() {
        this.#positie = {};
        this.#breedte = 0;
        this.#hoogte = 0;
        let heeftUitgangssituatie = Boolean(BGProcesSimulator.This().Uitgangssituatie().JuridischWerkendVanaf()?.HeeftWaarde());

        this.#MaakProjectBranchKoppen(heeftUitgangssituatie);

        if (heeftUitgangssituatie) {
            this.#VoegUitgangssituatieToe();
        }

        let iwtMomenten = [];
        let iwtBranches = {};
        Momentopname.VoorAlleMomentopnamen(undefined, undefined, (mo) => {
            if (!(mo instanceof Uitgangssituatie)) {
                if (mo.JuridischWerkendVanaf()?.HeeftWaarde()) {
                    let iwt = mo.JuridischWerkendVanaf().DatumHtml();
                    if (!(iwt in iwtBranches)) {
                        iwtMomenten.push(mo.JuridischWerkendVanaf());
                        iwtBranches[iwt] = [];
                    }
                    if (!iwtBranches[iwt].includes(mo.Branch())) {
                        iwtBranches[iwt].push(mo.Branch());
                    }
                }
            }
        });
        iwtMomenten.sort((a, b) => a.Vergelijk(b));
        let iwtVolgende = iwtMomenten.length > 0 ? 0 : undefined;

        for (let activiteit of Activiteit.Activiteiten()) {
            while (iwtVolgende !== undefined && activiteit.Tijdstip().Vergelijk(iwtMomenten[iwtVolgende]) >= 0) {
                this.#VoegIWTMomentToe(iwtMomenten[iwtVolgende], iwtBranches[iwtMomenten[iwtVolgende].DatumHtml()]);
                iwtVolgende++;
                if (iwtVolgende >= iwtMomenten.length) {
                    iwtVolgende = undefined;
                }
            }
            this.#VoegActiviteitToe(activiteit);
        }
        for (; iwtVolgende !== undefined && iwtVolgende < iwtMomenten.length; iwtVolgende++) {
            this.#VoegIWTMomentToe(iwtMomenten[iwtVolgende], iwtBranches[iwtMomenten[iwtVolgende].DatumHtml()]);
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

        let xProject = VersiebeheerDiagram.#TussenruimteBreedte + VersiebeheerDiagram.#TijdstipBreedte + VersiebeheerDiagram.#TussenruimteBreedte;
        let yProject = VersiebeheerDiagram.#NaamHoogte;
        let hProject = VersiebeheerDiagram.#NaamHoogte;
        let yBranch = yProject + hProject + VersiebeheerDiagram.#NaamHoogte;
        let hBranch = VersiebeheerDiagram.#ElementHoogte;
        let wBranch = VersiebeheerDiagram.#NaamBreedte;
        if (heeftUitgangssituatie) {
            let start = BGProcesSimulator.This().Uitgangssituatie();
            let wProject = VersiebeheerDiagram.#NaamBreedte;
            this.#Registreer(xProject, yProject, wProject, hProject);
            this.#svg += `<text x="${xProject + wProject / 2}" y="${yProject}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">${start.Branch().Project().Naam()}</text>
                          <path d="M ${xProject} ${yProject + hProject} L ${xProject + wProject} ${yProject + hProject}" class="bgvbd_naam_l"/>`;
            let xBranch = xProject;
            this.#Registreer(xBranch, yBranch, wBranch, hBranch);
            this.#svg += `<text x="${xBranch + wBranch / 2}" y="${yBranch}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">${start.Branch().Code()}</text>`;
            xProject += wProject + VersiebeheerDiagram.#TussenruimteBreedte;
        }
        for (let project of projecten) {
            let branches = Branch.Branches(undefined, project);
            if (branches.length == 0) {
                continue;
            }
            let wProject = branches.length * VersiebeheerDiagram.#NaamBreedte + (branches.length - 1) * VersiebeheerDiagram.#TussenruimteBreedte;
            this.#Registreer(xProject, yProject, wProject, hProject);

            this.#svg += `<text x="${xProject + wProject / 2}" y="${yProject}" data-prj="${project.Index()}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">${project.Naam()}</text>
                          <path d="M ${xProject} ${yProject + hProject} L ${xProject + wProject} ${yProject + hProject}" class="bgvbd_naam_l"/>`;
            let xBranch = xProject;
            for (let branch of branches) {
                this.#Registreer(xBranch, yBranch, wBranch, hBranch, branch.Index());
                this.#svg += `<text x="${xBranch + wBranch / 2}" y="${yBranch}" data-prj="${project.Index()}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_naam">${branch.Code()}</text>`;
                xBranch += wBranch + VersiebeheerDiagram.#TussenruimteBreedte;
            }

            xProject += wProject + VersiebeheerDiagram.#TussenruimteBreedte;
        }
    }

    /**
     * Voeg een blokje toe voor de uitgangssituatie
     */
    #VoegUitgangssituatieToe() {
        let x = VersiebeheerDiagram.#TussenruimteBreedte;
        let y = this.#hoogte;
        let w = VersiebeheerDiagram.#TijdstipBreedte;
        let h = VersiebeheerDiagram.#ElementHoogte;
        this.#svg += `<text x="${x}" y="${y + h / 2}" dominant-baseline="middle" text-anchor="start" class="bgvbd_naam">${BGProcesSimulator.This().Uitgangssituatie().Tijdstip().DatumTijdHtml()}</text>`;

        x += w + VersiebeheerDiagram.#TussenruimteBreedte + (VersiebeheerDiagram.#NaamBreedte - VersiebeheerDiagram.#ElementBreedte) / 2;
        w = VersiebeheerDiagram.#ElementBreedte;
        this.#Registreer(x, y, w, h, BGProcesSimulator.This().Uitgangssituatie().Index());
        this.#svg += `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="3" ry="3" class="bgvbd_mo bgvbd_BG_U"></rect>
                      <text x="${x + w / 2}" y="${y + h / 2}" dominant-baseline="middle" text-anchor="middle" class="bgvbd_symbolen">${VersiebeheerDiagram.#Symbool_Inhoud}${VersiebeheerDiagram.#Symbool_Tijdstempel}</text>`;
    }

    /**
     * Voeg de bijdrage van een activiteit toe
     * @param {Activiteit} activiteit
     */
    #VoegActiviteitToe(activiteit) {
        // Zoek uit welke branches geraakt worden en hoe ze van elkaar afhangen
        let momentopnamen = activiteit.Momentopnamen(true);
        if (momentopnamen.length === 0) {
            return;
        }
        let moPerBranch = Object.assign({}, ...momentopnamen.map((mo) => ({ [mo.Branch().Code()]: mo })));

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
                if (mo.TegelijkBeheerd() && mo.Branch().Project() !== activiteit.Project()) {
                    // Gebruik dezelfde rij als de momentopname die voor het project van de activiteit wordt toegewezen.
                    continue;
                }

                let kanGetekendWorden = true;
                for (let v of [mo.VoorgaandeMomentopname(), ...mo.OntvlochtenMet(), ...mo.VervlochtenMet()]) {
                    if (v && teTekenen.includes(v)) {
                        // Teken de voorgaande/vervlochten/ontvlochten momentopname eerder/hoger
                        kanGetekendWorden = false;
                        break;
                    }
                }
                if (kanGetekendWorden) {
                    if (!mo.TegelijkBeheerd()) {
                        // Teken op deze rij
                        teTekenenOpRij[mo.Index()] = aantalRijen;
                        gePlaatst.push(mo);
                    } else {
                        // Zet alle tegelijk beheerde op een rij
                        // Komen ze naast elkaar te staan in het diagram zonder andere ertussen?
                        let aansluitend = undefined;
                        let tussenliggend = [];
                        for (let m of momentopnamen) {
                            if (mo.TegelijkBeheerd().includes(m.Branch())) {
                                if (!aansluitend) {
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
                                if (rijNummer) {
                                    // Niet op deze rij tekenen
                                    tussenliggend.push(m);
                                } else if (rijNummer == aantalRijen) {
                                    // Zet al deze momentopnamen op de volgende rij
                                    tekenenOpVolgendeRij.push(...mo.TegelijkBeheerd().map(branch => moPerBranch[branch.Code()]));
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
                            for (let branch of mo.TegelijkBeheerd()) {
                                let m = moPerBranch[branch.Code()];
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
            let x = VersiebeheerDiagram.#TussenruimteBreedte;
            let h = aantalRijen * VersiebeheerDiagram.#ElementHoogte + (aantalRijen - 1) * VersiebeheerDiagram.#TussenruimteHoogte;
            this.#svg += `<text x="${x}" y="${y + h / 2}" data-bga="${activiteit.Index()}" dominant-baseline="middle" text-anchor="start" class="bgvbd_naam">${activiteit.Tijdstip().DatumTijdHtml()}</text>`;
            if (aantalRijen > 1) {
                let xl = x + VersiebeheerDiagram.#NaamBreedte + VersiebeheerDiagram.#TussenruimteBreedte / 4;
                this.#svg += `<path d="M ${xl} ${y} L ${xl} ${y + h}" class="bgvbd_naam_l"/>`;
            }
        }

        // Teken de momentopnamen
        let mo_css = activiteit.UitgevoerdDoorAdviesbureau() ? 'bgvbd_BG_A' : 'bgvbd_BG_I';
        let w = VersiebeheerDiagram.#ElementBreedte;
        let h = VersiebeheerDiagram.#ElementHoogte;
        for (let rijNummer = 1; rijNummer <= aantalRijen; rijNummer++) {
            let getekend = [];
            for (let mo of momentopnamen.filter((m) => teTekenenOpRij[m.Index()] === rijNummer)) {
                if (getekend.includes(mo)) {
                    continue;
                }

                // Teken alle momentopnamen
                /** @type {Momentopname[]} */
                let teTekenen = [mo];
                if (mo.TegelijkBeheerd()) {
                    teTekenen = momentopnamen.filter((m) => mo.TegelijkBeheerd().includes(m.Branch())); // in de juiste volgorde
                }
                let xPerMO = {};
                for (let m of teTekenen) {
                    let branchPositie = this.#positie[m.Branch().Index()];
                    xPerMO[m.Index()] = branchPositie.x + (branchPositie.w - w) / 2;
                }
                if (teTekenen.length > 1) {
                    // Teken een omhullende
                    let xBox = xPerMO[teTekenen[0].Index()];
                    let wBox = xPerMO[teTekenen[teTekenen.length - 1].Index()] - xBox + w;
                    this.#svg += `<rect x="${xBox}" y="${y}" width="${wBox}" height="${h}" rx="3" ry="3" class="bgvbd_mo_tegelijk"></rect>`;
                }

                for (let tekenMO of teTekenen) {
                    // Teken de momentopname
                    getekend.push(tekenMO);
                    let x = xPerMO[tekenMO.Index()];
                    this.#Registreer(x, y, w, h, tekenMO.Index());
                    this.#svg += this.#MomentopnameSvg(tekenMO, mo_css)

                    // Teken de lijn vanaf de vorige momentopname
                    if (tekenMO.VoorgaandeMomentopname()) {
                        // Dit is de branchlijn
                        let positieVorigeMO = this.#positie[tekenMO.VoorgaandeMomentopname().Index()];
                        if (tekenMO.VoorgaandeMomentopname().Branch() == tekenMO.Branch()) {
                            this.#svg += `<path d="M ${x + w / 2} ${positieVorigeMO.y + positieVorigeMO.h} L ${x + w / 2} ${y}" class="bgvbd_line_${tekenMO.IsTegelijkBeheerdEnVolgend() ? 'ex' : ''}branch"/>`;
                        } else {
                            // Basisversie
                            this.#svg += this.#BasisversieLijnMetPijlpuntSvg(tekenMO.VoorgaandeMomentopname(), tekenMO, true, 'bg')
                        }
                    }
                    // Ver- en ontvlechtingen
                    for (let v of tekenMO.VervlochtenMet()) {
                        this.#svg += this.#VervlochtenLijnMetPijlpuntSvg(v, tekenMO, 'bg')
                    }
                    for (let v of tekenMO.OntvlochtenMet()) {
                        this.#svg += this.#OntvlochtenLijnMetPijlpuntSvg(v, tekenMO, 'bg')
                    }
                }
            }
            // Volgende rij
            y += h + VersiebeheerDiagram.#TussenruimteHoogte;
        }
    }

    /**
     * Voeg een inwerkingtredingsmoment toe
     * @param {Tijdstip} iwtDatum - Datum van inwerkingtreding
     * @param {Branch[]} branches - Branches waarvoor de datum ooit geldig was
     */
    #VoegIWTMomentToe(iwtDatum, branches) {
        // Teken de datum
        let y = this.#hoogte;
        let h = VersiebeheerDiagram.#NaamHoogte;
        this.#svg += `<text x="${VersiebeheerDiagram.#TussenruimteBreedte}" y="${y + h / 2}" dominant-baseline="middle" text-anchor="start" class="bgvbd_naam">${iwtDatum.DatumHtml()}</text>`;

        // Teken de momenten voor de branches
        for (let branch of branches) {
            let branchPositie = this.#positie[branch.Index()];
            let x = branchPositie.x + branchPositie.w / 2;
            this.#Registreer(x, y, 0, h);

            let moPositie = this.#positie[branch.LaatsteMomentopname(iwtDatum).Index()];
            this.#svg += `<path d="M ${x} ${moPositie.y + moPositie.h} L ${x} ${y}" class="bgvbd_line_exbranch"/>
                          <text x="${x}" y="${y + h / 2}" dominant-baseline="middle" text-anchor="middle" class="bgvbd_symbolen">${VersiebeheerDiagram.#Symbool_Tijdstempel}</text>`;
        }
    }
    //#endregion

    //#region Stel de svg samen - STOP versiebeheer voor instrument
    /**
     * Maak de SVG voor het STOP versiebeheer voor het geselecteerde instrument
     * @param {string} voorInstrument - Het instrument waarvoor de SVG toegevoegd moet worden
     */
    #MaakInstrumentSvg(voorInstrument) {
        // Zoek uit welke momentopnamen relevant zijn
        let relevanteMO = [];
        let overigeMO = [];
        let relevanteBranches = {};
        Momentopname.VoorAlleMomentopnamen(undefined, undefined, (mo) => {
            if (mo instanceof Uitgangssituatie) {
                return;
            }
            let versie = mo.Instrumentversie(voorInstrument);
            if (versie && (versie.Instrumentversie().LVBBUitgewisseld() || versie.Instrumentversie().MomentopnameLaatsteWijziging() === mo)) {
                relevanteMO.push(mo);
                relevanteBranches[mo.Branch().Code()] = true;
            } else if (mo.Branch().Code() in relevanteBranches && mo.HeeftGewijzigdeTijdstempels()) {
                relevanteMO.push(mo);
            } else {
                overigeMO.push(mo);
            }
        });

        // Teken de momentopnamen
        this.#svg += `
<g data-bgvbd="${voorInstrument}" class="${voorInstrument === this.#voorInstrument ? 'bgvbd_active' : 'bgvbd_hidden'}">`
        for (let mo of overigeMO) {
            this.#svg += this.#MomentopnameSvg(mo, 'bgvbd_STOP_nvt');
        }
        for (let mo of relevanteMO) {
            this.#svg += this.#MomentopnameSvg(mo, mo.Activiteit().IsOfficielePublicatie() ? 'bgvbd_STOP_P' : 'bgvbd_STOP_R');
        }
        for (let mo of relevanteMO) {
            let versie = mo.Instrumentversie(voorInstrument).Instrumentversie();
            if (versie.LVBBBasisversie() && mo.Branch() !== versie.LVBBBasisversie().Branch()) {
                this.#svg += this.#BasisversieLijnMetPijlpuntSvg(versie.LVBBBasisversie(), mo, false, 'basis');
            }
            for (let v of versie.LVBBVervlochtenVersies()) {
                this.#svg += this.#VervlochtenLijnMetPijlpuntSvg(v, mo, 'vv');
            }
            for (let v of versie.LVBBOntvlochtenVersies()) {
                this.#svg += this.#OntvlochtenLijnMetPijlpuntSvg(v, mo, 'ov');
            }
        }
        this.#svg += `
</g>`
    }
    //#endregion

    //#region SVG hulpfuncties en constanten
    static #Symbool_Inhoud = '&#128214;'; // https://unicode-table.com/en/1F4D6/ open book
    static #Symbool_Tijdstempel = '&#128344;' // https://unicode-table.com/en/1F558/ clock 9
    static #Symbool_Uitwisseling = '&#128721;' // https://unicode-table.com/en/1F6D1/ STOP sign

    static #ElementBreedte = 60 // Breedte van een momentopname rechthoek in diagram-eenheden
    static #ElementHoogte = 30 // Hoogte van een momentopname rechthoek in diagram - eenheden
    static #TussenruimteBreedte = VersiebeheerDiagram.#ElementBreedte / 2;
    static #TussenruimteHoogte = VersiebeheerDiagram.#ElementHoogte * 2;
    static #TijdstipBreedte = 100 // Breedte van de tekst met een tijdstip
    static #NaamBreedte = 100 // Breedte van de naam van een project of branch
    static #NaamHoogte = 25 // Hoogte van de naam van een project of branch
    static #Punt_d = 7 // Afstand punt - punt tot raakpunt haaks op de lijn
    static #Punt_0 = 4 // Afstand punt - raakpunt langs de lijn
    static #Punt_1 = 10 // Afstand punt - punt - raakpunt langs de lijn

    /**
     * Registreer de positie en afmeting van een element en pas de grootte van het diagram aan
     * @param {number} x
     * @param {number} y
     * @param {number} w
     * @param {number} h
     * @param {any} key - Optioneel, geef een key om de positie later op te halen
     */
    #Registreer(x, y, w, h, key) {
        if (key) {
            this.#positie[key] = { x: x, y: y, w: w, h: h };
        }
        if (x + w + VersiebeheerDiagram.#TussenruimteBreedte > this.#breedte) {
            this.#breedte = x + w + VersiebeheerDiagram.#TussenruimteBreedte;
        }
        if (y + h + VersiebeheerDiagram.#TussenruimteHoogte > this.#hoogte) {
            this.#hoogte = y + h + VersiebeheerDiagram.#TussenruimteHoogte;
        }
    }
    #positie; // Cache van posities (array met x, y, w, h)

    /**
     * Teken een blokje voor een momentopname
     * @param {Momentopname} momentopname - Te tekenen momentopname
     * @param {string} css - CSS class voor weergave
     * @returns {string} - SVG
     */
    #MomentopnameSvg(momentopname, css) {
        let symbolen = '';
        if (!momentopname.IsTegelijkBeheerdEnVolgend()) {
            if (momentopname.HeeftGewijzigdeInstrumentversie()) {
                symbolen += VersiebeheerDiagram.#Symbool_Inhoud;
            }
            if (momentopname.HeeftGewijzigdeTijdstempels()) {
                symbolen += VersiebeheerDiagram.#Symbool_Tijdstempel;
            }
            if (momentopname.Activiteit().HeeftUitwisselingen()) {
                symbolen += VersiebeheerDiagram.#Symbool_Uitwisseling;
            }
        }
        let pos = this.#positie[momentopname.Index()];
        return `<rect x="${pos.x}" y="${pos.y}" width="${pos.w}" height="${pos.h}" data-bga="${momentopname.Activiteit().Index()}" data-prj="${momentopname.Branch().Project().Index()}" rx="3" ry="3" class="bgvbd_mo ${css}"></rect>
                <text x="${pos.x + pos.w / 2}" y="${pos.y + pos.h / 2}" data-bga="${momentopname.Activiteit().Index()}" data-prj="${momentopname.Branch().Project().Index()}" dominant-baseline="middle" text-anchor="middle" class="bgvbd_symbolen">${symbolen}</text>`;
    }

    /**
     * Teken een lijn met een pijlpunt die de basisversie van een branch weergeeft
     * @param {Momentopname} van - Momentopname waar de pijl begint
     * @param {Momentopname} naar - Momentopname waar de pijl eindigt
     * @param {boolean} isBasis - Vereenvoudige lijn voor de basisversie
     * @param {string} css - CSS class suffix voor weergave
     * @returns {string} - SVG
     */
    #BasisversieLijnMetPijlpuntSvg(van, naar, isBasis, css) {
        return this.#LijnMetPijlpuntSvg(van, naar, 0, 0.5, 0.25, isBasis, css);
    }

    /**
     * Teken een lijn met een pijlpunt die een vervlechting weergeeft
     * @param {Momentopname} van - Momentopname waar de pijl begint
     * @param {Momentopname} naar - Momentopname waar de pijl eindigt
     * @param {string} css - CSS class suffix voor weergave
     * @returns {string} - SVG
     */
    #VervlochtenLijnMetPijlpuntSvg(van, naar, css) {
        return this.#LijnMetPijlpuntSvg(van, naar, 0.5, 0.25, 0.5, false, css);
    }

    /**
     * Teken een lijn met een pijlpunt die een ontvlechting weergeeft
     * @param {Momentopname} van - Momentopname waar de pijl begint
     * @param {Momentopname} naar - Momentopname waar de pijl eindigt
     * @param {string} css - CSS class suffix voor weergave
     * @returns {string} - SVG
     */
    #OntvlochtenLijnMetPijlpuntSvg(van, naar, css) {
        return this.#LijnMetPijlpuntSvg(van, naar, -0.5, 0.375, 0.375, false, css);
    }

    /**
     * Teken een lijn met een pijlpunt - dit zijn relaties tussen branches
     * @param {Momentopname} van - Momentopname waar de pijl begint
     * @param {Momentopname} naar - Momentopname waar de pijl eindigt
     * @param {number} dx - Fractie van de elementbreedte, vanaf de branchlijn tot het punt waar de lijn start/eindigt
     * @param {number} dy - Fractie van verticale tussenruimte waar de lijn eerst naar toe gaat
     * @param {number} t_dx - Fractie van horizontale tussenruimte, afstand van element tot de vertikale lijn
     * @param {boolean} isBasis - Vereenvoudige lijn voor de basisversie
     * @param {string} css - CSS voor weergave
     * @returns {string} - SVG
     */
    #LijnMetPijlpuntSvg(van, naar, dx, dy, t_dx, isBasis, css) {
        let vanPositie = this.#positie[van.Index()];
        let naarPositie = this.#positie[naar.Index()];
        dx = Math.round(dx * VersiebeheerDiagram.#ElementBreedte / 2);
        dy = Math.round(dy * VersiebeheerDiagram.#TussenruimteHoogte);
        t_dx = Math.round(t_dx * VersiebeheerDiagram.#TussenruimteHoogte);

        // Lijn:
        // van b(egin) omlaag naar t(ussenpunt)1
        // van t1 naar tussenruimte t1b
        // van t1b omlaag naar t2b (*)
        // van t2b naar branchlijn, naar t2
        // van t2 naar e(eindelement)
        // Als elementen op opeenvolgende rijen liggen, is (*) niet nodig
        let yb = vanPositie.y + vanPositie.h;
        let yt1 = yb + dy; // y van t1 en t1b
        let yt2 = naarPositie.y - VersiebeheerDiagram.#TussenruimteHoogte + dy; // y van t2 en t2b
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
        let svg = `<path d="M ${xb} ${yb} L ${xb} ${yt1}`;
        if (isBasis) {
            svg += ` L ${xe} ${yt1}`;
        }
        else {
            svg += ` L ${xt1} ${yt1}`;
            if (yt1 != yt2) {
                svg += ` L ${xt1} ${yt2}`;
            }
            if (xt1 != xt2) {
                svg += ` L ${xt2} ${yt2}`;
            }
            svg += ` L ${xe} ${yt2}`;
        }
        svg += ` L ${xe} ${ye}" class="bgvbd_line_${css}"/>
                <path d="M ${xe} ${ye} L ${xe - VersiebeheerDiagram.#Punt_d} ${ye - VersiebeheerDiagram.#Punt_1} L ${xe} ${ye - VersiebeheerDiagram.#Punt_0} L ${xe + VersiebeheerDiagram.#Punt_d} ${ye - VersiebeheerDiagram.#Punt_1} Z" class="bgvbd_line_${css}_p"/>`;
        return svg;
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

//#region Intern datamodel voor instrumenten en instrumentversies
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
    static SoortAnnotatie_Toelichtingsrelaties = 'Toelichtingsrelaties';
    static SoortAnnotatie_Symbolisatie = 'Symbolisatie';
    static SoortAnnotatie_Gebiedsmarkering = 'Gebiedsmarkering';
    static SoortAnnotatie_NonSTOP = 'NonSTOP';
    //#endregion

    //#region Eigenschappen
    /**
     * Naam van de annotatie
     * @returns {string}
     */
    Naam() {
        return this.#naam;
    }
    /** @type {string} */
    #naam;
    /**
     * Geeft een vrije naam voor een non-STOP annotatie
     * @returns {string}
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
     * @returns {number}
     */
    UUID() {
        return this.#uuid;
    }
    /** @type {number} */
    #uuid;
    static #laatste_uuid = 0; // Absolute waarde is niet relevant mits >= 0, alleen gebruikt @runtime

    /**
     * Geeft de momentopname waarvoor de annotatie is aangemaakt
     * @returns {Momentopname}
     */
    Momentopname() {
        return this.#momentopname
    }
    /** @type {Momentopname} */
    #momentopname;

    /**
     * Geeft aan of deze annotatie hetzelfde is (naam + waarde) als een andere annotatie
     * @param {Annotatie} annotatie
     * @returns {boolean}
     */
    IsGelijkAan(annotatie) {
        return this.UUID() === annotatie?.UUID() && this.Naam() === annotatie?.Naam();
    }

    /**
     * Geeft aan of twee annotaties gelijk aan elkaar zijn.
     * @param {Annotatie} annotatie1
     * @param {Annotatie} annotatie2
     * @returns {boolean}
     */
    static ZijnGelijk(annotatie1, annotatie2) {
        if (annotatie1) {
            return annotatie1.IsGelijkAan(annotatie2);
        } else {
            return !Boolean(annotatie2);
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
     * @param {string} citeertitel - Citeertitel, een van de onderdelen van de metadata
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
     * @returns {string}
     */
    Citeertitel() {
        return this.#citeertitel;
    }
    /** @type {string} */
    #citeertitel;

    /**
     * Geeft aan of deze annotatie hetzelfde is (naam + waarde) als een andere annotatie
     * @param {Annotatie} annotatie
     * @returns {boolean}
     */
    IsGelijkAan(annotatie) {
        return this.Naam() === annotatie?.Naam() && this.Citeertitel() === annotatie?.Citeertitel();
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
    static SoortInstrument_Muteerbaar = [Instrument.SoortInstrument_Regeling, Instrument.SoortInstrument_GIO]

    static SoortAnnotatiesVoorInstrument = {
        b: [
            Annotatie.SoortAnnotatie_Citeertitel,
            Annotatie.SoortAnnotatie_Gebiedsmarkering
        ],
        reg: [
            Annotatie.SoortAnnotatie_Citeertitel,
            Annotatie.SoortAnnotatie_Toelichtingsrelaties
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
     * @param {string} instrumentnaam - Naam van het instrument
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
     * Geef een (ongesorteerde) lijst met bekende instrumentnamen
     * @returns {string[]}
     */
    static Instrumentnamen(soortInstrument) {
        let alleInstrumenten = {};
        Momentopname.VoorAlleMomentopnamen(undefined, undefined, (momentopname) => {
            for (let versie of momentopname.Instrumentversies()) {
                let naam = versie.Instrument();
                if (!soortInstrument || naam.startsWith(soortInstrument + '_')) {
                    alleInstrumenten[naam] = true;
                }
            }
        });
        return Object.keys(alleInstrumenten);
    }
    /**
     * Vergelijkt twee instrumentnamen (voor regelgeving) ten behoeve van sortering
     * @param {string} instrument1
     * @param {string} instrument2
     * @returns {number}
     */
    static VergelijkInstrumentnamen(instrument1, instrument2) {
        let soort1 = Instrument.SoortInstrument_Regelgeving.indexOf(Instrument.SoortInstrument(instrument1));
        let soort2 = Instrument.SoortInstrument_Regelgeving.indexOf(Instrument.SoortInstrument(instrument2));
        let verschil = soort1 - soort2;
        if (verschil === 0) {
            verschil = instrument1.localeCompare(instrument2);
        }
        return verschil;
    }

    /**
     * Geef een vrij te gebruiken naam voor een soort instrument
     * @param {string} soortInstrument
     * @returns {string}
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
     * @returns {string}
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
        if (gewijzigd) {
            this.#uuidNieuweVersie = gewijzigd?.#uuidNieuweVersie;
        }
        this.#Kopieer(gewijzigd ? gewijzigd : basisversie);
        if (gewijzigd?.IsEerdereVersie()) {
            this.#eerdereVersie = gewijzigd.#eerdereVersie;
        }
    }
    /**
     * Neem de inhoud over van het origineel
     * @param {Instrumentversie} origineel - Instrumentversie met originele inhoud
     */
    #Kopieer(origineel) {
        this.#meenemenInConsolidatie = true;
        if (origineel) {
            this.#uuid = origineel.#uuid;
            this.#publicatieIndex = origineel.#publicatieIndex;
            this.#work = origineel.#work;
            this.#isIngetrokken = origineel.#isIngetrokken;
            this.#eerdereVersie = origineel.#eerdereVersie;
            this.#juridischeInhoud = origineel.#juridischeInhoud;
            this.#meenemenInConsolidatie = origineel.#meenemenInConsolidatie;
            this.#versieWelInPublicatie = origineel.#versieWelInPublicatie;
            this.#nonStopAnnotaties = Object.assign({}, origineel.#nonStopAnnotaties);
            this.#stopAnnotaties = Object.assign({}, origineel.#stopAnnotaties);
            this.#momentopnameLaatsteWijziging = origineel.#momentopnameLaatsteWijziging;
            if (this.Branch() === origineel.Branch()) {
                this.#isTeruggetrokken = origineel.#isTeruggetrokken;
                this.#meenemenInConsolidatie = origineel.#meenemenInConsolidatie;
            } else {
                this.#isTeruggetrokken = true;
            }
        } else {
            this.#uuid = undefined;
            this.#isIngetrokken = false;
            this.#eerdereVersie = undefined;
            this.#juridischeInhoud = undefined;
            this.#nonStopAnnotaties = {}
            this.#stopAnnotaties = {}
            this.#isTeruggetrokken = true;
            this.#meenemenInConsolidatie = true;
            this.#versieWelInPublicatie = true;
            this.#momentopnameLaatsteWijziging = this.Momentopname();
        }
    }

    /**
     * Verwijder alle relaties met andere objecten
     */
    destructor() {
        if (this.#basisversie) {
            this.#isBasisversieVoor.splice(this.#isBasisversieVoor.indexOf(this), 1);
            this.#basisversie = undefined;
        }
    }
    //#endregion

    //#region Eigenschappen en wijzigen daarvan
    /**
     * De branch die deze instrumentversie beheert
     * @returns {Branch}
     */
    Branch() {
        return this.Momentopname().Branch();
    }

    /**
     * De momentopname waar deze instrumentversie deel van uitmaakt.
     * @returns {Momentopname}
     */
    Momentopname() {
        return this.#momentopname;
    }
    /** @type {Momentopname} */
    #momentopname;

    /**
     * De naam van het instrument
     * @returns {string}
     */
    Instrument() {
        return this.#instrument;
    }
    /** @type {string} */
    #instrument;

    /**
     * Geeft de soort van het instrument waar dit een versie van is
     * @returns {string}
     */
    SoortInstrument() {
        return this.#soortInstrument;
    }
    /** @type {string} */
    #soortInstrument;

    /**
     * Uniek ID voor deze instrumentversie.
     * @returns {number}
     */
    UUID() {
        return this.#uuid;
    }
    /** @type {number} */
    #uuid;
    #MaakNieuweVersie() {
        if (!this.#uuidNieuweVersie) {
            this.#uuidNieuweVersie = BGProcesSimulator.Singletons('UUID', 1);
            BGProcesSimulator.Singletons().UUID++;
        }
        this.#uuid = this.#uuidNieuweVersie;
        this.#publicatieIndex = 1;
        this.#isTeruggetrokken = false;
        this.#momentopnameLaatsteWijziging = this.Momentopname();
    }
    /**
     * De UUID te gebruiken als dit een nieuwe versie is.
     * Deze wordt bewaard zodat het uuid niet steeds wijzigt 
     * als in deze applicatie de eindgebruiker de versie wijzigt
     * en de wijziging weer terugdraait.
     * @type {number} */
    #uuidNieuweVersie;

    /**
     * Geef een UUID door die al in de specificatie wordt gebruikt
     * @param {number} uuid
     */
    static UUIDGebruiktInSpecificatie(uuid) {
        if (BGProcesSimulator.Singletons('UUID', 0) < uuid) {
            BGProcesSimulator.Singletons().UUID = uuid;
        }
    }

    /**
     * Geeft de AKN/JOIN identificatie van deze instrumentversie
     * @returns {string}
     */
    ExpressionIdentificatie() {
        return this.#ExpressionIdentificatie(this.#publicatieIndex);
    }
    #publicatieIndex = 1;
    #ExpressionIdentificatie(publicatieIndex) {
        if (this.#versieWelInPublicatie) {
            if (this.IsEerdereVersie()) {
                return this.#eerdereVersie.ExpressionIdentificatie();
            } else if (this.IsNieuweVersie()) {
                let work = this.WorkIdentificatie();
                if (this.SoortInstrument() === Instrument.SoortInstrument_Regeling) {
                    return `${work}/nld@${this.Momentopname().Tijdstip().DatumHtml()};${this.UUID()};${this.Momentopname().Branch().Code()}${publicatieIndex > 1 ? `;pub_${publicatieIndex}` : ''}`;
                } else {
                    return `${work}/@${this.Momentopname().Tijdstip().DatumHtml()};${this.UUID()};${this.Momentopname().Branch().Code()}${publicatieIndex > 1 ? `;pub_${publicatieIndex}` : ''}`;
                }
            } else if (this.HeeftJuridischeInhoud()) {
                return this.#basisversie.#ExpressionIdentificatie(publicatieIndex);
            }
        }
    }

    /**
     * Geeft de AKN/JOIN identificatie van het instrument waar dit een versie van is
     * @returns {string}
     */
    WorkIdentificatie() {
        if (!this.#work) {
            this.#work = Instrument.Work(this.Instrument());
        }
        return this.#work;
    }
    /** @type {string} */
    #work;

    /**
     * Geeft de momentopname waarin de instrumentversie voor het laatst gewijzigd is.
     * @returns {Momentopname}
     */
    MomentopnameLaatsteWijziging() {
        return this.#momentopnameLaatsteWijziging;
    }
    /** @type {Momentopname} */
    #momentopnameLaatsteWijziging;


    /**
     * Geeft aan dat dit een initiële versie is, d.w.z. dat de juridische uitgangssituatie
     * geen versie van het instrument kent en dat een instrumentversie op deze branch dus
     * een volledig nieuwe versie moet zijn.
     * @returns {boolean}
     */
    IsInitieleVersie() {
        let uitgangssituatie = this.Momentopname().JuridischeUitgangssituatie();
        if (uitgangssituatie) {
            if (uitgangssituatie.Instrumentversie(this.Instrument())) {
                // Instrument bekend in juridische uitgangssituatie
                return false;
            }
            if (uitgangssituatie.JuridischWerkendVanaf().HeeftWaarde()) {
                // Het kan nog zijn dat het instrument wel in de consolidatie zit maar niet in de juridische uitgangssituatie
                // als de consolidatie nog niet voltooid is
                for (let branchCode of uitgangssituatie.Activiteit().Consolidatiestatus().NuGeldend(uitgangssituatie.Tijdstip())?.IWTMoment().Inwerkingtredingbranchcodes() ?? []) {
                    if (Branch.Branch(branchCode).LaatsteMomentopname(uitgangssituatie.Tijdstip())?.Instrumentversie(this.Instrument())) {
                        return false;
                    }
                }
            }
        }
        return true;
    }

    /**
     * Geeft aan dat dit een nieuwe instrumentversie is, d.w.z. dat het een 
     * andere inhoud heeft als de voorgaande versie op de branch. Dit is nooit 
     * het geval als IsOngewijzigdInBranch = true of IsEerdereVersie.
     * @returns {boolean}
     */
    IsNieuweVersie() {
        if (this.IsOngewijzigdInBranch() || this.IsEerdereVersie()) {
            return false;
        }
        return this.#uuidNieuweVersie && this.#uuid === this.#uuidNieuweVersie;
    }

    /**
     * Geeft aan of het instrument ongewijzigd is op deze branch, d.w.z de
     * inhoud van het instrument is de instrumentversie bij het ontstaan 
     * van de branch.
     * @returns {boolean}
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
            this.#Kopieer(this.BasisversieStartBranch());
            // Wel gewijzigd
            this.#momentopnameLaatsteWijziging = this.Momentopname();
        }
    }
    /** @type {boolean} */
    #isTeruggetrokken;

    /**
     * Geef de ongewijzigde versie waarop deze instrumentversie is gebaseerd
     * @returns {Instrumentversie}
     */
    Basisversie() {
        return this.#basisversie;
    }
    /**
     * Geeft aan dat er een andere instrumentversie is waarvoor dit een basisversie is,
     * waarbij de andere instrumentversie anders is dan deze.
     * @returns {boolean}
     */
    IsBasisversie() {
        for (let latereVersie of this.#isBasisversieVoor) {
            if (latereVersie.UUID() != this.UUID() || latereVersie.IsBasisversie()) {
                return true;
            }
        }
        return false;
    }
    /** @type {Instrumentversie[]} */
    #isBasisversieVoor = [];

    /**
     * Geeft de basisversie die gebruikt is bij de start van de branch waarvoor dit een instrumentversie is
     * @returns {Instrumentversie}
     */
    BasisversieStartBranch() {
        for (let voorganger = this.#basisversie; voorganger; voorganger = voorganger.#basisversie) {
            if (voorganger.Branch() != this.Branch()) {
                // Dit is de versie
                return voorganger;
            }
        }
    }

    /**
     * Maak alle wijzigingen ongedaan en maak deze versie gelijk aan de ongewijzigde versie
     */
    Undo() {
        this.#Kopieer(this.#basisversie);
    }
    /** @type {Instrumentversie} */
    #basisversie;

    /**
     * Geeft aan dat een eerder gemaakte versie gebruikt wordt in plaats van 
     * een wijziging van de voorgaande versie.
     * @returns {boolean}
     */
    IsEerdereVersie() {
        return Boolean(this.#eerdereVersie);
    }
    /**
     * Geeft de eerder gemaakte versie (van een andere branch).
     * @returns {Instrumentversie}
     */
    EerdereVersie() {
        return this.#eerdereVersie;
    }
    /**
     * Gebruik een eerder gemaakte versie als volgende instrumentversie op de branch.
     * @param {Instrumentversie} instrumentversie
     */
    GebruikEerdereVersie(instrumentversie) {
        this.Undo();
        this.#isIngetrokken = false;
        this.#juridischeInhoud = instrumentversie.#juridischeInhoud;
        this.#nonStopAnnotaties = Object.assign({}, instrumentversie.#nonStopAnnotaties);
        this.#stopAnnotaties = Object.assign({}, instrumentversie.#stopAnnotaties);
        this.#eerdereVersie = instrumentversie;
        this.#uuid = instrumentversie.#uuidNieuweVersie;
        this.#publicatieIndex = instrumentversie.#publicatieIndex;
        this.#isTeruggetrokken = false;
        this.#momentopnameLaatsteWijziging = this.Momentopname();
    }
    /** @type {Instrumentversie} */
    #eerdereVersie;

    /**
     * Geeft aan dat een instrumentversie niet gebruikt moet worden bij 
     * consolidatie, omdat de eigenlijke juridische inhoud onbekend is. 
     * Als de instrumentversie wel een ExpressionIdentificatie heeft,
     * dan is de versie in de publicatie niet de goede versie om voor
     * de consolidatie te gebruiken.
     * @returns {boolean}
     */
    MeenemenInConsolidatie() {
        return this.#meenemenInConsolidatie;
    }
    /** @type {boolean} */
    #meenemenInConsolidatie;

    /**
     * Geeft aan of de instrumentversie niet gebruikt moet worden bij 
     * consolidatie.
     * @param {boolean} inderdaad - Niet gebruiken bij consolidatie?
     * @param {boolean} versieWelInPublicatie - Bij inderdaad: staat er wel een instrumentversie in de publicatie?
     */
    NietGebruikenVoorConsolidatie(inderdaad, versieWelInPublicatie) {
        this.#meenemenInConsolidatie = !inderdaad;
        this.#versieWelInPublicatie = this.#meenemenInConsolidatie || versieWelInPublicatie;
    }
    /** @type {boolean} */
    #versieWelInPublicatie;
    //#endregion

    //#region Inhoud van instrumentversie en wijzigen daarvan
    /**
     * Geeft aan dit een versie is met juridische inhoud (tekst of data). Zo niet,
     * dan is het een placeholder voor iets dat nog komen gaat.
     * @returns {boolean}
     */
    HeeftJuridischeInhoud() {
        return !this.#isIngetrokken && this.#juridischeInhoud;
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
    /** @type {Annotatie} */
    #juridischeInhoud;

    /**
     * Geeft aan of het instrument ingetrokken is
     * @returns {boolean}
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
    /** @type {boolean} */
    #isIngetrokken;

    /**
     * Geef aan of de instrumentversie annotaties heeft
     * @param {boolean} isStop - Geeft aan of het om de STOP annotaties gaat - undefined voor alle annotaties
     * @returns {boolean}
     */
    HeeftAnnotaties(isStop) {
        if (!this.HeeftJuridischeInhoud()) {
            return false;
        }
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
     * @returns {string[]}
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
            if (this.#basisversie) {
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
     * @returns {Annotatie}
     */
    Annotatie(isStop, naam) {
        if (this.HeeftJuridischeInhoud()) {
            if (isStop) {
                return this.#stopAnnotaties[naam];
            } else {
                return this.#nonStopAnnotaties[naam];
            }
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
            if (!Instrument.NonStopAnnotatiesVoorInstrument.includes(this.SoortInstrument())) {
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
        if (!this.#basisversie) {
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
        if (annotaties[naam]) {
            delete annotaties[naam];
            return true;
        }
        return false;
    }
    /** @type {Object.<string,Annotatie>} */
    #stopAnnotaties;
    /** @type {Object.<string,Annotatie>} */
    #nonStopAnnotaties;

    /**
     * Geeft aan of deze versie en de andere versie inhoudelijk gelijk zijn.
     * Ze hebben ofwel dezelfde juridische inhoud, ofwel zijn beide ingetrokken, etc.
     * @param {Instrumentversie} andereVersie
     * @returns {boolean}
     */
    HeeftDezelfdeInhoud(andereVersie) {
        if (andereVersie) {
            if (this.IsIngetrokken()) {
                return andereVersie.IsIngetrokken();
            } else if (andereVersie.IsIngetrokken()) {
                return false;
            } else {
                return this.UUID() === andereVersie.UUID();
            }
        } else {
            return false;
        }
    }
    //#endregion

    //#region Van / naar specificatie
    /**
     * Pas de specificatie toe op de ongewijzigde versie
     * @param {any} specificatie
     */
    PasSpecificatieToe(specificatie) {
        if (this.#basisversie) {
            this.#basisversie.#isBasisversieVoor.push(this);
        }

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
                    if (spec?.Instrumentversie().UUID() === specificatie) {
                        instrumentversie = spec.Instrumentversie();
                    }

                }
            });
            if (!instrumentversie) {
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
                    this.AnnotatieWordt(true, new Metadata(specificatie[annotatie], this.Momentopname()));
                } else if (annotatie !== Annotatie.SoortAnnotatie_NonSTOP) {
                    if (specificatie[annotatie] === false) {
                        this.AnnotatieWeg(true, annotatie);
                    } else {
                        this.AnnotatieWordt(true, new Annotatie(annotatie, this.Momentopname()));
                    }
                } else {
                    for (let nonStop in specificatie[annotatie]) {
                        if (specificatie[annotatie][nonStop] === false) {
                            this.AnnotatieWeg(false, nonStop);
                        } else {
                            this.AnnotatieWordt(false, new Annotatie(nonStop, this.Momentopname()));
                        }
                    }
                }
            }
            if (specificatie.uuid) {
                specificatie.uuid = this.UUID();
            }
        }
    }

    /**
     * Maak de specificatie van de wijziging
     */
    MaakSpecificatie() {
        if (this.IsEerdereVersie()) {
            // Verwijzing naar eerdere instrumentversie
            return this.#eerdereVersie.UUID();
        }
        if (this.IsOngewijzigdInBranch()) {
            if (this.Branch() !== this.#basisversie?.Branch()) {
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
                    let origineel = this.#basisversie?.Annotatie(true, naam);
                    let annotatie = this.Annotatie(true, naam);
                    if (!Annotatie.ZijnGelijk(origineel, annotatie)) {
                        if (!annotatie) {
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
                    let origineel = this.#basisversie?.Annotatie(false, naam);
                    let annotatie = this.Annotatie(false, naam);
                    if (!Annotatie.ZijnGelijk(origineel, annotatie)) {
                        specificatie[Annotatie.SoortAnnotatie_NonSTOP][naam] = Boolean(annotatie);
                    }
                }
                return specificatie;
            }
        }
    }
    //#endregion

    //#region Gepubliceerde instrumentversies
    /**
     * Geeft aan of een instrumentversie opgenomen wordt in de (concept-)publicatie
     * die als onderdeel van deze activiteit gemaakt wordt.
     * @returns {boolean}
     */
    IsOnderdeelVanLVBBPublicatie() {
        if (this.Momentopname().IsTegelijkBeheerdEnVolgend()) {
            // In publicaties is alleen juridische inhoud van de eerste branch aanwezig
            return false;
        }
        if (!this.HeeftJuridischeInhoud()) {
            // In publicaties is alleen juridische inhoud aanwezig
            return false;
        }
        if (this.IsOngewijzigdInBranch()) {
            // Als dit al een terugtrekking zou betekenen, dan is dat af te leiden uit de tekst.
            // De juridische inhoud is namelijk al in andere publicaties beschreven
            return false;
        }
        if (!this.#versieWelInPublicatie) {
            // Wel inhoud, maaar die komt niet in de publicatie voor
        }
        let collectie = BGProcesSimulator.Singletons("PubliekeInstrumentversies", {});
        let expressionId = this.ExpressionIdentificatie();
        if (this.IsEerdereVersie()) {
            // Verwijzing naar een (als het goed is) eerder gepubliceerde versie
            if (this.Momentopname().Activiteit().IsOfficielePublicatie() && !(expressionId in collectie)) {
                this.Momentopname().Activiteit().SpecificatieMelding(`Er wordt vanuit branch ${this.Momentopname().Branch().Code()} @${this.Momentopname().Tijdstip().DatumTijdHtml()} verwezen naar een eerdere versie (${expressionId}) maar die is nog niet gepubliceerd`);
            }
            return false;
        }
        else {
            // Dit is juridische inhoud die opgenomen wordt als het gewijzigd is ten opzichte van de uitgangssituatie
            if (this.UUID() === this.Momentopname().JuridischeUitgangssituatie()?.Instrumentversie(this.Instrument())?.Instrumentversie()?.UUID()) {
                // Geen wijziging ten opzichte van de uitgangssituatie
                return false;
            }
            let huidigeExpressionId = expressionId;
            if (this.Momentopname().Activiteit().IsOfficielePublicatie()) {
                // Zorg dat er een unieke expressionId ontstaat
                while (expressionId in collectie) {
                    if (collectie[expressionId] === this.Momentopname().Tijdstip().Specificatie()) {
                        // Deze methode is blijkbaar al eerder aangeroepen
                        break;
                    }
                    this.#publicatieIndex++;
                    expressionId = this.ExpressionIdentificatie();
                }
                collectie[expressionId] = this.Momentopname().Tijdstip().Specificatie();
            }
            if (huidigeExpressionId !== expressionId) {
                this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De software constateert dat versie van ${Instrument.SoortInstrumentNamen[this.SoortInstrument()]} ${huidigeExpressionId} 
                    onderdeel moet zijn van ${this.Momentopname().Activiteit().Publicatiebron()} maar al eerder is gepubliceerd. De (inhoudelijk ongewijzigde) versie krijgt daarom een nieuwe identificatie: ${expressionId}.`);
            }
            return true;
        }
    }

    /**
     * Maakt melding van de registratie van gepubliceerde instrumentversies
     * @param {Activiteit} activiteit
     */
    static MeldGepubliceerdeInstrumentversies(activiteit) {
        let toegevoegd = [];
        let collectie = BGProcesSimulator.Singletons("PubliekeInstrumentversies", {});
        for (const [expressionId, tijdstip] of Object.entries(collectie)) {
            if (activiteit.Tijdstip().Specificatie() == tijdstip) {
                toegevoegd.push(`<li>${expressionId}</li>`);
            }
        }
        if (toegevoegd.length > 0) {
            toegevoegd.sort();
            activiteit.UitvoeringMelding(Activiteit.Onderwerp_InternDatamodel, `<b>Gepubliceerde instrumentversies</b><br>De volgende expressionId zijn geregistreerd als gebruikt voor een instrumentversie 
            die onderdeel is van een publicatie. Deze expressionId zullen nooit meer voor een instrumentversie worden gebruikt die onderdeel is van een publicatie, zelfs
            als het om inhoudelijk dezelfde versie gaat:<ul>${toegevoegd.join('')}</ul>`);
        }
    }
    //#endregion

    //#region Uitwisseling via STOP
    /**
     * Geeft aan of deze instrumentversie-instantie onderdeel is van een uitwisseling met de LVBB.
     * Dit wordt in deze simulator gebruikt voor de weergave in het versiebeheer diagram.
     * @returns {boolean}
     */
    LVBBUitgewisseld() {
        return this.#instrumentversieUitgewisseld;
    }
    #instrumentversieUitgewisseld = false;

    /**
     * Geeft de laatst met de LVBB uitgewisselde versie.
     * @param {boolean} inclusiefDeze - Geeft aan of deze versie onderzocht moet worden, anders wordt naar de voorgaande versie gezocht.
     * @returns {Instrumentversie}
     */
    LaatsteLVBBUitgewisseld(inclusiefDeze) {
        for (let versie = inclusiefDeze ? this : this.#basisversie; versie; versie = versie.#basisversie) {
            if (versie.#instrumentversieUitgewisseld) {
                return versie;
            }
        }
    }

    /**
     * Geeft de basisversie die voor deze instrumentversie in de STOP ConsolidatieInformatie module 
     * aan de LVBB is gerapporteerd. Dit wordt in deze simulator gebruikt voor de weergave in het 
     * versiebeheer diagram.
     * @returns {Momentopname}
     */
    LVBBBasisversie() {
        return this.#stopBasisversie;
    }
    /** @type {Momentopname} */
    #stopBasisversie;

    /**
     * Geeft de vervlochten versies die voor deze instrumentversie in de STOP ConsolidatieInformatie module 
     * aan de LVBB zijn gerapporteerd. Dit wordt in deze simulator gebruikt voor de weergave in het 
     * versiebeheer diagram.
     * @returns {Momentopname[]}
     */
    LVBBVervlochtenVersies() {
        return this.#stopVervlochtenVersies;
    }
    /** @type {Momentopname[]} */
    #stopVervlochtenVersies = [];

    /**
     * Geeft de ontvlochten versies die voor deze instrumentversie in de STOP ConsolidatieInformatie module 
     * aan de LVBB zijn gerapporteerd. Dit wordt in deze simulator gebruikt voor de weergave in het 
     * versiebeheer diagram.
     * @returns {Momentopname[]}
     */
    LVBBOntvlochtenVersies() {
        return this.#stopOntvlochtenVersies;
    }
    /** @type {Momentopname[]} */
    #stopOntvlochtenVersies = [];

    /**
     * Geeft aan of de instrumentversie onderdeel is van de LVBB aanlevering
     * @param {boolean} isRevisie - Geeft aan of de momentopname deel is van een revisie en geen verwijzing naar de tekst kan hebben
     * @returns {[boolean, Instrumentversie]} Indicatie of de instrumentversie opgenomen moet worden in de consolidatie-informatie, en basisversie voor de LVBB
     */
    #IsOnderdeelVanLVBBAanlevering(isRevisie) {
        // Zoek de basisversie voor dit instrument
        let lvbbBasisversie = this.LaatsteLVBBUitgewisseld(false);
        let gebruikJuridischeUitgangssituatie = false;
        if (this.Momentopname().Branch() !== lvbbBasisversie?.Branch()) {
            // Dit is de eerste uitwisseling voor deze branch. Als de juridische uitgangssituatie op deze branch is bijgewerkt, dan is die als basisversie misschien beter.
            let juridischeBasisversie = this.Momentopname().JuridischeUitgangssituatie()?.Instrumentversie(this.Instrument())?.Instrumentversie().LaatsteLVBBUitgewisseld(true);
            if (!lvbbBasisversie || juridischeBasisversie.Momentopname().Tijdstip().Vergelijk(lvbbBasisversie.Momentopname().Tijdstip()) > 0) {
                lvbbBasisversie = juridischeBasisversie;
                gebruikJuridischeUitgangssituatie = true;
            }
        }

        // Bekijk of dit een wijziging is ten opzichte van de uitgewisselde versie
        let neemOpInCI = false;
        if (this.IsOngewijzigdInBranch()) {
            // Hoeft alleen gemeld te worden in de consolidatie-informatie als de lvbbBasisversie ook uit deze branch komt
            if (lvbbBasisversie?.Branch() === this.Branch() && !lvbbBasisversie.IsOngewijzigdInBranch()) {
                this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: instrument ${this.Instrument()} is teruggetrokken,
                want ${this.Momentopname().Activiteit().Publicatiebron()} bevat geen beschrijving meer van (een wijziging van) dit instrument.`)
                neemOpInCI = true;
            }
        } else if (this.IsIngetrokken()) {
            if (lvbbBasisversie?.Branch() !== this.Branch() || !lvbbBasisversie.IsIngetrokken()) {
                // Wijziging op deze branch
                if (isRevisie) {
                    this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: instrument ${this.Instrument()} wordt ingetrokken, van rechtswege of als gevolg van consolidatie.`)
                } else {
                    this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: ${this.Momentopname().Activiteit().Publicatiebron()} beschrijft de intrekking van instrument ${this.Instrument()}.`)
                }
                neemOpInCI = true;
            } else if (!isRevisie && !this.Momentopname().IsVaststellingsbesluitGepubliceerd()) {
                this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: ${this.Momentopname().Activiteit().Publicatiebron()} beschrijft de intrekking van instrument ${this.Instrument()}. 
                De intrekking is al eerder doorgegeven, maar wordt nogmaals opgenomen om de verwijzing naar de tekst (expression + eId van de publicatie) bij te werken.`)
                neemOpInCI = true;
            }
        } else if (this.HeeftJuridischeInhoud()) {
            // Zorg dat de expression ID goed gezet wordt
            if (!isRevisie) {
                this.IsOnderdeelVanLVBBPublicatie();
            }

            if (this.Momentopname().Instrumentversie(this.Instrument()).VervlochtenVersies().length > 0 || this.Momentopname().Instrumentversie(this.Instrument()).OntvlochtenVersies().length > 0 // Moet vermeld worden als er sprake is van vervlechting of ontvlechting
                || this.UUID() != lvbbBasisversie?.UUID() || this.ExpressionIdentificatie() !== lvbbBasisversie.ExpressionIdentificatie() // Hoeft anders alleen gemeld te worden in de consolidatie-informatie, als dat inhoudelijk of qua identificatie afwijkt van de voorgaande situatie
            ) {
                if (isRevisie) {
                    if (this.#meenemenInConsolidatie) {
                        this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: gebruik versie ${this.ExpressionIdentificatie()} in de consolidatie voor instrument ${this.Instrument()}.`)
                    }
                } else {
                    this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: ${this.Momentopname().Activiteit().Publicatiebron()} bevat een beschrijving van versie ${this.ExpressionIdentificatie()} van instrument ${this.Instrument()}.`)
                }
                if (!this.#meenemenInConsolidatie) {
                    if (this.#versieWelInPublicatie) {
                        this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: versie ${this.ExpressionIdentificatie()} mag niet gebruikt worden in de consolidatie.`)
                    } else {
                        this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: geen versie bekend voor instrument ${this.Instrument()} die in de consolidatie gebruikt kan worden.`)
                    }
                }
                neemOpInCI = true;
            }
        }
        if (!neemOpInCI) {
            return [false, undefined];
        }

        if (lvbbBasisversie && this.Momentopname().Branch() !== lvbbBasisversie.Branch()) {
            if (gebruikJuridischeUitgangssituatie) {
                this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()} en instrument ${this.Instrument()}:
                        dit is de eerste uitwisseling voor deze branch, en omdat sinds het aanmaken van deze branch de juridische uitgangssituatie is bijgewerkt, wordt die gebruikt
                        om de basisversie te vinden: branch ${lvbbBasisversie.Branch().Code()} op ${lvbbBasisversie.Momentopname().Tijdstip().DatumTijdHtml()}.`);
            } else {
                this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()} en instrument ${this.Instrument()}:
                        dit is de eerste uitwisseling sinds de uitwisseling voor branch ${lvbbBasisversie.Branch().Code()} op ${lvbbBasisversie.Momentopname().Tijdstip().DatumTijdHtml()}, dus dat wordt de basisversie.`);
            }
        }
        return [true, lvbbBasisversie];
    }

    /**
     * Voeg de informatie in deze instrumentversie toe aan de ConsolidatieInformatie module en
     * maak de "STOP" modules voor de annotaties die sinds de laatste uitwisseling met de LVBB zijn gewijzigd
     * @param {any} consolidatieInformatieModule - ConsolidatieInformatie module waaraan de informatie toegevoegd moet worden
     * @param {boolean} isRevisie - Geeft aan of de momentopname deel is van een revisie en geen verwijzing naar de tekst kan hebben
     * @param {registreerSTOPModule} registreerAnnotatieModule - Methode die wordt aangeroepen voor elke annotatiemodule, met de naam en STOP xml van de module
     */
    MaakModulesVoorLVBB(consolidatieInformatieModule, isRevisie, registreerAnnotatieModule) {
        let [isGewijzigd, lvbbBasisversie] = this.#IsOnderdeelVanLVBBAanlevering();
        if (!isGewijzigd) {
            return;
        }

        // Maak eerst het juiste element voor de consolidatie-informatie module
        let toegevoegd;
        let metVerOntVlechtingen = false;
        if (this.IsOngewijzigdInBranch()) {
            if (!consolidatieInformatieModule.Terugtrekkingen) {
                consolidatieInformatieModule.Terugtrekkingen = [];
            }
            if (this.SoortInstrument() === Instrument.SoortInstrument_Regeling) {
                toegevoegd = {
                    doel: this.Branch().Doel(),
                    instrument: this.WorkIdentificatie(),
                    eId: isRevisie ? undefined : "eId_terugtrekking"
                };
                consolidatieInformatieModule.Terugtrekkingen.push({
                    TerugtrekkingRegeling: toegevoegd
                });
            } else {
                toegevoegd = {
                    doel: this.Branch().Doel(),
                    instrument: this.WorkIdentificatie(),
                    eId: isRevisie ? undefined : "eId_bijlage_IO"
                };
                consolidatieInformatieModule.Terugtrekkingen.push({
                    TerugtrekkingInformatieobject: toegevoegd
                });
            }

        } else if (this.IsIngetrokken()) {
            if (this.SoortInstrument() === Instrument.SoortInstrument_Regeling) {
                toegevoegd = {
                    doel: this.Branch().Doel(),
                    instrument: this.WorkIdentificatie(this.Instrument()),
                    eId: isRevisie ? undefined : "eId_intrekking"
                };
            } else {
                toegevoegd = {
                    doel: this.Branch().Doel(),
                    instrument: this.WorkIdentificatie(this.Instrument()),
                    eId: isRevisie ? undefined : "eId_bijlage_IO"
                };
            }
            if (!consolidatieInformatieModule.Intrekkingen) {
                consolidatieInformatieModule.Intrekkingen = [];
            }
            consolidatieInformatieModule.Intrekkingen.push({ Intrekking: toegevoegd });
            metVerOntVlechtingen = true;

        } else {
            if (!consolidatieInformatieModule.BeoogdeRegelgeving) {
                consolidatieInformatieModule.BeoogdeRegelgeving = [];
            }
            toegevoegd = {
                doelen: [
                    { doel: this.Branch().Doel() }
                ]
            };
            if (this.Momentopname().IsEersteVanTegelijkBeheerd()) {
                // De instrumentversie geldt voor meerdere doelen
                for (let branch of this.Momentopname().TegelijkBeheerd()) {
                    if (branch != this.Momentopname().Branch()) {
                        toegevoegd.doelen.push({ doel: branch.Doel() });
                        // De bijbehorende instrumentversie moet ook als uitgewisseld gemarkeerd worden
                        branch.LaatsteMomentopname(this.Momentopname().Tijdstip()).Instrumentversie(this.Instrument()).Instrumentversie().#instrumentversieUitgewisseld = true;
                    }
                }
            }
            if (this.ExpressionIdentificatie()) {
                toegevoegd.instrumentVersie = this.ExpressionIdentificatie();
            } else {
                toegevoegd.instrument = this.WorkIdentificatie();
            }
            if (!this.#meenemenInConsolidatie) {
                toegevoegd.VoorConsolidatie = false;
            }
            if (this.SoortInstrument() === Instrument.SoortInstrument_Regeling) {
                toegevoegd.eId = isRevisie || !this.#versieWelInPublicatie ? undefined : "eId_wijzigartikel";
                consolidatieInformatieModule.BeoogdeRegelgeving.push({
                    BeoogdeRegeling: toegevoegd
                });
            } else {
                toegevoegd.eId = isRevisie || !this.#versieWelInPublicatie ? undefined : "eId_bijlage_IO";
                consolidatieInformatieModule.BeoogdeRegelgeving.push({
                    BeoogdInformatieobject: toegevoegd
                });
            }

            if (!this.#instrumentversieUitgewisseld || !this.ExpressionIdentificatie()) {
                // Eerste keer dat deze instrumentversie wordt uitgewisseld
                let voorgaandeVersie = lvbbBasisversie;
                if (BGProcesSimulator.Opties.AnnotatiesViaUitgangssituatie) {
                    // Voorgaande versie is de juridische uitgangssituatie
                    voorgaandeVersie = undefined;
                    if (Instrument.SoortInstrument_Muteerbaar.includes(this.SoortInstrument())) {
                        for (let momentopname = this.Momentopname().JuridischeUitgangssituatie(); momentopname; momentopname = momentopname.JuridischeUitgangssituatie()) {
                            let versie = momentopname.Instrumentversie(this.Instrument())?.Instrumentversie();
                            if (!versie?.HeeftJuridischeInhoud()) {
                                break;
                            }
                            if (versie.#instrumentversieUitgewisseld) {
                                voorgaandeVersie = versie;
                                break;
                            }
                        }
                    }
                } else if (this.HeeftAnnotaties()) {
                    this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Instrument ${this.Instrument()} is niet muteerbaar, dus worden alle annotaties bij elke instrumentversie (opnieuw) uitgewisseld.`)
                }
                this.#MaakAnnotatieModules(voorgaandeVersie, true, registreerAnnotatieModule);
            }
            metVerOntVlechtingen = true;
        }
        this.#instrumentversieUitgewisseld = true;

        if (lvbbBasisversie) {
            // Voeg de basisversie toe
            toegevoegd.gemaaktOpBasisVan = [{
                Basisversie: {
                    doel: lvbbBasisversie.Branch().Doel(),
                    gemaaktOp: lvbbBasisversie.Momentopname().Tijdstip().STOPDatumTijd()
                }
            }];
            this.#stopBasisversie = lvbbBasisversie.Momentopname();

            if (metVerOntVlechtingen && this.Momentopname().Branch() === lvbbBasisversie.Branch()) {
                if (!this.Momentopname().IsVaststellingsbesluitGepubliceerd()) {
                    // Een verandering van juridische uitgangssituatie voorafgaand aan de vaststelling moet als vervlechting gerapporteerd worden
                    if (this.Momentopname().JuridischeUitgangssituatie() !== lvbbBasisversie.Momentopname().JuridischeUitgangssituatie()) {
                        this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()} en instrument ${this.Instrument()}:
                        de juridische uitgangssituatie is gewijzigd sinds de voorgaande uitlevering, dat wordt als een vervlechting gerapporteerd.`)
                        toegevoegd.gemaaktOpBasisVan.push({
                            VervlochtenVersie: {
                                doel: this.Momentopname().JuridischeUitgangssituatie().Branch().Doel(),
                                gemaaktOp: this.Momentopname().JuridischeUitgangssituatie().Tijdstip().STOPDatumTijd()
                            }
                        });
                        this.#stopVervlochtenVersies.push(this.Momentopname().JuridischeUitgangssituatie());
                    }
                } else {
                    // Kijk of er ver-/ontvlechtingen zijn. In deze simulator worden ver-/ontvlechtingen direct doorgegeven.
                    let versies = this.MomentopnameLaatsteWijziging().Instrumentversie(this.Instrument()).VervlochtenVersies().map(v => v.Instrumentversie());
                    if (versies.length > 0) {
                        this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()} en instrument ${this.Instrument()}:
                        het oplossen van samenloop leidt tot een vervlechting met: ${versies.map(v => `branch ${v.MomentopnameLaatsteWijziging().Branch().Code()} @ ${v.MomentopnameLaatsteWijziging().Tijdstip().DatumTijdHtml()}`).join(', ')}.`)
                        for (let versie of versies) {
                            let uitgewisseldeMO = versie.LaatsteLVBBUitgewisseld(true).Momentopname();
                            toegevoegd.gemaaktOpBasisVan.push({
                                VervlochtenVersie: {
                                    doel: uitgewisseldeMO.Branch().Doel(),
                                    gemaaktOp: uitgewisseldeMO.Tijdstip().STOPDatumTijd()
                                }
                            });
                            this.#stopVervlochtenVersies.push(uitgewisseldeMO);
                        }
                    }
                    versies = this.MomentopnameLaatsteWijziging().Instrumentversie(this.Instrument()).OntvlochtenVersies().map(v => v.Instrumentversie());
                    if (versies.length > 0) {
                        this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()} en instrument ${this.Instrument()}:
                        het oplossen van samenloop leidt tot een ontvlechting met: ${versies.map(v => `branch ${v.MomentopnameLaatsteWijziging().Branch().Code()} @ ${v.MomentopnameLaatsteWijziging().Tijdstip().DatumTijdHtml()}`).join(', ')}.`)
                        for (let versie of versies) {
                            let uitgewisseldeMO = versie.LaatsteLVBBUitgewisseld(true).Momentopname();
                            toegevoegd.gemaaktOpBasisVan.push({
                                OntvlochtenVersie: {
                                    doel: uitgewisseldeMO.Branch().Doel(),
                                    gemaaktOp: uitgewisseldeMO.Tijdstip().STOPDatumTijd()
                                }
                            });
                            this.#stopOntvlochtenVersies.push(uitgewisseldeMO);
                        }
                    }
                }
            }
        }
    }

    /**
     * Voeg de informatie in deze instrumentversie toe aan de Momentopname module en
     * maak de "STOP" modules voor de annotaties die sinds de aanlevering van BG/download uit de LVBB zijn gewijzigd
     * @param {Activiteit} activiteit - Activiteit waarvoor de modules aangemaakt worden
     * @param {string} bron - Een van de Activiteit.Systeem* waarden die aangeeft welk systeem als bron optreedt
     * @param {any[]} pakbonComponenten - Componenten array uit de Pakbon module waaraan de informatie toegevoegd moet worden
     * @param {any[]} uitgewisseldeInstrumenten - UitgewisseldInstrument array uit de Momentopname module waaraan de informatie toegevoegd moet worden
     * @param {Momentopname} sindsMomentopname - De momentopname die de vorige levering aan het adviesbureau aangeeft.
     *                                           Undefined voor de beschrijving van een downloadpakket of uitlevering door bevoegd gezag.
     * @param {registreerSTOPModule} registreerModule - Methode die wordt aangeroepen voor elke STOP module, met de naam en STOP xml van de module
     */
    MaakModulesVoorUitwisseling(activiteit, bron, pakbonComponenten, uitgewisseldeInstrumenten, sindsMomentopname, registreerModule) {

        // Registratie in de momentopname module alleen met gemaaktOpBasisVan als het instrument in de sindsMomentopname aanwezig was
        let laatstUitgewisseldeVersie;
        if (bron === Activiteit.Systeem_LVBB || (bron === Activiteit.Systeem_Adviesbureau && !sindsMomentopname)) {
            // Laatst uitgewisselde versie is de laatst aan LVBB geleverde versie
            laatstUitgewisseldeVersie = this.LaatsteLVBBUitgewisseld(true);
        } else if (bron === Activiteit.Systeem_Adviesbureau) {
            // Laatst door BG geleverde versie
            laatstUitgewisseldeVersie = sindsMomentopname?.Instrumentversie(this.Instrument())?.Instrumentversie();
        }
        if (laatstUitgewisseldeVersie?.HeeftJuridischeInhoud()) {
            if (uitgewisseldeInstrumenten) {
                uitgewisseldeInstrumenten.push({
                    FRBRWork: this.WorkIdentificatie(),
                    gemaaktOpBasisVan: {
                        Basisversie: {
                            doel: laatstUitgewisseldeVersie.Momentopname().Branch().Doel(),
                            gemaaktOp: laatstUitgewisseldeVersie.Momentopname().Tijdstip().STOPDatumTijd()
                        }
                    }
                });
            }
            if (!this.HeeftJuridischeInhoud()) {
                // Geen onderdeel (meer) van de uitwisseling
                if (laatstUitgewisseldeVersie?.HeeftJuridischeInhoud()) {
                    activiteit.UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Instrument ${this.Instrument()} is geen onderdeel meer van de gewijzigde regelgeving en wordt niet uitgewisseld.`)
                }
                return;
            }
        } else if (!this.HeeftJuridischeInhoud()) {
            // Ook geen onderdeel (meer) van de uitwisseling
            return;
        } else if (uitgewisseldeInstrumenten) {
            // Nieuw instrument
            uitgewisseldeInstrumenten.push({
                FRBRWork: this.Instrument()
            });
        }
        activiteit.UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Instrument ${this.Instrument()} is onderdeel van de regelgeving en versie ${this.ExpressionIdentificatie()} wordt uitgewisseld.`)

        // Registreer de component in de pakbon
        let modules = [];
        let component = {
            Component: {
                FRBRWork: this.WorkIdentificatie(),
                soortWork: this.SoortInstrument() == Instrument.SoortInstrument_Regeling ? '/join/id/stop/work_019' : '/join/id/stop/work_010',
                heeftModule: {
                    Module: modules
                }
            }
        }
        pakbonComponenten.push(component);
        let bestandenIndex = pakbonComponenten.length;

        if (bron === Activiteit.Systeem_LVBB) {
            registreerModule('Momentopname', Activiteit.ModuleToXml('Momentopname', {
                _ns: Activiteit.STOP_Data,
                doel: laatstUitgewisseldeVersie.Momentopname().Branch().Doel(),
                gemaaktOp: laatstUitgewisseldeVersie.Momentopname().Tijdstip().STOPDatumTijd()
            }, this.ExpressionIdentificatie()));
            modules.push({
                localName: 'Momentopname',
                namespace: Activiteit.STOP_Data,
                bestandsnaam: `${bestandenIndex++}_Momentopname.xml`,
                mediatype: 'application/xml',
                schemaversie: BGProcesSimulator.STOP_Versie
            });
        }

        // Maak de module met juridische inhoud
        switch (this.SoortInstrument()) {
            case Instrument.SoortInstrument_Regeling:
                let naam = BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Rijksoverheid ? 'RegelingKlassiek' : 'RegelingCompact';
                registreerModule(naam, Activiteit.ModuleToXml(naam, {
                    _ns: Activiteit.STOP_Tekst
                }, this.ExpressionIdentificatie()));
                modules.push({
                    localName: naam,
                    namespace: Activiteit.STOP_Tekst,
                    bestandsnaam: `${bestandenIndex}_${naam}.xml`,
                    mediatype: 'application/xml',
                    schemaversie: BGProcesSimulator.STOP_Versie
                })
                break;

            case Instrument.SoortInstrument_GIO:
                registreerModule('GeoInformatieObjectVersie', Activiteit.ModuleToXml('GeoInformatieObjectVersie', {
                    _ns: Activiteit.STOP_Geo
                }, this.ExpressionIdentificatie()));
                modules.push({
                    localName: 'GeoInformatieObjectVersie',
                    namespace: Activiteit.STOP_Geo,
                    bestandsnaam: `${bestandenIndex}_GIO.xml`,
                    mediatype: 'application/gml+xml',
                    schemaversie: BGProcesSimulator.STOP_Versie
                })
                break;

            case Instrument.SoortInstrument_PDF:
                component.Component.heeftBestand = {
                    Bestand: {
                        bestandsnaam: `${bestandenIndex}_document.pdf`,
                        mediatype: 'application/pdf'
                    }
                }
                break;
        }

        this.#MaakAnnotatieModules(laatstUitgewisseldeVersie, false, (moduleNaam, stopXml, ns) => {
            modules.push({
                localName: moduleNaam,
                namespace: ns,
                bestandsnaam: `${bestandenIndex}_${moduleNaam}.xml`,
                mediatype: 'application/xml',
                schemaversie: ns === Activiteit.NonSTOP_Data ? 'x.y.z' : BGProcesSimulator.STOP_Versie
            })
            registreerModule(moduleNaam, stopXml);
        });
    }

    /**
     * Maak de "STOP" modules voor de annotaties die sinds de gespecificeerde versie zijn gewijzigd
     * @param {Instrumentversie} laatstUitgewisseldeVersie - Instrumentversie zoals die voor het laatst is uitgewisseld (vóór deze versie).
     * @param {boolean} alleenIndienGewijzigd - Geeft aan dat een module als wijziging wordt uitgewisseld in plaats van altijd als stand van zaken
     * @param {Instrumentversie~registreerAnnotatieModule} registreerModule - Methode die wordt aangeroepen voor elke module, met de naam, STOP xml en namespace van de module
     */
    #MaakAnnotatieModules(laatstUitgewisseldeVersie, alleenIndienGewijzigd, registreerModule) {
        if (!BGProcesSimulator.Opties.Annotaties && !BGProcesSimulator.Opties.NonStopAnnotaties) {
            return;
        }
        let expressionId = this.ExpressionIdentificatie();
        let gewijzigdTenOpzichteVan = laatstUitgewisseldeVersie?.ExpressionIdentificatie() ? ` (gewijzigd ten opzichte van de eerdere versie ${laatstUitgewisseldeVersie.ExpressionIdentificatie()})` : '';

        //#region STOP annotaties
        if (BGProcesSimulator.Opties.Annotaties) {
            let laatstUitgewisseld = laatstUitgewisseldeVersie ? Object.assign({}, laatstUitgewisseldeVersie.#stopAnnotaties) : {};
            for (let annotatie in this.#stopAnnotaties) {
                // Maak alleen een module als de aanwezige annotatie is gewijzigd
                if (!alleenIndienGewijzigd || !this.#stopAnnotaties[annotatie].IsGelijkAan(laatstUitgewisseld[annotatie])) {
                    // Geef de annotatie door
                    this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd: de STOP module ${annotatie} behorend bij versie ${expressionId}${gewijzigdTenOpzichteVan}`)
                    if (annotatie === Annotatie.SoortAnnotatie_Citeertitel) {
                        let moduleNaam = this.SoortInstrument() === Instrument.SoortInstrument_Regeling ? 'RegelingMetadata' : 'InformatieobjectMetadata';
                        registreerModule(moduleNaam, Activiteit.ModuleToXml(moduleNaam, {
                            _ns: Activiteit.STOP_Data,
                            Citeertitel: this.#stopAnnotaties[annotatie].Citeertitel()
                        }, expressionId),
                            Activiteit.STOP_Data);
                    }
                    else if (annotatie === Annotatie.SoortAnnotatie_Symbolisatie) {
                        registreerModule(annotatie, Activiteit.ModuleToXml('FeatureTypeStyle', {
                            _ns: Activiteit.STOP_SE
                        }, expressionId),
                            Activiteit.STOP_SE);
                    } else {
                        registreerModule(annotatie, Activiteit.ModuleToXml(annotatie, {
                            _ns: Activiteit.STOP_Data
                        }, expressionId),
                            Activiteit.STOP_Data);
                    }
                }
                delete laatstUitgewisseld[annotatie];
            }
            if (alleenIndienGewijzigd) {
                for (let annotatie in laatstUitgewisseld) {
                    // Deze annotatie is niet meer aanwezig
                    if (annotatie === Annotatie.SoortAnnotatie_Symbolisatie) {
                        registreerModule(annotatie, Activiteit.ModuleToXml('FeatureTypeStyle', {
                            _ns: Activiteit.STOP_SE,
                            Verwijder: true
                        }, expressionId),
                            Activiteit.STOP_SE);
                    } else {
                        registreerModule(annotatie, Activiteit.ModuleToXml(annotatie, {
                            _ns: Activiteit.STOP_Data,
                            Verwijder: true
                        }, expressionId),
                            Activiteit.STOP_Data);
                    }
                }
            }
        }
        //#endregion

        //#region Non-STOP annotaties
        if (BGProcesSimulator.Opties.NonStopAnnotaties) {
            let nonStopMutaties = [];

            let laatstUitgewisseld = laatstUitgewisseldeVersie ? Object.assign({}, laatstUitgewisseldeVersie.#nonStopAnnotaties) : {};
            for (let annotatie in this.#nonStopAnnotaties) {
                if (alleenIndienGewijzigd) {
                    if (!this.#nonStopAnnotaties[annotatie].IsGelijkAan(laatstUitgewisseld[annotatie])) {
                        nonStopMutaties.push({ Annotatie: { naam: annotatie, wijzigactie: 'nieuw' } });
                    }
                } else {
                    nonStopMutaties.push({ naam: annotatie });
                }
                delete laatstUitgewisseld[annotatie];
            }
            if (alleenIndienGewijzigd) {
                for (let annotatie in laatstUitgewisseld) {
                    nonStopMutaties.push({ Annotatie: { naam: annotatie, wijzigactie: 'verwijder' } });
                }
            }
            if (nonStopMutaties.length > 0) {
                this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd: de non-STOP annotaties bij de versie ${expressionId}${gewijzigdTenOpzichteVan}`)
                registreerModule('Non-STOP annotaties', Activiteit.ModuleToXml('NonSTOPAnnotaties', {
                    _ns: Activiteit.NonSTOP_Data,
                    mutaties: nonStopMutaties
                }, expressionId),
                    Activiteit.NonSTOP_Data);
            }
        }
        //#endregion
    }
    //#endregion
}

/**
 * Registratie van een uit te wisselen module
 * @callback registreerSTOPModule
 * @param {string} localName - Naam van de STOP module
 * @param {string} moduleXml - XML van de module
 */
/**
 * Registratie van een uit te wisselen module
 * @callback Instrumentversie~registreerAnnotatieModule
 * @param {string} localName - Naam van de STOP module
 * @param {string} moduleXml - XML van de module
 * @param {string} namespace - XML namespace van de module
 */
//#endregion

//#region Invoer van instrumentversie
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
     * @param {InstrumentversieSpecificatie[]} teOntvlechtenVersies - De wijzigingen die ontvlochten moeten worden met deze wijziging
     * @param {InstrumentversieSpecificatie[]} teVervlechtenVersies - De wijzigingen die vervlochten moeten worden met deze wijziging
     */
    constructor(momentopname, instrument, basisversie, teOntvlechtenVersies, teVervlechtenVersies) {
        super(momentopname.Specificatie(), instrument, undefined, momentopname);

        this.#actueleversie = new Instrumentversie(momentopname, instrument, basisversie?.Instrumentversie());
        if (basisversie && basisversie.Momentopname().Branch() === this.Momentopname().Branch() && !basisversie.Instrumentversie().LVBBUitgewisseld()) {
            this.#vervlochtenversies = Object.assign({}, basisversie.#vervlochtenversies);
            this.#ontvlochtenversies = Object.assign({}, basisversie.#ontvlochtenversies);
        }
        this.#BepaalSamenloop(teOntvlechtenVersies, teVervlechtenVersies);
        this.#actueleversie.PasSpecificatieToe(this.Specificatie());
    }

    destructor() {
        if (this.#actueleversie) {
            this.#actueleversie.destructor();
            this.#actueleversie = undefined;
        }
        super.destructor();
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Geeft de naam/code van het instrument waar dit een versie van is
     * @returns {string}
     */
    Instrument() {
        return this.Eigenschap();
    }

    /**
     * Geef de naam van het instrument zoals aan de eindgebruiker getoond wordt.
     * Dit is de citeertitel, tenzij die niet gezet is.
     * @returns {string}
     */
    InstrumentInteractienaam() {
        let versie = this.IsInvoer() ? this.#nieuweversie : this.#actueleversie;
        if (versie) {
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
     * @returns {Instrumentversie}
     */
    Instrumentversie() {
        return this.IsInvoer() ? this.#nieuweversie : this.#actueleversie;
    }
    /** @type {Instrumentversie} */
    #actueleversie;
    /** @type {Instrumentversie} */
    #nieuweversie;

    /**
     * Geeft aan dat de instrumentversie de oplossing is van samenloop bij vervlechting
     * of van het weghalen van wijzigingen bij ontvlechting.
     * @returns
     */
    IsOplossingSamenloop() {
        return this.#isOplossingSamenloop;
    }
    #isOplossingSamenloop = false;

    /**
     * Geeft de expliciet ontvlochten versies sinds de laatste uitwisseling met de LVBB
     * @returns {InstrumentversieSpecificatie[]}
     */
    OntvlochtenVersies() {
        return Object.values(this.#ontvlochtenversies);
    }
    /** @type {Object.<number,InstrumentversieSpecificatie>} */
    #ontvlochtenversies = {};

    /**
     * Geeft de expliciet vervlochten versies sinds de laatste uitwisseling met de LVBB
     * @returns {InstrumentversieSpecificatie[]}
     */
    VervlochtenVersies() {
        return Object.values(this.#vervlochtenversies);
    }
    /** @type {Object.<number,InstrumentversieSpecificatie>} */
    #vervlochtenversies = {};
    //#endregion

    //#region Statusoverzicht
    /**
      * Het overzicht van de instrumentversie als onderdeel van de momentopname in het projectoverzicht
     * @returns {string}
      */
    OverzichtHtml() {
        let html = '';
        let wijzigingHtml = '';
        let toonVersie = this.Instrumentversie();
        var laatstGewijzigd = this.Instrumentversie().MomentopnameLaatsteWijziging();
        if (laatstGewijzigd.Branch() === this.Momentopname().Branch()) {
            if (this.Instrumentversie().IsEerdereVersie()) {
                if (!this.Instrumentversie().IsOngewijzigdInBranch()) {
                    wijzigingHtml = `verwijzing naar andere versie ingesteld op ${laatstGewijzigd.Tijdstip().DatumTijdHtml()}`;
                }
                toonVersie = toonVersie.EerdereVersie();
            } else if (this.Instrumentversie().IsIngetrokken()) {
                html += `niet meer in gebruik sinds ${laatstGewijzigd.Tijdstip().DatumTijdHtml()}`;
            } else if (this.Instrumentversie().IsOngewijzigdInBranch()) {
                wijzigingHtml = `wijzigingen voor dit project teruggedraaid op ${laatstGewijzigd.Tijdstip().DatumTijdHtml()}`;
                toonVersie = toonVersie.BasisversieStartBranch();
            }
        }
        if (toonVersie?.HeeftJuridischeInhoud()) {
            html += `laatst gewijzigd op ${toonVersie.MomentopnameLaatsteWijziging().Tijdstip().DatumTijdHtml()}`;
            if (toonVersie.HeeftAnnotaties()) {
                html = `<table><tr><td colspan="2">${html}</td></tr>`;
                for (let isStop of [true, false]) {
                    for (let naam of toonVersie.AnnotatieNamen(isStop)) {
                        let annotatie = toonVersie.Annotatie(isStop, naam);
                        if (annotatie) {
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
        }
        if (wijzigingHtml) {
            html += `<br>(${wijzigingHtml})`;
        }
        return html;
    }
    //#endregion

    //#region Toepassen specificatie
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
            if (this.Instrumentversie().IsEerdereVersie()) {
                if (this.Momentopname().IsTegelijkBeheerdEnVolgend()) {
                    html += `Versie overgenomen van branch ${this.Momentopname().TegelijkBeheerd()[0].Code()}`;
                } else {
                    html += 'Verwijzing naar eerder gepubliceerde versie';
                }
            } else if (this.Instrumentversie().IsInitieleVersie()) {
                html += 'Initiële versie';
            } else {
                html += 'Gewijzigd in deze branch';
            }
            if (!this.Instrumentversie().MeenemenInConsolidatie()) {
                html += '; dit is niet de correcte versie om voor de consolidatie te gebruiken, die is onbekend';
            }
            html += ')';
            return html;
        }
    }
    //#endregion

    //#region Implementatie specificatie-element
    IsReadOnly() {
        return this.#actueleversie.IsBasisversie();
    }

    WeergaveInnerHtml() {
        return this.#InnerHtml(this.#actueleversie, false);
    }

    BeginInvoer() {
        this.#nieuweversie = new Instrumentversie(this.Momentopname(), this.Instrument(), this.#actueleversie.Basisversie(), this.#actueleversie);
    }

    InvoerInnerHtml() {
        return this.#InnerHtml(this.#nieuweversie, true);
    }

    /**
     * Maak de HTML voor een instrumentversie
     * @param {Instrumentversie} instrumentversie - Instrumentversie die weergegeven moet worden
     * @param {boolean} enabled - Geeft aan of de specificatie van de instrumentversie gewijzigd kan worden
     * @returns {string} HTML
     */
    #InnerHtml(instrumentversie, enabled) {
        let disabled = enabled ? '' : ' disabled';
        let html;
        let initieleVersie = instrumentversie.IsInitieleVersie();
        let branchHeeftEerdereWijziging = false;
        for (let versie = instrumentversie.Basisversie(); versie; versie = versie.Basisversie()) {
            if (versie.Branch() !== instrumentversie.Branch()) {
                break;
            }
            if (versie.UUID() != versie.Basisversie()?.UUID()) {
                branchHeeftEerdereWijziging = true;
                break;
            }
        }
        let teSelecterenVersies;
        if (instrumentversie.SoortInstrument() != Instrument.SoortInstrument_Regeling) {
            // Zoek eerst alle nieuwe instrumentversies die op dit moment bekend zijn
            Momentopname.VoorAlleMomentopnamen(this.Momentopname().Tijdstip(), undefined, (mo) => {
                let versie = mo.Instrumentversie(this.Instrument());
                if (versie && versie !== this && versie.Instrumentversie().IsNieuweVersie()) {
                    //Een andere instrumentversie dan deze die een nieuwe versie specificeert
                    if (instrumentversie.Basisversie()?.UUID() == versie.Instrumentversie().UUID()) {
                        // Naar een versie met dezelfde expression-ID als de ongewijzigde versie moet niet verwezen worden, dan moet van de wijziging afgezien worden.
                        return;
                    }
                    if (!teSelecterenVersies) {
                        teSelecterenVersies = {};
                    }
                    teSelecterenVersies[`Op ${versie.Momentopname().Tijdstip().DatumTijdHtml()} voor: ${versie.Momentopname().Branch().InteractieNaam()}`] = versie.Momentopname().Index();
                }
            });
        }
        if (!branchHeeftEerdereWijziging && initieleVersie && !teSelecterenVersies) {
            // Er is geen eerdere versie in een voorgaande momentopname
            html = `<input type="checkbox" id="${this.ElementId('N')}"${(instrumentversie.HeeftJuridischeInhoud() ? ' checked' : '')}${disabled}><label for="${this.ElementId('N')}">Nieuwe initiële versie</label>`
            if (instrumentversie.HeeftJuridischeInhoud()) {
                html += this.#AnnotatiesInnerHtml(instrumentversie, enabled);
            }
        } else {
            // Er is een eerdere versie, geef een keuze voor de status waarin een instrument zich bevindt.
            html = '<table>';
            let checked = 'B';
            if (instrumentversie.MomentopnameLaatsteWijziging() === this.Momentopname()) {
                if (instrumentversie.IsIngetrokken()) {
                    checked = 'D';
                } else if (branchHeeftEerdereWijziging && instrumentversie.IsOngewijzigdInBranch()) {
                    checked = 'T';
                }
                else if (instrumentversie.IsNieuweVersie()) {
                    checked = 'W';
                }
                else if (instrumentversie.IsEerdereVersie()) {
                    checked = 'V';
                }
            }
            if (this.IsOplossingSamenloop()) {
                html += '<tr><td class="verplicht">&#10045;</td><td>Een van de opties moet gekozen worden om de samenloop op te lossen</td></tr>';
            }
            if ((!this.IsOplossingSamenloop() || Instrument.SoortInstrument(this.Instrument()) != Instrument.SoortInstrument_Regeling) // Een informatieobject kan opnieuw verstgesteld worden; blijft ongewijzigd bij oplossen samenloop
                && (branchHeeftEerdereWijziging || !initieleVersie)) {
                html += `<tr><td><input type="radio" id="${this.ElementId('B')}" name="${this.ElementId('R')}"${(checked == 'B' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('B')}">Ongewijzigd laten</label></td></tr>`;
            }
            html += `<tr><td><input type="radio" id="${this.ElementId('W')}" name="${this.ElementId('R')}"${(checked == 'W' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('W')}">Nieuwe versie</label>${(checked == 'W' ? this.#AnnotatiesInnerHtml(instrumentversie, enabled) : '')}</td></tr>`;
            if (!initieleVersie) {
                html += `<tr><td><input type="radio" id="${this.ElementId('D')}" name="${this.ElementId('R')}"${(checked == 'D' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('D')}">Intrekken</label></td></tr>`;
            }
            if (branchHeeftEerdereWijziging) {
                html += `<tr><td><input type="radio" id="${this.ElementId('T')}" name="${this.ElementId('R')}"${(checked == 'T' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('T')}">${instrumentversie.IsInitieleVersie() ? 'Verwijderen' : 'Terug naar versie bij de start van het project'}</label></td></tr>`;
            }
            if (teSelecterenVersies) {
                html += `<tr><td><input type="radio" id="${this.ElementId('V')}" name="${this.ElementId('R')}"${(checked == 'V' ? ' checked' : '')}${disabled}></td><td><label for="${this.ElementId('V')}">Gelijk aan een eerder opgestelde versie:<label><br>`;
                html += `<select id="${this.ElementId('VL')}"${disabled}>`;
                for (let versie of Object.keys(teSelecterenVersies).sort()) {
                    html += `<option value="${teSelecterenVersies[versie]}"${(checked == 'V' && teSelecterenVersies[versie] === instrumentversie.UUID() ? ' selected' : '')}>${versie}</option>`;
                }
                html += '</select></td></tr>';
            }
            html += '</table>';
        }
        return html;
    }

    /**
     * Maak de HTML voor de weergave/invoer van de annotaties
     * @param {Instrumentversie} instrumentversie - Instrumentversie die weergegeven moet worden
     * @param {boolean} enabled - Geeft aan of de specificatie van de instrumentversie gewijzigd kan worden
     * @returns {string} HTML
     */
    #AnnotatiesInnerHtml(instrumentversie, enabled) {
        if (!BGProcesSimulator.Opties.Annotaties && !BGProcesSimulator.Opties.NonStopAnnotaties) {
            return '';
        }
        // Maak de invoer voor de annotaties
        let disabled = enabled ? '' : ' disabled';
        let html = '';
        let startHtml = '<div>Naast de juridische informatie ook een nieuwe versie van de annotatie(s):</div><table class="w100">';
        let idx = 0;
        let isStopBereik = [];
        if (BGProcesSimulator.Opties.Annotaties) {
            isStopBereik.push(true);
        }
        if (BGProcesSimulator.Opties.NonStopAnnotaties && Instrument.NonStopAnnotatiesVoorInstrument.includes(instrumentversie.SoortInstrument())) {
            isStopBereik.push(false);
        }

        let ongewijzigdeVersie = this.Momentopname().VoorgaandeMomentopname()?.Instrumentversie(this.Instrument())?.Instrumentversie();
        for (let isStop of isStopBereik) {
            // Zoek uit welke annotaties ingevoerd kunnen worden
            let namen = [...instrumentversie.AnnotatieNamen(isStop)];
            if (!isStop) {
                namen.push(Annotatie.VrijeNonStopAnnotatieNaam());
            }
            for (let naam of namen) {
                // Voeg de annotatie aan de tabel toe
                if (startHtml !== '') {
                    html += startHtml;
                    startHtml = '';
                }
                idx++;

                let versie = instrumentversie.Annotatie(isStop, naam);
                let ongewijzigd = ongewijzigdeVersie?.Annotatie(isStop, naam);
                let isNieuweVersie = false;
                if (versie) {
                    isNieuweVersie = !Annotatie.ZijnGelijk(versie, ongewijzigd);
                }
                if (isStop) {
                    if (naam === Annotatie.SoortAnnotatie_Citeertitel) {
                        // Citeertitel
                        html += `<tr>
                                    <td>${naam}</td>
                                    <td><input type="checkbox" id="${this.ElementId('AW' + idx)}" data-a="${naam}" data-s="1"${(isNieuweVersie ? ' checked' : '')}${disabled}> <label for="${this.ElementId('AW' + idx)}">Nieuwe versie<label></td>
                                </tr>
                                <tr><td class="ra">Citeertitel</td><td colspan="2"><input type="text" class="naam" id="${this.ElementId('CT')}" value="${(versie?.Citeertitel() ?? '')}"${disabled}></td></tr>`;
                    } else {
                        // Andere
                        html += `<tr>
                                    <td>${naam}</td>
                                    <td><input type="checkbox" id="${this.ElementId('AW' + idx)}" data-a="${naam}" data-s="1"${(isNieuweVersie ? ' checked' : '')}${disabled}> <label for="${this.ElementId('AW' + idx)}">Nieuwe versie<label></td></tr>`;
                    }
                }
                else {
                    if (!ongewijzigd && !versie) {
                        if (enabled) {
                            html += `<tr><td><input type="text" id="${this.ElementId('NNS' + idx)}" value="${naam}"${disabled}></td><td>${this.HtmlVoegToe("Voeg een nieuwe non-STOP annotatie toe", 'NS' + idx)}</td></tr>`;
                        }
                    } else {
                        html += `<tr>
                                    <td>${naam}</td>
                                    <td><input type="checkbox" id="${this.ElementId('AW' + idx)}" data-a="${naam}" data-s="0"${(isNieuweVersie ? ' checked' : '')}${disabled}> <label for="${this.ElementId('AW' + idx)}">Nieuwe versie<label></td>
                                    <td><input type="checkbox" id="${this.ElementId('AD' + idx)}" data-a="${naam}" data-s="0"${(versie ? '' : ' checked')}${disabled}> <label for="${this.ElementId('AD' + idx)}">Niet meer van toepassing<label></td>
                                 </tr>`;
                    }
                }
            }
        }
        if (startHtml === '') {
            html += '</table>';
        }
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
        if (!idSuffix) {
            return;
        }
        if (idSuffix.charAt(0) == 'A') {
            //#region Annotaties
            let naam = elt.dataset.a;
            let isStop = elt.dataset.s == '1';
            if (elt.checked) {
                if (idSuffix.charAt(1) == 'D') {
                    // Weghalen van annotatie
                    if (this.#nieuweversie.AnnotatieWeg(isStop, naam)) {
                        this.VervangInnerHtml();
                    }
                } else {
                    // Nieuwe annotatieversie
                    let annotatie;
                    if (isStop && naam === Annotatie.SoortAnnotatie_Citeertitel) {
                        annotatie = new Metadata(this.Element('CT').value, this.Momentopname());
                    } else {
                        annotatie = new Annotatie(naam, this.Momentopname());
                    }
                    if (this.#nieuweversie.AnnotatieWordt(isStop, annotatie)) {
                        this.VervangInnerHtml();
                    }
                }
            } else {
                // Toch geen eerste versie voor de annotatie
                if (this.#nieuweversie.AnnotatieUndo(isStop, naam)) {
                    this.VervangInnerHtml();
                }
            }
            //#endregion
        }
        else if (idSuffix.startsWith('NS')) {
            //#region Nieuwe non-STOP annotatie
            let naam = this.Element('N' + idSuffix).value.trim();
            if (naam) {
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
                    if (elt.checked) {
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
                    if (elt.checked) {
                        // Toch geen wijziging meer op deze branch
                        this.#nieuweversie.MaakOngewijzigdInBranch();
                        this.VervangInnerHtml();
                    }
                    break;
                case 'V':
                    if (elt.checked) {
                        // Verwijs naar een eerdere versie
                        this.#GebruikEerdereVersie(this.Element('VL'));
                        this.VervangInnerHtml();
                    }
                    break;
            }
            //#endregion
        }
    }

    ValideerInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            if (this.IsOplossingSamenloop() && this.#nieuweversie.MomentopnameLaatsteWijziging() !== this.Momentopname()
                && this.Instrumentversie().SoortInstrument() === Instrument.SoortInstrument_Regeling) {
                return true;
            }
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            this.SpecificatieWordt(this.#nieuweversie.MaakSpecificatie());
            this.#actueleversie = this.#nieuweversie;
        }
    }
    //#endregion

    //#region Samenloop bepalen
    /**
      * Bepaal de samenloop die ontstaat door de vervlechten/ontvlechting. Deze simulator doet dat door het STOP versiebeheer
      * ook toe te passen voor het BG-interne versiebeheer. Dat is geen vereiste; BG-software kan dat anders implementeren.
      * De BG-software kent ook de inhoud van de instrumentversies en kan desgewenst samenloop bijvoorbeeld op artikelniveau bepalen. 
      * @param {InstrumentversieSpecificatie[]} teOntvlechtenVersies - De wijzigingen die ontvlochten moeten worden met deze wijziging
      * @param {InstrumentversieSpecificatie[]} teVervlechtenVersies - De wijzigingen die vervlochten moeten worden met deze wijziging
      */
    #BepaalSamenloop(teOntvlechtenVersies, teVervlechtenVersies) {
        let meldBijwerkenVersie = false;
        let meldAlVervlochten = false;
        for (let teVervlechten of (teVervlechtenVersies ?? [])) {
            // Als de actuele versie een latere versie is van de te vervlechten versie, dan hoeft er niet vervlochten te worden
            if (this.#HeeftBijdrageIsVervlochten(this, teVervlechten.Momentopname())) {
                meldAlVervlochten = true;
                continue;
            }
            this.#vervlochtenversies[teVervlechten.Momentopname().Branch().Index()] = teVervlechten;

            // Als de te vervlechten versie en de actuele versie identiek zijn, dan hoeft de actuele versie niet aangepast te worden,
            // ook al zijn er verschillende dingen gebeurt op de twee routes (via branch en via vervlechting)
            if (this.Instrumentversie().HeeftDezelfdeInhoud(teVervlechten.Instrumentversie())) {
                meldAlVervlochten = true;
                continue;
            }

            // Als de actuele versie een eerdere versie is van de te vervlechten versie, dan moet de actuele versie bijgewerkt worden
            let werkActueleVersieBij = false;
            for (let gewijzigdIn = teVervlechten.Instrumentversie().MomentopnameLaatsteWijziging(); gewijzigdIn; gewijzigdIn = gewijzigdIn.Instrumentversie(this.Instrument()).Instrumentversie().Basisversie()?.MomentopnameLaatsteWijziging()) {
                if (gewijzigdIn === this.#actueleversie.MomentopnameLaatsteWijziging()) {
                    werkActueleVersieBij = true;
                    break;
                }
            }
            if (werkActueleVersieBij) {
                this.#actueleversie = new Instrumentversie(this.Momentopname(), this.Instrument(), teVervlechten.Instrumentversie());
                meldBijwerkenVersie = true;
                continue;
            }

            // Merge conflict!
            this.#isOplossingSamenloop = true;
        }
        let meldAlOntvlochten = (teOntvlechtenVersies?.length ?? 0) > 0;

        for (let teOntvlechten of (teOntvlechtenVersies ?? [])) {
            // Er is geen noodzaak tot ontvlechting als dit instrument geen bijdrage (meer) heeft van de te ontvlechten branch
            if (this.#HeeftBijdrageIsOntvlochten(this, teOntvlechten.Momentopname().Branch())[0]) {
                meldAlOntvlochten = false;
                this.#ontvlochtenversies[teOntvlechten.Momentopname().Branch().Index()] = teOntvlechten;

                // Actie vereist
                this.#isOplossingSamenloop = true;
            }
        }

        if (this.IsOplossingSamenloop()) {
            this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Procesbegeleiding, `Voor instrument ${this.Instrument()} kan de vervlechting/ontvlechting niet geautomatiseerd uitgevoerd worden; de software vraagt de eindgebruiker de samenloop op te lossen.`);
        } else if (meldBijwerkenVersie || meldAlVervlochten || meldAlOntvlochten) {
            let melding = `Voor instrument ${this.Instrument()} `
            if (meldBijwerkenVersie) {
                melding += 'kan de vervlechting geautomatiseerd uitgevoerd worden door de versie in de branch bij te werken';
                if (meldAlOntvlochten) {
                    melding += `; deze versie bevat geen wijzigingen van de te ontvlechten branch${teOntvlechtenVersies.length > 1 ? 'es' : ''}`;
                }
            } else if (meldAlVervlochten) {
                melding += `is geen actie nodig; de versie in de branch is gelijk of actueler dan de te vervlechten versie${teVervlechtenVersies.length > 1 ? 's' : ''}`;
                if (meldAlOntvlochten) {
                    melding += ` en deze versie bevat geen wijzigingen van de te ontvlechten branch${teOntvlechtenVersies.length > 1 ? 'es' : ''}`;
                }
            }
            else if (meldAlOntvlochten) {
                melding += `is geen actie nodig; deze versie bevat geen wijzigingen van de te ontvlechten branch${teOntvlechtenVersies.length > 1 ? 'es' : ''}`;
            }
            melding += '.';
            this.Momentopname().Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Procesbegeleiding, melding);
        }
    }

    /**
     * Geeft aan of de te onderzoeken versie een bijdrage heeft van de te vervlechten branch
     * @param {InstrumentversieSpecificatie} teOnderzoekenVersie
     * @param {Momentopname} teVervlechtenMomentopname
     * @returns {boolean} - Geeft aan of er een bijdrage is
     */
    #HeeftBijdrageIsVervlochten(teOnderzoekenVersie, teVervlechtenMomentopname) {
        // Loop de basisversies af van de instrumentversie
        for (let gewijzigdeVersie = teOnderzoekenVersie; gewijzigdeVersie; gewijzigdeVersie = gewijzigdeVersie.Instrumentversie().Basisversie()?.Momentopname().Instrumentversie(this.Instrument())) {
            if (gewijzigdeVersie.Momentopname().Branch() === teVervlechtenMomentopname.Branch()) {
                // De eerste bijdrage van de te vervlechten branch. Er is sprake van vervlechting 
                // als de bijdrage gelijk of recenter is dan de te vervlechten momentopname.
                return gewijzigdeVersie.Momentopname().Tijdstip().Vergelijk(teVervlechtenMomentopname.Tijdstip()) >= 0;
            }
            for (let versie of gewijzigdeVersie.VervlochtenVersies()) {
                if (this.#HeeftBijdrageIsVervlochten(versie, teVervlechtenMomentopname)) {
                    // Een van de vervlochten versies heeft de te vervlechten momentopname als bijdrage
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Geeft aan of de te onderzoeken versie een bijdrage heeft van de te ontvlechten branch
     * @param {InstrumentversieSpecificatie} teOnderzoekenVersie
     * @param {Branch} teOntvlechtenBranch
     * @returns {boolean[]} - Eerste geeft aan of er een bijdrage is, tweede of de branch ontvlochten is
     */
    #HeeftBijdrageIsOntvlochten(teOnderzoekenVersie, teOntvlechtenBranch) {
        // Loop de basisversies af van de instrumentversie
        for (let gewijzigdeVersie = teOnderzoekenVersie; gewijzigdeVersie; gewijzigdeVersie = gewijzigdeVersie.Instrumentversie().Basisversie()?.Momentopname().Instrumentversie(this.Instrument())) {
            if (gewijzigdeVersie.#ontvlochtenversies.map(v => v.Momentopname().Branch()).includes(teOntvlechtenBranch)) {
                // Eerdere versie is al het resultaat van een ontvlechting, en als we hier komen zijn er geen andere bijdragen van de te ontvlechten branch gedetecteerd
                return [false, true];
            }
            if (gewijzigdeVersie.Momentopname().Branch() === teOntvlechtenBranch) {
                // Momentopname van de te ontvlechten branch draagt bij aan deze versie
                return [true, false];
            }
            let enigeBijdrage = false;
            let enigeOntvlechting = false;
            for (let vervlochten of gewijzigdeVersie.VervlochtenVersies()) {
                let [bijdrage, ontvlochten] = this.#HeeftBijdrageIsOntvlochten(vervlochten, teOntvlechtenBranch);
                enigeBijdrage ||= bijdrage;
                enigeOntvlechting ||= ontvlochten;
            }
            if (enigeOntvlechting) {
                // Aanname: bij het vervlechten is het weghalen van de bijdrage van de te ontvlechten branch meegenomen,
                // waardoor de versie van deze momentopnamen de wijzigingen niet meer heeft
                return [false, true];
            }
            if (enigeBijdrage) {
                return [true, false];
            }
        }
        return [false, false];
    }
    //#endregion

    //#region Interne functionaliteit
    /**
     * Zoek naar een instrumentversie op basis van het UUID
     * @param {HTMLSelectElement} elt - Selectielijst
     */
    #GebruikEerdereVersie(elt) {
        if (elt.selectedIndex >= 0) {
            let moIndex = parseInt(elt.value);
            Momentopname.VoorAlleMomentopnamen(this.Momentopname().Tijdstip(), undefined, (mo) => {
                if (mo.Index() === moIndex) {
                    this.#nieuweversie.GebruikEerdereVersie(mo.Instrumentversie(this.Instrument()).Instrumentversie());
                    return true;
                }
            });
            // Als de versie niet gevonden is bestaat die misschien niet meer - maak de lijst opnieuw
            this.VervangInnerHtml();
        }
    }
    //#endregion
}
//#endregion

//#region TijdstempelsSpecificatie
/*------------------------------------------------------------------------------
*
* TijdstempelsSpecificatie is een specificatie-subelement die de invoer van
* de tijdstempels voor een momentopname kan vastleggen.
* 
*----------------------------------------------------------------------------*/
class TijdstempelsSpecificatie extends SpecificatieElement {
    //#region Initialisatie
    /**
     * Maak het specificatie-element aan
     * @param {Momentopname} momentopname - Momentopname waar de tijdstempels bij horen
     * @param {bool} tijdstempelsToegestaan - Geeft aan of tijdstippen ingevoerd mogen worden
     * @param {bool} tijdstempelsVerplicht - Geeft aan of tenminste de JuridischWerkendVanaf ingevuld moet worden
     */
    constructor(momentopname, tijdstempelsToegestaan, tijdstempelsVerplicht) {
        // Bepaal de effectieve tijdstempels
        if (!tijdstempelsToegestaan) {
            if (momentopname.Specificatie().JuridischWerkendVanaf !== undefined || momentopname.Specificatie().GeldigVanaf !== undefined) {
                momentopname.Activiteit().SpecificatieMelding(`Specificatie van tijdstempels is niet toegestaan - de tijdstempels worden genegeerd.')).`);
                delete momentopname.Specificatie().JuridischWerkendVanaf;
                delete momentopname.Specificatie().GeldigVanaf;
            }
        }
        let voorgaandeSpecificatie = momentopname.VoorgaandeMomentopname()?.Branch() === momentopname.Branch() ? momentopname.VoorgaandeMomentopname() : undefined;
        let juridischWerkendVanaf = momentopname.Specificatie().JuridischWerkendVanaf ?? voorgaandeSpecificatie?.JuridischWerkendVanaf()?.Specificatie();
        let geldigVanaf = momentopname.Specificatie().GeldigVanaf ?? voorgaandeSpecificatie?.GeldigVanaf()?.Specificatie();
        if (juridischWerkendVanaf !== undefined && geldigVanaf !== undefined && juridischWerkendVanaf === geldigVanaf) {
            geldigVanaf = undefined;
        }

        // Maak dit object aan
        super(undefined, undefined, { JuridischWerkendVanaf: juridischWerkendVanaf, GeldigVanaf: geldigVanaf }, momentopname);
        this.#tijdstempelsToegestaan = tijdstempelsToegestaan;
        this.#tijdstempelsVerplicht = tijdstempelsVerplicht;
        this.#InterpreteerSpecificatie();
    }

    #InterpreteerSpecificatie() {
        // Maak weergave-elementen voor de tijdstempels
        this.#juridischWerkendVanaf?.destructor();
        this.#geldigVanaf?.destructor();
        this.#juridischWerkendVanaf = new Tijdstip(this, this.Specificatie(), 'JuridischWerkendVanaf', false, this.Momentopname().Tijdstip(), this.IsReadOnly());
        if (this.Specificatie().GeldigVanaf && this.Specificatie().GeldigVanaf != this.Specificatie().JuridischWerkendVanaf) {
            this.#geldigVanaf = new Tijdstip(this, this.Specificatie(), 'GeldigVanaf', false, this.Momentopname().Tijdstip(), this.IsReadOnly());
        } else {
            this.#geldigVanaf = undefined;
        }
    }
    //#endregion Initialisatie

    //#region Eigenschappen
    /**
     * Geeft de momentopname waar de specificatie bijhoort
     * @returns {Momentopname}
     */
    Momentopname() {
        return this.SuperInvoer();
    }

    /**
     * Geef de datum van inwerkingtreding, indien bekend
     * @returns {Tijdstip}
     */
    JuridischWerkendVanaf() {
        return this.#juridischWerkendVanaf;
    }
    /** @type {Tijdstip} */
    #juridischWerkendVanaf;

    /**
     * Geef de datum van start geldigheid, indien bekend en indien afwijkend van JuridischWerkendVanaf
     * @returns {Tijdstip}
     */
    GeldigVanaf() {
        return this.#geldigVanaf;
    }
    /** @type {Tijdstip} */
    #geldigVanaf;

    /**
     * Geeft aan of de tijdstempels gewijzigd zijn in deze momentopname
     * @returns {boolean}
     */
    HeeftGewijzigdeTijdstempels() {
        if (!this.#tijdstempelsToegestaan) {
            return false;
        }
        let voorgaande = this.Momentopname().VoorgaandeMomentopname();
        if (voorgaande?.Branch() === this.Momentopname().Branch()) {
            if (!this.JuridischWerkendVanaf().IsGelijk(voorgaande.JuridischWerkendVanaf())) {
                return true;
            }
            if (this.GeldigVanaf()?.HeeftWaarde()) {
                return !this.GeldigVanaf().IsGelijk(voorgaande.GeldigVanaf());
            } else {
                return voorgaande.GeldigVanaf()?.HeeftWaarde();
            }
        } else {
            return this.JuridischWerkendVanaf().HeeftWaarde();
        }
    }
    //#endregion

    //#region Implementatie specificatie-element
    IsReadOnly() {
        return !this.#tijdstempelsToegestaan;
    }
    /** @type {boolean} */
    #tijdstempelsToegestaan;
    /** @type {boolean} */
    #tijdstempelsVerplicht;

    ContainerElement() {
        return 'table';
    }

    WeergaveInnerHtml() {
        return `<tr><td>${this.#tijdstempelsVerplicht ? '' : `<input type="checkbox"${this.#juridischWerkendVanaf.HeeftWaarde() ? ' checked' : ''} disabled> `} In werking vanaf</td><td>${this.#juridischWerkendVanaf.HeeftWaarde() ? this.#juridischWerkendVanaf.DatumTijdHtml() : '-'}</td></tr>
                <tr><td><input type="checkbox"${this.#geldigVanaf ? ' checked' : ''} disabled> Terugwerkend tot</td><td>${this.#geldigVanaf?.DatumTijdHtml() ?? '-'}</td></tr>`;
    }

    BeginInvoer() {
        if (this.#nieuweJwv) {
            this.#nieuweJwv.destructor();
            this.#nieuweGv?.destructor();
            this.#nieuweGv = undefined;
        }
        this.#nieuweJwv = new Tijdstip(this, { Datum: this.#juridischWerkendVanaf.Specificatie() }, 'Datum', false, this.Momentopname().Tijdstip());
        if (this.#geldigVanaf?.Specificatie()) {
            this.#nieuweGv = new Tijdstip(this, { Datum: this.#geldigVanaf.Specificatie() }, 'Datum', false);
        }
    }
    /** @type {Tijdstip} */
    #nieuweJwv;
    /** @type {Tijdstip} */
    #nieuweGv;

    InvoerInnerHtml() {
        return `<tr><td>${this.#tijdstempelsVerplicht ? '' : `<label for="${this.ElementId('JWV')}"><input type="checkbox" id="${this.ElementId('JWV')}"${this.#nieuweJwv?.HeeftWaarde() ? ' checked' : ''}>`}
                        In werking vanaf</label></td><td>${this.#nieuweJwv?.Html() ?? '-'}</td></tr>
                <tr><td><label for="${this.ElementId('GV')}"><input type="checkbox" id="${this.ElementId('GV')}"${this.#nieuweGv ? ' checked' : ''}${this.#nieuweJwv?.HeeftWaarde() ? '' : ' disabled'}>
                        Terugwerkend tot</label></td> <td>${this.#nieuweGv?.Html() ?? '-'}</td></tr>`
    }

    OnInvoerClick(elt, idSuffix) {
        switch (idSuffix) {
            case 'JWV':
                if (elt.checked) {
                    if (!this.#nieuweJwv) {
                        this.#nieuweJwv = new Tijdstip(this, { Datum: this.#juridischWerkendVanaf.Specificatie() }, 'Datum', false, this.Momentopname().Tijdstip());
                        this.VervangInnerHtml();
                    }
                } else {
                    if (this.#nieuweJwv) {
                        this.#nieuweJwv.destructor();
                        this.#nieuweJwv = undefined;
                        if (this.#nieuweGv) {
                            this.#nieuweGv?.destructor();
                            this.#nieuweGv = undefined;
                        }
                        this.VervangInnerHtml();
                    }
                }
                break;

            case 'GV':
                if (elt.checked) {
                    if (!this.#nieuweGv) {
                        this.#nieuweGv = new Tijdstip(this, { Datum: this.#nieuweJwv.Specificatie() }, 'Datum', false);
                        this.VervangInnerHtml();
                    }
                } else {
                    if (this.#nieuweGv) {
                        this.#nieuweGv?.destructor();
                        this.#nieuweGv = undefined;
                        this.VervangInnerHtml();
                    }
                }
                break;
        }
    }
    TijdstipGewijzigd(tijdstip) {
        if (tijdstip === this.#nieuweJwv) {
            if (!this.#nieuweJwv?.HeeftWaarde()) {
                this.#nieuweGv?.destructor();
                this.#nieuweGv = undefined;
            }
            this.VervangInnerHtml();
        } else if (tijdstip === this.#nieuweGv) {
            if (this.#nieuweGv.HeeftWaarde() && this.#nieuweGv.Vergelijk(this.#nieuweJwv) > 0) {
                this.#nieuweGv?.destructor();
                this.#nieuweGv = new Tijdstip(this, { Datum: this.#nieuweJwv.Specificatie() }, 'Datum', false);
                this.VervangInnerHtml();
            }
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            // OK
            let geldigVanaf = this.#nieuweGv && !this.#nieuweGv.IsGelijk(this.#nieuweJwv) ? this.#nieuweGv.Specificatie() : undefined;
            let juridischWerkendVanaf = this.#nieuweJwv?.Specificatie();

            let voorgaandeSpecificatie = this.Momentopname().VoorgaandeMomentopname()?.Branch() === this.Momentopname().Branch() ? this.Momentopname().VoorgaandeMomentopname() : undefined;
            let isGewijzigd = juridischWerkendVanaf !== voorgaandeSpecificatie?.JuridischWerkendVanaf()?.Specificatie();
            if (!isGewijzigd && geldigVanaf) {
                isGewijzigd = geldigVanaf !== voorgaandeSpecificatie?.GeldigVanaf()?.Specificatie();
            }
            if (isGewijzigd) {
                this.Momentopname().Specificatie().JuridischWerkendVanaf = juridischWerkendVanaf;
                this.Momentopname().Specificatie().GeldigVanaf = geldigVanaf;
                this.Specificatie().JuridischWerkendVanaf = juridischWerkendVanaf;
                this.Specificatie().GeldigVanaf = geldigVanaf;
                this.#InterpreteerSpecificatie();
            }
        }
    }
    //#endregion
}
//#endregion

//#region Momentopname
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
     * @param {bool} tijdstempelsVerplicht - Geeft aan of tenminste de JuridischWerkendVanaf ingevuld moet worden
     * @param {bool/int/Momentopname} werkUitgangssituatieBij - Geeft aan of de uitgangssituatie bijgewerkt moet worden, voor Branch.Soort_GeldendeRegelgeving
     *                                             evt voor welk tijdstip de geconsolideerde regelgeving gebruikt moet worden en voor anderen
     *                                             evt de Momentopname die als uitgangspunt genomen moet worden
     * @param {Momentopname[]} ontvlochtenversies - De wijzigingen die ontvlochten moeten worden met deze wijziging
     * @param {Momentopname[]} vervlochtenversies - De wijzigingen die vervlochten moeten worden met deze wijziging
     */
    constructor(superInvoer, eigenaarObject, branch, tijdstempelsToegestaan, tijdstempelsVerplicht, werkUitgangssituatieBij = false, ontvlochtenversies, vervlochtenversies) {
        super(eigenaarObject, branch.Code(), undefined, superInvoer, {});
        this.#branch = branch;
        this.#ontvlochtenMet = ontvlochtenversies ? [...ontvlochtenversies] : [];
        this.#vervlochtenMet = vervlochtenversies ? [...vervlochtenversies] : [];

        // Zoek de voorgaande momentopname waar deze momentopname op doorgaat
        let voorgaandeMomentopnameDezeBranch;
        if (!(this instanceof Uitgangssituatie)) {
            Momentopname.VoorAlleMomentopnamen(this.Tijdstip(), this.Branch(), (mo) => {
                if (mo != this) {
                    voorgaandeMomentopnameDezeBranch = mo;
                }
            });
        }

        if (voorgaandeMomentopnameDezeBranch) {
            // Neem informatie van voorgaande momentopname over
            this.#tegelijkBeheerd = voorgaandeMomentopnameDezeBranch.#tegelijkBeheerd;
            this.#doorAdviesbureau = voorgaandeMomentopnameDezeBranch.#doorAdviesbureau;

            if (voorgaandeMomentopnameDezeBranch.#isOnderdeelVanPublicatie) {
                // De vorige momentopname is nu de uitgangssituatie
                this.#juridischeUitgangssituatie = voorgaandeMomentopnameDezeBranch;
            } else {
                // Neem uitgangssituatie over
                this.#juridischeUitgangssituatie = voorgaandeMomentopnameDezeBranch.#juridischeUitgangssituatie;
            }
            this.#isVastgesteld = voorgaandeMomentopnameDezeBranch.#isOnderdeelVanPublicatie || voorgaandeMomentopnameDezeBranch.#isVastgesteld;
        }

        let voorgaandeMomentopname = voorgaandeMomentopnameDezeBranch;
        /** @type {Momentopname} */
        let uitgangssituatie;
        if (werkUitgangssituatieBij !== false || !voorgaandeMomentopnameDezeBranch) {
            // Zoek de laatste momentopname op van de uitgangssituatie waar de branch van uitgaat.
            if (this.Branch().Soort() === Branch.Soort_GeldendeRegelgeving) {
                if (!(this instanceof Uitgangssituatie)) {
                    // De uitgangssituatie (en tevens basisversie) is de geldende regelgeving.
                    let consolidatie = this.Activiteit().VoorgaandeConsolidatiestatus();
                    if (!consolidatie || consolidatie.Bepaald().length === 0) {
                        this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Er is nog geen geldende regelgeving bekend; deze branch leidt tot nieuwe regelingen.`);
                    } else {
                        let tijdstip = typeof werkUitgangssituatieBij === "number" ? Tijdstip.Maak(werkUitgangssituatieBij, true) : this.Branch().IWTDatum().HeeftWaarde() ? this.Branch().IWTDatum() : this.Tijdstip();
                        this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De uitgangssituatie van de regelgeving van deze branch wordt bijgewerkt naar de regelgeving die geldig is op ${tijdstip.DatumTijdHtml()}`);
                        let status = consolidatie.NuGeldend(tijdstip);
                        for (let iwtMomentopname of status.IWTMoment().Inwerkingtredingbranchcodes().map(bc => status.IWTMoment().LaatsteBijdrage(bc))) {
                            if (!uitgangssituatie) {
                                uitgangssituatie = iwtMomentopname;
                                if (!status.IsVoltooid()) {
                                    this.Activiteit().SpecificatieMelding(`Consolidatie van nu geldende regelgeving is incompleet; scenario gebruikt de regelgeving van de branch ${uitgangssituatie.Branch().Code()} per ${uitgangssituatie.Tijdstip().DatumTijdHtml()}.`);
                                }
                            }
                            iwtMomentopname.#gebruiktAlsConsolidatieDoor.push(this);
                        }
                    }
                }
            } else {
                // De uitgangssituatie is de laatste momentopname van de branch waar deze branch op volgt
                uitgangssituatie = werkUitgangssituatieBij instanceof Momentopname ? werkUitgangssituatieBij : this.Branch().VolgtOpBranch().LaatsteMomentopname(this.Tijdstip());
                this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De uitgangssituatie van de regelgeving van deze branch wordt bijgewerkt naar de regelgeving van de branch ${uitgangssituatie.Branch().Code()} per ${uitgangssituatie.Tijdstip().DatumTijdHtml()}.`);
                if (this.Branch().Soort() === Branch.Soort_OplossingSamenloop || this.Branch().Soort() === Branch.Soort_Consolidatie) {
                    // De andere branches werken als een vervlechting
                    for (let andereBranch of this.Branch().TreedtConditioneelInWerkingMet()) {
                        if (andereBranch != this.Branch().VolgtOpBranch()) {
                            let andereMO = andereBranch.LaatsteMomentopname(this.Tijdstip());
                            this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Tevens worden de wijzigingen van de regelgeving van de branch ${andereMO.Branch().Code()} (waarmee de samenloop opgelost moet worden) per ${andereMO.Tijdstip().DatumTijdHtml()} in deze momentopname vervlochten.`);
                            let huidigeMo = this.#vervlochtenMet.filter(mo => mo.Branch() === andereBranch);
                            if (!huidigeMo) {
                                this.#vervlochtenMet.push(andereMO);
                            }
                        }
                    }
                }
            }
            if (uitgangssituatie) {

                if (!voorgaandeMomentopnameDezeBranch) {
                    // Dit is de eerste momentopname van de branch, de voorgaande is tevens de juridische uitgangssituatie
                    this.#juridischeUitgangssituatie = voorgaandeMomentopname = uitgangssituatie;
                    // Vervlechting is niet nodig
                    let huidigeMo = this.#vervlochtenMet.filter(mo => mo.Branch() === uitgangssituatie.Branch());
                    if (huidigeMo?.length) {
                        this.#vervlochtenMet.splice(this.#vervlochtenMet.indexOf(huidigeMo[0]), 1);
                    }
                } else {
                    // Na vaststelling is de uitgangssituatie altijd de voorgaande publicatie op dezelfde branch
                    if (!this.#isVastgesteld) {
                        // Nog niet vastgesteld, dus de uitgangssituatie wijzigt.
                        this.#juridischeUitgangssituatie = uitgangssituatie
                    }
                    // Dit werkt hetzelfde als een vervlechting in versiebeheer
                    let huidigeMo = this.#vervlochtenMet.filter(mo => mo.Branch() === uitgangssituatie.Branch());
                    if (!huidigeMo?.length) {
                        this.#vervlochtenMet.push(uitgangssituatie);
                    }
                }
            }
        }

        // Bepaal de collectieve bijdragen van alle branches tbv consolidatie
        this.#voorgaandeMomentopname = voorgaandeMomentopname;
        this.#BepaalBijdragen();

        // Zoek uit welke instrumenten aanwezig zijn in deze momentopname
        if (voorgaandeMomentopname) {
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
                if (Instrument.SoortInstrument(instr)) {
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
            this.#actueleInstrumenten[instr] = new InstrumentversieSpecificatie(this, instr, (this.#voorgaandeMomentopname ? this.#voorgaandeMomentopname.#actueleInstrumenten[instr] : undefined), ontvl, vervl);
        }

        // Maak specificatie-elementen voor de tijdstempels
        if (this.Branch().Soort() !== Branch.Soort_OplossingSamenloop) {
            this.#tijdstempels = new TijdstempelsSpecificatie(this, tijdstempelsToegestaan, tijdstempelsVerplicht);
        }
    }

    destructor() {
        if (this.#juridischeUitgangssituatie) {
            this.#juridischeUitgangssituatie = undefined;
            Momentopname.VoorAlleMomentopnamen(undefined, undefined, (mo) => {
                let idx = mo.#gebruiktAlsConsolidatieDoor.indexOf(this);
                if (idx >= 0) {
                    mo.#gebruiktAlsConsolidatieDoor.splice(idx, 1);
                }
            });
        }
        super.destructor();
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
        if (!branch && BGProcesSimulator.This().Uitgangssituatie()) {
            if (tijdstip === undefined || 0 <= tijdstip.Specificatie()) {
                if (todo(BGProcesSimulator.This().Uitgangssituatie())) {
                    return true;
                }
            }
        }
        for (let activiteit of Activiteit.Activiteiten(tijdstip)) {
            for (let momentopname of activiteit.Momentopnamen()) {
                if (!branch || momentopname.Branch() == branch) {
                    if (todo(momentopname)) {
                        return true;
                    }
                }
            }
        };
    }

    /**
     * Geeft de branch waar deze instrumentversie deel van uitmaakt
     * @returns {Branch}
     */
    Branch() {
        return this.#branch;
    }
    /** @type {Branch} */
    #branch;

    /**
     * Geeft het tijdstip van de activiteit waarvoor de momentopname gespecificeerd wordt
     * @returns {Tijdstip}
     */
    Tijdstip() {
        return this.SuperInvoer().Tijdstip();
    }

    /**
     * Geeft de activiteit waarvoor de momentopname gespecificeerd wordt
     * @returns {Activiteit}
     */
    Activiteit() {
        return this.SuperInvoer();
    }

    /**
     * Geeft aan dat de momentopname door een adviesbureau is aangemaakt
     * @returns {boolean}
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
     * @returns {Momentopname}
     */
    JuridischeUitgangssituatie() {
        return this.#juridischeUitgangssituatie;
    }
    /** @type {Momentopname} */
    #juridischeUitgangssituatie;

    /**
     * Geeft aan of de regelgeving van de branch is gewijzigd ten opzichte van de
     * JuridischeUitgangssituatie. In deze applicatie alleen nodig voor weergave.
     * @returns {boolean}
     */
    IsInhoudGewijzigd() {
        for (let versie of this.Instrumentversies().map(x => x.Instrumentversie())) {
            if (!versie.IsOngewijzigdInBranch() && !versie.HeeftDezelfdeInhoud(this.#juridischeUitgangssituatie?.Instrumentversie(versie.Instrument())?.Instrumentversie())) {
                return true;
            }
        }
        return false;
    }

    /**
     * Geeft aan of de inwerkingtreding is gewijzigd ten opzichte van de laatste
     * publicatie van een vaststellingsbesluit of wijziging daarvan.
     * @returns {boolean}
     */
    IsInwerkingtredingGewijzigd() {
        if (this.Branch().Soort() === Branch.Soort_OplossingSamenloop) {
            // De trigger voor wijzigen van IWT komt altijd elders vandaan
            return false;
        } else if (!this.IsVaststellingsbesluitGepubliceerd() || this.IsOnderdeelVanPublicatieVastgesteldeInhoud()) {
            // Nog geen vaststellingsbesluit gepubliceerd (of deze momentopname beschrijft de publicatie)
            return this.JuridischWerkendVanaf().HeeftWaarde();
        } else {
            // De JuridischeUitgangssituatie wijst naar de voorgaande publicatie/revisie
            return this.JuridischeUitgangssituatie().JuridischWerkendVanaf().Specificatie() !== this.JuridischWerkendVanaf().Specificatie();
        }
    }

    /**
     * Geeft aan of deze momentopname onderdeel is van een besluit, rectificatie of
     * mededeling die (eerder) vastgestelde inhoud betreft (dus geen ontwerp).
     * Als dat zo is, dan is deze momentopname de JuridischeUitgangssituatie van 
     * de volgende momentopname.
     * @returns {boolean}
     */
    IsOnderdeelVanPublicatieVastgesteldeInhoud() {
        return this.#isOnderdeelVanPublicatie;
    }
    IsOnderdeelVanPublicatieVastgesteldeInhoudWordt() {
        if (this.TegelijkBeheerd()) {
            for (let branch of this.TegelijkBeheerd()) {
                this.#bijdragen[branch.Code()].#isOnderdeelVanPublicatie = true;
            }
        } else {
            this.#isOnderdeelVanPublicatie = true;
        }
    }
    #isOnderdeelVanPublicatie = false;

    /**
     * Geeft aan of het vaststellingsbesluit is gepubliceerd. Alleen nodig voor de 
     * weergave in deze applicatie (want dan zijn rectificaties mogelijk)
     * @returns {boolean}
     */
    IsVaststellingsbesluitGepubliceerd() {
        return this.#isVastgesteld;
    }
    #isVastgesteld = false;

    /**
     * Geeft de versies van de instrumenten (als InstrumentversieSpecificatie) op deze branch in deze momentopname
     * @param {boolean} sorteer - Geeft aan dat de instrumenten gesorteerd moeten worden
     * @returns {InstrumentversieSpecificatie[]}
     */
    Instrumentversies(sorteer = false) {
        let versies = Object.values(this.IsInvoer() ? this.#nieuweInstrumenten : this.#actueleInstrumenten);
        if (sorteer) {
            return versies.sort((a, b) => a.Instrumentversie().WorkIdentificatie().localeCompare(b.Instrumentversie().WorkIdentificatie()));
        }
        return versies;
    }
    /**
     * Geeft de versie van het instrument (als InstrumentversieSpecificatie of undefined) in deze momentopname
     * @returns {InstrumentversieSpecificatie}
     */
    Instrumentversie(instrument) {
        let versies = this.IsInvoer() ? this.#nieuweInstrumenten : this.#actueleInstrumenten;
        return versies[instrument];
    }
    /** @type {Object.<string,InstrumentversieSpecificatie>} */
    #actueleInstrumenten = {};
    /** @type {Object.<string,InstrumentversieSpecificatie>} */
    #nieuweInstrumenten = {};

    /**
     * Geeft aan dat tenminste één instrumentversie de oplossing is van samenloop bij vervlechting
     * of van het weghalen van wijzigingen bij ontvlechting.
     * @returns {boolean}
     */
    BevatOplossingSamenloop() {
        for (let versie of this.Instrumentversies()) {
            if (versie.IsOplossingSamenloop()) {
                return true;
            }
        }
        return false;
    }

    /**
     * Geeft aan dat de inhoud van tenminste een van de instrumentversies is gewijzigd 
     * in deze momentopname
     * @returns {boolean}
     */
    HeeftGewijzigdeInstrumentversie() {
        for (let versie of this.Instrumentversies()) {
            if (this === versie.Instrumentversie().MomentopnameLaatsteWijziging()) {
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
        if (this.Branch().Soort() === Branch.Soort_OplossingSamenloop) {
            let jwv;
            for (let branch of this.Branch().TreedtConditioneelInWerkingMet()) {
                let mo = this.Activiteit().LaatsteMomentopname(branch);
                if (!mo.JuridischWerkendVanaf().HeeftWaarde()) {
                    // Nog niet allemaal in werking
                    return mo.JuridischWerkendVanaf();
                } else if (!jwv || mo.JuridischWerkendVanaf().Specificatie() > jwv.Specificatie()) {
                    // Bewaar de laatste/grootste datum
                    jwv = mo.JuridischWerkendVanaf();
                }
            }
            return jwv;
        } else {
            return this.#tijdstempels.JuridischWerkendVanaf();
        }
    }

    /**
     * Geef de datum van start geldigheid, indien bekend en indien afwijkend van JuridischWerkendVanaf
     * @returns {Tijdstip}
     */
    GeldigVanaf() {
        if (this.Branch().Soort() === Branch.Soort_OplossingSamenloop) {
            let gv;
            for (let branch of this.Branch().TreedtConditioneelInWerkingMet()) {
                let mo = this.Activiteit().LaatsteMomentopname(branch);
                if (!mo.JuridischWerkendVanaf().HeeftWaarde()) {
                    // Nog niet allemaal in werking
                    return mo.JuridischWerkendVanaf();
                } else {
                    let datum = mo.GeldigVanaf()?.HeeftWaarde() ? mo.GeldigVanaf() : mo.JuridischWerkendVanaf();
                    if (!gv || datum.Specificatie() > gv.Specificatie()) {
                        // Bewaar de laatste/grootste datum
                        gv = datum;
                    }
                }
            }
            return gv && !gv.IsGelijk(this.JuridischWerkendVanaf()) ? gv : undefined;
        } else {
            return this.#tijdstempels.GeldigVanaf();
        }
    }

    /**
     * Geeft aan of de tijdstempels gewijzigd zijn in deze momentopname
     * @returns {boolean}
     */
    HeeftGewijzigdeTijdstempels() {
        if (this.Branch().Soort() === Branch.Soort_OplossingSamenloop) {
            for (let branch of this.Branch().TreedtConditioneelInWerkingMet()) {
                let mo = this.Activiteit().Momentopname(branch);
                if (mo?.HeeftGewijzigdeTijdstempels()) {
                    return true;
                }
            }
            return false;
        } else {
            return this.#tijdstempels.HeeftGewijzigdeTijdstempels();
        }
    }
    /** @type {TijdstempelsSpecificatie} */
    #tijdstempels;
    //#endregion

    //#region Eigenschappen - relatie met andere branches/momentopnamen
    /**
     * Geeft de voorgaande momentopname op dezelfde of een andere branch
     * @returns {Momentopname}
     */
    VoorgaandeMomentopname() {
        return this.#voorgaandeMomentopname;
    }
    /** @type {Momentopname} */
    #voorgaandeMomentopname;

    /**
     * Geeft de momentopnamen van de branches waarmee ontvlochten is
     * @returns {Momentopname[]}
     */
    OntvlochtenMet() {
        return this.#ontvlochtenMet;
    }
    /** @type {Momentopname[]} */
    #ontvlochtenMet;

    /**
     * Geeft de momentopnamen van de branches waarmee vervlochten is
     * @returns {Momentopname[]}
     */
    VervlochtenMet() {
        return this.#vervlochtenMet;
    }
    /** @type {Momentopname[]} */
    #vervlochtenMet;

    /**
     * Geeft de namen van de braches waarvan de inhoud is verwerkt in de
     * inhoud van deze momentopname. Dat is inclusief de branch van deze
     * momentopname.
     * @returns {string[]}
     */
    HeeftBijdragenVan() {
        return Object.keys(this.#bijdragen);
    }
    /**
     * Geeft de momentopname van de laatste bijdrage van een branch die in deze 
     * momentopname is verwerkt
     * @param {string} branchNaam - Een van de namen uit HeeftBijdragenVan
     * @returns {Momentopname|boolean} - Geeft de momentopname van laatste wijziging, of false
     */
    LaatsteBijdrage(branchNaam) {
        return this.#bijdragen[branchNaam];
    }

    /**
     * Per branch het tijdstip van laatste tijdstip van bijdragen
     */
    /** @type {Object.<string,Momentopname>} */
    #bijdragen = {};
    /**
     * Bepaal welke branches (en tot welk tijdstip) verwerkt zijn in deze momentopname
     */
    #BepaalBijdragen() {
        // Verzamel eerst alle bijdragen
        this.#bijdragen = this.#voorgaandeMomentopname ? Object.assign({}, this.#voorgaandeMomentopname.#bijdragen) : {};

        // Registreer deze momentopname (en die van de tegelijk beheerde branches)
        this.#bijdragen[this.Branch().Code()] = this;
        if (this.TegelijkBeheerd()) {
            for (let branch of this.TegelijkBeheerd()) {
                if (branch != this.Branch()) {
                    let mo = this.Activiteit().Momentopname(branch);
                    if (mo) { // Als BepaalBijdrage in de constructor wordt aangeroepen, dan hoeven nog niet alle momentopnamen aangemaakt te zijn
                        this.#bijdragen[branch.Code()] = mo;
                        mo.#bijdragen[this.Branch().Code()] = this;
                    }
                }
            }
        }

        // Pas de expliciete vervlechtingen toe
        for (let vervlochten of this.#vervlochtenMet) {
            for (let [branchcode, laatsteMO] of Object.entries(vervlochten.#bijdragen)) {
                let huidig = this.#bijdragen[branchcode];
                if (!huidig || huidig.Tijdstip().Vergelijk(laatsteMO.Tijdstip()) < 0) {
                    this.#bijdragen[branchcode] = laatsteMO;
                }
            }
        }

        // Markeer de bijdragen van de ontvlochten branches als niet aanwezig
        for (let v of this.#ontvlochtenMet) {
            this.#bijdragen[v.Branch().Code()] = false;
        }
    }
    //#endregion

    //#region Tegelijk beheren van verschillende branches
    /**
     * Geeft aan dat een aantal branches dezelfde inhoud hebben en altijd tegelijk beheerd
     * worden. Als dit niet undefined is, dan is deze branch onderdeel van de lijst.
     * @returns {Branch[]}
     */
    TegelijkBeheerd() {
        return this.#tegelijkBeheerd;
    }
    /**
     * Geeft aan dat er sprake is van tegelijk beheerde branches, en dat deze branch de 
     * eerste is waar het werk op uitgevoerd wordt
     * @returns
     */
    IsEersteVanTegelijkBeheerd() {
        return this.#tegelijkBeheerd && this.Branch() === this.#tegelijkBeheerd[0];
    }
    /**
     * Geeft aan dat er sprake is van tegelijk beheerde branches, en dat deze branch de 
     * niet een branch is waar het werk op uitgevoerd wordt; deze branch volgt andere branches.
     * @returns
     */
    IsTegelijkBeheerdEnVolgend() {
        return this.#tegelijkBeheerd && this.Branch() !== this.#tegelijkBeheerd[0];
    }
    /** @type {Branch[]} */
    #tegelijkBeheerd;

    /**
     * Geeft aan dat deze momentopname tegelijk beheerd wordt met andere momentopname(n).
     * Deze methode moet als eerste voor de eerste momentopname uitgevoerd worden.
     * De instrumentversies van de eerste momentopname uit momentopnamen moeten overgenomen worden.
     * @param {Momentopname[]} momentopnamen - De momentopname die tegelijk beheerd worden, of undefined als deze branch weer solo gaat.
     */
    BeheerTegelijk(momentopnamen) {
        this.#tegelijkBeheerd = momentopnamen?.map(mo => mo.Branch());
        if (momentopnamen) {
            if (this === momentopnamen[0]) {
                // Bepaal de bijdragen opnieuw
                this.#BepaalBijdragen();
            } else {
                // Werk de instrumentversies bij
                for (let instrumentversie of momentopnamen[0].Instrumentversies()) {
                    let huidig = this.Instrumentversie(instrumentversie.Instrument());
                    if (!huidig) {
                        // Voeg de instrumentversie toe
                        this.#actueleInstrumenten[instrumentversie.Instrument()] = new InstrumentversieSpecificatie(this, instrumentversie.Instrument(), instrumentversie);
                    } else if (!huidig.Instrumentversie().HeeftDezelfdeInhoud(instrumentversie.Instrumentversie())) {
                        huidig.Instrumentversie().GebruikEerdereVersie(instrumentversie.Instrumentversie());
                    }
                }
                // Neem alle bijdragen over
                this.#bijdragen = Object.assign({}, momentopnamen[0].#bijdragen);
            }
        } else {
            // Bepaal de bijdragen opnieuw
            this.#BepaalBijdragen();
        }
    }

    /**
     * Geeft aan dat deze branch niet langer tegelijk beheerd wordt met de opgegeven branch
     * @param {string[]} branchcodes - Codes van de branches die hun eigen weg gaan.
     */
    BeheerNietTegelijkMet(branchcodes) {
        if (this.#tegelijkBeheerd) {
            this.#tegelijkBeheerd = this.#tegelijkBeheerd.filter(b => !branchcodes.includes(b.Code()));
            if (this.#tegelijkBeheerd.length <= 1) {
                // Alleen deze branch over
                this.#tegelijkBeheerd = undefined;
            }
            // Bepaal de bijdragen opnieuw
            this.#BepaalBijdragen();
        }
    }
    //#endregion

    //#region Uitwisseling via STOP
    /**
     * Voeg de informatie in deze momentopname toe aan de ConsolidatieInformatie module en
     * maak de "STOP" modules voor de annotaties die sinds de laatste uitwisseling met de LVBB zijn gewijzigd
     * @param {any} consolidatieInformatieModule - ConsolidatieInformatie module waaraan de informatie toegevoegd moet worden
     * @param {boolean} isRevisie - Geeft aan of de momentopname deel is van een revisie en geen verwijzing naar de tekst kan hebben
     * @param {registreerSTOPModule} registreerAnnotatieModule - Methode die wordt aangeroepen voor elke annotatiemodule, met de naam en STOP xml van de module
     */
    MaakModulesVoorLVBB(consolidatieInformatieModule, isRevisie, registreerAnnotatieModule) {
        // Alleen de eerste van de tegelijk beheerde momentopnamen wordt gebruikt voor de uitwisseling van instrumentversies
        if (!this.IsTegelijkBeheerdEnVolgend()) {
            // Voeg de instrumentversie-informatie toe
            for (let instrumentversie of this.Instrumentversies(true)) {
                instrumentversie.Instrumentversie().MaakModulesVoorLVBB(consolidatieInformatieModule, isRevisie, registreerAnnotatieModule)
            }
        }

        // Voeg de tijdstempels toe
        let tijdstempelsEerderUitgewisseld = false;
        let tijdstempelsEerderBekend = false;
        for (let mo = this.VoorgaandeMomentopname(); mo && mo.Branch() === this.Branch(); mo = mo.VoorgaandeMomentopname()) {
            if (mo.#tijdstempelsUitgewisseld) {
                if (this.JuridischWerkendVanaf().IsGelijk(mo.JuridischWerkendVanaf()) && this.GeldigVanaf()?.Specificatie() === mo.GeldigVanaf()?.Specificatie()) {
                    // Waarde is niet gewijzigd
                    tijdstempelsEerderUitgewisseld = true;
                    break;
                }
                tijdstempelsEerderBekend = this.JuridischWerkendVanaf().HeeftWaarde();
                this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: tijdstempels,s zijn gewijzigd sinds laatste uitwisseling (gemaaktOp = ${this.Activiteit().Tijdstip().STOPDatumTijd()}).`)
                break;
            }
        }

        // Neem de tijdstempel op in de module
        if (!tijdstempelsEerderUitgewisseld) {
            if (this.JuridischWerkendVanaf().HeeftWaarde()) {
                this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, `Toegevoegd aan consolidatie-informatie voor branch ${this.Branch().Code()}: tijdstempels, zijn nog niet eerder uitgewisseld.`)
                if (!consolidatieInformatieModule.Tijdstempels) {
                    consolidatieInformatieModule.Tijdstempels = [];
                }
                consolidatieInformatieModule.Tijdstempels.push({
                    Tijdstempel: {
                        doel: this.Branch().Doel(),
                        soortTijdstempel: 'juridischWerkendVanaf',
                        datum: this.JuridischWerkendVanaf().STOPDatumTijd(),
                        eId: isRevisie ? undefined : 'eId_tijdstempels'
                    }
                });
                if (this.GeldigVanaf()?.HeeftWaarde()) {
                    consolidatieInformatieModule.Tijdstempels.push({
                        Tijdstempel: {
                            doel: this.Branch().Doel(),
                            soortTijdstempel: 'geldigVanaf',
                            datum: this.GeldigVanaf().STOPDatumTijd(),
                            eId: isRevisie ? undefined : 'eId_tijdstempels'
                        }
                    });
                }
                this.#tijdstempelsUitgewisseld = true;
            } else if (tijdstempelsEerderBekend) {
                if (!consolidatieInformatieModule.Terugtrekkingen) {
                    consolidatieInformatieModule.Terugtrekkingen = [];
                }
                consolidatieInformatieModule.Terugtrekkingen.push({
                    TerugtrekkingTijdstempel: {
                        doel: this.Branch().Doel(),
                        soortTijdstempel: 'juridischWerkendVanaf',
                        eId: isRevisie ? undefined : 'eId_tijdstempels'
                    }
                });
                this.#tijdstempelsUitgewisseld = true;
            }
        }
    }
    #tijdstempelsUitgewisseld = false;

    /**
     * Maak de modules voor de uitwisseling van regelgeving tussen downloadservice, adviesbureau en bevoegd gezag.
     * @param {string} bron - Een van de Activiteit.Systeem* waarden die aangeeft welk systeem als bron optreedt
     * @param {registreerSTOPModule} registreerModule - Methode die wordt aangeroepen voor elke STOP module, met de naam en STOP xml van de module
     */
    MaakModulesVoorUitwisseling(bron, registreerModule) {
        let pakbonModule = {
            _ns: Activiteit.STOP_Uitwisseling,
            Component: []
        }

        let momentopnameModule = {
            _ns: Activiteit.STOP_Data,
            doel: this.Branch().Doel(),
            gemaaktOp: this.Tijdstip().STOPDatumTijd()
        };
        let sindsMomentopname = undefined;
        let uitgewisseldInstrument = undefined;
        if (bron === Activiteit.Systeem_Adviesbureau) {
            // Van adviesbureau naar bevoegd gezag
            for (let mo = this.VoorgaandeMomentopname(); mo != undefined && mo.Branch() === this.Branch(); mo = mo.VoorgaandeMomentopname()) {
                sindsMomentopname = mo;
                if (mo.Activiteit().Soort().Naam == MogelijkeActiviteit.SoortActiviteit_Uitwisseling) {
                    break;
                }
                else if (mo.Activiteit().Soort().Naam == MogelijkeActiviteit.SoortActiviteit_Download) {
                    sindsMomentopname = undefined;
                    break;
                }
            }
            uitgewisseldInstrument = [];
            momentopnameModule.bevatWijzigingenVoor = {
                UitgewisseldInstrument: uitgewisseldInstrument
            }

            pakbonModule.Component.push({
                Component: {
                    FRBRWork: `/join/id/versie/${BGProcesSimulator.This().BGCode()}/${this.Tijdstip().Jaar()}/levering_aan_bg;${this.Tijdstip().DagUurHtml()[0]}`,
                    soortWork: '/join/id/stop/work_024',
                    heeftModule: {
                        Module: {
                            localName: 'Momentopname',
                            namespace: Activiteit.STOP_Data,
                            bestandsnaam: '00_momentopname.xml',
                            mediatype: 'application/xml',
                            schemaversie: BGProcesSimulator.STOP_Versie
                        }
                    }
                }
            });
        }

        let overigeModules = [];
        for (let instrumentversie of this.Instrumentversies(true)) {
            instrumentversie.Instrumentversie().MaakModulesVoorUitwisseling(this.Activiteit(), bron,
                pakbonModule.Component,
                uitgewisseldInstrument, sindsMomentopname,
                (moduleNaam, stopXml) => {
                    overigeModules.push({
                        ModuleNaam: moduleNaam,
                        STOPXml: stopXml
                    });
                });
        }

        // Geef de modules in de goede volgorde door
        registreerModule('Pakbon', Activiteit.ModuleToXml('Pakbon', pakbonModule))
        if (bron !== Activiteit.Systeem_LVBB) {
            registreerModule('Momentopname', Activiteit.ModuleToXml('Momentopname', momentopnameModule))
        }
        for (let module of overigeModules) {
            registreerModule(module.ModuleNaam, module.STOPXml);
        }
    }
    //#endregion

    //#region Statusoverzicht
    /**
     * Het overzicht van de momentopname in het projectoverzicht
     * @returns {string}
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
                if ((instrument.Instrumentversie().HeeftJuridischeInhoud() || instrument.Instrumentversie().MomentopnameLaatsteWijziging()?.Branch() === this.Branch()) && instrument.Instrumentversie().SoortInstrument() === soortInstrument) {
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
            if (this.GeldigVanaf()?.HeeftWaarde()) {
                html += `<tr><td colspan="${meerdereInstrumentenMogelijk ? 2 : 1}" class="nw">Terugwerkend tot</td><td>${this.GeldigVanaf().DatumTijdHtml()}</td></tr>`;
            }
        }

        if (heeftInstrumentversies && !this.Activiteit().UitgevoerdDoorAdviesbureau()) {
            let heeftIWTWijzigingen = false;
            let heeftInhoudWijzigingen = false;
            if (!this.Activiteit().IsOfficielePublicatie()) {
                heeftInhoudWijzigingen = true;
            } else {
                heeftInhoudWijzigingen = this.IsInhoudGewijzigd();
                if (!heeftInhoudWijzigingen) {
                    heeftIWTWijzigingen = this.IsInwerkingtredingGewijzigd();
                }
            }

            html += `<tr><td colspan="${(meerdereInstrumentenMogelijk ? 3 : 2)}">`;
            if (this.Activiteit().ConceptOfPublicatiebron()) {
                html += `In ${this.Activiteit().ConceptOfPublicatiebron()} wordt `;
            } else {
                html += `Indien aanwezig wordt in een ${this.#MogelijkePublicatie(this.IsVaststellingsbesluitGepubliceerd())} `;
            }
            if (heeftInhoudWijzigingen) {
                let uitgangssituatie = (this.IsTegelijkBeheerdEnVolgend() ? this.#bijdragen[this.TegelijkBeheerd()[0].Code()] : this).JuridischeUitgangssituatie();
                if (uitgangssituatie) {
                    html += `de wijziging ten opzichte van ${uitgangssituatie.Branch().InteractieNaam()} d.d. ${uitgangssituatie.Tijdstip().DatumTijdHtml()} beschreven`;
                } else {
                    html += 'een integrale versie van de tekst/informatieobjecten opgenomen.';
                }
            } else if (heeftIWTWijzigingen) {
                html += `de inwerkingtreding van het resultaat van ${this.JuridischeUitgangssituatie().Branch().InteractieNaam()} d.d. ${this.JuridischeUitgangssituatie().Tijdstip().DatumTijdHtml()} beschreven.`;
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
            <tr><th>Momentopname</th><td>Branch <code>${this.Branch().Code()}</code> @ ${this.Tijdstip().DatumTijdHtml()}</td></tr>
            <tr><td>Naam branch</td><td>${this.Branch().InteractieNaam()}</td></tr>
            <tr><td>Instrumentversies</td><td><ul>${this.Instrumentversies(true).map(iv => `<li>${iv.MeldInternDatamodelHtml()}</li>`).join('')}</ul></td></tr>
            <tr><td>Juridisch werkend vanaf</td><td>${this.JuridischWerkendVanaf().HeeftWaarde() ? this.JuridischWerkendVanaf().DatumTijdHtml() : '-'}</td></tr>
            <tr><td>Geldig vanaf</td><td>${this.GeldigVanaf()?.HeeftWaarde() ? this.GeldigVanaf().DatumTijdHtml() : '-'}</td></tr>
            <tr><td>Bevat wijzigingen van</td><td><ul>${Object.values(this.#bijdragen).sort((a, b) => -Branch.Vergelijk(a.Branch(), b.Branch())).map(mo => `<li>Branch <code>${mo.Branch().Code()}</code> @ ${mo.Tijdstip().DatumTijdHtml()}</li>`).join('')}</ul></td></tr>
            <tr><td>Regelgeving gepubliceerd in vaststellingsbesluit?</td><td>${this.IsVaststellingsbesluitGepubliceerd()
                ? 'Ja; juridische uitgangssituatie is een publicatie van deze branch' :
                this.IsOnderdeelVanPublicatieVastgesteldeInhoud()
                    ? 'Ja; dit is de juridische uitgangssituatie voor volgende publicaties.'
                    : 'Nee; juridische uitgangssituatie is geen publicatie deze branch.'
            }</td></tr >
            <tr><td>Juridische uitgangssituatie</td><td>`;
        let uitgangssituatie = this.IsOnderdeelVanPublicatieVastgesteldeInhoud() ? this : this.JuridischeUitgangssituatie();
        if (!uitgangssituatie) {
            html += '-';
        } else {
            html += `Branch <code>${uitgangssituatie.Branch().Code()}</code> @ ${uitgangssituatie.Tijdstip().DatumTijdHtml()}`;
        }
        html += `</td></tr>
        </table>`;
        if (this.TegelijkBeheerd()) {
            html += 'De regelgeving voor deze branch treedt tegelijk in werking met die van andere branches. Dezelfde instrumentversies zijn te vinden in: <ul>'
                + this.TegelijkBeheerd().map(b => `<li>Branch <code>${b.Code()}</code> @ ${this.Tijdstip().DatumTijdHtml()}</li>`).join('') + '</ul>';
        }
        this.Activiteit().UitvoeringMelding(Activiteit.Onderwerp_InternDatamodel, html);
    }
    //#endregion

    //#region Implementatie specificatie-element
    /**
     * Geeft aan dat er andere momentopnamen zijn die voortbouwen op de instrumentversies van deze momentopname
     * omdat ze gebruik maken van de consolidatie
     * @returns {boolean}
     */
    IsUitgangssituatieAlsConsolidatie() {
        return this.#gebruiktAlsConsolidatieDoor.length > 0;
    }
    /** @type {Momentopname[]} */
    #gebruiktAlsConsolidatieDoor = []

    /**
     * Geeft aan dat deze momentopname verwijderd kan worden zonder dat een van de
     * activiteiten in het scenario opnieuw gespecificeerd moet worden.
     * @returns {boolean}
     */
    KanVerwijderdWorden() {
        if (this.IsUitgangssituatieAlsConsolidatie()) {
            return false;
        }
        for (let instrumentversie of this.Instrumentversies()) {
            if (instrumentversie.Instrumentversie().IsBasisversie()) {
                return false;
            }
        }
        return true;
    }

    IsReadOnly() {
        if (BGProcesSimulator.Opties.MeerdereRegelingen
            || BGProcesSimulator.Opties.InformatieObjecten
            || BGProcesSimulator.Opties.Annotaties
            || BGProcesSimulator.Opties.NonStopAnnotaties) {
            return false;
        }
        if (!this.IsUitgangssituatieAlsConsolidatie()) {
            return false;
        }
        for (let instrumentversie of this.Instrumentversies()) {
            if (!instrumentversie.Instrumentversie().IsBasisversie()) {
                return false;
            }
        }
        return true;
    }

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
    TijdstempelsHtml() {
        return this.#tijdstempels?.Html() ?? '';
    }


    BeginInvoer() {
        this.#nieuweInstrumenten = Object.assign({}, this.#actueleInstrumenten);
        if (!BGProcesSimulator.Opties.MeerdereRegelingen && Object.keys(this.#nieuweInstrumenten).length == 0) {
            this.#MaakInstrument(Instrument.VrijeNaam(Instrument.SoortInstrument_Regeling, "Enige regeling"));
        }
    }

    InvoerInnerHtml() {
        // De opmaak is anders voor een wijziging of een initiële stand.
        let isWijzigig = Boolean(this.#voorgaandeMomentopname);

        // De opmaak verschilt tussen 1-instrument en meer-instrument scenario's.
        let meerdereInstrumentenMogelijk = BGProcesSimulator.Opties.MeerdereRegelingen || BGProcesSimulator.Opties.InformatieObjecten;
        let instrumentenAndereProjecten = {};
        if (meerdereInstrumentenMogelijk) {
            for (let instr of Instrument.Instrumentnamen()) {
                if (!(instr in this.#nieuweInstrumenten)) {
                    let soort = Instrument.SoortInstrument(instr);
                    if (instrumentenAndereProjecten[soort]) {
                        instrumentenAndereProjecten[soort].push(instr);
                    } else {
                        instrumentenAndereProjecten[soort] = [instr];
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
                if (instrumentenAndereProjecten[soortInstrument]) {
                    // Toevoegen van een instrument uit een ander project
                    let opties = []
                    for (let instr of instrumentenAndereProjecten[soortInstrument]) {
                        // Zoek de laatste citeertitel voor het instrument op
                        let tijdstip;
                        let interactienaam = undefined;
                        Momentopname.VoorAlleMomentopnamen(this.Tijdstip(), undefined, (mo) => {
                            if (!tijdstip || tijdstip.Vergelijk(mo.Tijdstip()) < 0) {
                                let versie = mo.Instrumentversie(instr);
                                if (versie?.Instrumentversie().IsNieuweVersie()) {
                                    let metadata = versie.Instrumentversie().Annotatie(true, Annotatie.SoortAnnotatie_Citeertitel);
                                    if (metadata?.Citeertitel()) {
                                        interactienaam = metadata.Citeertitel();
                                        tijdstip = mo.Tijdstip().Specificatie();
                                    }
                                }
                            }
                        });
                        opties.push({ id: instr, naam: (interactienaam ?? instr), citeertitel: (interactienaam ?? '') });
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
        if (!idSuffix) {
            return;
        }
        switch (idSuffix.charAt(0)) {
            case 'P':
                // Uit een ander project
                let select = this.Element('I' + idSuffix);
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
                if (!versie.Instrumentversie().Basisversie() && !versie.Instrumentversie().HeeftJuridischeInhoud()) {
                    this.#nieuweInstrumenten[instrument].Verwijder();
                    delete this.#nieuweInstrumenten[instrument];
                    delete specificatie[instrument];
                } else {
                    specificatie[instrument] = versie.Instrumentversie().MaakSpecificatie();
                }
            }
            this.#actueleInstrumenten = this.#nieuweInstrumenten;
        } else {
            // Annuleren
            let specificatie = this.Specificatie();
            if (specificatie !== undefined) {
                // Haal specificatie en nieuwe specificatie-elementen weg voor instrumenten die nog niet bestonden in de vorig gewijzigde versie
                for (let instrument in this.#nieuweInstrumenten) {
                    let vorigeVersie = this.#actueleInstrumenten[instrument];
                    if (vorigeVersie) {
                        specificatie[instrument] = vorigeVersie.Instrumentversie().MaakSpecificatie();
                    } else {
                        this.#nieuweInstrumenten[instrument].Verwijder();
                        delete specificatie[instrument];
                    }
                }
            }
        }
    }

    VerwijderInstrumentversies() {
        for (let instrumentversie of this.Instrumentversies()) {
            instrumentversie.Verwijder();
        }
        this.#actueleInstrumenten = {};
        this.#nieuweInstrumenten = {};
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
        if (citeertitel) {
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

//#region Branch
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
        if (code === Branch.Code_Uitgangssituatie) {
            this.Specificatie().Soort = Branch.Soort_GeldendeRegelgeving;
            this.Specificatie().Naam = 'Uitgangssituatie';
        }
        let branches = BGProcesSimulator.Singletons('Branches', {});
        if (code in branches) {
            throw new Error(`Branch met code ${code} bestaat al`);
        }
        branches[code] = this;

        this.#project = project;
        switch (this.Soort()) {
            case Branch.Soort_GeldendeRegelgeving:
                this.#iwtDatum = new Tijdstip(this, this.Specificatie(), 'IWTDatum', false);
                break;

            case Branch.Soort_VolgtOpAndereBranch:
                this.#volgtOpBranch = Branch.Branch(this.Specificatie().Branch);
                if (!this.#volgtOpBranch || this.#volgtOpBranch.OntstaanIn().Tijdstip().Vergelijk(this.OntstaanIn().Tijdstip()) > 0) {
                    throw new Error(`Branch met code ${this.Specificatie().Branch} bestaat (nog) niet`);
                }
                break

            case Branch.Soort_OplossingSamenloop:
            case Branch.Soort_Consolidatie:
                this.#inWerkingMet = this.Specificatie().Branches.map(bc => {
                    let b = Branch.Branch(bc);
                    if (!b || b.OntstaanIn().Tijdstip().Vergelijk(this.OntstaanIn().Tijdstip()) > 0) {
                        throw new Error(`Branch met code ${bc} bestaat (nog) niet`);
                    }
                    return b;
                });
                this.#volgtOpBranch = this.#inWerkingMet[0];
                break;
        }

        this.#volgorde = ++Branch.#volgende_volgorde;
    }

    /**
     * Maak een nieuwe branch
     * @param {Activiteit} activiteit - Activiteit die de branch aanmaakt
     * @param {Project} project - Project waarvoor de branch wordt aangemaakt
     * @param {string} code - Code voor de branch
     * @param {string} soort - Soort branch
     * @param {number|Branch|Branch[]} moAndereBranches - Optioneel: branch (Soort_VolgtOpAndereBranch)
     *                                                       / branches (Soort_OplossingSamenloop / Soort_Consolidatie)
     *                                                      / tijdstip (float) van consolidatie (Soort_GeldendeRegelgeving)
     */
    static MaakBranch(activiteit, project, code, soort, moAndereBranches) {
        if (!code) {
            code = BGProcesSimulator.VrijeNaam(Branch.Branches(undefined, project).map(b => b.Code()), `${project.Code()}_`);
        }
        activiteit.Specificatie()[code] = {
            Soort: soort
        };
        switch (soort) {
            case Branch.Soort_GeldendeRegelgeving:
                activiteit.Specificatie()[code].IWTDatum = moAndereBranches;
                break;
            case Branch.Soort_VolgtOpAndereBranch:
                activiteit.Specificatie()[code].Branch = moAndereBranches.Code();
                break;
            case Branch.Soort_OplossingSamenloop:
            case Branch.Soort_Consolidatie:
                activiteit.Specificatie()[code].Branches = moAndereBranches.map(b => b.Code());
                break;
        }
        return new Branch(activiteit, project, code);
    }

    destructor() {
        delete BGProcesSimulator.Singletons('Branches')[this.Code()];
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
     * Branch bevat de pro-actieve oplossing van samenloop tussen andere branches
     */
    static Soort_OplossingSamenloop = "TegelijkMet";
    /**
     * Branch bevat de oplossing-achteraf van samenloop tussen andere branches
     */
    static Soort_Consolidatie = "ConsolidatieVan";
    //#endregion

    //#region Eigenschappen
    /**
     * Geef de branches die in het scenario bekend zijn, gesorteerd op volgorde van aanmaken / onderlinge afhankelijkheid
     * Een branch die afhangt van een andere branch komt dus later in het resultaat.
     * @param {Tijdstip} tijdstip - Optioneel: tijdstip waarop de branch uiterlijk aangemaakt moet zijn - undefined voor alle branches
     * @param {Project} project - Optioneel: project waar de branch bij hoort - undefined voor branches van alle projecten
     * @returns {Branch[]}
     */
    static Branches(tijdstip, project) {
        let branches = [];
        for (let branch of Object.values(BGProcesSimulator.Singletons('Branches', {}))) {
            if (!project || branch.Project() === project) {
                if (tijdstip === undefined || branch.OntstaanIn().Tijdstip().Vergelijk(tijdstip) <= 0) {
                    branches.push(branch);
                }
            }
        }
        branches.sort(Branch.Vergelijk);
        return branches;
    }
    /** @type {number} */
    #volgorde;
    static #volgende_volgorde = 0; // Absolute waarde is niet relevant

    /**
     * Vergelijkingsfunctie om branches te sorteren
     * @returns {number}
     */
    static Vergelijk(a, b) {
        let diff = a.OntstaanIn().Tijdstip().Vergelijk(b.OntstaanIn().Tijdstip());
        if (diff === 0) {
            diff = a.#volgorde - b.#volgorde;
        }
        return diff;
    }

    /**
     * Geef de branch met de gegeven code
     * @param {string|Branch} branchcode - Code van de branch
     * @returns {Branch}
     */
    static Branch(branchcode) {
        if (branchcode instanceof Branch) {
            return branchcode
        }
        return BGProcesSimulator.Singletons('Branches', {})[branchcode];
    }

    /**
     * Geeft de activiteit waarin de branch is ontstaan
     * @returns {Momentopname}
     */
    OntstaanIn() {
        return this.SuperInvoer();
    }

    /**
     * Geeft de dag van IWT van de geconsolideerde regeling die als uitgangspunt gebruikt moet worden.
     * @returns {Tijdstip}
     */
    IWTDatum() {
        return this.#iwtDatum;
    }
    /** @type {Tijdstip} */
    #iwtDatum

    /**
     * Geeft het project waarvoor de branch is aangemaakt
     * @returns {Project}
     */
    Project() {
        return this.#project;
    }
    /** @type {Project} */
    #project;

    /**
     * Geeft de code van de branch zoals die in de specificatie voorkomt
     * @returns {string}
     */
    Code() {
        return this.Eigenschap();
    }

    /**
     * Geeft de naam van de branch zoals die in de user interface gebruikt moet worden
     * @returns {string}
     */
    InteractieNaam() {
        let branches = Branch.Branches(undefined, this.Project());
        if (branches.length <= 1) {
            return this.Project().Naam();
        }
        switch (this.Soort()) {
            case Branch.Soort_GeldendeRegelgeving:
                if (this === branches[0]) {
                    return `Kern van ${this.Project().Naam()}`;
                }
                break;
            case Branch.Soort_VolgtOpAndereBranch:
                if (this === branches[0]) {
                    return `Kern van ${this.Project().Naam()}`;
                } else {
                    return `Vervolg op ${this.VolgtOpBranch().InteractieNaam()}`;
                };
            case Branch.Soort_OplossingSamenloop:
                return `Samenloop van: ${this.TreedtConditioneelInWerkingMet().map(b => b.InteractieNaam()).join(', ')}`;
            case Branch.Soort_Consolidatie:
                return `Juridische samenvoeging van: ${this.TreedtConditioneelInWerkingMet().map(b => b.InteractieNaam()).join(', ')}`;
        }
        return `${this.Project().Naam()} (#${branches.indexOf(this)})`;
    }

    /**
     * Geeft de soort waartoe de branch behoort.
     * @returns {string}
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
    /** @type {Branch} */
    #volgtOpBranch;

    /**
     * Geeft de branches die eerst in werking moeten treden; deze branch 
     * treedt dan ook in werking. Als deze waarde niet undefined is,
     * dan behoort VolgtOpBranch tot hetzelfde project.
     * @returns {Branch[]}
     */
    TreedtConditioneelInWerkingMet() {
        return this.#inWerkingMet;
    }
    /** @type {Branch[]} */
    #inWerkingMet;

    /**
     * Geeft de laatste momentopname voor deze branch
     * @param {Tijdstip} tijdstip - Optioneel: tijdstip waarop de activiteit uiterlijk uitgevoerd moet zijn - undefined voor alle activiteiten
     * @returns {Momentopname}
     */
    LaatsteMomentopname(tijdstip) {
        let resultaat;
        Momentopname.VoorAlleMomentopnamen(tijdstip, this, (mo) => {
            resultaat = mo;
            return false;
        });
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

    //#region Specificatie
    /**
     * Maak de uitvoeringmeldingen voor het maken van de branch
     */
    PasSpecificatieToe() {
        // Meld de uitvoering
        let html = `<table>
                        <tr><th>Branch</th><td>${this.Code()}</td></tr>
                        <tr><td>Naam</td><td>${this.InteractieNaam()}</td></tr>`;
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
            case Branch.Soort_Consolidatie:
                html += `Regelgeving van de branch <code>${this.VolgtOpBranch().Code()}</code>`;
                break;
        }
        html += '</td></tr></table>';
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

//#region Project
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
        if (!code) {
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
        return Object.values(BGProcesSimulator.Singletons('Projecten', {})).filter((p) => !tijdstip || p.OntstaanIn().Tijdstip().Vergelijk(tijdstip) <= 0).sort((a, b) => a.Naam().localeCompare(b.Naam()));
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
     * @returns {string}
     */
    Code() {
        return this.Eigenschap();
    }

    /**
     * Naam van het project
     * @returns {string}
     */
    Naam() {
        return this.Specificatie().Naam;
    }

    /**
     * Geeft de activiteit waarin de branch is ontstaan
     * @returns {Activiteit}
     */
    OntstaanIn() {
        return this.SuperInvoer();
    }
    //#endregion

    //#region Implementatie van SpecificatieElement
    WeergaveInnerHtml() {
        let html = `<table class="w100">
                    <tr><td class="nw">Naam van het project:</td><td class="w100">${this.#naam.Html()}</td></tr>`
        if (this.IsInvoer() || this.#beschrijving.Specificatie()) {
            html += `<tr><td>Beschrijving:</td><td>${this.#beschrijving.Html()}</td></tr>`
        }
        html += '</table>';
        return html;
    }
    /** @type {Naam} */
    #naam;
    /** @type {Beschrijving} */
    #beschrijving;

    #MaakValideNaam(naam) {
        let namen = [];
        for (let project of Object.values(BGProcesSimulator.Singletons('Projecten', {}))) {
            if (project !== this) {
                namen.push(project.Naam());
            }
        }
        if (!naam || namen.includes(naam)) {
            return BGProcesSimulator.VrijeNaam(namen, 'Project #');
        }
        return naam;
    }
    //#endregion
}
//#endregion

//#endregion

//#region Consolidatie
/*==============================================================================
 *
 * De BG software moet ook bijhouden of er consolidatieproblemen optreden, dus
 * of er onopgeloste samenloop is.
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
     * @returns {Tijdstip}
     */
    Datum() {
        return this.#datum;
    }
    /** @type {Tijdstip} */
    #datum;

    /**
     * De namen van de branches die leiden tot het ontstaan
     * van dit iwt-moment
     * @returns {string[]}
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
    /** @type {Object.<string,Momentopname>} */
    #bijdragen = {};
    //#endregion

    //#region Bijwerken
    /**
     * Geef een branch door als bijdragend aan een IWT-moment
     * @param {Object.<string,IWTMoment>} perBranch - Collectie met IWTMoment per branch
     * @param {Object.<string,IWTMoment>} perDatum - Collectie met IWTMoment per datum
     * @param {string} branchcode - Naam van de branch
     * @param {Momentopname} momentopname - laatste momentopname voor de branch
     * @param {Tijdstip} iwtDatum - Nieuwe datum van inwerkingtreding
     */
    static WerkBij(perBranch, perDatum, branchcode, momentopname, iwtDatum) {
        let iwtMoment = perBranch[branchcode];
        if (iwtMoment) {
            if (!iwtMoment.Datum().IsGelijk(iwtDatum)) {
                iwtMoment.#VerwijderBranch(perBranch, perDatum, branchcode);
                if (!iwtDatum) {
                    return;
                }
                iwtMoment = undefined;
            }
        }
        if (iwtDatum?.HeeftWaarde()) {
            if (!iwtMoment) {
                iwtMoment = perDatum[iwtDatum.Specificatie()]
            }
            iwtMoment = iwtMoment ? iwtMoment.#Kloon() : new IWTMoment(iwtDatum);
            iwtMoment.#bijdragen[branchcode] = momentopname; // Nieuwe momentopname is altijd recenter dan eerder verwerkte
            iwtMoment.#WerkCollectieBij(perBranch, perDatum);
        }
    }

    /**
     * Verwijder een branch als bijdragend aan een IWT-moment
     * @param {Object.<string,IWTMoment>} perBranch - Collectie met IWTMoment per branch
     * @param {Object.<string,IWTMoment>} perDatum - Collectie met IWTMoment per datum
     * @param {string} branchnaam - Naam van de branch
     */
    #VerwijderBranch(perBranch, perDatum, branchnaam) {
        delete perBranch[branchnaam];
        if (this.Inwerkingtredingbranchcodes().length == 1) {
            delete perDatum[this.#datum.Specificatie()];
            return;
        }

        let kloon = this.#Kloon();
        delete kloon.#bijdragen[branchnaam];
        kloon.#WerkCollectieBij(perBranch, perDatum);
    }

    /**
     * Voeg deze instantie toe aan de collectie
     * @param {Object.<string,IWTMoment>} perBranch - Collectie met IWTMoment per branch
     * @param {Object.<string,IWTMoment>} perDatum - Collectie met IWTMoment per datum
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
     * @param {string[]} iwtVolgorde - Brachcodes op volgorde van inwerkingtreding, of undefined als de status niet bepaald hoeft te worden.
     * @param {Object.<string,Momentopname>} cumulatieveIWTBijdragen - Bijdragen aan de IWT-versie van alle branches die in werking zijn, of undefined als de status niet bepaald hoeft te worden.
     * @param {boolean} meldInternDatamodel - Geeft aan of het interne datamodel gerapporteerd moet worden
     */
    constructor(activiteit, iwtMoment, iwtVolgorde, cumulatieveIWTBijdragen, meldInternDatamodel) {
        this.#iwtMoment = iwtMoment;
        this.#isBepaald = Boolean(cumulatieveIWTBijdragen);

        if (this.#isBepaald) {
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
            /** @type {Object.<string,Momentopname>} */
            let bijdragenViaBranches = {}

            /**
             * Werk de bijdragenViaBranches bij
             * @param {Momentopname} bijdragendeMomentopname
             */
            function VoegBijdragenToe(bijdragendeMomentopname) {
                for (let branchCode of bijdragendeMomentopname.HeeftBijdragenVan()) {
                    let mo = bijdragendeMomentopname.LaatsteBijdrage(branchCode);
                    if (mo === false) {
                        bijdragenViaBranches[branchCode] = mo;
                    } else {
                        let laatste = bijdragenViaBranches[branchCode];
                        if (!laatste || laatste.Activiteit().Tijdstip().Vergelijk(mo.Activiteit().Tijdstip()) < 0) {
                            bijdragenViaBranches[branchCode] = mo;
                        }
                    }
                }
            }
            for (let branchcode of iwtMoment.Inwerkingtredingbranchcodes()) {
                VoegBijdragenToe(cumulatieveIWTBijdragen[branchcode]);
            }

            // Er is geen sprake van samenloop als elke laatste bijdrage aan het IWT-moment tevens de laatste bijdrage aan de instrumentversies
            // die voor het IWT-moment zijn klaargezet, dus de bijdragen in bijdragenViaBranches.
            this.#teVervlechten = [];
            for (let vereisteBranchcode of Object.keys(cumulatieveIWTBijdragen).sort((bc1, bc2) => iwtVolgorde.indexOf(bc2) - iwtVolgorde.indexOf(bc1))) {
                let bijdrage = bijdragenViaBranches[vereisteBranchcode];
                if (!bijdrage || bijdrage != cumulatieveIWTBijdragen[vereisteBranchcode]) {
                    this.#teVervlechten.push(cumulatieveIWTBijdragen[vereisteBranchcode]);
                    VoegBijdragenToe(cumulatieveIWTBijdragen[vereisteBranchcode]);
                }
            }

            // Via de bijdragen van de instrumentversies mogen er geen branches zijn die niet in werking zijn
            this.#teOntvlechten = [];
            for (let bijdragendeBranchcode in bijdragenViaBranches) {
                if (!cumulatieveIWTBijdragen[bijdragendeBranchcode]) {
                    this.#teOntvlechten.push(bijdragenViaBranches[bijdragendeBranchcode]);
                }
            }

            if (activiteit && meldInternDatamodel) {
                let html = `<table>
                <tr><th class="nw">Geconsolideerde regelgeving</th><td>inwerkingtredingsmoment ${this.#iwtMoment.Datum().DatumTijdHtml()}</td><tr>
                <tr><td class="mw">Status consolidatie</td><td>${this.IsVoltooid() ? 'Voltooid' : 'Nog niet afgerond'}</td></tr>
                <tr><td class="nw">Bevat wijzigingen uit</td><td><ul>${Object.keys(cumulatieveIWTBijdragen).sort((a, b) => -Branch.Vergelijk(Branch.Branch(a), Branch.Branch(b))).map(bc => `<li>Branch <code>${bc}</code> @ ${cumulatieveIWTBijdragen[bc].Tijdstip().DatumTijdHtml()}</li>`).join('')}</ul></td></tr>
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
                    html += `<tr><td class="nw">Alle eerdere wijzigingen meegenomen?</td><td>${this.#teOntvlechten.length > 0 || this.#teVervlechten.length > 0 ? 'Nee<br>' : this.#samenloopBijIWT ? 'Ja, mits de samenloop bij iwt wordt opgelost' : 'Ja'}`;
                    if (this.#teVervlechten.length > 0) {
                        html += `Nog te vervlechten:<ul>${this.#teVervlechten.sort((a, b) => -Branch.Vergelijk(a.Branch(), b.Branch())).map(mo => `<li>Branch <code>${mo.Branch().Code()}, wijzigingen na ${mo.Tijdstip().DatumTijdHtml()} niet meegenomen</li>`).join('')}</ul>`
                    }
                    if (this.#teOntvlechten.length > 0) {
                        html += `Nog te ontvlechten:<ul>${this.#teOntvlechten.sort((a, b) => -Branch.Vergelijk(a.Branch(), b.Branch())).map(mo => `<li>Branch <code>${mo.Branch().Code()}, wijzigingen t/m ${mo.Tijdstip().DatumTijdHtml()} onterecht meegenomen</li>`).join('')}</ul>`
                    }
                    html += '</td></tr>';
                }
                html += '</table>';
                activiteit.UitvoeringMelding(Activiteit.Onderwerp_InternDatamodel, html);
            }
        }
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Het IWT moment waar dit de status van is
     * @returns {IWTMoment}
     */
    IWTMoment() {
        return this.#iwtMoment;
    }
    /** @type {IWTMoment} */
    #iwtMoment;

    /**
     * Geeft aan dat de consolidatie begonnen is
     * @returns {boolean}
     */
    IsBepaald() {
        return this.#isBepaald;
    }
    /** @type {boolean} */
    #isBepaald;

    /**
     * Geeft aan dat de consolidatie voltooid is
     * @returns {boolean}
     */
    IsVoltooid() {
        return this.#isBepaald && (!this.#samenloopBijIWT && this.#teVervlechten.length == 0 && this.#teOntvlechten.length == 0);
    }

    /**
     * Geeft aan dat er samenloop is tussen de verschillende branches die tegelijk in werking treden
     * @returns {boolean}
     */
    HeeftSamenloopBijIWT() {
        return this.#samenloopBijIWT;
    }
    /** @type {boolean} */
    #samenloopBijIWT;

    /**
     * De momentopnamen (uit andere branches dan de iwt-branches) die vervlochten moeten worden
     * om tot een geconsolideerde versie voor het IWT moment te komen
     * @returns {Momentopname[]}
     */
    TeVervlechten() {
        return this.#teVervlechten;
    }
    /** @type {Momentopname[]} */
    #teVervlechten;

    /**
     * De momentopnamen (uit andere branches dan de iwt-branches) die vervlochten moeten worden
     * om tot een geconsolideerde versie voor het IWT moment te komen
     * @returns {Momentopname[]}
     */
    TeOntvlechten() {
        return this.#teOntvlechten;
    }
    /** @type {Momentopname[]} */
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
     * Geeft aan dat er nog geen enkele geldende regelgeving bekend is
     * @returns {boolean}
     */
    static IsConsolidatieAanwezig() {
        if (BGProcesSimulator.This().Uitgangssituatie().JuridischWerkendVanaf()?.HeeftWaarde()) {
            return true;
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
    /** @type {IWTMomentConsolidatiestatus[]} */
    #geldend = [];

    /**
     * Geeft de toekomstige IWT-momenten en de status ervan, voor zover bepaald.
     * Het resultaat is een lege lijst als er geen IWT momenten zijn.
     * @returns {IWTMomentConsolidatiestatus[]}
     */
    Bepaald() {
        return this.#geldend;
    }
    //#endregion

    //#region Weergave
    Html() {
        if (this.Bepaald().length == 0) {
            return 'Consolidatie voltooid';
        }
        let html = `<table><tr><td>Inwerkingtreding</td><td>Status</td></tr>`;
        for (let bepaald of this.Bepaald()) {
            html += `<tr><td class="nw">${bepaald.IWTMoment().Datum().DatumTijdHtml()}</td><td class="nw">`;
            if (!bepaald.IsBepaald()) {
                html += 'Incompleet';
            } else if (bepaald.IsVoltooid()) {
                html += 'Voltooid';
            } else {
                html += 'Incompleet';
            }
            html += '</td></tr>';
        }
        html += '</table>';
        return html;
    }
    //#endregion

    //#region Bijwerken van de consolidatie
    /**
     * Werk de consolidatie-informatie bij
     * @param {Consolidatiestatus} voorgaandeConsolidatie - Consolidatie van voorgaande activiteit of van de Uitgangssituatie
     * @param {Activiteit} activiteit - Activiteit of Uitgangssituatie waar de consolidatiestatus bij hoort
     * @returns {Consolidatiestatus} - De consolidatiestatus te gebruiken als voorgaandeConsolidatie voor de volgende activiteit
     */
    WerkBij(voorgaandeConsolidatie, activiteit) {
        this.#geldend = [];
        this.#iwtPerBranch = voorgaandeConsolidatie ? Object.assign({}, voorgaandeConsolidatie.#iwtPerBranch) : {}
        this.#iwtPerDatum = voorgaandeConsolidatie ? Object.assign({}, voorgaandeConsolidatie.#iwtPerDatum) : {}

        if (!(activiteit instanceof Uitgangssituatie) && !activiteit.BepaalConsolidatie()) {
            if (voorgaandeConsolidatie && voorgaandeConsolidatie.#geldend.length > 0) {
                // Neem de resultaten van de voorgaande consolidatie over voor zover ze nog gelden ten tijde van deze activiteit
                let laatsteVoorActiviteit;
                for (let bepaald of voorgaandeConsolidatie.#geldend) {
                    if (bepaald.IWTMoment().Datum().Vergelijk(activiteit.Tijdstip()) <= 0) {
                        laatsteVoorActiviteit = bepaald.IWTMoment().Datum();
                    }
                }
                if (laatsteVoorActiviteit) {
                    for (let bepaald of voorgaandeConsolidatie.#geldend) {
                        if (bepaald.IWTMoment().Datum().Vergelijk(laatsteVoorActiviteit) >= 0) {
                            this.#geldend.push(bepaald);
                        }
                    }
                } else {
                    this.#geldend.push(voorgaandeConsolidatie.#geldend[voorgaandeConsolidatie.#geldend.length - 1]);
                }
            }
            return voorgaandeConsolidatie;
        }

        // Werk de relatie tussen IWT-momenten en branches bij
        if (activiteit instanceof Uitgangssituatie) {
            IWTMoment.WerkBij(this.#iwtPerBranch, this.#iwtPerDatum, activiteit.Branch().Code(), activiteit, activiteit.JuridischWerkendVanaf());
        } else {
            for (let mo of activiteit.Momentopnamen()) {
                if (mo.Activiteit() !== activiteit) {
                    // Ongewijzigde momentopname
                    continue;
                }
                IWTMoment.WerkBij(this.#iwtPerBranch, this.#iwtPerDatum, mo.Branch().Code(), mo, mo.IsVaststellingsbesluitGepubliceerd() || mo.IsOnderdeelVanPublicatieVastgesteldeInhoud() ? mo.JuridischWerkendVanaf() : undefined);
            }
        }

        // Deze simulator bouwt de volledige consolidatie op. Dat zal in de praktijk na een enkele
        // activiteit niet nodig zijn, dan kan het oude deel ongemoeid gelaten worden. Maar omdat het
        // hier over bijzonder weinig gegevens gaat, wordt (qua codering) de meest eenvoudige oplossing
        // gekozen.
        let iwtDatums = Object.keys(this.#iwtPerDatum).map(t => parseInt(t)).sort((a, b) => a - b);
        if (iwtDatums.length == 0) {
            // Niets te consolideren
            return;
        }
        let meldConsolidatieActiviteit = !(activiteit instanceof Uitgangssituatie) && activiteit.BepaalConsolidatie();
        if (meldConsolidatieActiviteit) {
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
        let iwtVolgorde = [];
        let bepaalStatus = true;
        for (let iwtDatum of iwtDatums) {
            let iwtMoment = this.#iwtPerDatum[iwtDatum];
            if (!bepaalStatus) {
                this.#geldend.push(new IWTMomentConsolidatiestatus(undefined, undefined, iwtVolgorde, undefined, false));
                continue;
            }

            for (let branchnaam of iwtMoment.Inwerkingtredingbranchcodes()) {
                iwtVolgorde.push(branchnaam);
                cumulatieveIWTBijdragen[branchnaam] = iwtMoment.LaatsteBijdrage(branchnaam);
            }
            if (iwtDatum < teConsoliderenVanaf) {
                continue;
            }

            // Bepaal de status van de consolidatie
            let status = new IWTMomentConsolidatiestatus(activiteit instanceof Uitgangssituatie ? undefined : activiteit, iwtMoment, iwtVolgorde, cumulatieveIWTBijdragen, meldConsolidatieActiviteit);
            this.#geldend.push(status);
            if (!status.IsVoltooid() && bepaalStatus) {
                // Verder gaan heeft geen zin, de volgende zullen incompleet worden als dit IWT-moment wordt opgelost
                if (meldConsolidatieActiviteit && iwtDatum !== iwtDatums[iwtDatums.length - 1]) {
                    activiteit.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Controle van status van consolideren gestopt; de consolidatie voor latere inwerkingtredingsmomenten
                    zal nog niet afgerond zijn omdat het voltooien van de consolidatie voor ${iwtDatum} tot aanvullende consolidatiewerkzaamheden voor latere datums zal leiden.`);
                }
                bepaalStatus = false;
            }
        }
        return this;
    }
    /** @type {Object.<string,IWTMoment>} */
    #iwtPerBranch = {};
    /** @type {Object.<string,IWTMoment>} */
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
    ContainerElement() {
        return 'div';
    }

    WeergaveInnerHtml() {
        if (!this.SuperInvoer()) {
            if (this.Specificatie()) {
                return `<table><tr><td>${this.HtmlWerkBij("Wijzig de beschrijving", 'M')}</td><td>${this.Specificatie() ?? ''}</td></tr></table>`;
            } else {
                return this.HtmlVoegToe("Voeg een beschrijving toe", 'M');
            }
        } else {
            return this.Specificatie() ?? '';
        }
    }

    InvoerInnerHtml() {
        return `<textarea class="beschrijving" id="${this.ElementId('T')}">${(this.Specificatie() ?? '')}</textarea>`;
    }

    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix == 'M') {
            this.OpenModal();
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            let elt = this.Element('T');
            if (elt) {
                this.SpecificatieWordt(elt.value);
            }
            if (!this.SuperInvoer()) {
                BGProcesSimulator.This().WerkSpecificatiesBij();
            }
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
     * @param {Naam~maakValideNaam} maakValideNaam - Functie om een ingevoerde naam te valideren
     */
    constructor(specificatie, superInvoer, maakValideNaam) {
        super(specificatie, 'Naam', undefined, superInvoer);
        this.#maakValideNaam = maakValideNaam;
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        if (!this.SuperInvoer()) {
            if (this.Specificatie()) {
                return `<table><tr><td>${this.HtmlWerkBij("Wijzig de naam", 'M')}</td><td>${this.Specificatie() ?? ''}</td></tr></table>`;
            } else {
                return this.HtmlVoegToe("Voeg een beschrijving toe", 'M');
            }
        } else {
            return this.Specificatie() ?? '';
        }
    }

    InvoerInnerHtml() {
        return `<input type="text" class="naam" id="${this.ElementId('T')}" value="${(this.Specificatie() ?? '')}">`;
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
        let elt = this.Element('T');
        if (elt) {
            let valide = this.#maakValideNaam(elt.value, isNieuweVersie);
            if (valide !== elt.value) {
                elt.value = valide;
                return true;
            }
        }
    }
    /** @type {Naam~maakValideNaam} */
    #maakValideNaam;

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            let elt = this.Element('T');
            if (elt) {
                this.SpecificatieWordt(elt.value);
            }
            if (!this.SuperInvoer()) {
                BGProcesSimulator.This().WerkSpecificatiesBij();
            }
        }
    }
    //#endregion
}
/**
 * Controle-functie om de naam van de 
 * @callback Naam~maakValideNaam
 * @param {string} kandidaat - Voorgestelde naam
 * @param {boolean} isNieuweVersie - Geeft aan of de naam een geaccepteerde invoer is of een tijdelijke versie
 * @returns {string} - De valide versie van de naam
 */

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
        if (this.Specificatie()) {
            let spec = this.Specificatie();
            this.#WerkSpecificatieBij(new Date(Date.UTC(parseInt(spec.substr(0, 4)), parseInt(spec.substr(5, 2)) - 1, parseInt(spec.substr(8, 2)))));
        } else {
            this.#WerkSpecificatieBij(this.#Now());
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
    /** @type {Date} */
    #datum;
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return `${this.HtmlWerkBij("Pas de startdatum van het scenario aan", 'M')}${this.Specificatie() ?? `Vandaag (${this.#Now().toJSON().substr(0, 10)})`}`;
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
        let spec = datum.toJSON().substr(0, 10);
        let nu = this.#Now().toJSON().substr(0, 10);
        this.SpecificatieWordt(nu === spec ? null : spec);
    }
    /**
     * Geef de huidige datum als ware het een UTC datum
     * @returns
     */
    #Now() {
        let nu = new Date(Date.now());
        return new Date(Date.UTC(nu.getFullYear(), nu.getMonth(), nu.getDate()));
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
    PasSpecificatieToe() {
        this.#ModulesVoorLVBBSimulator();
        this.IsOnderdeelVanPublicatieVastgesteldeInhoudWordt()
    }
    //#endregion

    //#region Eigenschappen
    /**
     * De uitgangssituatie is in werking 
     * @returns {Tijdstip}
     */
    JuridischWerkendVanaf() {
        if (this.Instrumentversies().length > 0) {
            return Tijdstip.StartDatum();
        }
    }

    /**
     * Geef de datum van start geldigheid (als undefined)
     * @returns {Tijdstip}
     */
    GeldigVanaf() {
    }

    /**
     * Geef een overzicht van de status van het consolidatieproces na de uitgangssituatie
     * @returns {Consolidatiestatus}
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
                return 'Er is geen regelgeving in werking.';
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
                html += `<table><tr><td>${this.HtmlWerkBij("Wijzig de uitgangssituatie", 'M')}</td><td>${this.KanVerwijderdWorden() ? this.HtmlVerwijder("Verwijder de uitgangssituatie", 'D') : ''}</td > <td>${super.WeergaveInnerHtml()}</td></tr ></table >`;
            }
            return html;
        }
    }

    OnWeergaveClick(elt, idSuffix) {
        if (idSuffix == 'D') {
            this.VerwijderInstrumentversies();
            this.SpecificatieWordt(undefined);
            BGProcesSimulator.This().WerkScenarioUit(0);
        }
        else if (idSuffix == 'M') {
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
            this.#ModulesVoorLVBBSimulator();
            BGProcesSimulator.This().WerkScenarioUit(0);
        }
    }
    //#endregion

    //#region LVBB simulator
    /**
     * Geeft de STOP modules die voor de uitgangssituatie naar de LVBB simulator
     * gestuurd moeten worden.
     * @returns {Object[]}
     */
    ModulesVoorLVBBSimulator() {
        return this.#modules;
    }
    /** @type {Object[]} */
    #modules;
    #ModulesVoorLVBBSimulator() {
        this.#modules = []
        if (this.Instrumentversies().length == 0) {
            return;
        }
        let module = {
            _ns: Activiteit.STOP_Data,
            gemaaktOp: Tijdstip.StartTijd().STOPDatumTijd()
        }
        this.MaakModulesVoorLVBB(module, false, (moduleNaam, stopXml) => this.#modules.push({ ModuleNaam: moduleNaam, STOPXml: stopXml }));
        this.#modules.push({ ModuleNaam: 'ConsolidatieInformatie', STOPXml: Activiteit.ModuleToXml('ConsolidatieInformatie', module) });
    }
    //#endregion
}

//#endregion

//#region Activiteit generiek
/*==============================================================================
 *
 * Vastleggen wat de eindgebruiker uitvoert: Activiteit
 * 
 =============================================================================*/

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
     * @param {boolean} isNieuw - Geeft aan of de activiteit gemaakt wordt om de specificatie in te voeren
     */
    constructor(specificatie, isNieuw) {
        let isUitgangssituatie = specificatie.Soort === MogelijkeActiviteit.SoortActiviteit_Uitgangssituatie;
        super(isUitgangssituatie ? [] : BGProcesSimulator.This().Specificatie().Activiteiten, undefined, specificatie);
        this.#isNieuw = isNieuw;
        this.#naam = this.Specificatie().Soort;
        this.#soort = MogelijkeActiviteit.SoortActiviteit[this.Specificatie().Soort];
        this.#soort.Naam = this.Specificatie().Soort;
        this.#tijdstip = new Tijdstip(this, this.Specificatie(), 'Tijdstip', true);
        this.#beschrijving = new Beschrijving(this.Specificatie(), this);
        if (isUitgangssituatie) {
            this.#project = new Project(this, Project.Code_Uitgangssituatie);
        } else {
            BGProcesSimulator.Singletons('Activiteiten', {})[this.Index()] = this;
            if (this.Specificatie().Project) {
                this.#project = Project.Project(this.Specificatie().Project);
                if (!this.#project) {
                    this.SpecificatieMelding(`Activiteit is onderdeel van een onbekend project met code "${this.Specificatie().Project}"`);
                }
            }
        }
    }

    /**
     * Aangeroepen als een activiteit verwijderd wordt
     */
    destructor() {
        if (this.Index()) {
            delete BGProcesSimulator.Singletons('Activiteiten')[this.Index()];
            for (let activiteit of this.#blokkeertActiviteit) {
                activiteit.#blokkerendeActiviteiten.splice(activiteit.#blokkerendeActiviteiten.indexOf(this), 1);
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
        if (!soort.Constructor) {
            throw new Error(`Geen in-memory representatie beschikbaar voor activiteit ${specificatie.Soort}`);
        }
        let activiteit = undefined;
        try {
            activiteit = soort.Constructor(specificatie, false);
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
    static Systeem_BHKV = "Bronhouderkoppelvlak LVBB";
    static Systeem_LVBB = "Downloadservice LVBB";

    static Onderwerp_ScenarioFout = "Scenario";
    static Onderwerp_InternDatamodel = "Intern datamodel";
    static Onderwerp_Invoer = "Eindgebruiker";
    static Onderwerp_Procesbegeleiding = "Procesbegeleiding";
    static Onderwerp_Uitwisseling = "Uitwisseling";
    static Onderwerp_Verwerking_Invoer = "Verwerking invoer";

    static STOP_Data = "https://standaarden.overheid.nl/stop/imop/data/";
    static STOP_Consolidatie = "https://standaarden.overheid.nl/stop/imop/consolidatie/";
    static STOP_Geo = "https://standaarden.overheid.nl/stop/imop/geo/";
    static STOP_SE = "http://www.opengis.net/se";
    static STOP_Tekst = "https://standaarden.overheid.nl/stop/imop/tekst/"
    static STOP_Uitwisseling = "https://standaarden.overheid.nl/stop/imop/uitwisseling/"
    static NonSTOP_Data = "urn:non.stop";
    //#endregion

    //#region Eigenschappen
    /**
     * Geef alle gespecificeerde activiteiten, gesorteerd op tijdstip
     * @param {Tijdstip} tijdstip - Optioneel: tijdstip waarop de activiteit uiterlijk uitgevoerd moet zijn - undefined voor alle activiteiten
     * @param {Project} project - Optioneel: project waarbij de activiteiten getoond moeten worden.
     * @returns {Activiteit[]}
     */
    static Activiteiten(tijdstip, project) {

        return Object.values(BGProcesSimulator.Singletons('Activiteiten', {})).filter(
            (activiteit) => {
                if (!project || activiteit.ToonInProject(project)) {
                    if (!tijdstip || activiteit.Tijdstip().Vergelijk(tijdstip) <= 0) {
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
    /** @type {Project} */
    #project;

    /**
     * Geeft het tijdstip waarop de activiteit uitgevoerd wordt
     * @returns {Tijdstip}
     */
    Tijdstip() {
        return this.#tijdstip;
    }
    /** @type {Tijdstip} */
    #tijdstip;

    /**
     * Geeft de beschrijving van de soort activiteit uit SoortActiviteit
     * @returns {any}
     */
    Soort() {
        return this.#soort;
    }
    /** @type {any} */
    #soort;

    /**
     * Geeft de beschrijving van de activiteit
     * @returns {Beschrijving}
     */
    Beschrijving() {
        return this.#beschrijving;
    }
    /** @type {Beschrijving} */
    #beschrijving;


    /**
     * Geeft aan of de activiteit nieuw is, d.w.z. dat de specificatie nog ingevoerd wordt.
     * @returns {boolean}
     */
    IsNieuw() {
        return this.#isNieuw;
    }
    /** @type {boolean} */
    #isNieuw;


    /**
     * Geeft aan dat de activiteit verwijderd kan worden door de opsteller van het scenario.
     * Dit is niet mogelijk als het resultaat van deze activiteit gebruikt is in de specificatie
     * van een latere activiteit.
     * @returns {boolean}
     */
    KanVerwijderdWorden() {
        return this.#blokkerendeActiviteiten.length === 0;
    }
    /** @type {Activiteit[]} */
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
    /** @type {Activiteit[]} */
    #blokkeertActiviteit = [];

    /**
     * Geef de momentopnamen waarvoor inmiddels specificatie-elementen zijn aangemaakt
     * @param {boolean} - Geeft aan of de momentopnamen gesorteerd moeten worden
     * @returns {Momentopname[]}
     */
    Momentopnamen(sorteer = false) {
        let momentopnamen = [];
        for (let im of this.SubManagers()) {
            if (im instanceof Momentopname) {
                momentopnamen.push(im);
            }
        }
        if (sorteer) {
            momentopnamen.sort((a, b) => Branch.Vergelijk(a.Branch(), b.Branch()));
        }
        return momentopnamen;
    }

    /**
     * Geef de momentopname voor de branch als daarvoor inmiddels een specificatie-element is aangemaakt.
     * @param {Branch|string} branch - Branch of de code daarvan
     * @returns {Momentopname}
     */
    Momentopname(branch) {
        let branchCode = branch instanceof Branch ? branch.Code() : branch;
        for (let im of this.SubManagers()) {
            if (im instanceof Momentopname && im.Branch().Code() === branchCode) {
                return im;
            }
        }
    }

    /**
     * Geef de laatstbekende momentopname voor de branch, uit deze of uit een voorgaande activiteit
     * @param {Branch|string} branch - Branch of de code daarvan
     * @returns {Momentopname}
     */
    LaatsteMomentopname(branch) {
        let mo = this.Momentopname(branch);
        if (mo) {
            return mo;
        }
        let activiteiten = Activiteit.Activiteiten(this.Tijdstip(), Branch.Branch(branch).Project()).reverse();
        for (let activiteit of activiteiten) {
            if (activiteit != this) {
                let mo = activiteit.Momentopname(branch);
                if (mo) {
                    return mo;
                }
            }
        }
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
    /** @type {string} */
    #naam;

    /**
     * Geeft aan of de activiteit vermeld moet worden in het overzicht van het project
     * @param {Project} project - Het project waarvoor het overzicht gemaakt wordt
     * @returns {boolean}
     */
    ToonInProject(project) {
        if (!project) {
            return false;
        }
        if (this.Project() === project) {
            return true;
        }
        for (let momentopname of this.Momentopnamen()) {
            if (momentopname.Branch().Project() === project) {
                return true;
            }
        }
        return false;
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
     * Als de activiteit leidt tot een publicatie of revisie of concept daarvan: 
     * de naam van het concept/de bron met lidwoord.
     * @returns {string}
     */
    ConceptOfPublicatiebron() {
        return this.Publicatiebron();
    }

    /**
     * Pas de specificatie toe voor de activiteit die zojuist is aangemaakt op basis van de specificatie.
     * Doet standaard niets.
     */
    PasSpecificatieToe() {
    }

    /**
     * Geeft aan of tijdstempels ingevoerd mogen worden
     * @returns {boolean}
     */
    TijdstempelsMogelijk() {
        return this.Soort().MomentopnameTijdstempels;
    }

    /**
     * Geeft aan of de tijdstempels - indien ze ingevoerd kunnen worden, ook verplicht zijn.
     * @returns {boolean}
     */
    TijdstempelsVerplicht() {
        return false;
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
        for (let momentopname of this.Momentopnamen(true)) {
            momentopname.MeldInternDatamodel();
        }
        Instrumentversie.MeldGepubliceerdeInstrumentversies(this);
    }

    /**
     * Geeft aan of de consolidatie opnieuw bepaald moet worden naar aanleiding van de activiteit 
     */
    BepaalConsolidatie() {
        if (this.IsOfficielePublicatie() || this.IsRevisie()) {
            for (let mo of this.Momentopnamen()) {
                if (mo.IsVaststellingsbesluitGepubliceerd() || mo.IsOnderdeelVanPublicatieVastgesteldeInhoud()) {
                    if (mo.IsInwerkingtredingGewijzigd()) {
                        return true;
                    }
                    if (mo.JuridischWerkendVanaf().HeeftWaarde() && mo.IsInhoudGewijzigd()) {
                        return true;
                    }
                }
            }
        }
        return false;
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

    /**
     * Geeft aan of er meldingen over de specificatie zijn. Deze kunnen zowel bij het inlezen 
     * van de specificatie aangevuld worden als bij het wijzigen ervan, als een nieuwe activiteit
     * voor een eerdere datum leidt tot inconsistenties bij latere activiteiten.
     * @returns {boolean}
     */
    HeeftSpecificatieMeldingen() {
        return this.#heeftSpecificatieMeldingen;
    }
    #heeftSpecificatieMeldingen = false;

    /**
     * Lees de specificaties van de momentopnamen voor deze activiteit 
     * @param {boolean} inclusiefMomentopnameSpecificaties - Geeft aan dat er specificaties van momentopnamen in de specificatie kunnen staan.
     * @param {string} projectcode - De naam van het project waarvoor de momentopnamen worden aangemaakt
     *                               Alleen opgeven als de activiteit "Maak project" is en het project afwijkt van this.Project().
     */
    VerwerkMomentopnameSpecificaties(inclusiefMomentopnameSpecificaties, projectcode) {
        let specificatie = projectcode ? this.Specificatie()[projectcode] : this.Specificatie();
        let project = projectcode ? Project.Project(projectcode) : this.Project();

        let bestaandeBranches = []
        if (inclusiefMomentopnameSpecificaties) {
            // Maak momentopnamen aan op basis van de branches in de specificatie
            for (let branchcode in specificatie) {
                if (!this.#soort.Props.includes(branchcode) && branchcode.includes('_')) {
                    let branch = Branch.Branch(branchcode);
                    if (!branch) {
                        this.SpecificatieMelding(this.Tijdstip(), `branch <code>${branchcode}</code> bestaat (nog) niet`);
                        // Maak de branch toch maar aan
                        branch = new Branch(this, this.Project(), branchcode);
                    }
                    bestaandeBranches.push(branch)
                }
            }
        }
        // Voeg ook momentopnamen toe voor de overige branches uit het project
        for (let branch of Branch.Branches(this.Tijdstip(), project)) {
            if (!bestaandeBranches.includes(branch.Code())) {
                bestaandeBranches.push(branch);
            }
        }

        // Maak de in-memory momentopnamen aan
        // Doe dat op volgorde van de branches
        for (let branch of bestaandeBranches.sort((a, b) => Branch.Vergelijk(a, b))) {
            if (branch.Code() in specificatie) {
                this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Maak een nieuwe momentopname voor de branch ${branch.Code()}.`);
            }
            this.VerwerkMomentopnameSpecificatie(branch.Code(), specificatie);
        }

        // Verwijder momentopnamen die niet meer relevant zijn
        for (let momentopname of [...this.Momentopnamen()]) {
            if (!bestaandeBranches.includes(momentopname.Branch())) {
                momentopname.Verwijder();
            }
        }
    }


    /**
     * Maak een momentopname voor een branch als onderdeel van de specificatie
     * @param {string} branchcode - Code van de branch. De branch moet bestaan.
     * @param {any} specificatie - De specificatie voor zover die anders is dan de specificatie van deze activiteit
     * @param {bool/int/Momentopname} werkUitgangssituatieBij - Geeft aan of de uitgangssituatie bijgewerkt moet worden, voor Branch.Soort_GeldendeRegelgeving
     *                                             evt voor welk tijdstip de geconsolideerde regelgeving gebruikt moet worden en voor anderen
     *                                             evt de Momentopname die als uitgangspunt genomen moet worden
     * @param {Momentopname[]} ontvlochtenversies - De wijzigingen die ontvlochten moeten worden met deze wijziging
     * @param {Momentopname[]} vervlochtenversies - De wijzigingen die vervlochten moeten worden met deze wijziging
     * @returns {Momentopname}
     */
    VerwerkMomentopnameSpecificatie(branchcode, specificatie, werkUitgangssituatieBij = false, ontvlochtenversies, vervlochtenversies) {
        // Kijk of de momentopname al bestaat
        let momentopname = this.Momentopname(branchcode);
        if (!momentopname) {
            // Zoek de branch op
            let branch = Branch.Branch(branchcode);
            if (!branch) {
                this.SpecificatieMelding(this.Tijdstip(), `branch <code>${branchcode}</code> bestaat (nog) niet`);
                branch = new Branch(this, this.Project(), branchcode);
            }
            momentopname = new Momentopname(this, specificatie ?? this.Specificatie(), branch, this.TijdstempelsMogelijk(), this.TijdstempelsVerplicht(), werkUitgangssituatieBij, ontvlochtenversies, vervlochtenversies);
        }
        return momentopname;
    }
    //#endregion

    //#region Resultaat van de activiteit
    /**
     * Geeft aan of de activiteit leidt tot een officiële publicatie van de regelgeving (geen kennisgeving)
     * @returns {boolean}
     */
    IsOfficielePublicatie() {
        return this.Publicatiebron() && !this.Publicatiebron().endsWith("revisie");
    }

    /**
     * Geeft aan of de activiteit leidt tot een aanlevering van een revisie aan de LVBB
     * @returns {boolean}
     */
    IsRevisie() {
        return this.Publicatiebron() && this.Publicatiebron().endsWith("revisie");
    }

    /**
     * Vermeld een stap in de uitvoering van de activiteit
     * @param {string} onderwerp - Onderwerp waar de melding betrekking op heeft
     * @param {string} melding - Melding (HTML) van de stap in de uitvoering
     */
    UitvoeringMelding(onderwerp, melding) {
        if (onderwerp != Activiteit.Onderwerp_ScenarioFout) {
            if (this.#eersteUitvoeringMelding) {
                this.#eersteUitvoeringMelding = false;
                this.#uitvoeringMeldingen.push({
                    Onderwerp: Activiteit.Onderwerp_Invoer,
                    Melding: `De medewerker${BGProcesSimulator.This().BevoegdGezag() !== BGProcesSimulator.SoortBG_Gemeente ? '' : this.UitgevoerdDoorAdviesbureau() ? ' van het adviesbureau' : ' van het bevoegd gezag'} voert uit: ${this.Naam()}`
                });
            }
        }
        this.#uitvoeringMeldingen.push({
            Onderwerp: onderwerp,
            Melding: melding
        });
    }
    #eersteUitvoeringMelding = true;
    #uitvoeringMeldingen = [];

    /**
     * Geeft de HTML voor het verslag van de uitvoering van de geselecteerde activiteit
     * @returns {string}
     */
    UitvoeringsverslagHtml() {
        let html = '';
        if (this.#uitvoeringMeldingen.length === 0) {
            html += 'Er is geen verslag beschikbaar van de uitvoering van de activiteit.';
        } else {
            html += '<table>';

            let onderwerp;
            let trStart;
            let rows = [];
            function VoegMeldingenToe() {
                if (rows.length > 0) {
                    html += `<tr${onderwerp === Activiteit.Onderwerp_ScenarioFout ? ' class="specmelding"' : ''}>
                                <td rowspan="${rows.length}">${onderwerp === Activiteit.Onderwerp_ScenarioFout ? '<span class="specmelding">&#x26A0;</span>' : ''}</td>
                                <td class="nw" rowspan="${rows.length}">${onderwerp}</td>
                                <td>${rows.join(`</td></tr><tr${onderwerp === Activiteit.Onderwerp_ScenarioFout ? ' class="specmelding"' : ''}><td>`)}</td>
                            </tr>`;
                    rows = [];
                }
            }

            for (let melding of this.#uitvoeringMeldingen) {
                if (melding.Onderwerp !== onderwerp) {
                    VoegMeldingenToe();
                    onderwerp = melding.Onderwerp;
                }
                rows.push(melding.Melding);
            }
            VoegMeldingenToe();
            html += '</table>';
        }
        return html;
    }

    /**
     * Geeft aan of er STOP modules uitgewisseld zijn bij de uitvoering van de activiteit
     * @returns {boolean}
     */
    HeeftUitwisselingen() {
        return this.#uitwisselingen.length > 0;
    }

    /**
     * Geeft de STOP modules benodigd als invoer voor de LVBB simulator
     * @returns {any[]} STOP-XML modules die tijdens de uitvoering van deze activiteit naar de LVBB gestuurd worden.
     */
    ModulesVoorLVBBSimulator() {
        return this.#uitwisselingen.filter(u => u.Ontvanger == Activiteit.Systeem_BHKV).map(u => { return { ModuleNaam: u.ModuleNaam, STOPXml: u.STOPXml } });
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
     * @param {string} moduleNaam - Naam van de module
     * @param {string} stopXml - XML van de STOP module
     */
    VoegUitwisselingToe(systeemAfzender, systeemOntvanger, moduleNaam, stopXml) {
        this.#uitwisselingen.push({
            Afzender: systeemAfzender,
            Ontvanger: systeemOntvanger,
            ModuleNaam: moduleNaam,
            STOPXml: stopXml
        });
    }
    /**
     * Voeg de STOP modules toe die nodig zijn om wijzigingen in de momentopnamen door te geven
     */
    VoegModulesVoorMomentopnamenToe() {
        let consolidatieInformatieModule = {
            _ns: Activiteit.STOP_Data,
            gemaaktOp: this.Tijdstip().STOPDatumTijd()
        }
        let defaultKeys = Object.keys(consolidatieInformatieModule).length;

        for (let mo of this.Momentopnamen(true)) {
            mo.MaakModulesVoorLVBB(consolidatieInformatieModule, this.IsRevisie(),
                (moduleNaam, stopXml) => this.#uitwisselingen.push({
                    Afzender: Activiteit.Systeem_BG,
                    Ontvanger: Activiteit.Systeem_BHKV,
                    ModuleNaam: moduleNaam,
                    STOPXml: stopXml
                })
            );
        }
        if (Object.keys(consolidatieInformatieModule).length > defaultKeys) {
            this.#uitwisselingen.push({
                Afzender: Activiteit.Systeem_BG,
                Ontvanger: Activiteit.Systeem_BHKV,
                ModuleNaam: 'ConsolidatieInformatie',
                STOPXml: Activiteit.ModuleToXml('ConsolidatieInformatie', consolidatieInformatieModule)
            });
        }
    }

    /**
     * Vertaal een module naar STOP XML
     * @param {string} moduleNaam - Naam van de module
     * @param {any} module - Inhoud van de module
     * @param {string} instrumentversie - Optioneel: instrumentversie waar de module bij hoort
     * @returns {string}
     */
    static ModuleToXml(moduleNaam, module, instrumentversie) {
        let xml = `<${moduleNaam} xmlns="${module._ns}">`;
        if (instrumentversie) {
            xml += `
    <!--
    Deze module hoort bij de instrumentversie:

    ${instrumentversie}
    -->`
        }
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
                    xml += `
${indent}<${tag}>`;
                    for (let elt of value) {
                        xml = Activiteit.#ModuleToXml(xml, indent + '  ', elt);
                    }
                    xml += `
${indent}</${tag}>`;
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
     * @returns {Consolidatiestatus}
     */
    Consolidatiestatus() {
        return this.#consolidatiestatus;
    }
    #consolidatiestatus = new Consolidatiestatus();

    /**
     * Geef een overzicht van de status van het consolidatieproces voorafgaand aan deze activiteit
     * @returns {Consolidatiestatus}
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

        html += '<table>';
        let branches = Branch.Branches(this.Tijdstip(), project);
        for (let branch of branches) {
            html += '<tr>';
            if (branches.length > 1) {
                html += `<td><b>${branch.InteractieNaam()}</b></td>`;
            }
            html += `<td>${naActiviteit.LaatsteMomentopname(branch).OverzichtHtml()}</td></tr>`;
        }
        html += '</table>';
        return html;
    }
    //#endregion

    //#region Ondersteuning implementatie specificatie-element
    /**
     * Geeft de HTML die opgenomen moet worden aan het begin van de WeergaveInnerHtml/InvoerInnerHtml
     * @returns {string}
     */
    StartInnerHtml() {
        let html = `<h3>${this.Naam()}</h3>`;
        if (!this.IsInvoer() && this.UitgevoerdDoorAdviesbureau()) {
            html += `<p class="entry_detail">Deze activiteit is uitgevoerd door een adviesbureau.</p>`;
        }
        return html;
    }

    /**
     * Geeft de HTML die opgenomen moet worden aan het einde van de WeergaveInnerHtml/InvoerInnerHtml
     * @returns {string}
     */
    EindeInnerHtml() {
        let html = '';
        if (this.IsInvoer()) {
            html += `<div class="scenario">Geef een beschrijving van de rol van deze activiteit in het scenario (optioneel)${this.#beschrijving.Html()}</div>`;
        }
        return html;
    }

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
                // Adviesbureau is bezig
                switch (laatste.Soort().Naam) {
                    case MogelijkeActiviteit.SoortActiviteit_Uitwisseling:
                        // Laatste is levering van BG aan adviesbureau
                        this.#bijAdviesbureau[project.Code()] = [MogelijkeActiviteit.SoortActiviteit_Wijziging];
                        continue;
                    case MogelijkeActiviteit.SoortActiviteit_Download:
                        this.#bijAdviesbureau[project.Code()] = [MogelijkeActiviteit.SoortActiviteit_Wijziging];
                        continue;
                    default:
                        this.#bijAdviesbureau[project.Code()] = [MogelijkeActiviteit.SoortActiviteit_Wijziging, MogelijkeActiviteit.SoortActiviteit_Uitwisseling];
                        continue;
                }
            } else {
                // Bevoegd gezag aan de slag
                let mogelijk = [];
                for (let soort in MogelijkeActiviteit.SoortActiviteit) {
                    if (MogelijkeActiviteit.SoortActiviteit[soort].SoortBG) {
                        if (!MogelijkeActiviteit.SoortActiviteit[soort].SoortBG.includes(BGProcesSimulator.This().BevoegdGezag())) {
                            continue;
                        }
                    }
                    if (soort === MogelijkeActiviteit.SoortActiviteit_Uitwisseling) {
                        if (Branch.Branches(tijdstip, project).length > 1) {
                            // Geen uitwisseling mogelijk bij meerdere branches
                            continue;
                        }
                    }
                    let kan = false;
                    if (MogelijkeActiviteit.SoortActiviteit[soort].KanVolgenOp === true) {
                        kan = true;
                    } else {
                        for (let act of activiteiten) {
                            if (MogelijkeActiviteit.SoortActiviteit[soort].KanVolgenOp.includes(act.Soort().Naam)) {
                                kan = true;
                                break;
                            }
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
                    if (kan && MogelijkeActiviteit.SoortActiviteit[soort].KanTochNiet) {
                        kan = !MogelijkeActiviteit.SoortActiviteit[soort].KanTochNiet(tijdstip, activiteiten);
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
    }
    //#endregion

    //#region Constanten
    static SoortActiviteit_Uitgangssituatie = 'Uitgangssituatie';
    static SoortActiviteit_MaakProject = 'Maak project';
    static SoortActiviteit_Download = 'Download';
    static SoortActiviteit_Uitwisseling = 'Uitwisseling';
    static SoortActiviteit_Wijziging = 'Wijziging';
    static SoortActiviteit_Ontwerpbesluit = 'Ontwerpbesluit';
    static SoortActiviteit_Conceptvaststellingsbesluit = 'Concept-vaststellingsbesluit';
    static SoortActiviteit_Vaststellingsbesluit = 'Vaststellingsbesluit';
    static SoortActiviteit_VoltooiConsolidatie = 'Voltooi consolidatie';

    static SoortActiviteit = {
        'Uitgangssituatie': {
            KanVolgenOp: [],
            Props: []
        },
        'Maak project': {
            KanVolgenOp: [],
            Props: ['Invoer'],
            MomentopnameTijdstempels: false,
            MomentopnameProps: ['Soort', 'IWTDatum', 'Branch', 'Branches'],
            Constructor: (specificatie, nieuw) => {
                if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente) {
                    return new Activiteit_MaakProject_Gemeente(specificatie, nieuw);
                } else if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Rijksoverheid) {
                    return new Activiteit_MaakProject_Rijksoverheid(specificatie, nieuw);
                }
            }
        },
        'Download': {
            KanVolgenOp: [],
            Props: ['Invoer'],
            MomentopnameTijdstempels: false,
            MomentopnameProps: ['Soort'],
            Constructor: (specificatie, nieuw) => new Activiteit_Download(specificatie, nieuw)
        },
        'Wijziging': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Download],
            KanNietVolgenOp: false,
            Props: [],
            MomentopnameTijdstempels: false,
            MomentopnameProps: [],
            Constructor: (specificatie, nieuw) => new Activiteit_Wijzigen(specificatie, nieuw),
            Beschrijving: 'Werk aan de volgende versie van regelingen en/of informatieobjecten.'
        },
        'Uitwisseling': {
            SoortBG: [BGProcesSimulator.SoortBG_Gemeente],
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Download, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: [MogelijkeActiviteit.SoortActiviteit_Ontwerpbesluit, MogelijkeActiviteit.SoortActiviteit_Conceptvaststellingsbesluit, MogelijkeActiviteit.SoortActiviteit_Vaststellingsbesluit],
            Props: [],
            Constructor: (specificatie, nieuw, doorAdviesbureau) => new Activiteit_Uitwisseling(specificatie, nieuw, doorAdviesbureau),
            Beschrijving: 'Wissel een versie van de regelgeving uit tussen bevoegd gezag en adviesbureau.'
        },
        'Bijwerken uitgangssituatie': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: [MogelijkeActiviteit.SoortActiviteit_Vaststellingsbesluit],
            Props: ['Invoer'],
            MomentopnameTijdstempels: false,
            MomentopnameProps: ['IWTDatum'],
            Constructor: (specificatie, nieuw) => new Activiteit_BijwerkenUitgangssituatie(specificatie, nieuw),
            Beschrijving: 'Neem de wijzigingen over die zijn aangebrancht in de uitgangssituatie voor dit project sinds de start van het project (of sinds de vorige keer dat de uitgangssituatie is bijgewerkt).'
        }/*,
        'Maak branch': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: false,
            Props: [],
            MomentopnameTijdstempels: false,
            MomentopnameProps: ['Soort', 'Branch', 'Branches'],
            Constructor: (specificatie, nieuw) => new Activiteit_MaakBranch(specificatie, nieuw),
            Beschrijving: ''
        }*/,
        'Ontwerpbesluit': {
            SoortBG: [BGProcesSimulator.SoortBG_Gemeente],
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: ['Concept-vaststellingsbesluit', 'Vaststellingsbesluit'],
            Props: ['Begin inzagetermijn', 'Einde inzagetermijn'],
            MomentopnameTijdstempels: false,
            MomentopnameProps: [],
            Constructor: (specificatie, nieuw) => new Activiteit_Besluit(specificatie, nieuw),
            Beschrijving: 'Stel het ontwerpbesluit op en publiceer het.'
        },
        'Concept-vaststellingsbesluit': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: ['Vaststellingsbesluit'],
            Props: [],
            MomentopnameTijdstempels: true,
            MomentopnameProps: [],
            Constructor: (specificatie, nieuw) => new Activiteit_Besluit(specificatie, nieuw),
            Beschrijving: 'Stel het vaststellingsbesluit op; deze versie wordt gebruikt voor de interne besluitvorming binnen het bevoegd gezag.'
        },
        'Vaststellingsbesluit': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_MaakProject, MogelijkeActiviteit.SoortActiviteit_Uitwisseling],
            KanNietVolgenOp: false,
            Props: ['Einde beroepstermijn'],
            MomentopnameTijdstempels: true,
            MomentopnameProps: [],
            Constructor: (specificatie, nieuw) => new Activiteit_Besluit(specificatie, nieuw),
            Beschrijving: 'Finaliseer het vaststellingsbesluit en maak het bekend.'
        },
        'Voltooi consolidatie': {
            KanVolgenOp: [MogelijkeActiviteit.SoortActiviteit_Vaststellingsbesluit],
            KanNietVolgenOp: false,
            KanTochNiet: (tijdstip, activiteiten) => Activiteit_VoltooiConsolidatie.KanTochNiet(tijdstip, activiteiten),
            Props: ['IWTDatum', 'Branch'],
            MomentopnameTijdstempels: false,
            MomentopnameProps: [],
            Constructor: (specificatie, nieuw) => new Activiteit_VoltooiConsolidatie(specificatie, nieuw),
            Beschrijving: 'Voltooi de consolidatie door samenloop op te oplossen.'
        },
        'Anders...': {
            KanVolgenOp: true,
            KanNietVolgenOp: false,
            Props: ['Naam'],
            Constructor: (specificatie, nieuw) => new Activiteit_Overig(specificatie, nieuw),
            Beschrijving: 'Activiteit waarvoor de simulator geen ondersteuning biedt maar die wel genoemd moet worden om het scenario volledig te maken.'
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
    /** @type {Object.<string,string[]>} */
    #bijAdviesbureau = {};
    /** @type {Object.<string,string[]>} */
    #bijBevoegdGezag = {};

    /**
     * Geef de soort activiteiten die voor een project uitgevoerd kunnen worden
     * @returns {string[]}
     */
    ProjectActiviteiten(projectcode) {
        let soorten = this.#bijBevoegdGezag[projectcode];
        if (!soorten) {
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
        this.#tijdstip = new Tijdstip(this, { Tijdstip: 1 }, 'Tijdstip', true, Tijdstip.StartDatum(), () => Project.Projecten().length == 0);
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
                    if (!Consolidatiestatus.IsConsolidatieAanwezig()) {
                        // Er zijn nog geen projecten en er is ook nog geen geldende regelgeving te downloaden. Het maken van een nieuw project door het bevoegd gezag is de enig mogelijke activiteit.
                        inTeVoeren = this.#MaakActiviteit(MogelijkeActiviteit.SoortActiviteit_MaakProject, 1);
                    }
                } else {
                    // Er zijn nog geen projecten. Het maken van een nieuw project is de enig mogelijke activiteit.
                    inTeVoeren = this.#MaakActiviteit(MogelijkeActiviteit.SoortActiviteit_MaakProject, 1);
                }
            } else if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente && !Consolidatiestatus.IsConsolidatieAanwezig()) {
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
        if (BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente) {
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
        let html = '';
        let disabled = '';
        if (!Consolidatiestatus.IsConsolidatieAanwezig()) {
            this.#adviesbureau = false;
            disabled = ' disabled';
        }
        return `<table>
                <tr><td>Wie is de eindgebruiker?</td><td>Medewerker van <input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('BG')}"${this.#adviesbureau ? '' : ' checked'}${disabled}> <label for="${this.ElementId('BG')}">bevoegd gezag</label>
                                                        / <input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('AB')}"${this.#adviesbureau ? ' checked' : ''}${disabled}> <label for="${this.ElementId('AB')}">adviesbureau</label></td></tr>
                <tr><td>Tijdstip van uitvoering</td><td>${this.#tijdstip.Html()}</td></tr>
                </table>`;
    }
    /** @type {boolean} */
    #adviesbureau;
    /** @type {Tijdstip} */
    #tijdstip;

    #SelecteerActiviteit(voorBevoegdGezag) {
        if (!this.#mogelijkeActiviteit) {
            this.#mogelijkeActiviteit = new MogelijkeActiviteit(this.#tijdstip);
        }
        let heeftProjecten = this.#mogelijkeActiviteit.ActiviteitenMogelijk(voorBevoegdGezag);
        let html = `Welke activiteit voert de medewerker van het ${voorBevoegdGezag ? 'bevoegd gezag' : 'adviesbureau'} uit?
        <dl>
        <dt><input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('N')}"${!this.#projectcode || !heeftProjecten ? ' checked' : ''}> <label for="${this.ElementId('N')}">Maak een nieuw project${voorBevoegdGezag ? '' : ' via download uit de LVBB'}</label></dt>
        <dt><input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('B')}"${this.#projectcode && heeftProjecten ? ' checked' : ''}${heeftProjecten ? '' : ' disabled'}> <label for="${this.ElementId('B')}">Voor het project:</label> `;
        if (heeftProjecten) {

            html += `<select id="${this.ElementId('P')}">`;
            if (!this.#projectcode) {
                html += `<option value="" selected></option>`;
            }
            for (let project of this.#mogelijkeActiviteit.Projecten(voorBevoegdGezag)) {
                html += `<option value="${project.Code()}"${this.#projectcode === project.Code() ? ' selected' : ''}>${project.Naam()}</option>`;
            }
            html += '</select>';

            if (!this.#projectcode) {
                html += '</dt>';
            } else {
                html += `: <select id="${this.ElementId('A')}">`;
                if (!this.#soortActiviteit) {
                    html += `<option value="" selected></option>`
                }
                for (let soort of this.#mogelijkeActiviteit.ProjectActiviteiten(this.#projectcode)) {
                    html += `<option value="${soort}"${this.#soortActiviteit === soort ? ' selected' : ''}>${soort}</option>`
                }
                html += '</select></dt>';
                if (this.#soortActiviteit) {
                    html += `<dd>(${MogelijkeActiviteit.SoortActiviteit[this.#soortActiviteit].Beschrijving})</dd>`;
                }
            }
        } else {
            html += ' (geen projecten beschikbaar)</dt>';
        }
        html += `</dl>`;
        return html;
    }
    /** @type {MogelijkeActiviteit} */
    #mogelijkeActiviteit;
    /** @type {string} */
    #projectcode;
    /** @type {string} */
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
                if (this.#adviesbureau !== true) {
                    this.#adviesbureau = true;
                    this.#projectcode = undefined;
                }
                return;
            case 'BG':
                if (this.#adviesbureau !== false) {
                    this.#adviesbureau = false;
                    this.#projectcode = undefined;
                }
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
                    break;
                case 2:
                    if (this.#projectcode && !this.#soortActiviteit) {
                        return true;
                    }
                    break;
            }
        }
    }

    EindeModal(accepteerInvoer) {
        if (accepteerInvoer) {
            let activiteit;
            if (this.#projectcode) {
                activiteit = this.#MaakActiviteit(this.#soortActiviteit, this.#tijdstip.Specificatie(), this.#projectcode);
            } else {
                activiteit = this.#MaakActiviteit(this.#adviesbureau ? MogelijkeActiviteit.SoortActiviteit_Download : MogelijkeActiviteit.SoortActiviteit_MaakProject, this.#tijdstip.Specificatie());
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
        if (projectcode) {
            specificatie.Project = projectcode;
        }
        return definitie.Constructor(specificatie, true, this.#adviesbureau);
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
    /** @type {Activiteit} */
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
     * @param {boolean} isNieuw - Geeft aan of de activiteit gemaakt wordt om de specificatie in te voeren
     */
    constructor(specificatie, isNieuw) {
        super(specificatie, isNieuw);
        if (isNieuw) {
            this.#project = new Project(this);
            this.Specificatie().Invoer = {
                Project: this.#project.Code()
            };
        } else {
            if (!this.Specificatie().Invoer) {
                throw new Error(`De specificatie van de invoer voor nieuw project ontbreekt (Tijdstip = ${this.Tijdstip().Specificatie})`);
            }
            if (!this.Specificatie().Invoer.Project) {
                throw new Error(`De specificatie van het project ontbreekt (Tijdstip = ${this.Tijdstip().Specificatie})`);
            }
            if (!this.Specificatie().Invoer.Branch) {
                throw new Error(`De specificatie van de branch ontbreekt (Tijdstip = ${this.Tijdstip().Specificatie})`);
            }
            this.#project = new Project(this, this.Specificatie().Invoer.Project);
            this.#branch = new Branch(this, this.#project, this.Specificatie().Invoer.Branch);
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
    /** @type {Project} */
    #project;

    PasSpecificatieToe() {
        this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker voert de gegevens van het nieuwe project in.');
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Het project wordt aangemaakt.`);
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Voor het project wordt één nieuwe branch aangemaakt.`);
        this.#branch.PasSpecificatieToe();
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Maak een eerste momentopname voor de branch ${this.#branch.Code()}.`);
        this.VerwerkMomentopnameSpecificatie(this.#branch.Code());

        if (this.#volgtOpProject) {
            this.BlokkeerVerwijdering(this.#volgtOpProject.OntstaanIn());
        }
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
        this.#datumConsolidatie = undefined;
        this.#volgtOpProject = undefined;
        this.#volgtOpBranch = undefined;
        this.#beschikbareConsolidatie = []
        // Zoek beschikbare iwt-datums op
        let status = this.VoorgaandeConsolidatiestatus();
        if (status && status.Bepaald().length > 0) {
            let laatsteVoorDezeActiviteit;
            for (let beschikbaar of status.Bepaald()) {
                if (beschikbaar.IWTMoment().Datum().Vergelijk(this.Tijdstip()) <= 0) {
                    laatsteVoorDezeActiviteit = beschikbaar.IWTMoment().Datum();
                }
            }
            for (let beschikbaar of status.Bepaald()) {
                if (laatsteVoorDezeActiviteit && beschikbaar.IWTMoment().Datum().Vergelijk(laatsteVoorDezeActiviteit) < 0) {
                    continue;
                }
                if (beschikbaar.IsVoltooid()) {
                    this.#beschikbareConsolidatie.push(beschikbaar.IWTMoment().Datum());
                }
            }
        }
        if (this.#branch) {
            this.#isOnafhankelijk = this.#branch.Soort() == Branch.Soort_GeldendeRegelgeving;
            if (this.#isOnafhankelijk) {
                if (this.#branch.IWTDatum().HeeftWaarde()) {
                    for (let iwt of this.#beschikbareConsolidatie) {
                        if (iwt.Vergelijk(this.#branch.IWTDatum()) <= 0) {
                            this.#datumConsolidatie = iwt.Specificatie();
                        }
                    }
                    if (this.#datumConsolidatie === undefined) {
                        this.#branch.IWTDatum().SpecificatieWordt(undefined);
                    }
                }
            } else {
                this.#volgtOpBranch = this.#branch.VolgtOpBranch();
                this.#volgtOpProject = this.#volgtOpBranch.Project();
            }
        }
        if (this.#datumConsolidatie === undefined && this.#beschikbareConsolidatie.length === 1) {
            this.#datumConsolidatie = this.#beschikbareConsolidatie[0].Specificatie();
        }
    }
    /** @type {Branch} */
    #branch;
    /** @type {boolean} */
    #isOnafhankelijk;
    /** @type {number} */
    #datumConsolidatie;
    /** @type {Tijdstip[]} */
    #beschikbareConsolidatie;
    /** @type {Project} */
    #volgtOpProject;
    /** @type {Branch} */
    #volgtOpBranch;

    WeergaveInnerHtml() {
        let kanProjectSelecteren = this.IsInvoer() && this.KanVerwijderdWorden();
        let disabled = kanProjectSelecteren ? '' : ' disabled';
        let andereProjecten = Project.Projecten(this.Tijdstip()).filter((p) => p !== this.#project);

        let html = `${this.StartInnerHtml()}<p>Welk soort project moet aangemaakt worden?</p>
        <dl>
        <dt><input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('O')}"${this.#isOnafhankelijk === true ? ' checked' : ''}${disabled}> <label for="${this.ElementId('O')}">Onafhankelijk project</label></dt>
        <dd>Een nieuw project waarin regelgeving onafhankelijk van andere projecten aangepast wordt.`
        if (this.#beschikbareConsolidatie.length == 0) {
            html += ' In het project wordt aan nieuwe regelingen gewerkt.'
        } else {
            html += ` Het project begint met de regelgeving die geldig is op:<br><select id="${this.ElementId('I')}"${disabled}>`;
            if (this.#datumConsolidatie === undefined) {
                html += `<option value="" selected></option>`;
            }
            for (let iwt of this.#beschikbareConsolidatie) {
                html += `<option value="${iwt.Specificatie()}"${this.#datumConsolidatie === iwt.Specificatie() ? ' selected' : ''}>${iwt.DatumTijdHtml()}</option>`;
            }
            html += '</select>';
        }
        html += `</dd>
        <dt><input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('V')}"${this.#isOnafhankelijk === false ? ' checked' : ''}${andereProjecten.length === 0 ? ' disabled' : disabled}> <label for="${this.ElementId('V')}">Vervolgproject</label></dt>
        <dd>Een nieuw project dat voortbouwt op de regelgeving die in een ander (nog lopend) project wordt voorbereid`;
        if (andereProjecten.length === 0) {
            html += '. Op dit moment lopen er geen andere projecten.';
        } else {
            html += `, namelijk:<br><select id="${this.ElementId('P')}">`;
            if (!this.#volgtOpProject) {
                html += '<option value="" selected></option>';
            }
            for (let prj of andereProjecten) {
                html += `<option value="${prj.Code()}"${this.#volgtOpProject === prj ? ' selected' : ''}>${prj.Naam()}</option>`;
            }
            html += '</select>';
            if (this.#volgtOpProject) {
                let projectBranches = Branch.Branches(this.Tijdstip(), this.#volgtOpProject);
                if (projectBranches.length > 1) {
                    html += `<select id="${this.ElementId('B')}">`;
                    if (!this.#volgtOpBranch) {
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
            case 'I':
                this.#isOnafhankelijk = true;
                this.#datumConsolidatie = parseInt(elt.value);
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
                let elt = this.Element('I');
                if (elt && elt.value) {
                    this.#datumConsolidatie = parseInt(elt.value);
                }
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
            if (this.#isOnafhankelijk) {
                if (this.#beschikbareConsolidatie.length > 0 && !this.Element('I').value) {
                    return true;
                }
            }
            else if (!this.#volgtOpBranch) {
                return true;
            }
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            if (this.#branch) {
                this.#branch.Verwijder();
            }
            if (this.#isOnafhankelijk) {
                this.#branch = Branch.MaakBranch(this, this.#project, this.Specificatie().Invoer.Branch, Branch.Soort_GeldendeRegelgeving, this.#datumConsolidatie);
            } else {
                this.#branch = Branch.MaakBranch(this, this.#project, this.Specificatie().Invoer.Branch, Branch.Soort_VolgtOpAndereBranch, this.#volgtOpBranch);
            }
            this.Specificatie().Invoer.Branch = this.#branch.Code();
        }
        this.#InterpreteerInvoer();
    }
    //#endregion
}
//#endregion

//#region MaakBranch

//#endregion

//#region Download en Uitwisseling

class Activiteit_Download extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {any} specificatie - Specificatie van de activiteit
     * @param {boolean} isNieuw - Geeft aan of de activiteit gemaakt wordt om de specificatie in te voeren
     */
    constructor(specificatie, isNieuw) {
        super(specificatie, isNieuw);
        if (isNieuw) {
            this.#project = new Project(this);
            this.Specificatie().Invoer = {
                Project: this.#project.Code()
            };
        } else {
            if (!this.Specificatie().Invoer) {
                throw new Error(`De specificatie van de invoer voor nieuw project ontbreekt (Tijdstip = ${this.Tijdstip().Specificatie})`);
            }
            if (!this.Specificatie().Invoer.Project) {
                throw new Error(`De specificatie van het project ontbreekt (Tijdstip = ${this.Tijdstip().Specificatie})`);
            }
            if (!this.Specificatie().Invoer.Branch) {
                throw new Error(`De specificatie van de branch ontbreekt (Tijdstip = ${this.Tijdstip().Specificatie})`);
            }
            this.#project = new Project(this, this.Specificatie().Invoer.Project);
            this.#branch = new Branch(this, this.#project, this.Specificatie().Invoer.Branch);
        }
        this.#InterpreteerInvoer();
    }
    //#endregion

    //#region Implementatie van de activiteit
    Naam() {
        return "Download uit LVBB";
    }

    Project() {
        return this.#project;
    }
    /** @type {Project} */
    #project;

    PasSpecificatieToe() {
        this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker voert de gegevens van het nieuwe project in.');
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Het project wordt aangemaakt.`);
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Voor het project wordt één nieuwe branch aangemaakt.`);
        this.#branch.PasSpecificatieToe();
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Maak een eerste momentopname voor de branch ${this.#branch.Code()} met regelgeving gedownload uit de LVBB.`);
        this.VerwerkMomentopnameSpecificatie(this.#branch.Code());
        for (let mo of this.Momentopnamen()) {
            mo.UitgevoerdDoorAdviesbureauWordt(true);
            mo.MaakModulesVoorUitwisseling(Activiteit.Systeem_LVBB, (moduleNaam, stopXml) => this.VoegUitwisselingToe(Activiteit.Systeem_LVBB, Activiteit.Systeem_Adviesbureau, moduleNaam, stopXml));
        }
    }

    VerwijderGerelateerdeActiviteiten() {
        for (let activiteit of Activiteit.Activiteiten(undefined, this.#project)) {
            activiteit.Verwijder();
        }
    }
    //#endregion

    //#region Implementatie specificatie-element
    #InterpreteerInvoer() {
        this.#datumConsolidatie = undefined;
        this.#beschikbareConsolidatie = []
        // Zoek beschikbare iwt-datums op
        let status = this.VoorgaandeConsolidatiestatus();
        if (status && status.Bepaald().length > 0) {
            let laatsteVoorDezeActiviteit;
            for (let beschikbaar of status.Bepaald()) {
                if (beschikbaar.IWTMoment().Datum().Vergelijk(this.Tijdstip()) <= 0) {
                    laatsteVoorDezeActiviteit = beschikbaar.IWTMoment().Datum();
                }
            }
            for (let beschikbaar of status.Bepaald()) {
                if (laatsteVoorDezeActiviteit && beschikbaar.IWTMoment().Datum().Vergelijk(laatsteVoorDezeActiviteit) < 0) {
                    continue;
                }
                if (beschikbaar.IsVoltooid()) {
                    this.#beschikbareConsolidatie.push(beschikbaar.IWTMoment().Datum());
                }
            }
        }
        if (this.#branch) {
            if (this.#branch.IWTDatum().HeeftWaarde()) {
                for (let iwt of this.#beschikbareConsolidatie) {
                    if (iwt.Vergelijk(this.#branch.IWTDatum()) <= 0) {
                        this.#datumConsolidatie = iwt.Specificatie();
                    }
                }
                if (this.#datumConsolidatie === undefined) {
                    this.#branch.IWTDatum().SpecificatieWordt(undefined);
                }
            }
        }
        if (this.#datumConsolidatie === undefined && this.#beschikbareConsolidatie.length === 1) {
            this.#datumConsolidatie = this.#beschikbareConsolidatie[0].Specificatie();
        }
    }
    /** @type {Branch} */
    #branch;
    /** @type {number} */
    #datumConsolidatie;
    /** @type {Tijdstip[]} */
    #beschikbareConsolidatie;

    WeergaveInnerHtml() {
        let disabled = this.IsInvoer() && this.KanVerwijderdWorden() ? '' : ' disabled';

        let html = `${this.StartInnerHtml()}<p>Welke regelgeving wordt uit de LVBB gedownload?</p>
                    <p>De regelgeving die geldig is op: <select id="${this.ElementId('I')}"${disabled}>`;
        if (this.#datumConsolidatie === undefined) {
            html += `<option value="" selected></option>`;
        }
        for (let iwt of this.#beschikbareConsolidatie) {
            html += `<option value="${iwt.Specificatie()}"${this.#datumConsolidatie === iwt.Specificatie() ? ' selected' : ''}>${iwt.DatumTijdHtml()}</option>`;
        }
        html += `</select></p>
        ${this.#project.Html()}
        ${this.EindeInnerHtml()}`;

        return html;
    }

    OnInvoerChange(elt, idSuffix) {
        if (idSuffix === 'I') {
            if (elt.value) {
                this.#datumConsolidatie = parseInt(elt.value);
                this.VervangInnerHtml();
            }
        }
    }

    ValideerInvoer(accepteerInvoer) {
        if (!this.Element('I').value) {
            return true;
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            if (this.#branch) {
                this.#branch.Verwijder();
            }
            this.#datumConsolidatie = parseInt(this.Element('I').value);
            this.#branch = Branch.MaakBranch(this, this.#project, this.Specificatie().Invoer.Branch, Branch.Soort_GeldendeRegelgeving, this.#datumConsolidatie);
            this.Specificatie().Invoer.Branch = this.#branch.Code();
        }
        this.#InterpreteerInvoer();
    }
    //#endregion
}

class Activiteit_Uitwisseling extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {any} specificatie - Specificatie van de activiteit
     * @param {boolean} isNieuw - Geeft aan of de activiteit gemaakt wordt om de specificatie in te voeren
     * @param {boolean} doorAdviesbureau - Geeft aan of de activiteit door een adviesbureau wordt uitgevoerd
     */
    constructor(specificatie, isNieuw, doorAdviesbureau) {
        super(specificatie, isNieuw);
        this.#ontvangenDoorAdviesbureau = !doorAdviesbureau;
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
        return this.#ontvangenDoorAdviesbureau;
    }
    /** @type {boolean} */
    #ontvangenDoorAdviesbureau;

    PasSpecificatieToe() {
        if (this.#ontvangenDoorAdviesbureau) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker exporteert de regelgeving voor dit project als uitwisselpakket')
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker stuurt het uitwisselpakket naar het adviesbureau')
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'Een medewerker van het adviesbureau importeert het uitleverpakket in de eigen software')
        } else {
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker exporteert de aangepaste regelgeving als uitwisselpakket')
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker stuurt het uitwisselpakket naar het bevoegd gezag')
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'Een medewerker van het bevoegd gezag importeert het uitleverpakket in de eigen software')
        }

        this.VerwerkMomentopnameSpecificaties(false);
        if (this.Momentopnamen().length !== 1) {
            this.SpecificatieMelding(`Een uitwisseling kan alleen gedaan worden voor een project met één branch.`);
        }

        for (let mo of this.Momentopnamen()) {
            this.#ontvangenDoorAdviesbureau = !mo.UitgevoerdDoorAdviesbureau();
            mo.UitgevoerdDoorAdviesbureauWordt(this.#ontvangenDoorAdviesbureau);
        }

        for (let mo of this.Momentopnamen()) {
            mo.MaakModulesVoorUitwisseling(this.#ontvangenDoorAdviesbureau ? Activiteit.Systeem_BG : Activiteit.Systeem_Adviesbureau, (moduleNaam, stopXml) => this.VoegUitwisselingToe(
                this.#ontvangenDoorAdviesbureau ? Activiteit.Systeem_BG : Activiteit.Systeem_Adviesbureau,
                this.#ontvangenDoorAdviesbureau ? Activiteit.Systeem_Adviesbureau : Activiteit.Systeem_BG,
                moduleNaam, stopXml));
        }
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return `<h3>${this.Naam()}</h3>
                <p class="entry_detail">(Software van het ${this.#ontvangenDoorAdviesbureau ? 'bevoegd gezag' : 'adviesbureau'})</p>
                <p><input type="button" disabled value="Export project"></p>
                <p class="entry_detail">(Software van het ${!this.#ontvangenDoorAdviesbureau ? 'bevoegd gezag' : 'adviesbureau'})</p>
                <p><input type="button" disabled value="Import project"></p>
                ${this.EindeInnerHtml()}`;
    }
    //#endregion
}

//#endregion

//#region Wijzigen

class Activiteit_Wijzigen extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {any} specificatie - Specificatie van de activiteit
     * @param {boolean} isNieuw - Geeft aan of de activiteit gemaakt wordt om de specificatie in te voeren
     */
    constructor(specificatie, isNieuw) {
        super(specificatie, isNieuw);
        if (isNieuw) {
            this.VerwerkMomentopnameSpecificaties(false);
            this.#momentopnamen = this.Momentopnamen(true).filter(mo => !mo.IsTegelijkBeheerdEnVolgend());
        }
    }
    //#endregion

    //#region Implementatie van de activiteit
    Naam() {
        return "Wijzigen regelgeving";
    }

    PasSpecificatieToe() {
        this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker werkt verder aan het project.');
        this.VerwerkMomentopnameSpecificaties(true);
        this.#momentopnamen = this.Momentopnamen(true).filter(mo => !mo.IsTegelijkBeheerdEnVolgend());
    }
    //#endregion

    //#region Implementatie specificatie-element
    IsReadOnly() {
        for (let mo of this.#momentopnamen) {
            if (!mo.IsReadOnly()) {
                return false;
            }
        }
        return true;
    }
    /** @type {Momentopname[]} */
    #momentopnamen;

    WeergaveInnerHtml() {
        let html = this.StartInnerHtml();

        if (this.Momentopnamen().length > 1) {
            html += '<dl>';
            for (let mo of this.#momentopnamen) {
                let gewijzigd = mo.HeeftGewijzigdeInstrumentversie() || mo.HeeftGewijzigdeTijdstempels();
                html += `<dt><input type="checkbox" ${gewijzigd ? ' checked' : ''} disabled> ${mo.Branch().InteractieNaam()}</dt>`;
                if (gewijzigd) {
                    html += `<dd><div>${mo.Html()}</div></dd> `;
                }
            }
            html += '</dl>';
        } else {
            let heeftGewijzigd = false;
            for (let mo of this.#momentopnamen) {
                if (mo.HeeftGewijzigdeInstrumentversie() || mo.HeeftGewijzigdeTijdstempels()) {
                    html += mo.Html();
                    heeftGewijzigd = true;
                }
            }
            if (!heeftGewijzigd) {
                html += '(Geen regelgeving aangepast)';
            }
        }

        html += this.EindeInnerHtml();
        return html;
    }

    BeginInvoer() {
        this.#selecteerBranch = this.#momentopnamen.length > 1;
        this.#wijzigMomentopname = this.#selecteerBranch ? undefined : this.Momentopnamen()[0];
    }
    /** @type {boolean} */
    #selecteerBranch;
    /** @type {Momentopname} */
    #wijzigMomentopname;

    InvoerInnerHtml() {
        if (this.#selecteerBranch) {
            let html = `${this.StartInnerHtml()}
                        <p>Welke regelgeving moet gewijzigd worden?</p><ul>`;
            for (let mo of this.#momentopnamen) {
                html += `<li><input type="radio" name="${this.ElementId('R')}" id="${this.ElementId('B_' + mo.Branch().Code())}" value="${mo.Branch().Code()}"${mo.IsReadOnly() ? ' disabled' : ''}>${mo.Branch().InteractieNaam()}
                            ${mo.HeeftGewijzigdeInstrumentversie() || mo.HeeftGewijzigdeTijdstempels() ? ' (gewijzigd)' : ''}</li>`;
            }
            html += `</ul>
                    ${this.EindeInnerHtml()} `;
            return html;
        } else {
            if (this.#momentopnamen.length > 1) {
                this.VolgendeStapNodig();
            }

            let html = this.StartInnerHtml();
            if (this.Momentopnamen().length > 1) {
                html += `<h4>${this.#wijzigMomentopname.Branch().InteractieNaam()}</h4>`;
            }
            html += this.#wijzigMomentopname.Html();
            html += this.EindeInnerHtml();
            return html;
        }
    }

    OnInvoerClick(elt, idSuffix) {
        if (idSuffix.startsWith('B_') && elt.checked) {
            this.#wijzigMomentopname = this.Momentopname(elt.value);
            this.VolgendeStapNodig();
            this.SluitModal(true);
        }
    }

    ValideerInvoer(accepteerInvoer) {
        if (this.#selecteerBranch) {
            if (accepteerInvoer) {
                if (this.#wijzigMomentopname) {
                    this.#selecteerBranch = false;
                    this.VolgendeStapNodig();
                } else {
                    let heeftWijziging = false;
                    for (let mo of this.Momentopnamen()) {
                        if (mo.HeeftGewijzigdeInstrumentversie() || mo.HeeftGewijzigdeTijdstempels()) {
                            heeftWijziging = true;
                        }
                    }
                    if (!heeftWijziging) {
                        return true;
                    }
                }
            }
        }
        else if (this.#wijzigMomentopname) {
            if (accepteerInvoer && this.Momentopnamen().length == 1) {
                if (!this.#wijzigMomentopname.HeeftGewijzigdeInstrumentversie() && !this.#wijzigMomentopname.HeeftGewijzigdeTijdstempels()) {
                    return true;
                }
            }
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
     * @param {boolean} isNieuw - Geeft aan of de activiteit gemaakt wordt om de specificatie in te voeren
     */
    constructor(specificatie, isNieuw) {
        super(specificatie, isNieuw);
        if (isNieuw) {
            this.VerwerkMomentopnameSpecificaties(false);
        }
        for (let branch of Branch.Branches(this.Tijdstip(), this.Project())) {
            if (branch.Soort() === Branch.Soort_GeldendeRegelgeving) {
                this.#isRegulier = true;
                break;
            }
        }
        if (this.IsNieuw()) {
            this.#InterpreteerInvoer();
        } else {
            if (!this.Specificatie().Invoer) {
                throw new Error(`De specificatie van de invoer ontbreekt (Tijdstip = ${this.Tijdstip().Specificatie})`);
            }
            this.#datumConsolidatie = this.Specificatie().Invoer.IWTDatum;
        }
    }
    //#endregion

    //#region Implementatie van de activiteit
    PasSpecificatieToe() {
        this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker wil de regelgeving in het project bijwerken zodat de wijzigingen ten opzichte van een meer recente juridische uitgangssituatie beschreven kunnen worden.');
        this.VerwerkMomentopnameSpecificaties(true);
        this.#InterpreteerInvoer();
    }

    VerwerkMomentopnameSpecificatie(branchcode, specificatie, werkUitgangssituatieBij, ontvlochtenversies, vervlochtenversies) {
        super.VerwerkMomentopnameSpecificatie(branchcode, specificatie, this.IsNieuw() && !this.IsInvoer() ? false : this.#isRegulier && this.#datumConsolidatie ? this.#datumConsolidatie : true);
    }
    #isRegulier = false;
    /** @type {number} */
    #datumConsolidatie;
    //#endregion

    //#region Implementatie specificatie-element
    IsReadOnly() {
        for (let mo of this.Momentopnamen()) {
            if (!mo.IsReadOnly()) {
                return false;
            }
        }
        return true;
    }

    WeergaveInnerHtml() {
        let html = this.StartInnerHtml();

        if (this.#isRegulier) {
            html += `<p>Kies als nieuwe uitgangssituatie de regelgeving die geldig is op: <select id="${this.ElementId('I')}" disabled>`;
            if (this.#datumConsolidatie === undefined) {
                html += `<option value="" selected></option>`;
            }
            for (let iwt of this.#beschikbareConsolidatie) {
                html += `<option value="${iwt.Specificatie()}"${this.#datumConsolidatie === iwt.Specificatie() ? ' selected' : ''}>${iwt.DatumTijdHtml()}</option>`;
            }
            html += `</select></p>`;
        }

        if (this.Momentopnamen().length > 1) {
            html += '<dl>';
            for (let mo of this.Momentopnamen(true)) {
                let gewijzigd = mo.HeeftGewijzigdeInstrumentversie();
                html += `<dt><input type="checkbox" ${gewijzigd ? ' checked' : ''} disabled> ${mo.Branch().InteractieNaam()}</dt>`;
                if (gewijzigd) {
                    html += `<dd><div>${mo.Html()}</div></dd> `;
                }
            }
            html += '</dl>';
        } else {
            let heeftGewijzigd = false;
            for (let mo of this.Momentopnamen(true)) {
                if (mo.HeeftGewijzigdeInstrumentversie()) {
                    html += mo.Html();
                    heeftGewijzigd = true;
                }
            }
            if (!heeftGewijzigd) {
                html += '(Geen regelgeving aangepast)';
            }
        }

        html += this.EindeInnerHtml();
        return html;
    }

    BeginInvoer() {
        this.#vorigeDatumConsolidatie = this.#datumConsolidatie;
        this.#wijzigMomentopname = this.#isRegulier ? undefined : 0;
    }
    /** @type {number} */
    #vorigeDatumConsolidatie;
    #InterpreteerInvoer() {
        this.#beschikbareConsolidatie = [];

        if (this.#isRegulier) {
            let huidigeIWT;
            for (let mo of this.Momentopnamen()) {
                if (!mo.IsVaststellingsbesluitGepubliceerd() && mo.Branch().Soort() === Branch.Soort_GeldendeRegelgeving) {
                    huidigeIWT = mo.JuridischeUitgangssituatie().JuridischWerkendVanaf();
                    break;
                }
            }
            // Zoek beschikbare iwt-datums op
            let status = this.VoorgaandeConsolidatiestatus();
            if (status && status.Bepaald().length > 0) {
                let laatsteVoorDezeActiviteit;
                for (let beschikbaar of status.Bepaald()) {
                    if (beschikbaar.IWTMoment().Datum().Vergelijk(this.Tijdstip()) <= 0) {
                        laatsteVoorDezeActiviteit = beschikbaar.IWTMoment().Datum();
                    }
                }
                for (let beschikbaar of status.Bepaald()) {
                    if (laatsteVoorDezeActiviteit && beschikbaar.IWTMoment().Datum().Vergelijk(laatsteVoorDezeActiviteit) < 0) {
                        continue;
                    }
                    if (huidigeIWT && beschikbaar.IWTMoment().Datum().Specificatie() <= huidigeIWT) {
                        continue;
                    }
                    if (beschikbaar.IsVoltooid()) {
                        this.#beschikbareConsolidatie.push(beschikbaar.IWTMoment().Datum());
                    }
                }
            }
            if (!this.IsNieuw()) {
                let origineleWaarde = this.#datumConsolidatie;
                if (this.#datumConsolidatie && !this.#beschikbareConsolidatie.map(t => t.Specificatie()).includes(this.#datumConsolidatie)) {
                    this.#datumConsolidatie = undefined;
                    for (let beschikbaar of this.#beschikbareConsolidatie) {
                        if (beschikbaar <= origineleWaarde || this.#datumConsolidatie === undefined) {
                            this.#datumConsolidatie = beschikbaar;
                        }
                    }
                }
                if (this.#datumConsolidatie === undefined) {
                    this.SpecificatieMelding('De activiteit is gemaakt voor een oudere versie van het scenario. In dit scenario is er geen sprake van bijwerken van de regelgeving.');
                }
            }
        }
        if (this.#datumConsolidatie === undefined && this.#beschikbareConsolidatie.length === 1) {
            this.#datumConsolidatie = this.#beschikbareConsolidatie[0].Specificatie();
        }
    }
    /** @type {Tijdstip[]} */
    #beschikbareConsolidatie;
    /** @type {number} */
    #wijzigMomentopname;

    InvoerInnerHtml() {
        let html = this.StartInnerHtml();

        if (this.#isRegulier && this.#wijzigMomentopname === undefined) {
            this.VolgendeStapNodig();
            html += `<p>Kies als nieuwe uitgangssituatie de regelgeving die geldig is op: <select id="${this.ElementId('I')}">`;
            if (this.#datumConsolidatie === undefined) {
                html += `<option value="" selected></option>`;
            }
            for (let iwt of this.#beschikbareConsolidatie) {
                html += `<option value="${iwt.Specificatie()}"${this.#datumConsolidatie === iwt.Specificatie() ? ' selected' : ''}>${iwt.DatumTijdHtml()}</option>`;
            }
            html += `</select></p>`;

        } else {
            if (this.#wijzigMomentopname < this.Momentopnamen().length - 1) {
                this.VolgendeStapNodig();
            }
            let momentopname = this.Momentopnamen(true)[this.#wijzigMomentopname];
            if (this.Momentopnamen().length > 1) {
                html += `<h4>${momentopname.Branch().InteractieNaam()}</h4>`;
            }
            if (momentopname.BevatOplossingSamenloop()) {
                html += '<p>Er is sprake van samenloop. Geef aan hoe de verschillende versies samengevoegd moeten worden.</p>'
            } else {
                html += '<p>De software kon het bijwerken geautomatiseerd uitvoeren. Verifieer het resultaat.</p>'
            }
            html += momentopname.Html();
        }

        html += this.EindeInnerHtml();
        return html;
    }

    OnInvoerChange(elt, idSuffix) {
        if (idSuffix === 'I') {
            if (elt.value) {
                this.#datumConsolidatie = parseInt(elt.value);
                this.VervangInnerHtml();
            }
        }
    }

    ValideerInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            if (this.#isRegulier && this.#wijzigMomentopname === undefined) {
                if (this.#datumConsolidatie === undefined) {
                    return true;
                }
            }
        }
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            if (this.#isRegulier && this.#wijzigMomentopname === undefined) {
                this.Specificatie().Invoer = {
                    IWTDatum: this.#datumConsolidatie
                }
                this.#wijzigMomentopname = 0;
            } else {
                this.#wijzigMomentopname++;
            }
            // Maak de nieuwe bijgewerkte momentopnamen
            for (let mo of [...this.Momentopnamen()]) {
                mo.destructor();
            }
            this.VerwerkMomentopnameSpecificaties(true);
        } else if (this.#isRegulier) {
            this.Specificatie().Invoer = {
                IWTDatum: this.#vorigeDatumConsolidatie
            }
        }
    }
    //#endregion
}

//#endregion

//#region Ontwerp- en vaststellingsbesluit

class Activiteit_Besluit extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {any} specificatie - Specificatie van de activiteit
     * @param {boolean} isNieuw - Geeft aan of de activiteit gemaakt wordt om de specificatie in te voeren
     */
    constructor(specificatie, isNieuw) {
        super(specificatie, isNieuw);
        if (isNieuw) {
            this.#besluitNaam = this.SoortBesluit();
            this.VerwerkMomentopnameSpecificaties(false);
            this.#momentopnamenMetTijdstempels = this.Momentopnamen(true).filter(mo => !mo.IsTegelijkBeheerdEnVolgend() && mo.Branch().Soort() != Branch.Soort_OplossingSamenloop);
        } else {
            this.#besluitNaam = this.Specificatie().Besluitnaam ?? this.SoortBesluit();
        }
    }
    //#endregion

    //#region Eigenschappen
    /**
     * Geeft het soort besluit, beginnend met een hoofdletter en zonder lidwoord
     * @returns {string}
     */
    SoortBesluit() {
        return super.Naam();
    }

    /**
     * Geeft de bestpassende naam voor het besluit
     * @returns {string}
     */
    BesluitNaam() {
        return this.#besluitNaam;
    }
    /** @type {string} */
    #besluitNaam;

    /**
     * Geeft aan of het besluit gepubliceerd wordt
     * @returns {boolean}
     */
    LeidtTotPublicatie() {
        return this.SoortBesluit() !== MogelijkeActiviteit.SoortActiviteit_Conceptvaststellingsbesluit;
    }

    //#endregion

    //#region Implementatie van de Activiteit
    Naam() {
        switch (this.SoortBesluit()) {
            case MogelijkeActiviteit.SoortActiviteit_Conceptvaststellingsbesluit:
                return `Stel het ${this.BesluitNaam().toLowerCase()} op`;
            default:
                return `Publiceer het ${this.BesluitNaam().toLowerCase()}`;
        }
    }

    Publicatiebron() {
        if (this.SoortBesluit() !== MogelijkeActiviteit.SoortActiviteit_Conceptvaststellingsbesluit) {
            return 'het ' + this.BesluitNaam().toLowerCase();
        }
    }
    ConceptOfPublicatiebron() {
        return 'het ' + this.BesluitNaam().toLowerCase();
    }

    TijdstempelsVerplicht() {
        if (this.SoortBesluit() === MogelijkeActiviteit.SoortActiviteit_Vaststellingsbesluit && BGProcesSimulator.This().BevoegdGezag() === BGProcesSimulator.SoortBG_Gemeente) {
            return true;
        }
        return super.TijdstempelsVerplicht();
    }

    PasSpecificatieToe() {
        this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, `De medewerker stelt het ${this.BesluitNaam().toLowerCase()} op of rond het opstellen af.`);
        this.VerwerkMomentopnameSpecificaties(true);
        this.#momentopnamenMetTijdstempels = this.Momentopnamen(true).filter(mo => !mo.IsTegelijkBeheerdEnVolgend() && mo.Branch().Soort() != Branch.Soort_OplossingSamenloop);

        if (this.SoortBesluit() === MogelijkeActiviteit.SoortActiviteit_Vaststellingsbesluit) {
            // De inhoud van alle branches is nu vastgesteld.
            // Althans in deze applicatie, waarin het niet mogelijk is 
            // branches in aparte besluiten onder te brengen
            for (let mo of this.Momentopnamen()) {
                mo.IsOnderdeelVanPublicatieVastgesteldeInhoudWordt();
            }
        }

        if (this.Momentopnamen().filter(mo => mo.HeeftGewijzigdeTijdstempels()).length > 0) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker voert gegevens over de inwerkingtreding in.');
        }
        this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De software zoekt uit welke regelgeving in het besluit opgenomen moet worden.`);
        let versiesInPublicatie = [];
        for (let mo of this.Momentopnamen(true)) {
            versiesInPublicatie.push(...mo.Instrumentversies().filter((versie) => versie.Instrumentversie().IsOnderdeelVanLVBBPublicatie()));
        }
        versiesInPublicatie = versiesInPublicatie.sort((a, b) => a.Instrumentversie().WorkIdentificatie().localeCompare(b.Instrumentversie().WorkIdentificatie()));
        let mutatieMeldingen = [];
        for (let versie of versiesInPublicatie) {
            let mo = versie.Momentopname();
            let origineel = mo.JuridischeUitgangssituatie()?.Instrumentversie(versie.Instrumentversie().Instrument())?.Instrumentversie();
            let melding = `<tr><td>-</td><td colspan="2">${Instrument.SoortInstrumentNamen[versie.Instrumentversie().SoortInstrument()]} ${versie.Instrumentversie().ExpressionIdentificatie()}</td></tr><tr><td>&nbsp;</td>`;
            if (!origineel) {
                melding += '<td colspan="2"><i>Initiële versie</i>';
            } else if (!Instrument.SoortInstrument_Muteerbaar.includes(versie.Instrumentversie().SoortInstrument())) {
                melding += '<td colspan="2"><i>Integrale versie</i>';
            } else {
                melding += `<td><i>Wijziging ten opzichte van</i></td><td>${origineel.ExpressionIdentificatie()}`;
            }
            mutatieMeldingen.push(`${melding}</td></tr>`);
        }
        if (mutatieMeldingen.length > 0) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De software neemt in het ${this.BesluitNaam().toLowerCase()} op:
                        <table>
                        ${mutatieMeldingen.join('')}
                        </table>`);
        }
        if (this.LeidtTotPublicatie()) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, `Na uitvoerige controle geeft een medewerker het ${this.BesluitNaam().toLowerCase()} vrij voor publicatie`);
            this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, 'De software maakt het aanleverpakket voor het bronhouderkoppelvlak klaar');
            this.VoegModulesVoorMomentopnamenToe();
            this.UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, 'De software verstuurt het aanleverpakket aan het bronhouderkoppelvlak');
        }
    }
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        let html = this.StartInnerHtml();

        if (this.Soort().MomentopnameTijdstempels && this.#momentopnamenMetTijdstempels.length > 0) {
            let meerdereMO = this.Momentopnamen().length > 1;

            if (meerdereMO) {
                html += '<dl>';
            }
            for (let mo of this.#momentopnamenMetTijdstempels) {
                if (meerdereMO) {
                    html += `<dt>${mo.Branch().InteractieNaam()}</dt><dd>`;
                }
                html += mo.TijdstempelsHtml();
                if (meerdereMO) {
                    html += `</dd>`;
                }
            }
            if (meerdereMO) {
                html += '</dl>';
            }
        }

        if (this.IsOfficielePublicatie()) {
            html += `<p><input type="button" disabled value="Publiceer het ${this.BesluitNaam().toLowerCase()}"></p>`;
        }

        html += this.EindeInnerHtml();
        return html;
    }
    #momentopnamenMetTijdstempels;

    InvoerInnerHtml() {
        let html = this.StartInnerHtml();

        if (this.Soort().MomentopnameTijdstempels && this.#momentopnamenMetTijdstempels.length > 0) {
            let meerdereMO = this.Momentopnamen().length > 1;

            if (meerdereMO) {
                html += '<dl>';
            }
            for (let mo of this.#momentopnamenMetTijdstempels) {
                if (meerdereMO) {
                    html += `<dt>${mo.Branch().InteractieNaam()}</dt><dd>`;
                }
                html += mo.TijdstempelsHtml();
                if (meerdereMO) {
                    html += `</dd>`;
                }
            }
            if (meerdereMO) {
                html += '</dl>';
            }
        }

        html += this.EindeInnerHtml();
        return html;
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            if (this.SoortBesluit() === MogelijkeActiviteit.SoortActiviteit_Vaststellingsbesluit) {
                // Voor weergave: kan de naam van het besluit accurater?
                // Kijk of er al eerder een vaststellingsbesluit is geweest
                let eerderBesluit;
                for (let activiteit of Activiteit.Activiteiten(this.Tijdstip(), this.Project())) {
                    if (activiteit != this && activiteit instanceof Activiteit_Besluit && activiteit.SoortBesluit() === MogelijkeActiviteit.SoortActiviteit_Vaststellingsbesluit) {
                        eerderBesluit = activiteit;
                    }
                }
                if (eerderBesluit) {
                    this.#besluitNaam = 'Vervolgbesluit';
                    for (let mo of this.#momentopnamenMetTijdstempels) {
                        if (mo.JuridischWerkendVanaf().HeeftWaarde() && mo.IsInwerkingtredingGewijzigd()) {
                            this.#besluitNaam = 'Inwerkingtredingsbesluit';
                            break;
                        }
                    }
                }
                this.Specificatie().Besluitnaam = this.#besluitNaam;
            }
        }
    }
    //#endregion
}

//#endregion

//#region Voltooien van consolidatie / oplossen samenloop
class Activiteit_VoltooiConsolidatie extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {any} specificatie - Specificatie van de activiteit
     * @param {boolean} isNieuw - Geeft aan of de activiteit gemaakt wordt om de specificatie in te voeren
     */
    constructor(specificatie, isNieuw) {
        super(specificatie, isNieuw);
        this.#viaRevisie = isNieuw;
        this.#teVoltooien = Activiteit_VoltooiConsolidatie.#TeVoltooien(this.Tijdstip(), Activiteit.Activiteiten(this.Tijdstip(), this.Project()).filter(a => a !== this));
        this.#mergeBranches = this.#teVoltooien.IWTMoment().Inwerkingtredingbranchcodes().map(bc => Branch.Branch(bc)).sort((a, b) => Branch.Vergelijk(a, b));
        // Bepaal de branch waarvoor de wijziging wordt aangemaakt. Als er meerdere branches in een project zitten, dan in afnemend logische volgorde:
        for (let soort of [Branch.Soort_Consolidatie, Branch.Soort_OplossingSamenloop, Branch.Soort_VolgtOpAndereBranch, Branch.Soort_GeldendeRegelgeving]) {
            for (let branch of this.#mergeBranches) {
                if (branch.Project() === this.Project() && branch.Soort() === soort) {
                    if (branch.TreedtConditioneelInWerkingMet()) {
                        if (branch.TreedtConditioneelInWerkingMet().filter(b => !this.#teVoltooien.IWTMoment().LaatsteBijdrage(b.Code())).length > 0) {
                            // Niet alle branches zijn al in werking
                            continue;
                        }
                    }
                    // Dit is een goede kandidaat
                    this.#wijzigBranch = branch;
                    break;
                }
            }
            if (this.#wijzigBranch) {
                break;
            }
        }
        if (isNieuw) {
            this.VerwerkMomentopnameSpecificaties()
        }
    }
    /**
     * Geeft aan of het consolideren van toepassing is
     * @param {Tijdstip} tijdstip - Tijdstip waarop de consolidatie voltooid gaat worden
     * @param {Activiteit[]} activiteiten Activiteiten behorend bij het project
     * @returns {boolean} - Geeft aan of de activiteit toch niet uitgevoerd kan worden
     */
    static KanTochNiet(tijdstip, activiteiten) {
        return !Boolean(Activiteit_VoltooiConsolidatie.#TeVoltooien(tijdstip, activiteiten));
    }
    /**
     * Geeft de status van de eerstvolgende te voltooien consolidatie
     * @param {Tijdstip} tijdstip - Tijdstip waarop de consolidatie voltooid gaat worden
     * @param {Activiteit[]} activiteiten - Activiteiten behorend bij het project
     * @returns {IWTMomentConsolidatiestatus}
     */
    static #TeVoltooien(tijdstip, activiteiten) {
        let project = activiteiten[activiteiten.length - 1].Project();
        let teVoltooien;
        for (let bepaald of activiteiten[activiteiten.length - 1].Consolidatiestatus().Bepaald()) {
            if (bepaald.IsBepaald() && !bepaald.IsVoltooid()) {
                if (teVoltooien !== undefined && bepaald.IWTMoment().Datum().Dag() >= tijdstip.Dag()) {
                    break;
                }
                if (bepaald.IWTMoment().Inwerkingtredingbranchcodes().map(bc => Branch.Branch(bc).Project()).includes(project)) {
                    teVoltooien = bepaald;
                }
            }
        }
        return teVoltooien;
    }
    //#endregion

    //#region Implementatie van de activiteit
    Publicatiebron() {
        return this.#viaRevisie ? "de revisie" : undefined;
    }
    /** @type {boolean} */
    #viaRevisie;

    PasSpecificatieToe() {
        this.#viaRevisie = !Boolean(this.Specificatie().Branch);
        if (this.#mergeBranches.length > 1) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, `De medewerker kiest ervoor de samenloop op te lossen voor branch ${this.#wijzigBranch.Code()}.`);
        }
        if (this.#viaRevisie) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker constateert dat de samen te voegen wijzigingen inderdaad juridisch onafhankelijk zijn van elkaar.');
        } else {
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker constateert dat de samen te voegen wijzigingen niet juridisch onafhankelijk zijn van elkaar. De oplossing van de samenloop zal in een nieuw vaststellingsbesluit vastgelegd moeten worden.');
        }
        this.VerwerkMomentopnameSpecificaties();

        this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, 'De medewerker lost de samenloop op.');
        if (this.#mergeBranches.length > 1) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De software neemt de inhoud van de branch ${this.#wijzigBranch.Code()}
            over in de andere branch${this.#mergeBranches.length > 2 ? 'es' : ''} die tegelijk in werking ${this.#mergeBranches.length > 2 ? 'treden' : 'treedt'}: ${this.#mergeBranches.filter(b => b != this.#wijzigBranch).map(b => b.Code()).join(', ')}`);
        }
        let nietMeerTegelijk = this.Momentopnamen(true).filter(mo => mo.Branch() != this.#wijzigBranch && this.#mergeBranches.indexOf(mo.Branch()) < 0);
        if (nietMeerTegelijk.length > 0) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `Deze branch${this.#mergeBranches.length > 1 ? 'es worden' : ' wordt'} niet meer tegelijk beheerd met de branch${nietMeerTegelijk.length > 1 ? 'es' : ''} ${nietMeerTegelijk.map(b => b.Branch().Code()).join(', ')}`);
        }

        let versiesInRevisie = this.Momentopnamen()[0].Instrumentversies().filter((versie) => versie.Instrumentversie().IsOnderdeelVanLVBBPublicatie());
        versiesInRevisie = versiesInRevisie.sort((a, b) => a.Instrumentversie().WorkIdentificatie().localeCompare(b.Instrumentversie().WorkIdentificatie()));
        let mutatieMeldingen = [];
        for (let versie of versiesInRevisie) {
            let mo = versie.Momentopname();
            let origineel = mo.JuridischeUitgangssituatie()?.Instrumentversie(versie.Instrumentversie().Instrument())?.Instrumentversie();
            let melding = `<tr><td>-</td><td colspan="2">${Instrument.SoortInstrumentNamen[versie.Instrumentversie().SoortInstrument()]} ${versie.Instrumentversie().ExpressionIdentificatie()}</td></tr><tr><td>&nbsp;</td>`;
            if (!origineel) {
                melding += '<td colspan="2"><i>Initiële versie</i>';
            } else if (!Instrument.SoortInstrument_Muteerbaar.includes(versie.Instrumentversie().SoortInstrument())) {
                melding += '<td colspan="2"><i>Integrale versie</i>';
            } else {
                melding += `<td><i>Wijziging ten opzichte van</i></td><td>${origineel.ExpressionIdentificatie()}`;
            }
            mutatieMeldingen.push(`${melding}</td></tr>`);
        }
        if (mutatieMeldingen.length > 0) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De software neemt in de revisie op:
                        <table>
                        ${mutatieMeldingen.join('')}
                        </table>`);
        }
        if (this.#viaRevisie) {
            this.UitvoeringMelding(Activiteit.Onderwerp_Invoer, `Na uitvoerige controle geeft een medewerker de revisie vrij voor doorgifte aan de LVBB`);
            this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, 'De software maakt het aanleverpakket voor het bronhouderkoppelvlak klaar');
            this.VoegModulesVoorMomentopnamenToe();
            this.UitvoeringMelding(Activiteit.Onderwerp_Uitwisseling, 'De software verstuurt het aanleverpakket aan het bronhouderkoppelvlak');
        }
    }

    VerwerkMomentopnameSpecificaties() {
        // Bij een revisie is this.#wijzigBranch de branch waarop de samenloop opgelost wordt
        let overigeBranches = this.#teVoltooien.IWTMoment().Inwerkingtredingbranchcodes().filter(bc => bc !== this.#wijzigBranch.Code());
        let teVervlechten = [];
        if (this.#teVoltooien.HeeftSamenloopBijIWT()) {
            teVervlechten.push(...overigeBranches.map(bc => this.#teVoltooien.IWTMoment().LaatsteBijdrage(bc)));
        }
        teVervlechten.push(...this.#teVoltooien.TeVervlechten());

        // Maak de momentopname waarop de invoer geschiedt
        if (!this.#viaRevisie) {
            // De specificatie bevat niet de gegevens van het type branch, maak die opnieuw
            overigeBranches = [this.#wijzigBranch.Code(), ...overigeBranches];
            teVervlechten = [this.#teVoltooien.IWTMoment().LaatsteBijdrage(this.#wijzigBranch.Code()), ...teVervlechten];
            let spec = Object.assign({}, this.Specificatie()[this.Specificatie().Branch]);
            let branch = Branch.MaakBranch(this, this.Project(), this.Specificatie().Branch, Branch.Soort_Consolidatie, teVervlechten.map(mo => mo.Branch()));
            this.Specificatie()[this.Specificatie().Branch] = Object.assign(spec, branch.Specificatie());
            branch.destructor();

            // Maak nu de branch aan
            this.#wijzigBranch = new Branch(this, this.Project(), this.Specificatie().Branch);
            this.UitvoeringMelding(Activiteit.Onderwerp_Verwerking_Invoer, `De software maakt een nieuwe branch ${this.#wijzigBranch.Code()} aan om de oplossing van de samenloop te beheren`);
            this.#wijzigBranch.PasSpecificatieToe();
        }
        let bijgewerkt = super.VerwerkMomentopnameSpecificatie(this.#wijzigBranch.Code(), this.Specificatie(), false, this.#teVoltooien.TeOntvlechten(), teVervlechten);

        /**
         * Verzamel alle branches die tot nu toe tegelijk beheerd werden 
         * @type {Momentopname[]} */
        let werdenTegelijkBeheerd = [];
        if (bijgewerkt.TegelijkBeheerd()) {
            werdenTegelijkBeheerd.push(...bijgewerkt.TegelijkBeheerd().map(b => b.Code()));
        }
        /**
         * Verzamel alle branches die vanaf nu toe tegelijk beheerd werden
         * @type {Momentopname[]} */
        let wordenTegelijkBeheerd = [bijgewerkt];
        if (overigeBranches.length > 0) {
            // Maak de momentopnamen voor de overige IWT-branches
            for (let branchcode of overigeBranches) {
                let momentopname = super.VerwerkMomentopnameSpecificatie(branchcode, {});
                wordenTegelijkBeheerd.push(momentopname);
                if (momentopname.TegelijkBeheerd()) {
                    werdenTegelijkBeheerd.push(...momentopname.TegelijkBeheerd().map(b => b.Code()));
                }
            }
        }
        for (let momentopname of wordenTegelijkBeheerd) {
            momentopname.BeheerTegelijk(wordenTegelijkBeheerd);
        }
        if (this.#viaRevisie) {
            bijgewerkt.IsOnderdeelVanPublicatieVastgesteldeInhoudWordt();
        }

        // Maak de momentopnamen die niet meer tegelijk beheerd worden
        werdenTegelijkBeheerd = werdenTegelijkBeheerd.filter((bc, idx, a) => !this.#teVoltooien.IWTMoment().Inwerkingtredingbranchcodes().includes(bc) && a.indexOf(bc) === idx);
        if (werdenTegelijkBeheerd.length > 0) {
            for (let branchcode of werdenTegelijkBeheerd) {
                let momentopname = super.VerwerkMomentopnameSpecificatie(branchcode, {});
                momentopname.BeheerNietTegelijkMet(this.#teVoltooien.IWTMoment().Inwerkingtredingbranchcodes());
            }
        }
    }
    /** @type {Branch[]} */
    #mergeBranches = [];
    /** @type {Branch} */
    #wijzigBranch;
    /** @type {IWTMomentConsolidatiestatus} */
    #teVoltooien;
    //#endregion

    //#region Implementatie specificatie-element
    IsReadOnly() {
        for (let mo of this.Momentopnamen()) {
            if (!mo.IsReadOnly()) {
                return false;
            }
        }
        return true;
    }

    WeergaveInnerHtml() {
        let html = `${this.StartInnerHtml()}
                    <p>Los in ${this.#wijzigBranch.InteractieNaam()} de samenloop op`;

        if (this.#teVoltooien.HeeftSamenloopBijIWT()) {
            html += ` van de regelgeving die tegelijk in werking treedt: ${this.#mergeBranches.map(b => b.InteractieNaam()).join(', ')}`;
            if (this.#teVoltooien.TeVervlechten().length > 0) {
                html += `. Neem tevens de wijzigingen over van ${this.#teVoltooien.TeVervlechten().map(mo => mo.Branch().InteractieNaam())}`;
                if (this.#teVoltooien.TeOntvlechten().length > 0) {
                    html += ` en verwijder de wijzigingen uit ${this.#teVoltooien.TeOntvlechten().map(mo => mo.Branch().InteractieNaam())}`
                }
            } else if (this.#teVoltooien.TeOntvlechten().length > 0) {
                html += ` Verwijder tevens de wijzigingen uit ${this.#teVoltooien.TeOntvlechten().map(mo => mo.Branch().InteractieNaam())}`
            }
        }
        else {
            if (this.#teVoltooien.TeVervlechten().length > 0) {
                html += ` door de wijzigingen over te nemen van ${this.#teVoltooien.TeVervlechten().map(mo => mo.Branch().InteractieNaam())}`;
                if (this.#teVoltooien.TeOntvlechten().length > 0) {
                    html += ` en de wijzigingen uit ${this.#teVoltooien.TeOntvlechten().map(mo => mo.Branch().InteractieNaam())} te verwijderen`
                }
            } else if (this.#teVoltooien.TeOntvlechten().length > 0) {
                html += ` door de wijzigingen uit ${this.#teVoltooien.TeOntvlechten().map(mo => mo.Branch().InteractieNaam())} te verwijderen`
            }
        }

        html += `.</p>
                 <p>
                   <input type="checkbox" id="${this.ElementId('R')}"${this.#viaRevisie ? ' checked' : ''}${this.IsInvoer() ? '' : ' disabled'}>
                   <label for="${this.ElementId('R')}">De onderliggende wijzigingen zijn juridisch onafhankelijk; oplossing van de samenloop vereist geen nieuw besluit.</label>
                 </p>
                 ${this.Momentopnamen()[0].Html()}
                 ${this.EindeInnerHtml()}`;
        return html;
    }

    EindeInvoer(accepteerInvoer) {
        if (accepteerInvoer) {
            let wasRevisie = this.#viaRevisie;
            this.#viaRevisie = this.Element('R').checked;
            if (this.#viaRevisie !== wasRevisie) {
                let momentopnameSpec = this.#wijzigBranch.Specificatie();
                this.Specificatie()[this.#wijzigBranch.Code()] = undefined;
                let branch;
                if (this.#viaRevisie) {
                    // Het was een aparte branch; nu niet meer
                    branch = this.#wijzigBranch.VolgtOpBranch();
                    momentopnameSpec.Soort = momentopnameSpec.Branches = undefined;
                } else {
                    // Het was een gewone branch, wordt een aparte branch
                    branch = Branch.MaakBranch(this, this.Project(), undefined, Branch.Soort_Consolidatie, [this.#wijzigBranch, this.#mergeBranches.filter(b => b != this.#wijzigBranch)])
                }
                this.Specificatie()[branch.Code()] = momentopnameSpec;
                // De activiteit wordt opnieuw vanuit de specificatie ingelezen, dan worden de overige properties goed gezet
            }
        }
    }
    //#endregion
}

//#endregion

//#region Activiteit met alleen beschrijving
class Activiteit_Overig extends Activiteit {
    //#region Initialisatie
    /**
     * Maak de activiteit aan vanuit de specificatie
     * @param {any} specificatie - Specificatie van de activiteit
     * @param {boolean} isNieuw - Geeft aan of de activiteit gemaakt wordt om de specificatie in te voeren
     */
    constructor(specificatie, isNieuw) {
        super(specificatie, isNieuw);
        this.#naam = new Naam(this.Specificatie(), this, (n) => n);
    }
    //#endregion

    //#region Implementatie van de activiteit
    Naam() {
        return this.#naam.Specificatie() ?? '...';
    }
    /** @type {string} */
    #naam;
    //#endregion

    //#region Implementatie specificatie-element
    WeergaveInnerHtml() {
        return `${this.StartInnerHtml()}
                ${this.Beschrijving().Html()}
                ${this.EindeInnerHtml()}`;
    }

    InvoerInnerHtml() {
        return `${this.StartInnerHtml()}
                ${this.#naam.Html()}
                ${this.EindeInnerHtml()}`;
    }
    //#endregion
}

//#endregion

//#endregion
