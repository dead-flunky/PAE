
Es werden bei diesen Grafikpaket einige etwas ausgefallenere Konzepte kombiniert.
Diese sollen im folgenden erläutert werden.

EDIT: Anders als in Punkt 2 des folgenden Textes beschrieben, muss diese Version
  leider ohne das Nachladen der Unter-Nifs auskommen, weil anderenfalls die Option
  'contourgeometry' nicht angewendet wird. Daher wurde alles in ein NIF ge-
  packt und die erwünschten Teile werden per Python eingeblendet. (Standardmäßig
  ist bei den Knoten das Hidden-Flag gesetzt. Das blendet sie auch in Nifskope
  aus! )


Allgemein: Um die Flussfelder in das Spiel einzubauen setzt man das Feature 
  auf einen Plot. Dieses Feature besitzt zwei Varianten. In Variante 0 ist 
  das Feature leer, d.h. graphisch wird das Feld nicht davon beeinflusst.
  In Variante 1 wird RiverRoot.nif geladen. Dieses Nif ist ein fast leerer Container,
  der verschiedene Unterknoten enthält. Diese werden zur Laufzeit so mit Grafiken
  gefüllt, dass ein Flussverlauf entsteht. Sollte die automatische Generierung
  unpassend aussehen, kann man manuell (Python) eingreifen. Die manuellen Werte werden
  im Skriptfeld des Plots gespeichert.
  Das Nachladen der Nifs sollte man am besten in  CvEventmanager.onGameLoad und
  CvEventmanager.onGameStart anstoßen.


1. Benutzung von ContourGeometry-Eigenschaft.
  Um Nifs an die Höhe des Geländeuntegrundes anzupassen gibt es zwei Mechanismen:
  „countourgeometry“ und „OFFSETCOUNT=X [Punkte]“.
  Die ContourGeometry-Eigenschaft wird hier verwendet, um die Feature-Texturen
  unabhängig vom Gelände knapp über die Oberfläche zu legen. (Auf Wasserfeldern fällt
  das Gelände unter die Wasseroberfläche ab.)
  Leider wird die Eigenschaft ignoriert, wenn man sie nur in den nachgeladenen
  Nifs angibt. Daher enthält RiverRoot.nif an den passenden Knoten schon (unsichtbare)
  Unterknoten mit der ContourGeometry-Eigenschaft! Diese sollte man daher nicht entfernen.
  

2. Nachladen von Nifs mit DummyNodes.
  Hier muss erst das Konzept der DummyNodes erklärt werden. Der ART-Eintrag des Features
  enthält Tags folgender Form:
          <FeatureDummyNode>
            <Tag>NODE_1</Tag>
            <Name>RiverLeft_0</Name>
          </FeatureDummyNode>
          <FeatureDummyNode>
            <Tag>MODEL_1</Tag>
            <Name>Art/path/to/model.nif</Name>
          </FeatureDummyNode>
          <FeatureDummyNode>
            <Tag>TEXTURE_1</Tag>
            <Name>Art/path/to/texture.dds</Name>
          </FeatureDummyNode>
  
  Es ist zwar dreimal der gleiche Tag (FeatureDummyNode) aber diese
  drei Tags erfüllen drei unterschiedliche Funktionen. Um später
  nicht durcheinander zu kommen, wird dies bei der Benennung berücksichtigt
  und der Tag beginnt immer entweder mit NODE_, MODEL_ oder TEXTURE_.

  Die NODE-Einträge sollten den Namen eines Knotes aus dem Wurzel-Nif enthalten.
  Die MODEL-Einträge verweisen auf Nifs und die TEXTURE-Eintäge auf Texturen...

  Per Python stehen einem folgende Funktionen zur Verfügung:
    pPlot.setFeatureDummyVisibility("NODE_[...]", bVisible)
     - Steuert Sichtbarkeit eines Knoten (aus RiverRoot.nit)

    pPlot.addFeatureDummyModel("NODE_[...]", "MODEL_[...]")
     - Erweitert Knoten um das angegeben Modell. 
     - Man kann mehrere Modelle am gleichen Knoten einhängen!

    pPlot.setFeatureDummyTexture("NODE_[...]", "TEXTURE_[...]")
     - Ändert Texturpfad des letzten Models, welches mit addFeatureDummyModel 
       hinzugefügt wurde.
     - Man kann auch die Textur eines Knotens aus dem Wurzelmodel ändern,
       sofern man für den Knoten noch nicht addFeatureDummyModel aufgerufen hat!

  Um ein Feature zurück zu setzen kann man pPlot.resetFeatureModel() nutzen.

  Dieses Konzept wird angewendet, um ein passendes Flussstück (Quelle, Mündung,
  Mittelstück) auf einem Feld zu laden. 


3. Austausch von Nifs-Texturen mit DummyNodes
  Da die Textur des Flussfeatures auf den Untergrund der Nachbarfelder reagieren muss
  gibt es unterschliedliche Untergrundtexturen. Diese müssen mit setFeatureDummyTexture
  gesetzt werden.
  Außerdem bestehen die Flussfeatures teilweise aus zwei Stücken so dass man das Terrain
  der linken und der rechten Flussseite separat abhandeln kann! Bei Nifs für Flussquellen
  gibt es nur eine Seite und „rechts“ ist leer.


4. Hui, es sind viele Modelle … Namenskonventionen.
  EDIT: Dieser Punkt ist obsolent, da jetzt alles in einer Datei steckt. Die
  Namenskonvention spiegelt sich allerdings noch in den Knotennamen wieder.

  Es wurden für alle vier Ausrichtungen der Fließrichtung des Flusses entsprechende Modelle
  erstellt. Außerdem gibt es Modelle für Quellen und Mündungen und die Teile müssen
  in der Flussmitte geteilt werden. Das führt zu einer großen Anzahl an Dateien...

  Die Namenskonvention ist folgende.
    river[N|W][N|W|S|E][nwse]_[Variante].nif   Beispiel:  riverWEn_08.nif
    source[N|W|S|E]_[Variante].nif             Beispiel:  sourceN_08.nif
    dest[N|W|S|E][nwse]_[Variante].nif         Beispiel:  destNw_08.nif

  N,W,S,E beschreiben immer die Himmelsrichtung an weitere Stücke anliegen.
  D.h. 'destNw' ist folendermaßen zu lesen: Fluss mündet von Norden
  kommend in das Feld. Das Modell beinhalt die Westseite der Mündung.


5. Benutzen der Rotationen in RiverRoot.nif (0, 90, 180, 270)
  EDIT: Derzeit wird auf Rotationen verzichtet.

  Das Riverpaket kann ohne Rotationen genutzt werden, denn es liegen
  Grafiken für alle vier Varianten vor. Für mehr Vielfalt
  kann man diese Modelle aber zusätzlich drehen und so die ursprüngliche
  „Nord-Mündung“ auch nach Westen münden lassen.
  In vielen Fällen könnte einem allerdings die Texturierung der Felder
  einen Strich durch die Rechnung machen, denn diese wird oftmals nur
  passen, wenn alle Felder eines Fluss zusammen gedreht sind.

  Tipp: Lange Flüsse kann man unterteilen indem man zwei Mündungen
  nebeneinander packt. Dann kann man die Teile unabhängig voneinander
  drehen.
  Mit dem Verfahren kann man auch Flussverzweigungen umsetzen.


6. Benutzen von NiStencilProperty für Straßen, normale Flüsse, etc.
  Da Features von der Rendering-Engine erst sehr spät gezeichnet werden,
  übermalen sie in der Regel den Untergrund, wenn sie über ihm liegen (bei aktiviertem Z-Buffer).
  Es gibt allerdings neben dem Z-Buffer noch den Stencil-Buffer und man kann Nif-Modelle
  mit ihnen ausstatten!
  Den Flussfeatures wurden damit ein Filter gegeben, der sie auf Pixeln mit einem Stencil-Wert
  > 1 nicht zeichnet. Damit dies aber eine Wirkung erzielt müssen die anderen Modelle ebenfalls
  mit einem NiStencilProperty-Knoten ergänzt werden. Das führt zu vielen geänderten
  Modellen!! Für Straßen, Flüsse und den Einheiten-Selektor habe ich es bereits durchgeführt.

  Leider gibt es einige Bugs, welche die Verwendung des Stencilbuffers sehr schwierig gestalten.
  Per try&error wurden folgende Probleme festgestellt. Darunter steht die aktuelle Implemantation,
  welche diese Fehler versucht zu umgehen.

  6.1 In Nifskope scheinen einige Menüpunkte falsch benannt zu sein. Beim Feld "Stencil Function" 
    haben TEST_GREATER, TEST_GREATER_EQUAL, TEST_LESS und TEST_LESS_EQUAL invertierte Auswirkungen,
    d.h TEST_LESS wirkt wie TEST_GREATER und umgekehrt.
    Weiterhin fehlen die „Stencil values“ GL_DECR_WRAP und GL_INCR_WRAP.

  6.2 Setzt man Stencils bei Straßen und Flüssen so wird in OpenGL die Stencil-Funktion nicht 
    zurück gesetzt! Das führt dazu, dass der letzte verwendete Stencil danach auch auf die Wasseroberflächen
    angewendet wird, was zu merkwürdigen Effekten führt, wenn man über die Karte scrollt.
    Je nachdem welche Straßenmodell/Flussmodell als letztes gezeichnet wird, wechselt der Stenciv-Filter.
    
  6.3 Bei Flüssen kommt die Einschränkung hinzu, dass pro Nif nur der letzte gesetzte Stencil
    zum Einsatz kommt! D.h. im Unterschied zu Straßen kann man nicht einfach einen zweiten,
    deaktivierten Stencil-Knoten hinzufügen, um das Problem von 9.2 zu beheben. Es wird immer
    nur der letzte im Nif gesetzte gewählt.

  Aufgrund dieser Probleme ist es nicht ganz einfach einen Stecil-Filter zu kreieren, der auf Straßen
  und Flüssen wirkt, aber nicht auf der Wasseroberfläche.
  
  Lösungs-Idee:
    Das Problem von 6.3 kann man entschärfen, indem man dort das River-Base-Mesh verdoppelt und
    die Stencil-Funktion GL_INCR wählt! Dadurch erhält man dann folgende Stencil-Werte:
    0 - Default-Wert, wenn kein Stencilfilter zum Einsatz kam. Kommt auf Land und 
        der Wasseroberfläche vor.
    1 - Wert auf der Wasseroberfläche sofern ein Model aus routes/rivers gezeichnet wird.
    2 - Wert von Straßen und den BTS-Flüssen
    >2 - Teilweise überlagern noch mehr Schichten mit dem GL_INCR-Filter und es enstehen höhere
        Werte.

    • Straßen-Nifs enthalten zwei Stencil-Buffer. Der erste setzt die Straßen-Pixel auf 2. Der zweite
      sorgt dafür, dass der erste auf Wasseroberflächen deaktiviert wird.
    • River-Nifs mit Mündungen enthalten den GL-INCR-Filter und eine doppelte Untergrundfläche.
      - NiStringExtraData draf nur bei der zweiten Untergrundfläche den String "RiverBase" enthalten.
        „RiverBase“ sorgt dafür, dass immer die Detail-Textur gezeichnet wird. Ohne sieht es pixelig aus!
      - Der Stencil-Wert auch erhöht werden, wenn der Z-Buffer-Test fehl schlägt.
    • Neues Feature-Nif zeichnet Pixel nur für die Stencil-Werte [0,1]. Dafür muss die (falsch be-
      schriftete) Option "TEST_GREATER" verwendet werden.
    • In Art/Units/selection effekt/ muss ein Wert >1 gesetzt werden.


7. Benutzung von plot.getScriptData()
  Das Feature ist zu komplex, um es über die normalen Feature-Mechanismen vollständig zu beschreiben.
  Daher habe ich das ScriptData-Feld so erweitert, dass es nun Strings enthalten kann,
  welche Python-Dics enthalten. Diese werden mittels simplejson geparst. 
  CvUtil enthält die dafür notwendigen Hilfsfunktionen. 
  Achtung, ich habe versucht das halbwegs abwärtskompatibel einzubauen, aber es könnte
  zu Problemen zu anderen Mechanismen kommen, die auf das Skriptfeld zurück greifen.


8. Dekorationen 
  An den Rändern können drei verschieden Arten von Bäumen gesetzt werden. Da bei dieser
  Art von Feature die OFFSET-Angaben ignoriert werden kann man leider nicht den
  elegantesten Weg beschreiten, um die Baumpositionen an die Geländehöhe anzupassen.
  
  Daher werden alle Bäume per "contourgeometry" verschoben, d.h. jeder Z-Wert wird
  einzeln angepasst. Damit die Modelle nicht zu stark verzerrt werden sollten sie nicht
  zu hoch und relativ schmal sein.

  Auf weitere Dekorationen, wie beispielsweise Furten undBrücken, wurde bisher verzichtet,
  um das große Nif nicht noch weiter aufzublähen. 


9. Wellen (Adaption der 'Rapdis'-Knoten von kleinen Flüssen)
  Die Wurzelmodelle beinhalten jetzt Knoten an denen man Animationen (Rapids*.nif) einhängen
	kann. Welche Modelle (Wellenrichtung) zu welchen Flussteil passen ist in 
	'RapidTypes'  (CvRiverUtil.py) codiert.
	(!) In Nifskope fließen die Wellen in die entgegengesetzte Richtung.
	(!) Einige Animationen werden mehrfach verwendet. Die Wellen sind daher in der Regel
	breiter als der Fluss. Die hohe Breite hat allerdings den Nachteil, dass das Ausblenden (Alphawert 
	wird über Vertex-Color gesteuert) nicht überall stimmig ist.
	Da besteht also noch viel Verbesserungspotential.

10 Wasserfarben.
  Geplant für Blauen + Weißen Nil und Katastrophen :D
