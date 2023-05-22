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
        this.#uitgangssituatie = new Momentopname(this.#data.Uitgangssituatie, doel.Specificatie(), new GemaaktOp(undefined, 0, 0));
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

        if (data.Beschrijving) {
            bgpg.#data.Beschrijving = data.Beschrijving;
        }

        let instrumenten = {}; // vertaling van workId naar instrumenten

        if (data.Uitgangssituatie) {
            let prefix = '/join/id/proces/' + bgpg.BGCode() + '/';
            for (doel in Object.keys(data.Uitgangssituatie)) {
                if (doel === this.StartDoel()) {
                    this.WerkTijdstippenBij(new Date(parseInt(this.Specificatie().substring(0, 4)), parseInt(this.Specificatie().substring(4, 2)), parseInt(this.Specificatie().substring(6, 2))));
                    this.#uitgangssituatie.LeesSpecificatie(data.Uitgangssituatie[doel], instrumenten);
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

    /**
     * Manager van de gehele specificatie, te gebruiken om de specificatie
     * opnieuw te maken als er ergens iets wijzigt.
     */
    SpecificatieManager() {
        return this.#specManager;
    }
    #specManager;

    /**
     * Laatst gebruikte startdatum van het scenario
     */
    Startdatum() {
        return this.#startdatum;
    }
    #startdatum;

    /**
     * Geef de Identificatie van het doel van de uitgangssituatie
     */
    StartDoel() {
        return this.#uitgangssituatie.Doel();
    }
    #uitgangssituatie;

    /**
     * Geef een (gesorteerde) lijst met bekende instrumenten weer
     * @param {any} soortInstrument
     * @returns
     */
    Instrumenten(soortInstrument) {
        if (soortInstrument === undefined) {
            return instrumenten;
        } else {
            return instrumenten.filter(i => i.SoortInstrument().Naam() == soortInstrument.Naam());
        }
    }
    #instrumenten = [];

    /*--------------------------------------------------------------------------
     *
     * Interne administratie van gebruikte instrumenten
     *
     -------------------------------------------------------------------------*/

    /**
     * Maak een nieuw instrument
     * @param {SoortInstrument} soortInstrument - Soort instrument
     * @param {GemaaktOp} gemaaktOp - tijdstip van de momentopname waarvoor een versie van de regeling gemaakt wordt.
     */
    MaakNieuwInstrument(soortInstrument, gemaaktOp) {
        let instrument = new Instrument(soortInstrument, gemaaktOp);
        this.#instrumenten.push(instrument);
        this.#instrumenten.sort((a, b) => a.WorkId().Specificatie().localeCompare(b.WorkId().Specificatie()));
    }

    /**
     * Pas een functie toe op elke instrumentversie in de specificatie voor een instrument
     * @param {Instrument} instrument instrument waarvoor de instrumentversies opgevraagd moeten worden
     * @param {lambda} todo - Uit te voeren functie die de instrumentversie ontvangt
     */
    VoorElkeInstrumentversie(instrument, todo) {
        if (this.#data.Uitgangssituatie[this.StartDoel()] !== undefined) {
            let versie = this.#data.Uitgangssituatie[this.StartDoel()]._This.Instrumentversie(instrument);
            if (versie !== undefined) {
                todo(versie);
            }
        }
    }

    /**
     * Werk alle onderdelen van de specificatie bij als de startdatum verandert
     * @param {Date} datum - Nieuwe startdatum
     */
    WerkTijdstippenBij(datum) {
        this.#startdatum = datum;
        for (const instrument of this.#instrumenten) {
            instrument.WerkTijdstipBij(datum);
        }
        if (this.#data.Uitgangssituatie[this.StartDoel()] !== undefined) {
            this.#data.Uitgangssituatie[this.StartDoel()]._This.WerkTijdstipBij(datum);
        }
    }

    /*--------------------------------------------------------------------------
     *
     * UI ondersteuning
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
        for (let elt = elt_invoer; elt.id !== this.#spec_invoer.id; elt = elt.parentElement) {
            if (elt.dataset) {
                if (elt.dataset.im) {
                    let im = parseInt(elt.dataset.im);
                    handler(this.#invoer_managers[im], elt_invoer);
                }
            }
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
 * Nu volgen een aantal klassen die de informatie over de regelgeving 
 * en het versiebeheer modelleren. Te beginnen met een aantal algemene 
 * beheerklassen die voor de administratie nodig zijn. Deze moeten hier 
 * staan omdat javascript geen forward declaration van klassen kent.
 * 
 =============================================================================*/

/*------------------------------------------------------------------------------
 *
 * SpecificatieElement is een basisklasse voor een object dat een deel van 
 * de specificatie kan manipuleren.
 * 
 *----------------------------------------------------------------------------*/
class SpecificatieElement {
    /**
     * Maak een beheerobject aan
     * @param {any} eigenaarObject - Object of array waar dit een eigenschap van is
     * @param {string} eigenschap - Eigenschap waaraan dit element toegekend wordt. Als eigenaarObject een array is, laat dit dan leeg.
     * @param {any} data - In-memory object voor het element. Mag weggelaten worden als Specificatie() geïmplementeerd wordt.
     */
    constructor(eigenaarObject, eigenschap, data) {
        this.#eigenaarObject = eigenaarObject;
        this.#eigenschap = eigenschap;
        if (data !== undefined) {
            this.#data = data;
        }
        else if (eigenaarObject !== undefined && eigenschap !== undefined) {
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
            if (this.#eigenschap === undefined) {
                let idx = this.#eigenaarObject.indexOf(this.#data);
                if (this.IsValide()) {
                    if (idx < 0) {
                        this.#eigenaarObject.push(this.#data);
                    }
                } else if (idx >= 0) {
                    delete this.#eigenaarObject[idx];
                }
            }
            else {
                if (this.IsValide()) {
                    this.#eigenaarObject[this.#eigenschap] = this.Specificatie();
                } else if (this.#eigenaarObject[this.#eigenschap] !== undefined) {
                    delete this.#eigenaarObject[this.#eigenschap];
                }
            }
        }
    }

    /**
     * Verwijder de waarde uit de specificatie
     */
    Verwijder() {
        if (this.#eigenaarObject !== undefined) {
            if (this.#eigenschap === undefined) {
                let idx = this.#eigenaarObject.indexOf(this.#data);
                if (idx >= 0) {
                    delete this.#eigenaarObject[idx];
                }
            }
            else {
                delete this.#eigenaarObject[this.#eigenschap];
            }
        }
    }
}

/*------------------------------------------------------------------------------
 *
 * Identificatie is een klasse die helpt om op deze pagina met korte
 * identifiers te kunnen werken terwijl de specificatie met lange identifiers
 * werkt.
 * 
 *----------------------------------------------------------------------------*/
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

    /**
     * Verander de prefix van de identificatie
     * @param {string} prefix - De prefix om van de afkorting naar de volledige identificatie te komen
     */
    PrefixWordt(prefix) {
        this.#prefix = prefix;
        if (this.#afkorting === undefined) {
            this.SpecificatieWordt();
        } else {
            this.SpecificatieWordt(this.#prefix + this.#afkorting);
        }
    }
    #prefix;

    /**
     * Geeft de afkorting van de identificatie
     */
    Afkorting() {
        return this.#afkorting;
    }
    /**
     * Pas de afkorting van de identificatie aan
     * @param {string} afkorting - De korte naam voor de identificatie
     */
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

/*------------------------------------------------------------------------------
 *
 * GemaaktOp is een gemaaktOp tijdstip dat op deze pagina als aantal dagen
 * sinds de start en de tijd getoond wordt.
 * 
 *----------------------------------------------------------------------------*/
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

    /**
     * Geeft het aantal dagen na de start van het scenario
     */
    Dag() {
        return this.#dag;
    }
    #dag;

    /**
     * Geeft het aantal uren op de dag
s     */
    Uur() {
        return this.#uur;
    }
    #uur;

    /**
     * Pas het tijdstip aan
     * @param {int} dag - Aantal dagen na de start van het scenario; optioneel
     * @param {int} uur - Aantal uren in de dag; optioneel
     */
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
            if (this.#uur < 0) {
                this.#uur = 0;
            }
            else if (this.#uur > 23) {
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
    /**
     * Werk het tijdstip bij als de startdatum van het scenario wijzigt
     * @param {Date} startdatum
     */
    WerkTijdstipBij(startdatum) {
        let tijdstip = new Date(startdatum.getFullYear(), startdatum.getMonth(), startdatum.getDate() + this.#dag, this.#uur);
        this.SpecificatieWordt(`${tijdstip.getFullYear()}${('0' + (tijdstip.getMonth() + 1)).slice(-2)}${('0' + tijdstip.getDate()).slice(-2)}T${('0' + tijdstip.getHours()).slice(-2)}:00:00Z`);
    }
}

/*==============================================================================
 *
 * Instrument en gerelateerde klassen geven alle informatie over de instrumenten
 * die door deze pagina ondersteund worden.
 * 
 =============================================================================*/
class SoortAnnotatie {
    /**
     * De citeertitel zoals die in de metadata voorkomt. De simulator bevat niet
     * alle metadata velden, voor de uitleg van het principe van annotaties is dat
     * niet nodig.
     */
    static Citeertitel() {
        return "Metadata_Citeertitel";
    }
    /**
     * De Toelichtingrelaties relateren de toelichting aan de tekst van de regeling.
     */
    static Toelichtingrelaties() {
        return "Toelichtingrelaties";
    }
    /**
     * De symbolisatie geeft aan hoe een GIO weergegeven moet worden.
     */
    static Symbolisatie() {
        return "Symbolisatie";
    }
}

/**
 * Basisklasse met informatie over een soort instrument.
 * De details worden per soort instrument in een afgeleide klasse vastgelegd.
 * Hardcoded is dat een informatieobject altijd gerelateerd moet zijn aan 
 * dezelfde (geboorte)regeling. De simulator kan ook met informatieobjecten
 * omgaan die bij meerdere regelingen horen, deze pagina niet.
 */
class SoortInstrument {

    /**
     * Geef de naam van het soort instrument
     */
    Naam() {
        throw new Error('Naam ontbreekt');
    }

    /**
    * Maak een unieke afkorting voor een nieuw instrument
    */
    MaakAfkorting() {
        throw new Error('MaakAfkorting ontbreekt');
    }
    /**
     * Reset alle indices gebruikt voor MaakAfkorting
     */
    static ResetIndex() {
        Regeling.ResetIndex();
        GIO.ResetIndex();
        PDF.ResetIndex();
    }

    /**
     * Maak de prefix nodig om een Identificatie voor een work identificatie 
     * voor een instrument te maken.
     * @param {string} gemaaktOp - Volledig tijdstip van uitwisseling
     * @returns Prefix te gebruiken in de constructor van Identificatie
     */
    MaakWorkIdPrefix(gemaaktOp) {
        throw new MaakWorkIdPrefix('Naam ontbreekt');
    }

    /**
     * Maak de prefix nodig om een Identificatie voor een expression identificatie 
     * voor een instrumentversie te maken.
     * @param {string} workId - Volledige identificatie van het instrument als work
     * @param {string} gemaaktOp - Volledig tijdstip van uitwisseling
     * @returns Prefix te gebruiken in de constructor van Identificatie
     */
    MaakExpressionIdPrefix(workId, gemaaktOp) {
        return workId + '@' + gemaaktOp.substring(0, 4) + ';';
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

class Regeling extends SoortInstrument {
    /**
     * Geef de naam van het soort instrument
     */
    Naam() {
        return "Regeling";
    }

    /**
    * Maak een unieke afkorting voor een nieuw instrument
    */
    MaakAfkorting() {
        Regeling.#index += 1;
        return `reg_${Regeling.#index}`;
    }
    /**
     * Reset de index gebruikt voor MaakAfkorting
     */
    static ResetIndex() {
        Regeling.#index = 0;
    }
    static #index = 0;

    /**
     * Maak de prefix nodig om een Identificatie voor een work identificatie 
     * voor een instrument te maken.
     * @param {string} gemaaktOp - Volledig tijdstip van uitwisseling
     * @returns Prefix te gebruiken in de constructor van Identificatie
     */
    MaakWorkIdPrefix(gemaaktOp) {
        return '/akn/nl/act/' + BGProcesGenerator.This().BGCode() + '/' + gemaaktOp.substring(0, 4) + '/';
    }

    /**
     * Maak de prefix nodig om een Identificatie voor een expression identificatie 
     * voor een instrumentversie te maken.
     * @param {string} workId - Volledige identificatie van het instrument als work
     * @param {string} gemaaktOp - Volledig tijdstip van uitwisseling
     * @returns Prefix te gebruiken in de constructor van Identificatie
     */
    MaakExpressionIdPrefix(workId, gemaaktOp) {
        return workId + '/nl@' + gemaaktOp.substring(0, 4) + ';';
    }

    /**
     * Geeft een lijst met de STOP annotaties die voor dit instrument zijn toegestaan
     */
    ToegestaneAnnotaties() {
        return [SoortAnnotatie.Citeertitel(), SoortAnnotatie.Toelichtingrelaties()];
    }

    /**
     * Geeft aan of non-STOP annotaties zijn toegestaan
     */
    NonSTOPAnnotatiesToegestaan() {
        return false;
    }
}

class GIO extends SoortInstrument {
    /**
     * Geef de naam van het soort instrument
     */
    Naam() {
        return "Geo-informatieobject";
    }

    /**
    * Maak een unieke afkorting voor een nieuw instrument
    */
    MaakAfkorting() {
        GIO.#index += 1;
        return `gio_${GIO.#index}`;
    }
    /**
     * Reset de index gebruikt voor MaakAfkorting
     */
    static ResetIndex() {
        GIO.#index = 0;
    }
    static #index = 0;

    /**
     * Maak de prefix nodig om een Identificatie voor een work identificatie 
     * voor een instrument te maken.
     * @param {string} gemaaktOp - Volledig tijdstip van uitwisseling
     * @returns Prefix te gebruiken in de constructor van Identificatie
     */
    MaakWorkIdPrefix(gemaaktOp) {
        return '/join/regdata/' + BGProcesGenerator.This().BGCode() + '/' + gemaaktOp.substring(0, 4) + '/';
    }

    /**
     * Geeft een lijst met de STOP annotaties die voor dit instrument zijn toegestaan
     */
    ToegestaneAnnotaties() {
        return [SoortAnnotatie.Citeertitel(), SoortAnnotatie.Symbolisatie()];
    }
}

class PDF extends SoortInstrument {
    /**
     * Geef de naam van het soort instrument
     */
    Naam() {
        return "Geo-informatieobject";
    }

    /**
    * Maak een unieke afkorting voor een nieuw instrument
    */
    MaakAfkorting() {
        PDF.#index += 1;
        return `pdf_${PDF.#index}`;
    }
    /**
     * Reset de index gebruikt voor MaakAfkorting
     */
    static ResetIndex() {
        PDF.#index = 0;
    }
    static #index = 0;

    /**
     * Maak de prefix nodig om een Identificatie voor een work identificatie 
     * voor een instrument te maken.
     * @param {string} gemaaktOp - Volledig tijdstip van uitwisseling
     * @returns Prefix te gebruiken in de constructor van Identificatie
     */
    MaakWorkIdPrefix(gemaaktOp) {
        return '/join/regdata/' + BGProcesGenerator.This().BGCode() + '/' + gemaaktOp.substring(0, 4) + '/';
    }

    /**
     * Geeft een lijst met de STOP annotaties die voor dit instrument zijn toegestaan
     */
    ToegestaneAnnotaties() {
        return [SoortAnnotatie.Citeertitel()];
    }
}

/**
 * Een instrument staat voor een regeling of informatieobject (als work)
 */
class Instrument {
    /**
     * Maak een nieuw instrument aan
     * @param {SoortInstrument} soortInstrument - Soort instrument
     * @param {GemaaktOp} gemaaktOp - tijdstip van de momentopname waar de eerste versie van het instrument voorkomt
     */
    constructor(soortInstrument, gemaaktOp) {
        this.#soortInstrument = soortInstrument;
        this.#workId = new Identificatie(undefined, undefined, soortInstrument.MaakWorkIdPrefix(gemaaktOp.Specificatie()), soortInstrument.MaakAfkorting());
        this.#eerstGemaaktOp = gemaaktOp;
    }

    /**
     * Geeft aan welk soort instrument het is
     */
    SoortInstrument() {
        return this.#soortInstrument;
    }
    #soortInstrument;

    /**
     * Geeft de Identificatie van het instrument
     */
    WorkId() {
        return this.#workId;
    }
    #workId;

    /**
     * Maak de prefix voor gebruik in de Identificatie voor een instrumentversie die onderdeel is van een momentopname.
     * @param {Momentopname} momentopname - Momentopname waarvoor de prefix gemaakt wordt
     * @returns prefix
     */
    MaakExpressionIdPrefix(momentopname) {
        return this.#soortInstrument.MaakExpressionIdPrefix(this.#workId.Specificatie(), momentopname.GemaaktOp().Specificatie());
    }

    /**
     * Geeft aan dat een versie van het instrument gemaakt/gewijzigd wordt in een momentopname
     * @param {GemaaktOp} gemaaktOp - tijdstip van de momentopname
     */
    HeeftVersieInMomentopname(gemaaktOp) {
        if (this.#eerstGemaaktOp === undefined || this.#eerstGemaaktOp.Vergelijk(gemaaktOp) > 0) {
            this.#eerstGemaaktOp = gemaaktOp;
            this.#workId.PrefixWordt(this.#soortInstrument.MaakWorkIdPrefix(gemaaktOp.Specificatie()))
            BGProcesGenerator.This().VoorElkeInstrumentversie(this, (versie) => versie.WerkIdentificatieBij());
        }
    }
    /**
     * Werk de identificatie bij als de startdatum van het scenario is aangepast
     * @param {Date} startdatum
     */
    WerkTijdstipBij(startdatum) {
        this.#eerstGemaaktOp.WerkTijdstipBij(startdatum);
        this.#workId.PrefixWordt(this.#soortInstrument.MaakWorkIdPrefix(this.#eerstGemaaktOp.Specificatie()))
    }

    /**
     * Op een aantal momenten wordt het gebruik van het instrument opnieuw bepaald en afkortingen herzien op 
     * basis van eerste voorkomen.
     * ResetGebruik moet aangeroepen worden aan het begin van dat proces.
     */
    ResetGebruik() {
        this.#eerstGemaaktOp = undefined;
    }
    /**
     * Geeft aan of het instrument nog gebruikt wordt
     */
    InGebruikt() {
        return this.#eerstGemaaktOp !== undefined;
    }
    #eerstGemaaktOp;
    /**
     * Maak opnieuw de afkorting voor het workId
     */
    MaakAfkorting() {
        this.#workId.AfkortingWordt(this.#soortInstrument.MaakAfkorting());
    }
}

/*==============================================================================
 *
 * Versiebeheerinformatie. Momentopname geeft aan voor welke instrumenten
 * en evt annotaties een nieuwe versie voor de momentopname wordt gemaakt.
 * Deze pagina kent vervolgens zelf nummers toe. Momentopnamen worden per 
 * branch per project georganiseerd (en voor de uitgangssituatie).
 * 
 =============================================================================*/

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
     * @param {GemaaktOp} gemaaktOp - tijdstip waarop de momentopname is gemaakt
     * @param {string} code - korte naam van de actie waarvoor de momentopname wordt toegepast, voor gebruik in instrumentversies
     */
    constructor(branch, index, gemaaktOp, code) {
        super(branch, index, {
            gemaaktOp: gemaaktOp,
            Instrumentversies: []
        });
        this.Specificatie()._This = this;
        this.#gemaaktOp = new GemaaktOp(this.Specificatie(), gemaaktOp.Dag(), gemaaktOp.Uur());
        this.#code = code;
    }

    LeesSpecificatie(data, instrumenten) {
        if (data.Instrumentversies !== undefined) {
            for (const versie of data.Instrumentversies) {
                Instrumentversie.LeesSpecificatie(this, versie, instrumenten);
            }
        }
    }

    /**
     * Maak een kloon van de momentopname voor wijzigen in de UI
     */
    Kloon() {
        let kloon = new Momentopname(this.EigenaarObject(), this.Eigenschap(), this.#gemaaktOp, this.#code);
        for (const versie of this.Specificatie().Instrumentversies) {
            kloon.Instrumentversies.push(versie.Kloon());
        }
        kloon.Specificatie().Instrumentversies.sort((a, b) => a.ExpressionId.Specificatie().localeCompare(b.ExpressionId.Specificatie()));
    }

    GemaaktOp() {
        return this.#gemaaktOp;
    }
    #gemaaktOp;

    Code() {
        return this.#code;
    }
    /**
     * Als onderdeel van het auto-nummeren kan de code wijzigen. Pas de nieuwe code toe
     * @param {any} code
     */
    CodeWordt(code) {
        this.#code = code;
        this.#WerkIdentificatiesBij();
    }
    #code;

    /**
     * Geeft de instrumentversie voor het instrument, indien aanwezig
     * @param {Instrument} instrument
     */
    Instrumentversie(instrument) {
        for (const versie of this.Specificatie().Instrumentversies) {
            if (versie.Instrument() === instrument) {
                return versie;
            }
        }
    }

    /**
     * Geeft aan of de in-memory Data valide is en onderdeel kan zijn van de specificatie
     */
    IsValide() {
        return this.Specificatie().Instrumentversies.length > 0;
    }

    /**
     * Werk de specificatie bij als de startdatum verandert
     * @param {Date} datum - Nieuwe startdatum
     */
    WerkTijdstipBij(datum) {
        this.#gemaaktOp.WerkTijdstipBij(datum);
        this.#WerkIdentificatiesBij();
    }

    /**
     * Werk de identificaties van de instrumentversies bij
     */
    #WerkIdentificatiesBij() {
        for (const versie of this.Specificatie().Instrumentversies) {
            versie.WerkIdentificatieBij();
        }
    }
}

/*------------------------------------------------------------------------------
 *
 * Instrumentversie geeft aan dat voor een momentopname een nieuwe 
 * versie voor een instrument wordt gemaakt, en ook of de annotaties wijzigen.
 * 
 *----------------------------------------------------------------------------*/
class Instrumentversie extends SpecificatieElement {
    /**
     * Maak een nieuwe instrumentversie
     * @param {Momentopname} momentopname - momentopname waarvoor deze instrumentversie wordt gemaakt.
     * @param {Instrument} instrument - instrument waarvan dit een instrumentversie is
     */
    constructor(momentopname, instrument) {
        super(momentopname.Specificatie().Instrumentversies, undefined, {
            ExpressionId: undefined,
            Annotaties: {}
        });
        this.#momentopname = momentopname;
        this.#instrument = instrument;
        this.#expressionId = new Identificatie(this.Specificatie(), 'ExpressionId', instrument.MaakExpressionIdPrefix(momentopname), momentopname.Code());
        if (instrument.NonSTOPAnnotatiesToegestaan()) {
            this.Specificatie().NonSTOP = {};
        }
    }

    /**
     * Maak een kloon van de instrumentversie voor wijzigen in de UI
     */
    Kloon() {
        let kloon = new Instrumentversie(this.#momentopname, this.#instrument);
        for (const annotatie of instrument.ToegestaneAnnotaties()) {
            let data = this.Specificatie()[annotatie];
            if (data !== undefined) {
                kloon.Specificatie()[annotatie] = data;
            }
        }
        if (instrument.NonSTOPAnnotatiesToegestaan() && this.Specificatie()[NonSTOP] !== undefined) {
            kloon.Specificatie()[NonSTOP] = { ...this.Specificatie()[NonSTOP] };
        }
        return kloon;
    }

    /**
     * Lees de momentopname uit de specificatie
     * @param {Momentopname} momentopname - momentopname waarvan de specificaties ingelezen worden
     * @param {any} data - specificatie van de instrumentversie
     * @param {any} instrumenten - vertaaltabel om de juiste Instrument te vinden bij een work-ID.
     * @returns de instrumentversie
     */
    static LeesSpecificatie(momentopname, data, instrumenten) {
        if (data.ExpressionId) {
            let idx = data.ExpressionId.indexOf('@');
            if (idx >= 0) {
                let workId = data.ExpressionId.substring(0, idx);
                let instrument = instrumenten[workId];
                if (instrument === undefined) {
                    if (workId.startsWith('/akn/')) {
                        instrument = BGProcesGenerator.This().MaakNieuwInstrument(new Regeling(), momentopname.GemaaktOp());
                    } else {
                        idx = workId.lastIndexOf('/');
                        workId = workId.substring(idx + 1);
                        if (workId.startsWith('gio')) {
                            instrument = BGProcesGenerator.This().MaakNieuwInstrument(new GIO(), momentopname.GemaaktOp());
                        }
                        else if (workId.startsWith('pdf')) {
                            instrument = BGProcesGenerator.This().MaakNieuwInstrument(new PDF(), momentopname.GemaaktOp());
                        }
                    }
                }
                if (instrument !== undefined) {
                    let versie = new Instrumentversie(momentopname, instrument);
                    for (const annotatie of instrument.ToegestaneAnnotaties()) {
                        if (data[annotatie]) {
                            versie.Specificatie()[annotatie] = data[annotatie];
                        }
                    }
                    if (instrument.NonSTOPAnnotatiesToegestaan() && data[NonSTOP] !== undefined) {
                        for (const objIdx in data.NonSTOP) {
                            versie.Specificatie().NonSTOP[objIdx] = (data.NonSTOP[objIdx] ? true : false);
                        }
                    }
                    return versie;
                }
            }
        }
        throw new Error('Instrumentversie van instrument "' + instrument.Code + '" voor gemaaktOp = ' + gemaaktOp + ' heeft geen (herkenbare) ExpressionId');
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
     * Geeft het volledige expression-ID als Identificatie van de 
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

    /**
     * Werk de expressionId bij omdat er iets gewijzigd is aan de momentopname
     */
    WerkIdentificatieBij() {
        this.#expressionId.PrefixWordt(this.#instrument.MaakExpressionIdPrefix(this.#momentopname));
        this.#expressionId.AfkortingWordt(this.#momentopname.Code());
    }
    #momentopname;
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
            let json = JSON.stringify(this.Specificatie(), SpecificatieInvoerManager.#ObjectFilter, 4).trim();
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
            let all = Object.values(value);
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
