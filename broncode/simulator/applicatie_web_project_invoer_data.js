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
    constructor(elt_invoer, titel) {
        this.#spec_invoer = elt_invoer;
        this.#spec_invoer.innerHTML = '<h3>' + titel + '</h3>';
    }
    #spec_invoer = null;
    #data = { // Data voor het scenario
        BevoegdGezag: '',
        Beschrijving: '',
        Start: {},
        Projecten: {},
        Interventies: [],
    };

    /**
     * Lees een eerder aangemaakte specificatie
     * @param {HTMLElement} elt_invoer - Element waarin specificatieform wordt opgebouwd
     * @param {string} json - JSON specificatie
     */
    static LeesSpecificatie(elt_invoer, json) {
        var data = JSON.parse(json);
        if (data.BevoegdGezag) {
            var bgpg;
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

        if (data.Beschrijving) {
            bgpg.#data.Beschrijving = data.Beschrijving;
        }

        if (data.Start) {
            for (doel in Object.keys(data.Start)) {
                Momentopname.LeesSpecificatie(bgpg.#data.Start, doel, bgpg.BGCode(), doel, data.Start[doel]);
            }
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
        var bgpg;
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
        var This = this;
        this.#spec_invoer.addEventListener('change', (e) => {
            This.#Invoer_Change(e.target);
        });

        this.#specManager = new SpecificatieInvoerManager(this, this.#data, elt_data, startknop, downloadLink);

        this.#spec_invoer.insertAdjacentHTML('beforeend', '<p><b>Beschrijving van het scenario</b><br/>Geef een korte beschrijving van het scenario waarvoor deze specificatie is opgesteld (optioneel)<br/>');
        new TekstInvoerManager(this, this.#specManager, this.#data, 'Beschrijving').MaakHTML(this.#spec_invoer);
        this.#spec_invoer.insertAdjacentHTML('beforeend', '</p>');
    }
    #specManager;

    /**
     * Registreer een invoermanager
     * @param {any} im
     * @returns De index om voor de invoerelementen te gebruiken
     */
    Registreer_InvoerManager(im) {
        this.#invoer_manager_idx++;
        this.#invoer_managers[this.#invoer_manager_idx] = im;
        return this.#invoer_manager_idx;
    }
    #invoer_managers = {};
    #invoer_manager_idx = 0;

    /**
     * Verwerk een change event in een van de specificatie elementen
     * @param {HTMLElement} elt_invoer - element waarvoor het change element is gegenereerd
     */
    #Invoer_Change(elt_invoer) {
        if (elt_invoer.dataset) {
            if (elt_invoer.dataset.im) {
                var im = parseInt(elt_invoer.dataset.im);
                this.#invoer_managers[im].OnChange();
            }
        }
    }
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
        super(elt_invoer, 'Invoer voor een gemeente');
    }

    BGCode() {
        return "gm9999";
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
        super(elt_invoer, 'Invoer voor de rijksoverheid');
    }

    BGCode() {
        return "mnre9999";
    }
}

/*==============================================================================
 *
 * Nu volgen een aantal klassen die het versiebeheer modelleren en de invoer
 * van wat er op een branch wijzigt.
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
 *
 * Momentopname bevat alle versie-informatie inclusief annotaties voor een
 * moment/commit op een branch.
 * 
 *----------------------------------------------------------------------------*/
class Instrument {
    constructor(code, workId) {
        this.#code = code;
        this.#workId = workId;
    }

    /**
     * Geeft de verkorte vorm van het workID
     */
    Code() {
        return this.#code;
    }
    #code;

    /**
     * Geeft het volledige work-ID van het instrument
     */
    WorkId() {
        return this.#workId;
    }
    #workId;

    /**
     * Maak een expression identificatie voor een instrumentversie
     * @param {any} code - Korte versie identificatie; moet uniek zijn voor het instrument
     * @param {any} gemaaktOp - tijdstip van uitwisseling
     * @returns Expression identificatie
     */
    MaakEpressionId(code, gemaaktOp) {
        return this.#workId + '@' + gemaaktOp.substring(0, 4) + ';' + code;
    }

    /**
     * Geeft een lijst met de STOP annotaties die voor dit instrument zijn toegestaan
     */
    ToegestaneAnnotaties() {
        throw new Error('ToegestaneAnnotaties ontbreekt');
    }

    /**
     * Geeft aan of non-STOP annotaties zijn toegestaan
     */
    NonSTOPAnnotatiesToegestaan() {
        return false;
    }
}

class Regeling extends Instrument {
    constructor(code, bgcode, gemaaktOp) {
        super(code, '/akn/nl/act/' + bgcode + '/' + gemaaktOp.substring(0, 4) + '/' + code);
    }

    /**
     * Maak een expression identificatie voor een instrumentversie
     * @param {any} code - Korte versie identificatie; moet uniek zijn voor het instrument
     * @param {any} gemaaktOp - tijdstip van uitwisseling
     * @returns Expression identificatie
     */
    MaakEpressionId(code, gemaaktOp) {
        return this.WorkId() + '/nl@' + gemaaktOp.substring(0, 4) + ';' + code;
    }

    /**
     * Geeft een lijst met de STOP annotaties die voor dit instrument zijn toegestaan
     */
    ToegestaneAnnotaties() {
        return ["Metadata_Citeertitel", "Toelichtingrelaties"];
    }
    /**
     * Geeft aan dat non-STOP annotaties zijn toegestaan
     */
    NonSTOPAnnotatiesToegestaan() {
        return true;
    }

    /**
     * Geeft de prefix van de code die voor een regeling gebruikt moet worden.
     */
    static CodePrefix() {
        return "reg_";
    }
    /**
     * Gaat na of de regeling bekend is, en zo ja, geeft de Regeling informatie terug
     * @param {string} workId
     * @returns {Regeling}
     */
    static IsBekend(workId) {
        if (workId in Regeling.#workIds) {
            return Regeling.#workIds(workId);
        }
    }
    static Registreer(workId, bgcode, gemaaktOp) {
        var instrument = new Regeling(workId, bgcode, gemaaktOp);
        Regeling.#workIds[workId] = instrument;
        return instrument;
    }
    static #workIds = {}
}

class GIO extends Instrument {
    constructor(code, bgcode, gemaaktOp) {
        super(code, '/join/regdata/' + bgcode + '/' + gemaaktOp.substring(0, 4) + '/' + code);
    }

    /**
     * Geeft een lijst met de STOP annotaties die voor dit instrument zijn toegestaan
     */
    ToegestaneAnnotaties() {
        return ["Metadata_Citeertitel", "Symbolisatie"];
    }

    /**
     * Geeft de prefix van de code die voor een GIO gebruikt moet worden.
     */
    static CodePrefix() {
        return "gio_";
    }
    /**
     * Gaat na of het GIO bekend is, en zo ja, geeft de GIO informatie terug
     * @param {string} workId
     * @returns {GIO}
     */
    static IsBekend(workId) {
        if (workId in GIO.#workIds) {
            return GIO.#workIds(workId);
        }
    }
    static Registreer(workId, bgcode, gemaaktOp) {
        var instrument = new GIO(workId, bgcode, gemaaktOp);
        GIO.#workIds[workId] = instrument;
        return instrument;
    }
    static #workIds = {}
}

class PDF extends Instrument {
    constructor(code, bgcode, gemaaktOp) {
        super(code, '/join/regdata/' + bgcode + '/' + gemaaktOp.substring(0, 4) + '/' + code);
    }

    /**
     * Geeft een lijst met de STOP annotaties die voor dit instrument zijn toegestaan
     */
    ToegestaneAnnotaties() {
        return ["Metadata_Citeertitel"];
    }

    /**
     * Geeft de prefix van de code die voor een PDF gebruikt moet worden.
     */
    static CodePrefix() {
        return "pdf_";
    }
    /**
     * Gaat na of de PDF bekend is, en zo ja, geeft de PDF informatie terug
     * @param {string} workId
     * @returns {PDF}
     */
    static IsBekend(workId) {
        if (workId in PDF.#workIds) {
            return PDF.#workIds(workId);
        }
    }
    static Registreer(workId, bgcode, gemaaktOp) {
        var instrument = new PDF(workId, bgcode, gemaaktOp);
        PDF.#workIds[workId] = instrument;
        return instrument;
    }
    static #workIds = {}
}

/*------------------------------------------------------------------------------
 *
 * SpecificatieElement is een basisklasse voor een object dat een deel van 
 * de specificatie kan manipuleren. De klasse moet hier staan omdat javascript
 * geen forward declaration van klassen kent. 
 * 
 *----------------------------------------------------------------------------*/
class SpecificatieElement {
    /**
     * Maak een beheerobject aan
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Index als eigenaarObject een array is
     * @param {any} data - In-memory object voor het element. Mag weggelaten worden als Specificatie() geïmplementeerd wordt.
     */
    constructor(eigenaarObject, eigenschap, data) {
        this.#eigenaarObject = eigenaarObject;
        this.#eigenschap = eigenschap;
        if (data !== undefined) {
            this.#data = data;
        }
        else if (eigenschap in eigenaarObject) {
            this.#data = eigenaarObject[eigenschap];
        }
    }
    #eigenaarObject;
    #eigenschap;
    #data;

    /**
     * Geef het in-memory object voor het element
     */
    Specificatie() {
        return this.#data;
    }

    /**
     * Geeft aan of de in-memory Data valide is en onderdeel kan zijn van de specificatie
     */
    IsValide() {
        return true;
    }

    /**
     * Neem de waarde van Data over in de specificatie
     */
    WerkSpecificatieBij() {
        if (this.IsValide()) {
            this.#eigenaarObject[this.#eigenschap] = this.Specificatie();
        } else if (this.#eigenschap in this.#eigenaarObject) {
            delete this.#eigenaarObject[this.#eigenschap];
        }
    }
}

/*------------------------------------------------------------------------------
 *
 * Momentopname bevat alle versie-informatie inclusief annotaties voor een
 * moment/commit op een branch. Instrumentversie geeft invulling aan een 
 * versie voor een van de instrumenten.
 * 
 *----------------------------------------------------------------------------*/
class Momentopname extends SpecificatieElement {

    constructor(branch, index, doel, gemaaktOp, vorigeMomentopname) {
        super(branch, index, {
            _This: this,
            gemaaktOp: gemaaktOp,
            Regelingen: {},
            GIO: {},
            PDF: {}
        });
        this.#doel = doel;
        if (vorigeMomentopname) {
            for (workId in Object.keys(vorigeMomentopname.Specificatie().Regelingen)) {
                this.Specificatie().Regelingen[workId] = vorigeMomentopname.Specificatie().Regelingen[workId].Kloon();
            }
            for (workId in Object.keys(vorigeMomentopname.Specificatie().GIO)) {
                this.Specificatie().GIO[workId] = vorigeMomentopname.Specificatie().Regelingen[workId].Kloon();
            }
            for (workId in Object.keys(vorigeMomentopname.Specificatie().PDF)) {
                this.Specificatie().PDF[workId] = vorigeMomentopname.Specificatie().Regelingen[workId].Kloon();
            }
        }
    }
    static LeesSpecificatie(branch, index, bgcode, doel, data, vorigeMomentopname) {
        if (data.gemaaktOp) {
            var mo = new Momentopname(branch, index, doel, data.gemaaktOp, vorigeMomentopname);
        } else {
            throw new Error('Momentopname voor doel ' + doel + ' heeft geen gemaaktOp');
        }
        if (data.Regelingen !== undefined) {
            for (workId in Object.keys(data.Regelingen)) {
                var instrument = Regeling.IsBekend(workId);
                if (instrument === undefined) {
                    instrument = Regeling.Registreer(workId, bgcode, data.gemaaktOp);
                } else if (!(workId in this.Specificatie().Regelingen)) {
                    throw new Error('Regeling "' + workId + '" komt twee keer voor als initiele versie');
                }
                Instrumentversie.LeesSpecificatie(this.Specificatie().Regelingen, instrument, data.gemaaktOp, data.Regelingen[workId]).Specificatie();
            }
        }
        if (data.GIO !== undefined) {
            for (workId in Object.keys(data.GIO)) {
                var instrument = GIO.IsBekend(workId);
                if (instrument === undefined) {
                    instrument = GIO.Registreer(workId, bgcode, data.gemaaktOp);
                } else if (!(workId in this.Specificatie().GIO)) {
                    throw new Error('GIO "' + workId + '" komt twee keer voor als initiele versie');
                }
                Instrumentversie.LeesSpecificatie(this.Specificatie().GIO, instrument, data.gemaaktOp, data.GIO[workId]).Specificatie();
            }
        }
        if (data.PDF !== undefined) {
            for (workId in Object.keys(data.PDF)) {
                var instrument = PDF.IsBekend(workId);
                if (instrument === undefined) {
                    instrument = PDF.Registreer(workId, bgcode, data.gemaaktOp);
                } else if (!(workId in this.Specificatie().PDF)) {
                    throw new Error('PDF "' + workId + '" komt twee keer voor als initiele versie');
                }
                Instrumentversie.LeesSpecificatie(this.Specificatie().PDF, instrument, data.gemaaktOp, data.PDF[workId]).Specificatie();
            }
        }
        return mo;
    }

    /**
     * Geef het doel waarvoor dit een momentopname is
     */
    Doel() {
        return this.#doel;
    }
    #doel;

    /**
     * Geeft aan of de in-memory Data valide is en onderdeel kan zijn van de specificatie
     */
    IsValide() {
        return this.Specificatie().gemaaktOp !== undefined && this.Specificatie().Regelingen.length > 0;
    }
}

class Instrumentversie extends SpecificatieElement {
    constructor(collectie, instrument, code, gemaaktOp) {
        super(collectie, instrument.Code(), {
            _This: this,
            Versie: code
        });
        this.#instrument = instrument;
        this.#expressionId = instrument.MaakEpressionId(code, gemaaktOp);
        if (instrument.NonSTOPAnnotatiesToegestaan()) {
            this.Specificatie().NonSTOP = {};
        }
    }
    static LeesSpecificatie(collectie, instrument, gemaaktOp, data) {
        if (data.Versie) {
            var versie = new Instrumentversie(collectie, instrument, data.Versie, gemaaktOp);
        } else {
            throw new Error('Instrumentversie van instrument "' + instrument.Code + '" voor gemaaktOp = ' + gemaaktOp + ' heeft geen Versie');
        }
        for (var annotatie in instrument.ToegestaneAnnotaties()) {
            if (annotatie in data) {
                versie.Specificatie()[annotatie] = data[annotatie];
            }
        }
        if (instrument.NonSTOPAnnotatiesToegestaan() && data.NonSTOP !== undefined) {
            versie.Specificatie().NonSTOP = data.NonSTOP;
        }
        return versie;
    }

    /**
     * Geeft het instrument waar dit een versie van is
     */
    Instrument() {
        return this.#instrument;
    }
    #instrument;

    /**
     * Geeft de verkorte vorm van de versie identificatie
     */
    Code() {
        return this.Specificatie().Versie;
    }

    /**
     * Geeft het volledige expression-ID van de versie i
     */
    ExpressionId() {
        return this.#expressionId;
    }
    #expressionId;

    /**
     * Geeft aan of de in-memory Data valide is en onderdeel kan zijn van de specificatie
     */
    IsValide() {
        return this.Specificatie().Versie !== undefined;
    }
}


/*==============================================================================
 *
 * Invoermanagers maken de HTML invoervelden, handelen events af en zorgen dat
 * de specificatie bijgewerkt wordt. Vanaf hier gaat de javascript over de
 * details van de pagina-afhandeling, niet meer over STOP-gerelateerde
 * onderwerpen.
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
 *
 * InvoerManager is javascript dat de invoer voor een deel van de specificatie
 * kan valideren en vertalen naar JSON.
 * 
 *----------------------------------------------------------------------------*/
class InvoerManager extends SpecificatieElement {
    /**
     * Maak een invoermanager aan
     * @param {BGProcesGenerator} bgpg - Generator
     * @param {InvoerManager} superInvoer - InvoerManager voor eigenaarObject
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Index als eigenaarObject een array is
     * @param {any} data - In-memory object voor het element. Mag weggelaten worden als Specificatie() geimplementeerd wordt.
     */
    constructor(bgpg, superInvoer, eigenaarObject, eigenschap, data) {
        super(eigenaarObject, eigenschap, data);
        this.#procesgenerator = bgpg;
        this.#index = bgpg.Registreer_InvoerManager(this);
        this.#superInvoer = superInvoer;
    }

    /**
     * Geef de procesgenerator voor deze invoermanager
     * @returns {BGProcesGenerator} Procesgenerator
     */
    ProcesGenerator() {
        return this.#procesgenerator;
    }
    #procesgenerator = null;

    /**
     * Geef de unieke code voor deze invoermanager
     */
    Index() {
        return this.#index;
    }
    #index = 0;

    /**
     * Geef de prefix voor HTML elementen gemaakt door de invoermanager
     */
    ElementPrefix() {
        return '_bgpg_' + this.#index;
    }
    /**
     * Geef de dataset declaratie voor het top-level element
     */
    DataSet() {
        return ' data-im="' + this.#index + '" ';
    }

    /**
     * Aangeroepen om de HTML voor de invoer te maken
     * @param {HTMLElement} container - Container element waarin de HTML geplaatst moet worden
     */
    MaakHTML(container) {
    }

    /**
     * Aangeroepen als er iets in de invoer is gewijzigd
     */
    OnChange() {
        this.WerkSpecificatieBij();
        if (this.#superInvoer !== undefined && this.#superInvoer !== null) {
            this.#superInvoer.OnChange();
        }
    }
    #superInvoer;
}


/*------------------------------------------------------------------------------
 *
 * InvoerManager voor de specificatie als geheel
 * 
 *----------------------------------------------------------------------------*/
class SpecificatieInvoerManager extends InvoerManager {
    /**
     * Maak de invoermanager aan
     * @param {BGProcesGenerator} bgpg - Generator
     * @param {any} data - In-memory specificatie
     * @param {HTMLElement} elt_data - HTML element van het form waarin de specificatie opgenomen moet worden
     * @param {HTMLElement} elt_startknop - HTML element van de startknop, de submit van het form
     * @param {HTMLElement} elt_download - HTML element van de download link
     */
    constructor(bgpg, data, elt_data, elt_startknop, elt_download) {
        super(bgpg, null, null, null, data);
        this.#elt_data = elt_data;
        this.#elt_startknop = elt_startknop;
        this.#elt_download = elt_download;
        this.WerkSpecificatieBij();
    }
    #elt_data;
    #elt_startknop;
    #elt_download;

    WerkSpecificatieBij() {
        if (this.Specificatie().Beschrijving || this.Specificatie().Projecten.length > 0 || this.Specificatie().Interventies.length > 0) {
            var json = JSON.stringify(this.Specificatie(), SpecificatieInvoerManager.#ObjectFilter, 4).trim();
            this.#elt_data.value = json;
            this.#elt_download.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(json);
            this.#elt_download.style.visibility = 'visible';
        } else {
            this.#elt_download.href = '#';
            this.#elt_download.style.visibility = 'hidden';
        }
        if (this.Specificatie().Projecten.length > 0 || this.Specificatie().Interventies.length > 0) {
            this.#elt_startknop.style.display = '';
        } else {
            this.#elt_startknop.style.display = 'none';
        }
    }

    /**
     * Filter om lege objecten uit de JSON te houden
     */
    static #ObjectFilter(key, value) {
        if (key[0] !== '_' && !SpecificatieInvoerManager.#IsEmpty(value)) {
            return value;
        }
    }
    static #IsEmpty(value) {
        if (value === null || value === undefined) {
            return true;
        }

        if (Array.isArray(value)) {
            if (value.length == 0) {
                return true;
            }
            return value.every(SpecificatieInvoerManager.#IsEmpty);
        }
        else if (typeof (value) === 'object') {
            var all = Object.values(value);
            if (all.length == 0) {
                return true;
            }
            return all.every(SpecificatieInvoerManager.#IsEmpty);
        }
        return false;
    }
}

/*------------------------------------------------------------------------------
 *
 * InvoerManager voor een tekst die als titel gebruikt wordt.
 * 
 *----------------------------------------------------------------------------*/
class TitelInvoerManager extends InvoerManager {
    /**
     * Maak de invoermanager aan
     * @param {BGProcesGenerator} bgpg - Generator
     * @param {InvoerManager} superInvoer - InvoerManager voor eigenaarObject
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Index als eigenaarObject een array is
     */
    constructor(bgpg, superInvoer, eigenaarObject, eigenschap) {
        super(bgpg, superInvoer, eigenaarObject, eigenschap);
    }

    Specificatie() {
        return document.getElementById(this.ElementPrefix()).value.trim();
    }

    IsValide() {
        return this.Specificatie() ? true : false;
    }

    MaakHTML(container) {
        container.insertAdjacentHTML('beforeend', '<input type="text" class="tekst" id="' + this.ElementPrefix() + '"' + this.DataSet() + '>' + super.Specificatie() + '</textarea>');
    }
}

/*------------------------------------------------------------------------------
 *
 * InvoerManager voor een tekst die als beschrijving gebruikt wordt.
 * 
 *----------------------------------------------------------------------------*/
class TekstInvoerManager extends InvoerManager {
    /**
     * Maak de invoermanager aan
     * @param {BGProcesGenerator} bgpg - Generator
     * @param {InvoerManager} superInvoer - InvoerManager voor eigenaarObject
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Index als eigenaarObject een array is
     */
    constructor(bgpg, superInvoer, eigenaarObject, eigenschap) {
        super(bgpg, superInvoer, eigenaarObject, eigenschap);
    }

    Specificatie() {
        return document.getElementById(this.ElementPrefix()).value.trim();
    }

    IsValide() {
        return this.Specificatie() ? true : false;
    }

    MaakHTML(container) {
        container.insertAdjacentHTML('beforeend', '<textarea class="tekst" id="' + this.ElementPrefix() + '"' + this.DataSet() + '>' + super.Specificatie() + '</textarea>');
    }
}

