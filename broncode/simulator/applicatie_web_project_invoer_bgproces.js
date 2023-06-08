/*==============================================================================
 *
 * BGProcesGenerator
 * 
 *------------------------------------------------------------------------------
 *
 * Generator voor de bg_proces.json specificatie voor de simulator.
 * BGProcesGenerator bevat de generieke functionaliteit
 * 
 =============================================================================*/
class BGProcesGenerator {
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
        this.#spec_invoer.innerHTML = '<h3>' + titel + '</h3>';
        this.#data.BGCode = bgcode;
    }
    #spec_invoer = undefined;
    #data = { // Data voor het scenario
        BevoegdGezag: '',
        BGCode: '',
        Beschrijving: '',
        Uitgangssituatie: {},
        Projecten: {},
        Overig: [],
    };

    /**
     * Lees een eerder aangemaakte specificatie
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

        let regelingen = {};
        let projectBranches = {};
        function copyMomentopname(target, src, extraProps) {
            if (src === undefined) {
                return;
            }
            for (let instr in src) {
                if (extraProps.includes(instr)) {
                    target[instr] = src[instr];
                    continue;
                }
                for (let prefix of [BGProcesGenerator.SoortInstrument_Regeling, BGProcesGenerator.SoortInstrument_GIO, BGProcesGenerator.SoortInstrument_PDF]) {
                    if (instr.startsWith(prefix + "_")) {
                        if (!BGProcesGenerator.#instrumenten.includes(instr)) {
                            BGProcesGenerator.#instrumenten.push(instr);
                        }
                        if (src[instr] === null || typeof src[instr] === "boolean") {
                            target[instr] = src[instr];
                        } else {
                            target[instr] = {
                                _json: true
                            };
                            if (prefix == BGProcesGenerator.SoortInstrument_Regeling) {
                                regelingen[instr] = true;
                            } else {
                                BGProcesGenerator.Opties.InformatieObjecten = true;
                            }
                            for (let annotatie of BGProcesGenerator.ToegestaneAnnotaties[prefix]) {
                                if (annotatie in src[instr]) {
                                    target[instr][annotatie] = src[instr];
                                    if (annotatie == BGProcesGenerator.SoortAnnotatie_NonSTOP) {
                                        BGProcesGenerator.Opties.NonStopAnnotaties = true;
                                    } else {
                                        BGProcesGenerator.Opties.Annotaties = true;
                                    }
                                }
                            }
                            break;
                        }
                    }
                }
            }
        }
        function copyActiviteiten(project, target, src) {
            for (let activiteit of src) {
                if (activiteit.Soort === undefined) {
                    continue;
                }
                let spec = BGProcesGenerator.SoortActiviteit[activiteit.Soort];
                if (spec === undefined) {
                    continue;
                }
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
                            throw new Error("Branches moeten specifiek voor een project (of overig) zijn: " + prop);
                        }
                        targetActiviteit[prop] = {}
                        copyMomentopname(targetActiviteit[prop], activiteit[prop], spec.MomentopnameProps);
                    }
                }
            }
        }

        copyMomentopname(bgpg.#data.Uitgangssituatie, data.Uitgangssituatie, []);
        if (data.Projecten !== undefined) {
            for (let project in data.Projecten) {
                bgpg.#data.Projecten[project] = []
                copyActiviteiten(project, bgpg.#data.Projecten[project], data.Projecten[project]);
            }
        }
        if (data.Overig !== undefined) {
            copyActiviteiten(null, bgpg.#data.Overig, data.Overig);
        }

        if (Object.keys(regelingen).length > 1) {
            BGProcesGenerator.Opties.MeerdereRegelingen = true;
        }

        return bgpg;
    }

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
     * Presenteren van de invoermogelijkheden
     *
     -------------------------------------------------------------------------*/
    /**
     * Start met de invoer van de specificatie
     * @param {HTMLElement} elt_data - element om JSON specificatie in op te slaan
     * @param {HTMLElement} startknop - element waarin de start knop staat van de simulator
     * @param {HTMLAnchorElement} downloadLink - element met de downloadlink voor de specificatie
     */
    Start(elt_data, startknop, downloadLink) {
        if (!BGProcesGenerator.Opties.MeerdereRegelingen && BGProcesGenerator.Instrumentnamen(BGProcesGenerator.SoortInstrument_Regeling).length == 0) {
            BGProcesGenerator.RegistreerInstrumentnaam(BGProcesGenerator.VrijeInstrumentnaam(BGProcesGenerator.SoortInstrument_Regeling));
        }

        InvoerManager.AddEventListener(this.#spec_invoer)

        new Specificatie(this.#data, elt_data, startknop, downloadLink);

        this.#spec_invoer.insertAdjacentHTML('beforeend', `<p>
<b>Beschrijving van het scenario</b><br/>
Geef een korte beschrijving van het scenario waarvoor deze specificatie is opgesteld (optioneel)<br/>
${new Beschrijving(this.#data).VolledigeHtml()}
</p>
<div id="_bgpg_modal" class="modal">
  <div class="modal-content">
    <span class="modal-close"><span id="_bgpg_modal_ok">&#x2714;</span> <span id="_bgpg_modal_cancel">&#x2716;</span></span>
    <p id="_bgpg_modal_content"></p>
  </div>
</div>
<p>
<b>Uitgangssituatie</b> per ${new Startdatum(this.#data).VolledigeHtml()}<br/>
${new Momentopname(this.#data, 'Uitgangssituatie', false).VolledigeHtml()}
</p>

<b>Activiteiten in projecten</b>
<table id="_bgpg_projecten">
  <tr><td>Project</td><td><td>+</td></tr>
  <tr><td>Doel</td></tr>
  <tr><td>+</td></tr>
</table>

<b>Overige activiteiten</b>
<table id="_bgpg_overig">
  <tr><td>Tijdstip</td><td>Gebeurtenis</td><td>Details</td></tr>
  <tr><td>${new Tijdstip({}, 'Tijdstip', 1).VolledigeHtml()}</td></tr>
</table>

<b>Status consolidatie</b>
<table id="_bgpg_consolidatie">
  <tr><td>Juridisch werkend vanaf</td></tr>
</table>
`);
        document.getElementById("_bgpg_modal_ok").addEventListener('click', () => InvoerManager.SluitModal(true));
        document.getElementById("_bgpg_modal_cancel").addEventListener('click', () => InvoerManager.SluitModal(false));
    }

    /*--------------------------------------------------------------------------
     *
     * Opties
     *
     -------------------------------------------------------------------------*/
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

    /*--------------------------------------------------------------------------
     *
     * Instrumenten en annotaties
     *
     -------------------------------------------------------------------------*/
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

    static SoortAnnotatie_Citeertitel = 'Metadata_Citeertitel';
    static SoortAnnotatie_Toelichtingrelaties = 'Toelichtingrelaties';
    static SoortAnnotatie_Symbolisatie = 'Symbolisatie';
    static SoortAnnotatie_Gebiedsmarkering = 'Gebiedsmarkering';
    static SoortAnnotatie_NonSTOP = 'NonSTOP';
    static ToegestaneAnnotaties = {
        b: [
            BGProcesGenerator.SoortAnnotatie_Citeertitel,
            BGProcesGenerator.SoortAnnotatie_Gebiedsmarkering
        ],
        reg: [
            BGProcesGenerator.SoortAnnotatie_Citeertitel,
            BGProcesGenerator.SoortAnnotatie_Toelichtingrelaties,
            BGProcesGenerator.SoortAnnotatie_NonSTOP
        ],
        gio: [
            BGProcesGenerator.SoortAnnotatie_Citeertitel,
            BGProcesGenerator.SoortAnnotatie_Symbolisatie
        ],
        pdf: [
            BGProcesGenerator.SoortAnnotatie_Citeertitel
        ]
    };

    /**
     * Geef een (gesorteerde) lijst met bekende instrumentnamen
     */
    static Instrumentnamen(soortInstrument) {
        if (soortInstrument === undefined) {
            return BGProcesGenerator.#instrumenten;
        } else {
            return BGProcesGenerator.#instrumenten.filter(i => i.startsWith(soortInstrument + '_'));
        }
    }
    static #instrumenten = [];

    static RegistreerInstrumentnaam(instrumentnaam) {
        BGProcesGenerator.#instrumenten.push(instrumentnaam);
        BGProcesGenerator.#instrumenten.sort();
    }

    static VrijeInstrumentnaam(soortInstrument) {
        return this.VrijeNaamIndex(BGProcesGenerator.#instrumenten, soortInstrument + '_')
    }

    /**
    * Vind een vrije naamindex voor een nieuw object
    * @param {string[]} alBekend - lijst met namen van de al bekende objecten.
    * @param {string} prefix - Optioneel: prefix van het object
    * @returns De vrije naam
    */
    static VrijeNaamIndex(alBekend, prefix) {
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

    /*--------------------------------------------------------------------------
     *
     * Projecten en branches
     *
     -------------------------------------------------------------------------*/

    static Projecten() {

    }

    static SoortActiviteit = {
        'Maak branch': {
            IsWijziging: true,
            Props: [],
            MomentopnameProps: ['Soort', 'Branch', 'Branches']
        },
        'Download': {
            IsWijziging: false,
            Props: ['Branch']
        },
        'Wijziging': {
            IsWijziging: true,
            Props: [],
            MomentopnameProps: []
        },
        'Uitwisseling': {
            IsWijziging: false,
            Props: []
        },
        'Bijwerken uitgangssituatie': {
            IsWijziging: true,
            Props: [],
            MomentopnameProps: []
        },
        'Ontwerpbesluit': {
            IsWijziging: true,
            Props: [],
            MomentopnameProps: []
        },
        'Vaststellingsbesluit': {
            IsWijziging: true,
            Props: [],
            MomentopnameProps: ['JuridischWerkendVanaf', 'GeldigVanaf']
        }
    };


}

/*==============================================================================
 *
 * GemeenteProcesGenerator
 * 
 *------------------------------------------------------------------------------
 *
 * Invulling van de procesgenerator voor processtappen die gebruikelijk zijn 
 * voor een gemeente.
 * 
 =============================================================================*/
class GemeenteProcesGenerator extends BGProcesGenerator {
    constructor(elt_invoer) {
        super(elt_invoer, 'gm9999', 'Invoer voor een gemeente');
    }
}

/*==============================================================================
 *
 * RijkProcesGenerator
 * 
 *------------------------------------------------------------------------------
 *
 * Invulling van de procesgenerator voor processtappen die gebruikelijk zijn 
 * voor de rijksoverheid.
 * 
 =============================================================================*/
class RijkProcesGenerator extends BGProcesGenerator {
    constructor(elt_invoer) {
        super(elt_invoer, 'mnre9999', 'Invoer voor de rijksoverheid');
    }
}

/*==============================================================================
 *
 * Nu volgen een aantal basisklassen voor de manipulatie van de specificatie
 * en het ondersteunen van de invoer. Deze moeten hier staan omdat javascript 
 * geen forward declaration van klassen kent.
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
 *
 * Een Invoermanager maakt HTML invoervelden, handelt UI events af en zorgen dat
 * een kopie van de specificatie bijgewerkt wordt. 
 * 
 *----------------------------------------------------------------------------*/
class InvoerManager {
    /**
     * Maak een invoermanager aan
     * @param {InvoerManager} superInvoer - InvoerManager waar dit een sub-invoermanager van is
     */
    constructor() {
        this.#index = InvoerManager.#invoer_manager_idx++;
        InvoerManager.#invoer_managers[this.#index] = this;
    }

    destructor() {
        if (this.#index !== undefined) {
            delete InvoerManager.#invoer_managers.p[this.#index];
            this.#index = undefined;
        }
    }

    /**
     * Aangeroepen om de HTML voor de invoer te maken om in een pagina te zetten.
     */
    VolledigeHtml() {
        return this.MaakVolledigeHtml('span');
    }

    /**
     * Aangeroepen om de HTML voor de invoer te maken. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} container - Container element waarin de HTML geplaatst moet worden
     */
    Html() {
    }

    /**
     * Aangeroepen als er iets in de invoer is gewijzigd. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is; weggelaten als kind-invoermanager gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnChange(elt, idSuffix) {
    }

    /**
     * Aangeroepen als er op een element geklikt wordt. Wordt geïmplementeerd in afgeleide klassen.
     * @param {HTMLElement} elt - element dat gewijzigd is
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    OnClick(elt, idSuffix) {
    }

    /**
     * Geef de unieke code voor deze invoermanager
     */
    Index() {
        return this.#index;
    }
    #index = 0;

    /**
     * Geef het ID voor een HTML element gemaakt door de invoermanager
     * @param {string} idSuffix - Suffix voor de identificatie van het element
     */
    ElementId(idSuffix) {
        if (idSuffix === undefined || idSuffix === '') {
            return `_bgpg_${this.#index}`;
        } else {
            return `_bgpg_${this.#index}_${idSuffix}`;
        }
    }
    /**
     * Geef het HTML element gemaakt door de invoermanager
     * @param {string} idSuffix - Suffix voor de identificatie van het element
     */
    Element(idSuffix) {
        return document.getElementById(this.ElementId(idSuffix));
    }

    /**
     * Geef de dataset declaratie voor het top-level element
     */
    DataSet() {
        return `data-im="${this.#index}"`;
    }

    /**
     * Aangeroepen om de HTML voor de invoer te maken om in een pagina te zetten.
     * @param {string} containerElement - Tag van het containerelement
     */
    MaakVolledigeHtml(containerElement, cssClass) {
        if (cssClass) {
            cssClass = ` class="${cssClass}"`;
        } else {
            cssClass = '';
        }
        return `<${containerElement} id="${this.ElementId()}" ${this.DataSet()} ${cssClass}>${this.Html()}</${containerElement}>`
    }

    /**
     * Maakt de HTML voor een voegtoe knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    HtmlVoegToe(hint, idSuffix) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} class="voegtoe">&#x271A;</span>`;
    }
    /**
     * Maakt de HTML voor een edit knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    HtmlWerkBij(hint, idSuffix) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} class="werkbij">&#x270E;</span>`;
    }
    /**
     * Maakt de HTML voor een verwijder knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    HtmlVerwijder(hint, idSuffix) {
        return `<span title="${hint}" id="${this.ElementId(idSuffix)}" ${this.DataSet()} class="verwijder">&#x1F5D1;</span>`;
    }

    /**
     * Open een modal invoer box
     * @param {string} html - HTML voor de invoer
     * @param {lambda} onVerwerk - Functie aangeroepen voordat box sluit; argument geeft aan of het via ok was (en niet cancel)
     * @param {lambda} onClose - Functie aangeroepen nadat box gesloten is; argument geeft aan of het via ok was (en niet cancel)
     */
    static OpenModal(html, onVerwerk, onClose) {
        document.getElementById('_bgpg_modal_content').innerHTML = html;
        document.getElementById('_bgpg_modal').style.display = 'block';
        InvoerManager.#onModalVerwerk = onVerwerk;
        InvoerManager.#onModalClose = onClose;
        InvoerManager.#preModalIM = Object.assign({}, InvoerManager.#invoer_managers);
    }
    static #onModalVerwerk;
    static #onModalClose;
    static #preModalIM;

    /**
     * Sluit de modal invoer box
     * @param {any} accepteerInvoer - Geeft aan of het via ok was (en niet cancel)
     */
    static SluitModal(accepteerInvoer) {
        if (InvoerManager.#preModalIM !== undefined) {
            InvoerManager.#invoer_managers = InvoerManager.#preModalIM;
            InvoerManager.#preModalIM = undefined;
        }
        if (InvoerManager.#onModalVerwerk !== undefined) {
            InvoerManager.#onModalVerwerk(accepteerInvoer);
            InvoerManager.#onModalVerwerk = undefined;
        }
        document.getElementById('_bgpg_modal').style.display = 'none';
        document.getElementById('_bgpg_modal_content').innerHTML = '';
        if (InvoerManager.#onModalClose !== undefined) {
            InvoerManager.#onModalClose(accepteerInvoer);
            InvoerManager.#onModalClose = undefined;
        }
    }
    /**
     * Link de invoermanagers aan dat deel van de webpagina waar de UI events gegenereerd worden.
     * @param {any} spec_invoer Top-level HTML element van het UI-gebied
     */
    static AddEventListener(spec_invoer) {
        InvoerManager.#spec_invoer = spec_invoer
        spec_invoer.addEventListener('change', e => InvoerManager.#Invoer_Event(e.target, (im, s, a) => im.OnChange(a, s)));
        spec_invoer.addEventListener('click', e => InvoerManager.#Invoer_Event(e.target, (im, s, a) => im.OnClick(a, s)));
    }
    static #spec_invoer;
    /**
     * Verwerk een UI event in een van de specificatie elementen
     * @param {HTMLElement} elt_invoer - element waarvoor het change element is gegenereerd
     * @param {lambda} handler - functie die de juiste methode voor de invoermanager uitvoert
     */
    static #Invoer_Event(elt_invoer, handler) {
        for (let elt = elt_invoer; elt && elt.id !== InvoerManager.#spec_invoer.id; elt = elt.parentElement) {
            if (elt.dataset) {
                if (elt.dataset.im) {
                    let im = parseInt(elt.dataset.im);
                    let idPrefix = `_bgpg_${im}_`;
                    let suffix = undefined;
                    if (elt_invoer.id.startsWith(idPrefix)) {
                        suffix = elt_invoer.id.substring(idPrefix.length);
                    }
                    else if (elt.id.startsWith(idPrefix)) {
                        suffix = elt.id.substring(idPrefix.length);
                    }
                    handler(InvoerManager.#invoer_managers[im], suffix, elt_invoer);
                    return;
                }
            }
        }
    }
    static #invoer_managers = {};
    static #invoer_manager_idx = 0;
}

/*------------------------------------------------------------------------------
*
* SpecificatieElement is een basisklasse voor een object dat een deel van 
* de specificatie kan manipuleren.
* 
*----------------------------------------------------------------------------*/
class SpecificatieElement extends InvoerManager {
    /**
     * Maak een beheerobject aan
     * @param {any} eigenaarObject - Object of array in de specificatie waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Als eigenaarObject een array is, laat dit dan leeg.
     * @param {any} data - In-memory object voor het element.
     */
    constructor(eigenaarObject, eigenschap, data) {
        super();
        this.#eigenaarObject = eigenaarObject;
        this.#eigenschap = eigenschap;
        if (data !== undefined) {
            this.#data = data;
        }
        else if (eigenaarObject !== undefined && eigenschap !== undefined) {
            this.#data = eigenaarObject[eigenschap];
        }
        SpecificatieElement.#elementen.push(this);
    }

    /**
     * Methode om aan te geven dat het specificatie-element niet meer nodig is
     */
    destructor() {
        super.destructor();
        let idx = SpecificatieElement.#elementen.indexOf(this);
        if (idx >= 0) {
            delete SpecificatieElement.#elementen[idx];
        }
    }

    /**
     * Informeer elke andere SpecificatieElement die het horen wil dat dit 
     * element gewijzigd is. Deze methode moet in afgeleide klassen 
     * geïmplementeerd worden.
     */
    NotificeerWijziging() {
    }

    /**
     * Reageer op een verstuurde notificatie. Deze methode moet in afgeleide klassen 
     * geïmplementeerd worden.
     * @param {any} bron - SpecificatieElement dat de notificatie verstuurd heeft
     * @param {any} naam - Naam van het soort notificatie
     * @param {any} data - Eventueel aanvullende informatie
     */
    OntvangNotificatie(bron, naam, data) {
    }

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
        this.#data = data;
        this.WerkSpecificatieBij();
    }
    #data;

    /**
     * Geeft aan of de in-memory Data valide is en onderdeel kan zijn van de specificatie
     */
    IsValide() {
        return this.#data !== undefined;
    }

    /**
     * Neem de waarde van Specificatie() over in de specificatie
     */
    WerkSpecificatieBij() {
        let isGewijzigd = false;
        let data = this.Specificatie()
        if (this.#eigenaarObject !== undefined) {
            if (this.#eigenschap === undefined) {
                let idx = this.#eigenaarObject.indexOf(data);
                if (this.IsValide()) {
                    if (idx < 0) {
                        this.#eigenaarObject.push(data);
                        isGewijzigd = true;
                    }
                } else if (idx >= 0) {
                    delete this.#eigenaarObject[idx];
                    isGewijzigd = true;
                }
            }
            else {
                if (this.IsValide()) {
                    this.#eigenaarObject[this.#eigenschap] = data;
                    isGewijzigd = true;
                } else if (this.#eigenaarObject[this.#eigenschap] !== undefined) {
                    delete this.#eigenaarObject[this.#eigenschap];
                    isGewijzigd = true;
                }
            }
        }
        if (isGewijzigd) {
            this.IsGewijzigd();
        }
    }

    /**
     * Verwijder de waarde uit de specificatie
     */
    Verwijder() {
        let isGewijzigd = false;
        if (this.#eigenaarObject !== undefined) {
            if (this.#eigenschap === undefined) {
                let idx = this.#eigenaarObject.indexOf(this.#data);
                if (idx >= 0) {
                    delete this.#eigenaarObject[idx];
                    isGewijzigd = false;
                }
            }
            else {
                delete this.#eigenaarObject[this.#eigenschap];
                isGewijzigd = false;
            }
        }
        if (isGewijzigd) {
            this.IsGewijzigd();
        }
    }

    /**
     * Methode die aangeroepen moet worden voor het versturen van een notificatie
     * vanuit OntvangNotificatie
     * @param {string} naam  - Naam van het soort notificatie
     * @param {any} data - Eventueel aanvullende informatie
     */
    VerstuurNotificatie(naam, data) {
        let bron = this;
        let inNotificatie = this.#inNotificatie;
        try {
            for (let elt of SpecificatieElement.#elementen) {
                if (elt != this) {
                    elt.#OntvangNotificatie(bron, inNotificatie + 1, naam, data);
                }
            }
        }
        finally {
            this.#inNotificatie = inNotificatie;
        }

    }
    /**
     * Reageer op een verstuurde notificatie. Deze methode moet in afgeleide klassen 
     * geïmplementeerd worden.
     * @param {any} bron - SpecificatieElement dat de notificatie verstuurd heeft
     * @param {int} diepte - Diepte van de nesting van events
     * @param {any} naam - Naam van het soort notificatie
     * @param {any} data - Eventueel aanvullende informatie
     */
    #OntvangNotificatie(bron, diepte, naam, data) {
        let inNotificatie = this.#inNotificatie;
        this.#inNotificatie = diepte;
        try {
            this.OntvangNotificatie(bron, naam, data);
        }
        finally {
            this.#inNotificatie = inNotificatie;
        }
    }
    static #elementen = [];

    /**
     * Methode die intern aangeroepen moet worden voor aansturen van NotificeerWijziging
     */
    IsGewijzigd() {
        this.WerkHtmlBij();
        this.NotificeerWijziging();
        if (this.#inNotificatie == 0) {
            this.VerstuurNotificatie('Specificatie');
        }
    }
    #inNotificatie = 0;

    /**
     * Werk de HTML representatie van het element bij
     */
    WerkHtmlBij() {
        let elt = document.getElementById(this.ElementId());
        if (elt) {
            elt.innerHTML = this.Html();
        }
    }
}

/*------------------------------------------------------------------------------
 *
 * Specificatie als geheel
 * 
 *----------------------------------------------------------------------------*/
class Specificatie extends SpecificatieElement {
    /**
     * Maak de invoermanager aan
     * @param {any} data - Volledige in-memory specificatie
     * @param {HTMLElement} elt_data - HTML element van het form waarin de specificatie opgenomen moet worden
     * @param {HTMLElement} elt_startknop - HTML element van de startknop, de submit van het form
     * @param {HTMLElement} elt_download - HTML element van de download link
     */
    constructor(data, elt_data, elt_startknop, elt_download) {
        super(undefined, undefined, data);
        this.#elt_data = elt_data;
        this.#elt_startknop = elt_startknop;
        this.#elt_download = elt_download;
        this.#PubliceerSpecificatie();
    }
    #elt_data;
    #elt_startknop;
    #elt_download;

    /**
     * Reageer op een verstuurde notificatie.
     * @param {any} bron - SpecificatieElement dat de notificatie verstuurd heeft
     * @param {any} naam - Naam van het soort notificatie
     * @param {any} data - Eventueel aanvullende informatie
     */
    OntvangNotificatie(bron, naam, data) {
        if (naam == 'Specificatie') {
            this.#PubliceerSpecificatie();
        }
    }

    /**
     * Werk de HTML pagina bij met de specificatie
     */
    #PubliceerSpecificatie() {
        if (this.Specificatie().Beschrijving || this.Specificatie().Projecten.length > 0 || this.Specificatie().Overig.length > 0) {
            let json = JSON.stringify(this.Specificatie(), Specificatie.#ObjectFilter, 4).trim();
            this.#elt_data.value = json;
            this.#elt_download.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(json);
            this.#elt_download.style.visibility = 'visible';
        } else {
            this.#elt_download.href = '#';
            this.#elt_download.style.visibility = 'hidden';
        }
        if (this.Specificatie().Projecten.length > 0 || this.Specificatie().Overig.length > 0) {
            this.#elt_startknop.style.display = '';
        } else {
            this.#elt_startknop.style.display = 'none';
        }
    }

    /**
     * Filter om lege objecten uit de JSON te houden
     */
    static #ObjectFilter(key, value) {
        if (key[0] !== '_' && !Specificatie.#IsEmpty(value)) {
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
            return value.every(Specificatie.#IsEmpty);
        }
        else if (typeof (value) === 'object') {
            let all = Object.values(value);
            if (all.length == 0) {
                return true;
            }
            return all.every(Specificatie.#IsEmpty);
        }
        return false;
    }
}

/*==============================================================================
 *
 * Globale eigenschappen: Beschrijving en Startdatum, en tevens de invoer van
 * een tijdstip dat meebeweegt met de startdatum.
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
 *
 * Beschrijving
 * 
 *----------------------------------------------------------------------------*/
class Beschrijving extends SpecificatieElement {
    /**
     * Maak de invoermanager aan voor de beschrijving van het scenario
     * @param {any} specificatie - Volledige specificatie
     */
    constructor(specificatie) {
        super(specificatie, 'Beschrijving');
    }

    Html() {
        return `${this.Specificatie()}`;
    }
    VolledigeHtml() {
        return this.MaakVolledigeHtml('textarea', 'tekst');
    }

    OnChange() {
        this.SpecificatieWordt(this.Element().value.trim());
    }
}

/*------------------------------------------------------------------------------
 *
 * Startdatum
 * 
 *----------------------------------------------------------------------------*/
class Startdatum extends SpecificatieElement {
    /**
     * Maak de invoermanager aan voor de startdatum van het scenario
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

    static Datum() {
        return Startdatum.#startdatum;
    }
    static #startdatum;

    Html() {
        return `${this.Specificatie()}${this.HtmlWerkBij("Pas de startdatum van het scenario aan", 'W')}`;
    }

    OnClick(elt, idSuffix) {
        if (idSuffix == 'W') {
            InvoerManager.OpenModal(`<div ${this.DataSet()}><input type="number" class="number2" min="1" max="31" id="${this.ElementId('D')}" value="${this.Specificatie().substr(8, 2)}"/> -
        <input type="number" class="number2" min="1" max="12" id="${this.ElementId('M')}" value="${this.Specificatie().substr(5, 2)}"/> -
        <input type="number" class="number4" min="2020" id="${this.ElementId('J')}" value="${this.Specificatie().substr(0, 4)}"/></div>`,
                (ok) => this.#WerkBij(ok))
        }
    }

    #WerkBij(ok) {
        if (ok) {
            let dag = parseInt(this.Element('D').value);
            let maand = parseInt(this.Element('M').value);
            let jaar = parseInt(this.Element('J').value);
            let datum = new Date(Date.UTC(jaar, maand - 1, dag));
            this.#WerkSpecificatieBij(datum);
        }
    }
    #WerkSpecificatieBij(datum) {
        Startdatum.#startdatum = datum;
        this.SpecificatieWordt(datum.toJSON().substr(0, 10));
    }

    NotificeerWijziging() {
        this.VerstuurNotificatie('Startdatum');
    }
}

/*------------------------------------------------------------------------------
 *
 * Tijdstip
 * 
 *----------------------------------------------------------------------------*/
class Tijdstip extends SpecificatieElement {
    /**
     * Maak de invoermanager aan
     * @param {any} eigenaarObject - Object of array in de specificatie waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Als eigenaarObject een array is, laat dit dan leeg.
     * @param {int} aantalDagen - Initiële waarde voor het aantal dagen
     * @param {lambda} tijdstipIngevoerd - Functie die met deze instantie van Tijdstip aangeroepen wordt
     */
    constructor(eigenaarObject, eigenschap, aantalDagen, tijdstipIngevoerd) {
        super(eigenaarObject, eigenschap);
        this.#tijdstipIngevoerd = tijdstipIngevoerd;
        this.#aantalDagen = aantalDagen;
    }
    #tijdstipIngevoerd;
    #aantalDagen;
    #uurOpDag = 0;

    Html() {
        if (this.IsValide()) {
            let datum = new Date(Startdatum.Datum());
            datum.setDate(datum.getDate() + this.#aantalDagen);
            let str = datum.toJSON().substr(0, 10);
            if (this.#uurOpDag > 0) {
                str += 'T' + ('00' + this.#uurOpDag).slice(-2) + ':00:00Z';
            }
            return str;
        } else {
            return this.HtmlVoegToe("Voeg een nieuwe activiteit toe", 'A');
        }
    }

    OnClick(elt, idSuffix) {
        if (idSuffix == 'A') {
            InvoerManager.OpenModal(`<div ${this.DataSet()}>
            <label for="${this.ElementId('D')}">Aantal dagen sinds de startdatum:</label> <input type="number" class="number4" min="1" id="${this.ElementId('D')}" value="${this.#aantalDagen}"/>
            <br/>
            <label for="${this.ElementId('T')}">Tijdstip op de dag:</label> <input type="number" class="number2" min="0" max="23" id="${this.ElementId('T')}" value="${this.#uurOpDag}"/>:00
            </div>`, (ok) => this.#WerkBij(ok));
        }
    }

    #WerkBij(ok) {
        if (ok) {
            this.#aantalDagen = parseInt(this.Element('D').value);
            if (this.#aantalDagen < 1) {
                this.#aantalDagen = 1;
            }
            this.#uurOpDag = parseInt(this.Element('T').value);
            if (this.#uurOpDag < 0) {
                this.#uurOpDag = 0;
            }
            else if (this.#uurOpDag > 23) {
                this.#uurOpDag = 23;
            }
            this.SpecificatieWordt(this.#aantalDagen + 0.01 * this.#uurOpDag);
            if (this.#tijdstipIngevoerd) {
                this.#tijdstipIngevoerd(this);
            }
        }
    }

    /**
     * Reageer op een verstuurde notificatie.
     * @param {any} bron - SpecificatieElement dat de notificatie verstuurd heeft
     * @param {any} naam - Naam van het soort notificatie
     * @param {any} data - Eventueel aanvullende informatie
     */
    OntvangNotificatie(bron, naam, data) {
        if (naam == 'Startdatum') {
            this.WerkHtmlBij();
        }
    }
}

/*==============================================================================
 *
 * Wijziging en momentopname
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
*
* Momentopname
* 
*----------------------------------------------------------------------------*/
class Momentopname extends SpecificatieElement {
    /**
     * Maak de invoermanager aan
     * @param {any} eigenaarObject - Object of array in de specificatie waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Als eigenaarObject een array is, laat dit dan leeg.
     * @param {bool} inclusiefTijdstempels - Geeft aan of tijdstempels toegestaan zijn
     * @param {Momentopname} basisversie - Momentopname die de basisversie is voor deze momentopname
     * @param {Momentopname[]} vervlochtenVersies - Lijst met momentopname die met deze momentopname vervlochten worden
     * @param {Momentopname[]} ontvlochtenVersies - Lijst met momentopname die met deze momentopname ontvlochten worden
     */
    constructor(eigenaarObject, eigenschap, inclusiefTijdstempels, basisversie, vervlochtenVersies, ontvlochtenVersies) {
        super(eigenaarObject, eigenschap);
        this.#inclusiefTijdstempels = inclusiefTijdstempels;
        this.#basisversie = basisversie;
        this.#vervlochtenVersies = (vervlochtenVersies === undefined ? [] : vervlochtenVersies);
        this.#ontvlochtenVersies = (ontvlochtenVersies === undefined ? [] : ontvlochtenVersies);
    }
    #inclusiefTijdstempels;
    #basisversie;
    #vervlochtenVersies;
    #ontvlochtenVersies;

    Html() {
        if (this.IsValide()) {
            return this.HtmlWerkBij("Wijzig de momentopname", 'W');
        } else {
            return this.HtmlVoegToe("Voeg een nieuwe momentopname toe", 'A');
        }
    }

    OnClick(elt, idSuffix) {
        if (idSuffix === undefined) {
            return;
        }
        if (idSuffix == 'A' || idSuffix == 'W') {
            // Nieuwe momentopname of wijzigen van bestaande
            this.#nieuweData = idSuffix == 'A' ? {} : Object.assign({}, this.Specificatie());
            InvoerManager.OpenModal(`<div ${this.DataSet()} id="${this.ElementId('MHtml')}">${this.#ModalHtml()}</div>`, undefined, (ok) => this.#WerkBij(ok));
        }
        else if (BGProcesGenerator.SoortInstrumentNamen[idSuffix] !== undefined) {
            // Initiële versie van nieuw instrument
            let instr = this.#NieuweInstrumentNaam(idSuffix)
            this.#nieuweData[instr] = {
                _json: true
            };
            this.#VervangModalHtml();
        }
        else if (idSuffix.startsWith('IV')) {
            // Instrumentversie selectie
            let instr = elt.dataset.instr;
            if (elt.value == 'true') {
                this.#nieuweData[instr] = true;
            }
            else if (elt.value == 'false') {
                this.#nieuweData[instr] = false;
            }
            else if (elt.value == 'null') {
                if (this.Specificatie()[instr] === undefined) {
                    delete this.#nieuweData[instr];
                } else {
                    this.#nieuweData[instr] = null;
                }
            }
            else if (elt.value == '{}' || elt.value == '+') {
                this.#nieuweData[instr] = {
                    _json: true
                };
            }
            this.#VervangModalHtml();
        }
    }

    #ModalHtml() {
        let idx = 0;
        let html = '<table>';
        let titel = '<tr><td colspan="3"><b>Beheerd op deze branch</b></td></tr>';
        let gedaan = []
        for (let prefix of (BGProcesGenerator.Opties.InformatieObjecten ? [BGProcesGenerator.SoortInstrument_Regeling, BGProcesGenerator.SoortInstrument_GIO, BGProcesGenerator.SoortInstrument_PDF] : [BGProcesGenerator.SoortInstrument_Regeling])) {
            let soortnaam = BGProcesGenerator.SoortInstrumentNamen[prefix];
            soortnaam = soortnaam.charAt(0).toUpperCase() + soortnaam.slice(1)
            for (let instr of Object.keys(this.#nieuweData).sort()) {
                if (instr.startsWith(prefix)) {
                    if (titel) {
                        html += titel; titel = '';
                    }
                    gedaan.push(instr);
                    idx++;
                    html += `<tr><td rowspan="3">${soortnaam}</td><td rowspan="3">${instr}</td>`;
                    let huidig = this.#nieuweData[instr];
                    let checked = huidig !== null && huidig !== true && huidig !== false ? ' checked="checked"' : '';
                    html += `<td><input type="radio" ${checked} name="${this.ElementId(idx)}" id="${this.ElementId('IV_1' + idx)}" data-instr="${instr}" value="{}"><label for="${this.ElementId('IV_1' + idx)}">Nieuwe versie<label></td></tr>`;
                    checked = huidig === false ? ' checked="checked"' : '';
                    html += `<tr><td><input type="radio" ${checked} name="${this.ElementId(idx)}" id="${this.ElementId('IV_2' + idx)}" data-instr="${instr}" value="false"><label for="${this.ElementId('IV_2' + idx)}">Intrekken<label></td></tr>`;
                    checked = huidig === null ? ' checked="checked"' : '';
                    html += `<tr><td><input type="radio" ${checked} name="${this.ElementId(idx)}" id="${this.ElementId('IV_3' + idx)}" data-instr="${instr}" value="null"><label for="${this.ElementId('IV_3' + idx)}">Geen wijziging; terugzetten naar uitgangssituatie<label></td></tr>`;
                }
            }
        }
        titel = '<tr><td colspan="3"><b>Toevoegen aan deze branch</b></td></tr>';
        for (let prefix of (BGProcesGenerator.Opties.InformatieObjecten ? [BGProcesGenerator.SoortInstrument_Regeling, BGProcesGenerator.SoortInstrument_GIO, BGProcesGenerator.SoortInstrument_PDF] : [BGProcesGenerator.SoortInstrument_Regeling])) {
            if (titel) {
                html += titel; titel = '';
            }
            let soortnaam = BGProcesGenerator.SoortInstrumentNamen[prefix];
            soortnaam = soortnaam.charAt(0).toUpperCase() + soortnaam.slice(1)
            for (let instr of BGProcesGenerator.Instrumentnamen(prefix)) {
                if (!gedaan.includes(instr)) {
                    idx++;
                    html += `<tr><td>${soortnaam}</td><td>${instr}</td><td><input type="checkbox" id="${this.ElementId('IV' + idx)}" data-instr="${instr}" value="+"><label for="${this.ElementId('IV' + idx)}">Initiële versie (${BGProcesGenerator.SoortInstrumentNamen[prefix]} wordt elders ook al geïnitieerd)<label></td></tr>`;
                }
            }
            if (prefix != BGProcesGenerator.SoortInstrument_Regeling || BGProcesGenerator.Opties.MeerdereRegelingen) {
                let instr = this.#NieuweInstrumentNaam(prefix)
                html += `<tr><td></td><td>${instr}</td><td>${this.HtmlVoegToe("Voeg initiële versie toe", prefix)} Initiële versie van nieuwe ${BGProcesGenerator.SoortInstrumentNamen[prefix]}</td></tr>`;
            }
        }
        html += '</table>';
        return html;
    }

    #NieuweInstrumentNaam(soortInstrument) {
        let bekend = Object.keys(this.#nieuweData);
        bekend.push(...BGProcesGenerator.Instrumentnamen(soortInstrument))
        return BGProcesGenerator.VrijeNaamIndex(bekend, soortInstrument + "_");
    }

    #VervangModalHtml() {
        document.getElementById(this.ElementId('MHtml')).innerHTML = this.#ModalHtml();
    }

    #WerkBij(ok) {
        if (ok) {
            this.SpecificatieWordt(this.#nieuweData);
        }
    }
    #nieuweData;
}
