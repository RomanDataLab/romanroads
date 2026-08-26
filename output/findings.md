# Do All the Roads Lead to Rome? — findings

Graph: **5086 nodes / 7048 edges** (100 connected components).

## Top hexagons by summed degree
Rome's hexagon ranks **#1** by summed degree.

| rank | cell | lat | lng | value |
|---|---|---|---|---|
| 1 | 831e80fffffffff | 42.05 | 12.98 | 2098 |
| 2 | 833862fffffffff | 36.69 | 6.95 | 184 |
| 3 | 833f6efffffffff | 36.90 | 30.00 | 175 |
| 4 | 831e83fffffffff | 41.14 | 13.78 | 174 |
| 5 | 833875fffffffff | 36.54 | 5.59 | 159 |
| 6 | 832db0fffffffff | 32.33 | 35.00 | 151 |
| 7 | 831e8efffffffff | 41.21 | 15.29 | 149 |
| 8 | 833845fffffffff | 35.92 | 9.12 | 129 |
| 9 | 833871fffffffff | 35.65 | 6.39 | 125 |
| 10 | 831edafffffffff | 38.29 | 23.51 | 122 |

## Top hexagons by summed betweenness
Rome's hexagon ranks **#1** by summed betweenness.

| rank | cell | lat | lng | value |
|---|---|---|---|---|
| 1 | 831e80fffffffff | 42.05 | 12.98 | 32168838 |
| 2 | 831ec9fffffffff | 40.94 | 29.00 | 16950084 |
| 3 | 831ec8fffffffff | 41.05 | 27.48 | 12231446 |
| 4 | 831f99fffffffff | 45.55 | 9.60 | 12163320 |
| 5 | 831ef5fffffffff | 44.17 | 20.68 | 11318281 |
| 6 | 831f8bfffffffff | 46.65 | 11.86 | 10731355 |
| 7 | 831e16fffffffff | 46.76 | 13.45 | 10485743 |
| 8 | 831e13fffffffff | 45.96 | 15.90 | 10136902 |
| 9 | 831e1efffffffff | 46.01 | 17.51 | 9253405 |
| 10 | 831e10fffffffff | 46.85 | 15.06 | 9234493 |

## Verdict

The hexagon containing Rome (`831e80fffffffff`) **is** the top-degree cell — all roads lead to Rome.

## Roman cities connected by the roads

Of **1388** known Roman cities (Hanson 2016, 100 BC – AD 300), **1105 (80%)** lie within 5 km of a DARMC road.

### Major cities (Barrington rank 1–2) and their nearest road

| city | modern name | province | rank | nearest road |
|---|---|---|---|---|
| Damascus | Damascus | Syria | 2 | 0.0 km |
| Antiochia (Cappadocia et Galatia) | Yalvaç | Cappadocia et Galatia | 2 | 0.0 km |
| Naissus | Ni | Moesia Superior | 2 | 0.0 km |
| Placentia | Piacenza | Italia (VIII Aemilia) | 2 | 0.0 km |
| Miletus | Balat | Asia | 2 | 0.0 km |
| Vienna | Vienne | Gallia Narbonensis | 2 | 0.0 km |
| Orchomenus Minyeaus | Skripú | Achaea | 2 | 0.0 km |
| Demetrias | Volos | Achaea | 2 | 0.0 km |
| Byzantium | Istanbul | Thracia | 1 | 0.0 km |
| Lepcis Magna | Lebda | Africa Proconsularis | 1 | 0.0 km |
| Mediolanum (Italia (XI Transpadana)) | Milan | Italia (XI Transpadana) | 1 | 0.0 km |
| Lanuvium | Lanuvio | Italia (I Latium and Campania) | 2 | 0.0 km |
| Lydda | Lod | Syria Palestina | 2 | 0.1 km |
| Eburacum | York | Britannia | 2 | 0.1 km |
| Philippopolis (Thracia) | Plovdiv | Thracia | 2 | 0.1 km |
| Hippo Regius | Annaba | Numidia | 2 | 0.1 km |
| Ostia | Ostia | Italia (I Latium and Campania) | 2 | 0.1 km |
| Reate | Rieti | Italia (IV Samnium) | 2 | 0.1 km |
| Bracara | Braga | Hispania Tarraconensis | 2 | 0.1 km |
| Ephesus | Efes | Asia | 2 | 0.1 km |
| Arretium | Arezzo | Italia (VII Etruria) | 2 | 0.1 km |
| Lugdunum | Lyon | Gallia Lugdunensis | 1 | 0.1 km |
| Scythopolis | Beth Shean | Syria Palestina | 2 | 0.1 km |
| Bostra | Bosra | Arabia | 2 | 0.1 km |
| Pisae | Pisa | Italia (VII Etruria) | 2 | 0.1 km |
| Neapolis (Italia (I Latium and Campania)) | Naples | Italia (I Latium and Campania) | 2 | 0.1 km |
| Beneventum | Benevento | Italia (II Apulia et Calabria) | 2 | 0.1 km |
| Augusta Emerita | Mérida | Lusitania | 2 | 0.1 km |
| Tibur | Tivoli | Italia (IV Samnium) | 2 | 0.1 km |
| Ancyra | Ankara | Cappadocia et Galatia | 2 | 0.1 km |
| Ascalon | Ashkelon | Syria Palestina | 2 | 0.1 km |
| Pergamum | Bergama | Asia | 2 | 0.1 km |
| Caere | Cerveteri | Italia (VII Etruria) | 2 | 0.2 km |
| Massalia | Marseille | Gallia Narbonensis | 2 | 0.2 km |
| Amphipolis | Amfipoli | Macedonia | 2 | 0.2 km |
| Patavium | Padua | Italia (X Venetia et Histria) | 2 | 0.2 km |
| Aquinum | Aquino | Italia (I Latium and Campania) | 2 | 0.2 km |
| Laodicea (Asia) | Eskihisar and Gonçal? | Asia | 2 | 0.2 km |
| Sirmium | Sremska Mitrovica | Pannonia Inferior | 2 | 0.2 km |
| Asculum | Ascoli Piceno | Italia (V Picenum) | 2 | 0.2 km |
| Astigi | Ecija | Baetica | 2 | 0.2 km |
| Londinium | London | Britannia | 2 | 0.2 km |
| Sagalassus | Aglasun | Lycia et Pamphylia | 2 | 0.3 km |
| Spoletium | Spoleto | Italia (VI Umbria and Ager Gallicus) | 2 | 0.3 km |
| Capua | S. Maria di Capua Vetere | Italia (I Latium and Campania) | 2 | 0.3 km |
| Gades | Cádiz | Baetica | 2 | 0.3 km |
| Smyrna | Izmir | Asia | 2 | 0.3 km |
| Portus | Fuimicino | Italia (VII Etruria) | 2 | 0.3 km |
| Tarracina | Terracina | Italia (I Latium and Campania) | 2 | 0.3 km |
| Avaricum | Bourges | Gallia Aquitania | 2 | 0.3 km |
| Luna | Luni | Italia (VII Etruria) | 2 | 0.3 km |
| Luca | Lucca | Italia (VII Etruria) | 2 | 0.3 km |
| Gabii | Castiglione | Italia (I Latium and Campania) | 2 | 0.3 km |
| Athenae | Athens | Achaea | 1 | 0.3 km |
| Megara | Megara | Achaea | 2 | 0.3 km |
| Puteoli | Pozzuoli | Italia (I Latium and Campania) | 2 | 0.3 km |
| Casinum | Cassino | Italia (I Latium and Campania) | 2 | 0.4 km |
| Sabratha | Sabrata | Africa Proconsularis | 2 | 0.4 km |
| Antium | Anzio | Italia (I Latium and Campania) | 2 | 0.4 km |
| Lucus Augusti (Hispania Tarraconensis) | Lugo | Hispania Tarraconensis | 2 | 0.4 km |
| Eleutheropolis | Beit Jibrin | Syria Palestina | 2 | 0.4 km |
| Arelate | Arles | Gallia Narbonensis | 2 | 0.4 km |
| Anagnia | Anagni | Italia (I Latium and Campania) | 2 | 0.4 km |
| Sitifis | Sétif | Mauretania Caesariensis | 2 | 0.4 km |
| Ptolemais (Cyrenaica) | Tolmeita | Creta et Cyrenaica | 2 | 0.4 km |
| Siscia | Sisak | Pannonia Superior | 2 | 0.4 km |
| Ancona | Ancona | Italia (V Picenum) | 2 | 0.4 km |
| Neapaphus | Kato Paphos | Cilicia et Cyprus | 2 | 0.4 km |
| Pelusium | Tell el Farama | Aegyptus | 2 | 0.4 km |
| Brixia | Brescia | Italia (X Venetia et Histria) | 2 | 0.4 km |
| Corduba | Córdoba | Baetica | 1 | 0.5 km |
| Side | Selimiye | Lycia et Pamphylia | 2 | 0.5 km |
| Verona | Verona | Italia (X Venetia et Histria) | 2 | 0.5 km |
| Praeneste | Palestrina | Italia (I Latium and Campania) | 2 | 0.5 km |
| Tarraco | Tarragona | Hispania Tarraconensis | 1 | 0.5 km |
| Cyrene | Aïn Shahat | Creta et Cyrenaica | 2 | 0.5 km |
| Larisa (Achaea) | Unknown | Achaea | 2 | 0.5 km |
| Tarentum | Taranto | Italia (II Apulia et Calabria) | 2 | 0.5 km |
| Delphi | Delphi | Achaea | 2 | 0.6 km |
| Pistorium | Pistoia | Italia (VII Etruria) | 2 | 0.6 km |
| Colonia Agrippinensis | Cologne | Germania Inferior | 2 | 0.6 km |
| Gaza | Gaza | Syria Palestina | 2 | 0.6 km |
| Heliopolis (Syria) | Baalbek | Syria | 2 | 0.6 km |
| Aquileia | Aquileia | Italia (X Venetia et Histria) | 2 | 0.7 km |
| Berytus | Beirut | Syria | 2 | 0.7 km |
| Salamis | Salamis | Cilicia et Cyprus | 2 | 0.7 km |
| Clusium | Chiusi | Italia (VII Etruria) | 2 | 0.7 km |
| Panormus | Palermo | Silicia | 2 | 0.7 km |
| Iol | Cherchell | Mauretania Caesariensis | 2 | 0.7 km |
| Thebae | Thebes | Achaea | 2 | 0.7 km |
| Perusia | Perugia | Italia (VII Etruria) | 2 | 0.7 km |
| Cyzicus | Belkis | Asia | 2 | 0.7 km |
| Tarsus | Tarsus | Cilicia et Cyprus | 2 | 0.8 km |
| Vulci | Volci | Italia (VII Etruria) | 2 | 0.8 km |
| Aegina | Aigina | Achaea | 2 | 0.8 km |
| Nicomedia | Ismit | Bithynia et Pontus | 2 | 0.8 km |
| Salona | Solin | Dalmatia | 2 | 0.8 km |
| Germa | Babadat | Cappadocia et Galatia | 2 | 0.8 km |
| Nicaea | Iznik | Bithynia et Pontus | 2 | 0.9 km |
| Colonia Augusta Treverorum | Trier | Gallia Belgica | 2 | 0.9 km |
| Arae Flaviae | Rottweil | Germania Superior | 2 | 0.9 km |
| Apulum (1) | Weissenburg | Dacia | 2 | 0.9 km |
| Serdica | Sophia | Thracia | 2 | 0.9 km |
| Eretria | Eretria | Achaea | 2 | 0.9 km |
| Barcino | Barcelona | Hispania Tarraconensis | 2 | 1.0 km |
| Oea | Tripoli | Africa Proconsularis | 2 | 1.0 km |
| Gortyna | Kainourgiou | Creta et Cyrenaica | 2 | 1.0 km |
| Syracusae | Syracuse | Silicia | 2 | 1.0 km |
| Narbo Martius | Narbonne | Gallia Narbonensis | 2 | 1.0 km |
| Pax Iulia | Beja | Lusitania | 2 | 1.0 km |
| Sinope | Sinop | Bithynia et Pontus | 2 | 1.0 km |
| Sidon | Saida | Syria | 2 | 1.0 km |
| Antiochia (Syria) | Antakya | Syria | 1 | 1.1 km |
| Chalcis | Chalkis | Achaea | 2 | 1.1 km |
| Caesaraugusta | Zaragoza | Hispania Tarraconensis | 2 | 1.1 km |
| Apulum (2) | Weissenburg | Dacia | 2 | 1.1 km |
| Mazaca | Kayseri | Cappadocia et Galatia | 2 | 1.1 km |
| Augusta Vindelicum | Augsburg | Raetia | 2 | 1.1 km |
| Mogontiacum | Mainz | Germania Superior | 2 | 1.2 km |
| Corinthia | Corinth | Achaea | 1 | 1.3 km |
| Nola | Nola | Italia (I Latium and Campania) | 2 | 1.3 km |
| Aquincum | Obuda | Pannonia Inferior | 2 | 1.3 km |
| Apollonia (Macedonia) | Pojani | Macedonia | 2 | 1.3 km |
| Palmyra | Tadmor | Syria | 2 | 1.3 km |
| Carthago Nova | Cartagena | Hispania Tarraconensis | 2 | 1.3 km |
| Thessalonica | Thessaloniki | Macedonia | 1 | 1.4 km |
| Apamea (Syria) (1) | Qalaat al Mudik | Syria | 2 | 1.4 km |
| Dyrrachium | Durrës | Macedonia | 2 | 1.4 km |
| Virunum | Zollfeld | Noricum | 2 | 1.4 km |
| Carthago | Tunis | Africa Proconsularis | 1 | 1.5 km |
| Tacapae | Gabès | Africa Proconsularis | 2 | 1.5 km |
| Sopianae | PECS | Pannonia Superior | 2 | 1.5 km |
| Romula | Re?ca | Dacia | 2 | 1.6 km |
| Roma | Rome | Italia (VII Etruria) | 1 | 1.6 km |
| Aelia Capitolina | Jerusalem | Syria Palestina | 1 | 1.6 km |
| Celaenae | Dinar | Asia | 2 | 1.7 km |
| Alexandria (Aegyptus) | Alexandria | Aegyptus | 1 | 1.7 km |
| Tripolis | Tarablis | Syria | 2 | 1.8 km |
| Anazarbus | Anavarza | Cilicia et Cyprus | 2 | 1.8 km |
| Tingis | Tangier | Mauretania Tingitana | 2 | 1.9 km |
| Scallabis | Santarem | Lusitania | 2 | 1.9 km |
| Minturnae | Minturno | Italia (I Latium and Campania) | 2 | 1.9 km |
| Philadelphia (Syria) | Amman | Syria | 2 | 2.0 km |
| Sardis | Sart | Asia | 2 | 2.0 km |
| Pella (Macedonia) | Pella | Macedonia | 2 | 2.0 km |
| Perge | Aksu | Lycia et Pamphylia | 2 | 2.0 km |
| Viminacium (2) | Kostolac | Moesia Superior | 2 | 2.1 km |
| Viminacium (1) | Kostolac | Moesia Superior | 2 | 2.1 km |
| Petra | Petra | Arabia | 2 | 2.3 km |
| Scupi | Skopje | Moesia Superior | 2 | 2.3 km |
| Melitene | Malatya | Cappadocia et Galatia | 2 | 2.3 km |
| Samosata | Samsat | Syria | 2 | 2.4 km |
| Tyrus | Tyre | Syria | 2 | 2.4 km |
| Lambaesis | Tazzoult | Numidia | 2 | 2.5 km |
| Volsinii Novi | Bolsena | Italia (VII Etruria) | 2 | 2.5 km |
| Marcianopolis | Reka Devnija | Moesia Inferior | 2 | 2.8 km |
| Burdigala | Bordeaux | Gallia Aquitania | 2 | 2.8 km |
| Hispalis | Seville | Baetica | 2 | 3.3 km |
| Philippi | Krenides | Macedonia | 2 | 4.1 km |
| Asturica | Astorga | Hispania Tarraconensis | 2 | 4.7 km |
| Memphis | Kom Rabia | Aegyptus | 2 | 5.5 km |
| Elateia | Lefta | Achaea | 2 | 5.7 km |
| Clunia | Peñalba de Castro | Hispania Tarraconensis | 2 | 12.2 km |
| Sicyon | Basiliko | Achaea | 2 | 16.6 km |
| Patrae | Patrai | Achaea | 2 | 18.4 km |
| Cydonea | Khania | Creta et Cyrenaica | 2 | 24.9 km |
| Cnossus | Knossos | Creta et Cyrenaica | 2 | 27.7 km |
| Argos (Achaea) (2) | Argos | Achaea | 2 | 35.3 km |
| Lyctus | Xydas | Creta et Cyrenaica | 2 | 37.2 km |
| Mantinea | Mantineia | Achaea | 2 | 53.2 km |
| Tegea | Alea | Achaea | 2 | 69.4 km |
| Hierapytna | Ierapetra | Creta et Cyrenaica | 2 | 71.8 km |
| Elis | Ilida | Achaea | 2 | 73.6 km |
| Megalopolis | Sinánu | Achaea | 2 | 89.0 km |
| Sparta | Sparti | Achaea | 2 | 103.4 km |
| Messene | Mavromati | Achaea | 2 | 125.8 km |

Major cities **not** within 5 km of any digitized road: Memphis (6 km), Elateia (6 km), Clunia (12 km), Sicyon (17 km), Patrae (18 km), Cydonea (25 km), Cnossus (28 km), Argos (Achaea) (2) (35 km), Lyctus (37 km), Mantinea (53 km), Tegea (69 km), Hierapytna (72 km), Elis (74 km), Megalopolis (89 km), Sparta (103 km), Messene (126 km).

Data: DARMC Roman Road Network (2008), CC BY-NC 3.0; Hanson 2016 Cities Database v1.0 (OxREP), doi:10.5287/bodleian:eqapevAn8.