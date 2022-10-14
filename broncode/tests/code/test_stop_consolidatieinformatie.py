#======================================================================
# Unit tests voor Python code in stop_consolidatieinformatie.py
#======================================================================
import unittest

import xml.etree.ElementTree as ET

import test_init
from stop_consolidatieinformatie import ConsolidatieInformatie, Doel
from applicatie_meldingen import Meldingen

class Test_stop_consolidatieinformatie(unittest.TestCase):
#======================================================================
# Lezen van XML
#======================================================================

#----------------------------------------------------------------------
# Lezen van XML : BeoogdInstrument
#----------------------------------------------------------------------
    def test_Lees_BeoogdeRegeling_variant1(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <BeoogdeRegelgeving>
    <BeoogdeRegeling>
      <doelen>
        <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      </doelen>
      <instrumentVersie>/akn/nl/act/gm9999/2020/REG0001/nld@2020-01-15;1</instrumentVersie>
      <eId>art_I</eId>
    </BeoogdeRegeling>
  </BeoogdeRegelgeving>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'BeoogdeVersies', "2022-05-13T07:00:00Z")
        self.assertEqual ("2022-05-13", element.BekendOp ())
        self.assertEqual ("2022-05-13", element.ConsolidatieInformatie.OntvangenOp)
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001", element.WorkId)
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001/nld@2020-01-15;1", element.ExpressionId)
        self.assertEqual (1, len (element.Doelen))
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doelen[0].Identificatie)
        self.assertEqual (0, len (element.Basisversies))
        self.assertEqual (0, len (element.OntvlochtenVersies))
        self.assertEqual (0, len (element.VervlochtenVersies))

    def test_Lees_BeoogdeRegeling_variant2(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <BeoogdeRegelgeving>
    <BeoogdeRegeling>
      <doelen>
        <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
        <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan2</doel>
      </doelen>
      <instrumentVersie>/akn/nl/act/gm9999/2020/REG0001/nld@2020-01-15;1</instrumentVersie>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
        <VervlochtenVersie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanVervlochtenVersie</doel>
          <gemaaktOp>2020-02-18T10:00:00Z</gemaaktOp>
        </VervlochtenVersie>
        <OntvlochtenVersie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanOntvlochtenVersie</doel>
          <gemaaktOp>2020-02-18T11:00:00Z</gemaaktOp>
        </OntvlochtenVersie>
      </gemaaktOpBasisVan>
      <bekendOp>2022-01-01</bekendOp>
    </BeoogdeRegeling>
  </BeoogdeRegelgeving>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'BeoogdeVersies', "2022-05-13T07:00:00Z")
        self.assertEqual ("2022-01-01", element.BekendOp ())
        self.assertEqual ("2022-05-13", element.ConsolidatieInformatie.OntvangenOp)
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001", element.WorkId)
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001/nld@2020-01-15;1", element.ExpressionId)
        self.assertEqual (2, len (element.Doelen))
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doelen[0].Identificatie)
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan2", element.Doelen[1].Identificatie)
        self.assertEqual (1, len (element.Basisversies))
        doel = Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanBasis")
        self.assertEqual (True, doel in element.Basisversies)
        self.assertEqual ("/join/id/proces/gm9999/2020/OmgevingsplanBasis", element.Basisversies[doel].Doel.Identificatie)
        self.assertEqual ("2020-02-28T09:00:00Z", element.Basisversies[doel].GemaaktOp)
        self.assertEqual (1, len (element.OntvlochtenVersies))
        doel = Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanOntvlochtenVersie")
        self.assertEqual (True, doel in element.OntvlochtenVersies)
        self.assertEqual ("/join/id/proces/gm9999/2020/OmgevingsplanOntvlochtenVersie", element.OntvlochtenVersies[doel].Doel.Identificatie)
        self.assertEqual ("2020-02-18T11:00:00Z", element.OntvlochtenVersies[doel].GemaaktOp)
        self.assertEqual (1, len (element.VervlochtenVersies))
        doel = Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanVervlochtenVersie")
        self.assertEqual (True, doel in element.VervlochtenVersies)
        self.assertEqual ("/join/id/proces/gm9999/2020/OmgevingsplanVervlochtenVersie", element.VervlochtenVersies[doel].Doel.Identificatie)
        self.assertEqual ("2020-02-18T10:00:00Z", element.VervlochtenVersies[doel].GemaaktOp)

    def test_Lees_BeoogdeRegeling_variant3(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <BeoogdeRegelgeving>
    <BeoogdeRegeling>
      <doelen>
        <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
        <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan2</doel>
      </doelen>
      <instrumentVersie>/akn/nl/act/gm9999/2020/REG0001/nld@2020-01-15;1</instrumentVersie>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis2</doel>
          <gemaaktOp>2020-02-28T10:00:00Z</gemaaktOp>
        </Basisversie>
        <VervlochtenVersie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanVervlochtenVersie</doel>
          <gemaaktOp>2020-02-18T10:00:00Z</gemaaktOp>
        </VervlochtenVersie>
        <VervlochtenVersie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanVervlochtenVersie2</doel>
          <gemaaktOp>2020-02-18T11:00:00Z</gemaaktOp>
        </VervlochtenVersie>
        <OntvlochtenVersie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanOntvlochtenVersie</doel>
          <gemaaktOp>2020-02-18T11:00:00Z</gemaaktOp>
        </OntvlochtenVersie>
        <OntvlochtenVersie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanOntvlochtenVersie2</doel>
          <gemaaktOp>2020-02-18T12:00:00Z</gemaaktOp>
        </OntvlochtenVersie>
      </gemaaktOpBasisVan>
    </BeoogdeRegeling>
  </BeoogdeRegelgeving>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'BeoogdeVersies', "2022-05-13T07:00:00Z")
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001", element.WorkId)
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001/nld@2020-01-15;1", element.ExpressionId)
        self.assertEqual (2, len (element.Doelen))
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doelen[0].Identificatie)
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan2", element.Doelen[1].Identificatie)
        self.assertEqual (2, len (element.Basisversies))
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanBasis") in element.Basisversies)
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanBasis2") in element.Basisversies)
        self.assertEqual (2, len (element.OntvlochtenVersies))
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanOntvlochtenVersie") in element.OntvlochtenVersies)
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanOntvlochtenVersie2") in element.OntvlochtenVersies)
        self.assertEqual (2, len (element.VervlochtenVersies))
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanVervlochtenVersie") in element.VervlochtenVersies)
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanVervlochtenVersie2") in element.VervlochtenVersies)

    def test_Lees_BeoogdeRegeling_fout_geen_doel(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <BeoogdeRegelgeving>
    <BeoogdeRegeling>
      <instrumentVersie>/akn/nl/act/gm9999/2020/REG0001/nld@2020-01-15;1</instrumentVersie>
      <eId>art_I</eId>
    </BeoogdeRegeling>
  </BeoogdeRegelgeving>
</ConsolidatieInformatie>''')

    def test_Lees_BeoogdeRegeling_fout_geen_instrumentversie(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <BeoogdeRegelgeving>
    <BeoogdeRegeling>
      <doelen>
        <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      </doelen>
      <eId>art_I</eId>
    </BeoogdeRegeling>
  </BeoogdeRegelgeving>
</ConsolidatieInformatie>''')

    def test_Lees_BeoogdeRegeling_fout_geen_regeling(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <BeoogdeRegelgeving>
    <BeoogdeRegeling>
      <doelen>
        <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      </doelen>
      <instrumentVersie>/join/id/regdata/2022/io001@2022</instrumentVersie>
      <eId>art_I</eId>
    </BeoogdeRegeling>
  </BeoogdeRegelgeving>
</ConsolidatieInformatie>''')

    def test_Lees_BeoogdInformatieobject(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <BeoogdeRegelgeving>
    <BeoogdInformatieobject>
      <doelen>
        <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      </doelen>
      <instrumentVersie>/join/id/regdata/2022/io001@2022</instrumentVersie>
      <eId>art_I</eId>
    </BeoogdInformatieobject>
  </BeoogdeRegelgeving>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'BeoogdeVersies', "2022-05-13T07:00:00Z")
        self.assertEqual ("/join/id/regdata/2022/io001", element.WorkId)
        self.assertEqual ("/join/id/regdata/2022/io001@2022", element.ExpressionId)
        self.assertEqual (1, len (element.Doelen))
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doelen[0].Identificatie)
        self.assertEqual (0, len (element.Basisversies))
        self.assertEqual (0, len (element.OntvlochtenVersies))
        self.assertEqual (0, len (element.VervlochtenVersies))

    def test_Lees_BeoogdInformatieobject_fout_geen_io(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <BeoogdeRegelgeving>
    <BeoogdInformatieobject>
      <doelen>
        <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      </doelen>
      <instrumentVersie>/akn/nl/act/gm9999/2020/REG0001/nld@2020-01-15;1</instrumentVersie>
      <eId>art_I</eId>
    </BeoogdInformatieobject>
  </BeoogdeRegelgeving>
</ConsolidatieInformatie>''')

#----------------------------------------------------------------------
# Lezen van XML : Terugtrekking instrument
#----------------------------------------------------------------------
    def test_Lees_TerugtrekkingBeoogdeRegeling(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingRegeling>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </TerugtrekkingRegeling>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'Terugtrekkingen', "2022-05-13T07:00:00Z")
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001", element.WorkId)
        self.assertEqual (1, len (element.Doelen))
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doelen[0].Identificatie)
        self.assertEqual (1, len (element.Basisversies))
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanBasis") in element.Basisversies)

    def test_Lees_TerugtrekkingBeoogdeRegeling_fout_geen_doel(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingRegeling>
      <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </TerugtrekkingRegeling>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_TerugtrekkingBeoogdeRegeling_fout_geen_instrument(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingRegeling>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </TerugtrekkingRegeling>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_TerugtrekkingBeoogdeRegeling_fout_geen_Basisversie(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingRegeling>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
      </gemaaktOpBasisVan>
    </TerugtrekkingRegeling>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_TerugtrekkingBeoogdeRegeling_fout_geen_gemaaktOpBasisVan(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingRegeling>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
      <eId>art_I</eId>
    </TerugtrekkingRegeling>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_TerugtrekkingBeoogdeRegeling_fout_geen_regeling(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingRegeling>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/join/id/regdata/2022/io001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </TerugtrekkingRegeling>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_TerugtrekkingBeoogdInformatieobject(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingInformatieobject>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/join/id/regdata/2022/io001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </TerugtrekkingInformatieobject>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'Terugtrekkingen', "2022-05-13T07:00:00Z")
        self.assertEqual ("/join/id/regdata/2022/io001", element.WorkId)
        self.assertEqual (1, len (element.Doelen))
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doelen[0].Identificatie)
        self.assertEqual (1, len (element.Basisversies))
        self.assertTrue (Doel.DoelInstantie ("/join/id/proces/gm9999/2020/OmgevingsplanBasis") in element.Basisversies)

    def test_Lees_TerugtrekkingBeoogdInformatieobject_fout_geen_io (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingInformatieobject>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </TerugtrekkingInformatieobject>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')

#----------------------------------------------------------------------
# Lezen van XML : Intrekking instrument + terugtrekking intrekking
#----------------------------------------------------------------------
    def test_Lees_IntrekkingRegeling(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Intrekkingen>
    <Intrekking>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </Intrekking>
  </Intrekkingen>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'Intrekkingen', "2022-05-13T07:00:00Z")
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001", element.WorkId)
        self.assertEqual (1, len (element.Doelen))
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doelen[0].Identificatie)
        self.assertEqual (1, len (element.Basisversies))
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanBasis") in element.Basisversies)

    def test_Lees_IntrekkingInformatieobject(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Intrekkingen>
    <Intrekking>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/join/id/regdata/2022/io001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </Intrekking>
  </Intrekkingen>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'Intrekkingen', "2022-05-13T07:00:00Z")
        self.assertEqual ("/join/id/regdata/2022/io001", element.WorkId)
        self.assertEqual (1, len(element.Doelen))
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doelen[0].Identificatie)
        self.assertEqual (1, len (element.Basisversies))
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanBasis") in element.Basisversies)

    def test_Lees_Intrekking_fout_geen_regeling_of_io(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Intrekkingen>
    <Intrekking>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>huh</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </Intrekking>
  </Intrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_Intrekking_fout_geen_doel(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Intrekkingen>
    <Intrekking>
      <instrument>/join/id/regdata/2022/io001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </Intrekking>
  </Intrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_Intrekking_fout_geen_instrument(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Intrekkingen>
    <Intrekking>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </Intrekking>
  </Intrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_Intrekking_fout_geen_gemaaktOpBasisVan(self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Intrekkingen>
    <Intrekking>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/join/id/regdata/2022/io001</instrument>
      <eId>art_I</eId>
    </Intrekking>
  </Intrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_TerugtrekkingIntrekking(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingIntrekking>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
      <eId>art_I</eId>
      <gemaaktOpBasisVan>
        <Basisversie>
          <doel>/join/id/proces/gm9999/2020/OmgevingsplanBasis</doel>
          <gemaaktOp>2020-02-28T09:00:00Z</gemaaktOp>
        </Basisversie>
      </gemaaktOpBasisVan>
    </TerugtrekkingIntrekking>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'TerugtrekkingenIntrekking', "2022-05-13T07:00:00Z")
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001", element.WorkId)
        self.assertEqual (1, len (element.Doelen))
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doelen[0].Identificatie)
        self.assertEqual (1, len (element.Basisversies))
        self.assertTrue (Doel.DoelInstantie("/join/id/proces/gm9999/2020/OmgevingsplanBasis") in element.Basisversies)

#----------------------------------------------------------------------
# Lezen van XML : Tijdstempels
#----------------------------------------------------------------------
    def test_Lees_JuridischWerkendVanaf(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Tijdstempels>
    <Tijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <soortTijdstempel>juridischWerkendVanaf</soortTijdstempel>
      <datum>2020-02-01</datum>
      <eId>art_II</eId>
    </Tijdstempel>
  </Tijdstempels>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'Tijdstempels', "2022-05-13T07:00:00Z")
        self.assertEqual ("2022-05-13", element.BekendOp ())
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doel.Identificatie)
        self.assertEqual (False, element.IsGeldigVanaf)
        self.assertEqual ("2020-02-01", element.Datum)

    def test_Lees_TerugtrekkingJuridischWerkendVanaf(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingTijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <soortTijdstempel>juridischWerkendVanaf</soortTijdstempel>
      <eId>art_II</eId>
    </TerugtrekkingTijdstempel>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'TijdstempelTerugtrekkingen', "2022-05-13T07:00:00Z")
        self.assertEqual ("2022-05-13", element.BekendOp ())
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doel.Identificatie)
        self.assertEqual (False, element.IsGeldigVanaf)

    def test_Lees_GeldigVanaf(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Tijdstempels>
    <Tijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <soortTijdstempel>geldigVanaf</soortTijdstempel>
      <datum>2020-02-01</datum>
      <eId>art_II</eId>
      <bekendOp>2022-01-01</bekendOp>
    </Tijdstempel>
  </Tijdstempels>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'Tijdstempels', "2022-05-13T07:00:00Z")
        self.assertEqual ("2022-01-01", element.BekendOp ())
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doel.Identificatie)
        self.assertEqual (True, element.IsGeldigVanaf)
        self.assertEqual ("2020-02-01", element.Datum)

    def test_Lees_GeldigVanaf_BekendOpToekomst(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Tijdstempels>
    <Tijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <soortTijdstempel>geldigVanaf</soortTijdstempel>
      <datum>2020-02-01</datum>
      <eId>art_II</eId>
      <bekendOp>2023-01-01</bekendOp>
    </Tijdstempel>
  </Tijdstempels>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'Tijdstempels', "2022-05-13T07:00:00Z")
        self.assertEqual ("2023-01-01", element.BekendOp ())
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doel.Identificatie)
        self.assertEqual (True, element.IsGeldigVanaf)
        self.assertEqual ("2020-02-01", element.Datum)

    def test_Lees_TerugtrekkingGeldigVanaf(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingTijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <soortTijdstempel>geldigVanaf</soortTijdstempel>
      <eId>art_II</eId>
      <bekendOp>2022-01-01</bekendOp>
    </TerugtrekkingTijdstempel>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'TijdstempelTerugtrekkingen', "2022-05-13T07:00:00Z")
        self.assertEqual ("2022-01-01", element.BekendOp ())
        self.assertEqual ("/join/id/proces/gm9999/2020/InstellingOmgevingsplan", element.Doel.Identificatie)
        self.assertEqual (True, element.IsGeldigVanaf)

    def test_Lees_Tijdstempel_fout_geen_doel (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Tijdstempels>
    <Tijdstempel>
      <soortTijdstempel>geldigVanaf</soortTijdstempel>
      <datum>2020-02-01</datum>
      <eId>art_II</eId>
    </Tijdstempel>
  </Tijdstempels>
</ConsolidatieInformatie>''')

    def test_Lees_Tijdstempel_fout_onbekende_soort (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Tijdstempels>
    <Tijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <soortTijdstempel>bekendVanaf</soortTijdstempel>
      <datum>2020-02-01</datum>
      <eId>art_II</eId>
    </Tijdstempel>
  </Tijdstempels>
</ConsolidatieInformatie>''')

    def test_Lees_Tijdstempel_fout_geen_soort (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Tijdstempels>
    <Tijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <datum>2020-02-01</datum>
      <eId>art_II</eId>
    </Tijdstempel>
  </Tijdstempels>
</ConsolidatieInformatie>''')

    def test_Lees_Tijdstempel_fout_datum (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Tijdstempels>
    <Tijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <soortTijdstempel>geldigVanaf</soortTijdstempel>
      <datum>20200201</datum>
      <eId>art_II</eId>
    </Tijdstempel>
  </Tijdstempels>
</ConsolidatieInformatie>''')

    def test_Lees_TerugtrekkingTijdstempel_fout_geen_doel (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingTijdstempel>
      <soortTijdstempel>geldigVanaf</soortTijdstempel>
      <eId>art_II</eId>
    </TerugtrekkingTijdstempel>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_TerugtrekkingTijdstempel_fout_onbekende_soort (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingTijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <soortTijdstempel>bekendVanaf</soortTijdstempel>
      <eId>art_II</eId>
    </TerugtrekkingTijdstempel>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')

    def test_Lees_TerugtrekkingTijdstempel_fout_geen_soort (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingTijdstempel>
      <doel>/join/id/proces/gm9999/2020/InstellingOmgevingsplan</doel>
      <eId>art_II</eId>
    </TerugtrekkingTijdstempel>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')


#----------------------------------------------------------------------
# Lezen van XML : Materieel uitgewerkt en terugtrekking
#----------------------------------------------------------------------
    def test_Lees_MaterieelUitgewerkt_Regeling(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <MaterieelUitgewerkt>
    <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
    <datum>2022-06-01</datum>
  </MaterieelUitgewerkt>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'MaterieelUitgewerkt', "2022-05-13T07:00:00Z")
        self.assertEqual ("2022-06-01", element.Datum)
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001", element.WorkId)

    def test_Lees_MaterieelUitgewerkt_IO(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <MaterieelUitgewerkt>
    <instrument>/join/id/regdata/2022/io001</instrument>
    <datum>2022-06-01</datum>
  </MaterieelUitgewerkt>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'MaterieelUitgewerkt', "2022-05-13T07:00:00Z")
        self.assertEqual ("2022-06-01", element.Datum)
        self.assertEqual ("/join/id/regdata/2022/io001", element.WorkId)

    def test_Lees_TerugtrekkingMaterieelUitgewerkt(self):
        actual = self._Lees_Valide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <Terugtrekkingen>
    <TerugtrekkingMaterieelUitgewerkt>
      <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
    </TerugtrekkingMaterieelUitgewerkt>
  </Terugtrekkingen>
</ConsolidatieInformatie>''')
        element = self._EnigElement (actual, 'MaterieelUitgewerkt', "2022-05-13T07:00:00Z")
        self.assertIsNone (element.Datum)
        self.assertEqual ("/akn/nl/act/gm9999/2020/REG0001", element.WorkId)

    def test_Lees_MaterieelUitgewerkt_fout_geen_instrument (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <MaterieelUitgewerkt>
    <datum>2022-06-01</datum>
  </MaterieelUitgewerkt>
</ConsolidatieInformatie>''')

    def test_Lees_MaterieelUitgewerkt_fout_invalide_instrument (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <MaterieelUitgewerkt>
    <instrument>/geen/instrument</instrument>
    <datum>2022-06-01</datum>
  </MaterieelUitgewerkt>
</ConsolidatieInformatie>''')

    def test_Lees_MaterieelUitgewerkt_fout_invalide_datum (self):
        actual = self._Lees_Invalide_Xml ('''<ConsolidatieInformatie xmlns="https://standaarden.overheid.nl/stop/imop/data/">
  <gemaaktOp>2022-05-13T07:00:00Z</gemaaktOp>
  <MaterieelUitgewerkt>
    <instrument>/akn/nl/act/gm9999/2020/REG0001</instrument>
    <datum>AA22-06-01</datum>
  </MaterieelUitgewerkt>
</ConsolidatieInformatie>''')

#----------------------------------------------------------------------
# Lezen van XML : Hulpfuncties
#----------------------------------------------------------------------
    def _Lees_Valide_Xml(self, xml):
        log = Meldingen (False)
        root = ET.fromstring(xml)
        actual = ConsolidatieInformatie.LeesXml (log, "test", root)
        if log.Fouten > 0 or log.Waarschuwingen > 0:
            self.fail (log.MaakTekst ())
        self.assertIsNotNone (actual)
        self.assertTrue (actual.IsValide)
        return actual

    def _Lees_Invalide_Xml(self, xml):
        log = Meldingen (False)
        root = ET.fromstring(xml)
        actual = ConsolidatieInformatie.LeesXml (log, "test", root)
        if log.Fouten == 0 and log.Waarschuwingen == 0:
            self.fail ("Fouten verwacht, maar; " + log.MaakTekst ())
        self.assertIsNotNone (actual)
        self.assertFalse (actual.IsValide)

    def _EnigElement (self, actual, naamCollectie, gemaaktOp):
        self.assertEqual (gemaaktOp, actual.GemaaktOp, "ConsolidatieInformatie.GemaaktOp")
        element = None
        for naam in ['BeoogdeVersies', 'Terugtrekkingen', 'Intrekkingen', 'TerugtrekkingenIntrekking', 'Tijdstempels', 'TijdstempelTerugtrekkingen', 'MaterieelUitgewerkt']:
            collectie = getattr(actual,naam)
            self.assertEqual (1 if naam == naamCollectie else 0, len (collectie), naam)
            if naam == naamCollectie:
                element = collectie[0]
        self.assertEqual (actual, element.ConsolidatieInformatie, "ConsolidatieInformatieElement.ConsolidatieInformatie")
        return element


#======================================================================
# Nodig voor unittest
#======================================================================
if __name__ == '__main__':
    unittest.main()
