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
        BGProcesGenerator.#This = this;
        this.#spec_invoer = elt_invoer;
        this.#spec_invoer.innerHTML = '<h3>' + titel + '</h3>';
        this.#startdatum = new Date(Date.now());
        this.#startdatum.setHours(0, 0, 0, 0);
        let doel = new Identificatie(`/join/id/proces/${this.BGCode()}/`, 'uitgangssituatie');
        this.#uitgangssituatie = new Momentopname(this.#data.Uitgangssituatie, doel.Specificatie(), doel, new GemaaktOp(undefined, 0, 0));
    }
    #spec_invoer = undefined;
    #data = { // Data voor het scenario
        BevoegdGezag: '',
        Beschrijving: '',
        Uitgangssituatie: {},
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

        if (data.Uitgangssituatie) {
            let prefix = '/join/id/proces/' + bgpg.BGCode() + '/';
            for (doel in Object.keys(data.Uitgangssituatie)) {
                if (doel === this.StartDoel()) {
                    this.WerkTijdstippenBij(new Date(parseInt(this.Specificatie().substring(0, 4)), parseInt(this.Specificatie().substring(4, 2)), parseInt(this.Specificatie().substring(6, 2))));
                    this.#uitgangssituatie.LeesSpecificatie(data.Uitgangssituatie[doel]);
                }
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
        this.#spec_invoer.addEventListener('change', e => this.#Invoer_Event(e.target, (im, a) => im.OnChange(a)));
        this.#spec_invoer.addEventListener('click', e => this.#Invoer_Event(e.target, (im, a) => im.OnClick(a)));

        this.#specManager = new SpecificatieInvoerManager(this.#data, elt_data, startknop, downloadLink);

        this.#spec_invoer.insertAdjacentHTML('beforeend', `<p>
<b>Beschrijving van het scenario</b><br/>
Geef een korte beschrijving van het scenario waarvoor deze specificatie is opgesteld (optioneel)<br/>
${new TekstInvoerManager(this.#specManager, this.#data, 'Beschrijving').Html()}
</p>
<div id="_bgpg_modal" class="modal">
  <div class="modal-content">
    <span class="modal-close"><span id="_bgpg_modal_ok">&#x2714;</span> <span id="_bgpg_modal_cancel">&#x2716;</span></span>
    <p id="_bgpg_modal_content"></p>
  </div>
</div>
<p>
<b>Uitgangssituatie</b> per ${new StartdatumInvoerManager(this).Html()}<br/>
${new UitgangspuntInvoerManager(this.#uitgangssituatie).Html()}
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
  <tr><td>${new GemaaktOpInvoerManager(gm => this.#VoegInvoerOverigeActiviteitToe(gm)).Html()}</td></tr>
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
     * Eigenschappen
     *
     -------------------------------------------------------------------------*/
    /**
     * Huidige procesgenerator
     */
    static This() {
        return BGProcesGenerator.#This;
    }
    static #This;

    SpecificatieManager() {
        return this.#specManager;
    }
    #specManager;

    /**
     * Laatst gebruikte startdatum
     */
    Startdatum() {
        return this.#startdatum;
    }
    #startdatum;

    /**
     * Geef het doel van de uitgangssituatie
     * @returns
     */
    StartDoel() {
        return this.#uitgangssituatie.Doel();
    }
    #uitgangssituatie;

    /*--------------------------------------------------------------------------
     *
     * Interne administratie
     *
     -------------------------------------------------------------------------*/
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
     * @param {lambda} handler - functie die de juiste methode voor de invoermanager uitvoert
     */
    #Invoer_Event(elt_invoer, handler) {
        for (var elt = elt_invoer; elt.id !== this.#spec_invoer.id; elt = elt.parentElement) {
            if (elt.dataset) {
                if (elt.dataset.im) {
                    var im = parseInt(elt.dataset.im);
                    handler(this.#invoer_managers[im], elt_invoer);
                }
            }
        }
    }

    /**
     * Werk de gemaaktOp bij van alle activiteiten
     * @param {Date} datum - Nieuwe startdatum
     */
    WerkTijdstippenBij(datum) {
        this.#startdatum = datum;
        if (this.#data.Uitgangssituatie[this.StartDoel()] !== undefined) {
            this.#data.Uitgangssituatie[StartDoel()]._This.GemaaktOp().WerkTijdstipBij(datum);
        }
    }

    /**
     * Voeg de invoer voor een overige activiteit toe voor het gegeven aantal dagen
     * @param {any} aantalDagen
     */
    #VoegInvoerOverigeActiviteitToe(aantalDagen) {

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
 * SpecificatieElement is een basisklasse voor een object dat een deel van 
 * de specificatie kan manipuleren. De klasse moet hier staan omdat javascript
 * geen forward declaration van klassen kent.
 * 
 * Identificatie is een klasse die helpt om op deze pagina met korte
 * identifiers te kunnen werken terwijl de specificatie met lange identifiers
 * werkt.
 * 
 * GemaaktOp is een gemaaktOp tijdstip dat op deze pagina als aantal dagen
 * sinds de start en de tijd getoond wordt.
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
        else if (eigenaarObject !== undefined) {
            this.#data = eigenaarObject[eigenschap];
        }
    }

    EigenaarObject() {
        return this.#eigenaarObject;
    }
    #eigenaarObject;

    Eigenschap() {
        return this.#eigenschap;
    }
    #eigenschap;
    #data;

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

    /**
     * Geeft aan of de in-memory Data valide is en onderdeel kan zijn van de specificatie
     */
    IsValide() {
        return this.#data !== undefined;
    }

    /**
     * Neem de waarde van Data over in de specificatie
     */
    WerkSpecificatieBij() {
        if (this.#eigenaarObject !== undefined) {
            if (this.IsValide()) {
                this.#eigenaarObject[this.#eigenschap] = this.Specificatie();
            } else if (this.#eigenschap in this.#eigenaarObject) {
                delete this.#eigenaarObject[this.#eigenschap];
            }
        }
    }

    /**
     * Verwijder de waarde uit de specificatie
     */
    Verwijder() {
        if (this.#eigenaarObject !== undefined) {
            delete this.#eigenaarObject[this.#eigenschap];
        }
    }
}

class Identificatie extends SpecificatieElement {
    /**
     * Maak een identificatie aan
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt.
     * @param {string} prefix - De prefix om van de afkorting naar de volledige identificatie te komen
     * @param {string} afkorting - De korte naam voor de identificatie
     */
    constructor(eigenaarObject, eigenschap, prefix, afkorting) {
        if (afkorting === undefined) {
            super(eigenaarObject, eigenschap)
            if (this.IsValide()) {
                this.#afkorting = this.Specificatie().substring(prefix.length);
            }
        } else {
            super(eigenaarObject, eigenschap, prefix + afkorting)
            this.#afkorting = afkorting;
        }
        this.#prefix = prefix;
    }
    #prefix;

    Afkorting() {
        return this.#afkorting;
    }
    AfkortingWordt(afkorting) {
        this.#afkorting = afkorting;
        if (afkorting === undefined) {
            this.SpecificatieWordt();
        } else {
            this.SpecificatieWordt(this.#prefix + afkorting);
        }
    }
    #afkorting;
}

class GemaaktOp extends SpecificatieElement {
    /**
     * Maak een identificatie aan
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {int} dag - Aantal dagen na de start van het scenario; optioneel
     * @param {int} uur - Aantal uren in de dag; optioneel
     */
    constructor(eigenaarObject, dag, uur) {
        super(eigenaarObject, 'gemaaktOp')
        if (dag === undefined) {
            if (this.IsValide()) {
                let datum = new Date(parseInt(this.Specificatie().substring(0, 4)), parseInt(this.Specificatie().substring(4, 2)), parseInt(this.Specificatie().substring(6, 2)));
                let dag = Math.floor((datum - BGProcesGenerator.This().Startdatum()) / (1000 * 60 * 60 * 24));
                let uur = parseInt(this.Specificatie().substring(9, 2));
                this.DagUurWordt(dag, uur);
            }
        } else {
            this.DagUurWordt(dag, uur);
        }
    }

    Dag() {
        return this.#dag;
    }
    #dag;

    Uur() {
        return this.#uur;
    }
    #uur;

    DagUurWordt(dag, uur) {
        if (dag === undefined) {
            this.#dag = undefined;
            this.#uur = undefined;
            this.SpecificatieWordt();
        } else {
            this.#dag = dag;
            if (this.#dag < 0) {
                this.#dag = 0;
            }
            this.#uur = (uur === undefined ? 0 : uur);
            if (this.#uur > 23) {
                this.#uur = 23;
            }
            this.WerkTijdstipBij(BGProcesGenerator.This().Startdatum());
        }
    }

    /**
     * Vergelijkt dit tijdstip met het opgegeven tijdstip.
     * @param {GemaaktOp} gemaaktOp - te vergelijken tijdstip
     * @returns Geeft <, =, > 0 als dit tijdstip eerder, tegelijk, later is dan het andere, en undefined als een van de twee niet gezet is
     */
    Vergelijk(gemaaktOp) {
        if (this.IsValide() && gemaaktOp.IsValide()) {
            let diff = this.#dag - gemaaktOp.Dag();
            if (diff == 0) {
                diff = this.#uur - gemaaktOp.Uur();
            }
            return diff;
        }
    }

    WerkTijdstipBij(startdatum) {
        let tijdstip = new Date(startdatum.getFullYear(), startdatum.getMonth(), startdatum.getDate() + this.#dag, this.#uur);
        this.SpecificatieWordt(`${tijdstip.getFullYear()}${('0' + (tijdstip.getMonth() + 1)).slice(-2)}${('0' + tijdstip.getDate()).slice(-2)}T${('0' + tijdstip.getHours()).slice(-2)}:00:00Z`);
    }
}

/*------------------------------------------------------------------------------
 *
 * Instrument en afgeleide klassen geven alle informatie over de instrumenten
 * die door deze pagina ondersteund worden.
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
 * Momentopname bevat alle versie-informatie inclusief annotaties voor een
 * moment/commit op een branch. Instrumentversie geeft invulling aan een 
 * versie voor een van de instrumenten.
 * 
 *----------------------------------------------------------------------------*/
class Momentopname extends SpecificatieElement {
    /**
     * Maak een nieuwe momentopname aan
     * @param {any} branch - object waarvan de momentopname een eigenschap is
     * @param {any} index - naam of index van de momentopname op de branch
     * @param {Identificatie} doel - doel waarvoor de momentopname is gemaakt
     * @param {GemaaktOp} gemaaktOp - tijdstip waarop de momentopname is gemaakt
     * @param {Momentopname} vorigeMomentopname - momentopname eerder op de branch
     */
    constructor(branch, index, doel, gemaaktOp, vorigeMomentopname) {
        super(branch, index, {
            gemaaktOp: gemaaktOp,
            Regelingen: {},
            GIO: {},
            PDF: {}
        });
        this.Specificatie()._This = this;
        this.#doel = doel;
        this.#gemaaktOp = new GemaaktOp(this.Specificatie(), gemaaktOp.Dag(), gemaaktOp.Uur());
        if (vorigeMomentopname) {
            let diff = this.#gemaaktOp.Vergelijk(vorigeMomentopname.GemaaktOp());
            if (diff >= 0) {
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
            else {
                throw new Error(`Momentopname met gemaaktOp = ${this.#gemaaktOp.Specificatie()} hoort vooraf te gaan aan die met gemaaktOp = ${vorigeMomentopname.GemaaktOp().Specificatie()}`)
            }
        }
    }

    LeesSpecificatie(data) {
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
    }

    /**
     * Maak een kloon voor het wijzigen van de momentopname
     */
    Kloon() {
        return new Momentopname(this.EigenaarObject(), this.Eigenschap(), this.#doel, this.#gemaaktOp, this);
    }

    /**
     * Geef het doel (als Identificatie) waarvoor dit een momentopname is
     */
    Doel() {
        return this.#doel;
    }
    #doel;

    GemaaktOp() {
        return this.#gemaaktOp;
    }
    #gemaaktOp;

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
     * @param {InvoerManager} superInvoer - InvoerManager voor eigenaarObject
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Index als eigenaarObject een array is
     * @param {any} data - In-memory object voor het element. Mag weggelaten worden als Specificatie() geimplementeerd wordt.
     */
    constructor(superInvoer, eigenaarObject, eigenschap, data) {
        super(eigenaarObject, eigenschap, data);
        this.#index = BGProcesGenerator.This().Registreer_InvoerManager(this);
        this.#superInvoer = superInvoer;
    }

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
        return `_bgpg_${this.#index}`;
    }
    /**
     * Geef de dataset declaratie voor het top-level element
     */
    DataSet() {
        return `data-im="${this.#index}"`;
    }

    /**
     * Aangeroepen om de HTML voor de invoer te maken
     * @param {HTMLElement} container - Container element waarin de HTML geplaatst moet worden
     */
    Html() {
    }

    /**
     * Maakt de HTML voor een voegtoe knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    HtmlVoegToe(hint, idSuffix = '') {
        return `<span title="${hint}" id="${this.ElementPrefix()}${idSuffix}" ${this.DataSet()} class="voegtoe">&#x271A;</span>`;
    }
    /**
     * Maakt de HTML voor een edit knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    HtmlWerkBij(hint, idSuffix = '') {
        return `<span title="${hint}" id="${this.ElementPrefix()}${idSuffix}" ${this.DataSet()} class="werkbij">&#x270E;</span>`;
    }
    /**
     * Maakt de HTML voor een verwijder knop aan
     * @param {string} hint - Mouseover hint voor de knop
     * @param {string} idSuffix - Suffix voor de identificatie van de knop
     */
    HtmlVerwijder(hint, idSuffix = '') {
        return `<span title="${hint}" id="${this.ElementPrefix()}${idSuffix}" ${this.DataSet()} class="verwijder">&#x1F5D1;</span>`;
    }

    /**
     * Aangeroepen als er iets in de invoer is gewijzigd. Werkt standaard de specificatie bij en \
     * roept de OnChange van de superInvoer aan.
     * @param {HTMLElement} elt - element dat gewijzigd is; weggelaten als kind-invoermanager gewijzigd is
     */
    OnChange(elt) {
        this.WerkSpecificatieBij();
        if (this.#superInvoer !== undefined && this.#superInvoer !== undefined) {
            this.#superInvoer.OnChange();
        }
    }
    #superInvoer;

    /**
     * Aangeroepen als er op een element geklikt wordt. Doet standaard niets.
     * @param {HTMLElement} elt - element dat gewijzigd is
     */
    OnClick(elt) {
    }

    /**
     * Open een modal invoer box
     * @param {string} html - HTML voor de invoer
     * @param {lambda} onClose - Functie aangeroepen nadat box gesloten is; argument geeft aan of het via ok was (en niet cancel)
     */
    static OpenModal(html, onClose) {
        document.getElementById('_bgpg_modal_content').innerHTML = html;
        document.getElementById('_bgpg_modal').style.display = 'block';
        InvoerManager.#onModalClose = onClose;
    }
    static #onModalClose;

    /**
     * Sluit de modal invoer box
     * @param {any} accepteerInvoer - Geeft aan of het via ok was (en niet cancel)
     */
    static SluitModal(accepteerInvoer) {
        if (InvoerManager.#onModalClose !== undefined) {
            document.getElementById('_bgpg_modal').style.display = 'none';
            document.getElementById('_bgpg_modal_content').innerHTML = '';
            InvoerManager.#onModalClose(accepteerInvoer);
            InvoerManager.#onModalClose = undefined;
        }
    }
}


/*------------------------------------------------------------------------------
 *
 * InvoerManager voor de specificatie als geheel
 * 
 *----------------------------------------------------------------------------*/
class SpecificatieInvoerManager extends InvoerManager {
    /**
     * Maak de invoermanager aan
     * @param {any} data - In-memory specificatie
     * @param {HTMLElement} elt_data - HTML element van het form waarin de specificatie opgenomen moet worden
     * @param {HTMLElement} elt_startknop - HTML element van de startknop, de submit van het form
     * @param {HTMLElement} elt_download - HTML element van de download link
     */
    constructor(data, elt_data, elt_startknop, elt_download) {
        super(undefined, undefined, undefined, data);
        this.#elt_data = elt_data;
        this.#elt_startknop = elt_startknop;
        this.#elt_download = elt_download;
        this.WerkSpecificatieBij();
    }
    #elt_data;
    #elt_startknop;
    #elt_download;

    WerkSpecificatieBij() {
        if (this.Specificatie().Beschrijving || this.Specificatie().Projecten.length > 0 || this.Specificatie().Overig.length > 0) {
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
 * InvoerManager voor de startdatum en gemaaktOp.
 * 
 *----------------------------------------------------------------------------*/
class StartdatumInvoerManager extends InvoerManager {
    /**
     * Maak de invoermanager aan
     */
    constructor() {
        super(BGProcesGenerator.This().SpecificatieManager());
    }

    Specificatie() {
        return BGProcesGenerator.This().Startdatum();
    }

    IsValide() {
        return true;
    }

    Html() {
        return `<span ${this.DataSet()}>
        <input type="number" class="number2" min="1" max="31" id="${this.ElementPrefix()}_D" value="${this.Specificatie().getDate()}"/> -
        <input type="number" class="number2" min="1" max="12" id="${this.ElementPrefix()}_M" value="${this.Specificatie().getMonth() + 1}"/> -
        <input type="number" class="number4" min="2020" id="${this.ElementPrefix()}_J" value="${this.Specificatie().getFullYear()}"/>
        </span>`;
    }

    OnChange(elt) {
        let dag = (elt.id.endsWith('D') ? parseInt(elt.value) : this.Specificatie().getDate());
        let maand = (elt.id.endsWith('M') ? parseInt(elt.value) : this.Specificatie().getMonth() + 1);
        let jaar = (elt.id.endsWith('J') ? parseInt(elt.value) : this.Specificatie().getFullYear());
        let datum = new Date(jaar, maand - 1, dag);
        document.getElementById(`${this.ElementPrefix()}_D`).value = datum.getDate();
        document.getElementById(`${this.ElementPrefix()}_M`).value = datum.getMonth() + 1;
        document.getElementById(`${this.ElementPrefix()}_J`).value = datum.getFullYear();
        if (this.Specificatie() !== datum) {
            BGProcesGenerator.This().WerkTijdstippenBij(datum);
            super.OnChange();
        }
    }
}

class GemaaktOpInvoerManager extends InvoerManager {
    /**
     * Maak de invoermanager aan
     * @param {lambda} gemaaktOpIngevoerd - Functie die met het tijdstip aangeroepen moet worden na invoer
     */
    constructor(gemaaktOpIngevoerd) {
        super();
        this.#gemaaktOpIngevoerd = gemaaktOpIngevoerd;
    }
    #gemaaktOpIngevoerd;

    Html() {
        return this.HtmlVoegToe("Voeg een nieuwe activiteit toe");
    }

    OnChange(elt) {
        this.#aantalDagen = parseInt(elt.value);
    }
    #aantalDagen = 1;

    OnClick(elt) {
        if (elt.id == this.ElementPrefix()) {
            InvoerManager.OpenModal(`<div ${this.DataSet()}>
            <label for="${this.ElementPrefix()}_D">Aantal dagen sinds de startdatum: <input type="number" class="number4" min="1" id="${this.ElementPrefix()}_D" value="${this.#aantalDagen}"/>
            <br/>
            <label for="${this.ElementPrefix()}_T">Tijdstip op de dag: <input type="number" class="number2" min="0" max="23" id="${this.ElementPrefix()}_D" value="${this.#aantalDagen}"/>:00
            </div>`, (ok) => this.#GemaaktOpIngevoerd(ok));
        }
    }
    #GemaaktOpIngevoerd(ok) {
        if (ok) {
            this.#gemaaktOpIngevoerd(this.#aantalDagen);
        }
    }
}

/*------------------------------------------------------------------------------
 *
 * InvoerManagers voor teksten
 * 
 *----------------------------------------------------------------------------*/
class TitelInvoerManager extends InvoerManager {
    /**
     * Maak de invoermanager aan
     * @param {InvoerManager} superInvoer - InvoerManager voor eigenaarObject
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Index als eigenaarObject een array is
     */
    constructor(superInvoer, eigenaarObject, eigenschap) {
        super(superInvoer, eigenaarObject, eigenschap);
    }

    Specificatie() {
        return document.getElementById(this.ElementPrefix()).value.trim();
    }

    IsValide() {
        return this.Specificatie() ? true : false;
    }

    Html() {
        return `<input type="text" class="tekst" id="${this.ElementPrefix()}" ${this.DataSet()}>${super.Specificatie()}</textarea>`;
    }
}

class TekstInvoerManager extends InvoerManager {
    /**
     * Maak de invoermanager aan
     * @param {InvoerManager} superInvoer - InvoerManager voor eigenaarObject
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Index als eigenaarObject een array is
     */
    constructor(superInvoer, eigenaarObject, eigenschap) {
        super(superInvoer, eigenaarObject, eigenschap);
    }

    Specificatie() {
        return document.getElementById(this.ElementPrefix()).value.trim();
    }

    IsValide() {
        return this.Specificatie() ? true : false;
    }

    Html() {
        return `<textarea class="tekst" id="${this.ElementPrefix()}" ${this.DataSet()}>${super.Specificatie()}</textarea>`;
    }
}


/*------------------------------------------------------------------------------
 *
 * InvoerManager voor een van de momentopnamen
 * 
 *----------------------------------------------------------------------------*/
class MomentopnameInvoerManager extends InvoerManager {
    /**
     * Maak de invoermanager aan
     * @param {Momentopname} momentopname - Momentopname (al dan niet valide)
     */
    constructor(momentopname) {
        super();
        this.#momentopname = momentopname;
    }

    Momentopname() {
        return this.#momentopname;
    }
    #momentopname;

    Html() {
        return `<div id="${this.ElementPrefix()}">${this.#Html()}</div>`;
    }
    #Html() {
        if (this.#momentopname.IsValide()) {
            return this.HtmlWerkBij("Pas de momentopname aan", '_W') + ' - ' + this.HtmlVerwijder("Pas de momentopname aan", '_D');
        } else {
            return this.HtmlVoegToe("Voeg een nieuwe momentopname toe", '_N');
        }
    }

    OnChange(elt) {
        // NNTB
    }
    #nieuweMomentopname;

    OnClick(elt) {
        if (elt.id == this.ElementPrefix() + '_D') {
            this.#nieuweMomentopname = new Momentopname(this.#momentopname.EigenaarObject(), this.#momentopname.Eigenschap(), this.#momentopname.Doel(), this.#momentopname.GemaaktOp());
            InvoerManager.OpenModal(`Verwijder de momentopname?`, (ok) => this.#MomentopnameIngevoerd(ok));
        } else if (elt.id == this.ElementPrefix() + '_N' || elt.id == this.ElementPrefix() + '_W') {
            this.#nieuweMomentopname = this.#momentopname.Kloon();
            InvoerManager.OpenModal(`<span ${this.DataSet()}>
            NNTB
            </span>`, (ok) => this.#MomentopnameIngevoerd(ok));
        }
    }

    #MomentopnameIngevoerd(ok) {
        if (ok) {
            this.#momentopname = this.#nieuweMomentopname;
            document.getElementById(this.ElementPrefix()).innerHTML = this.#Html();
            this.MomentopnameGewijzigd();
        }
    }
    MomentopnameGewijzigd() {
    }
}

class UitgangspuntInvoerManager extends MomentopnameInvoerManager {
    /**
    * Maak de invoermanager aan
    * @param {Momentopname} uitgangssituatie - Generator
    */
    constructor(uitgangssituatie) {
        super(uitgangssituatie);
    }

    MomentopnameGewijzigd() {
    }
}
