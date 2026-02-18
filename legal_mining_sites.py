"""
Legal Mining Areas Database
Contains coordinates of verified legal mining sites worldwide

Mineral types:
  Iron Ore, Bauxite/Aluminum, Copper, Limestone, Granite, Manganese
"""

LEGAL_MINING_AREAS = {
    # ==================== IRON ORE MINES ====================
    "Bailadila Iron Ore Complex":    (18.6297,  81.3025,  "India",        "Iron Ore"),
    "NMDC Bailadila Mine 14":        (18.6500,  81.2800,  "India",        "Iron Ore"),
    "Donimalai Iron Ore Mine":       (15.1833,  76.9167,  "India",        "Iron Ore"),
    "Kudremukh Iron Ore Mine":       (13.3167,  75.2500,  "India",        "Iron Ore"),
    "Barbil Iron Ore Mines":         (22.1167,  85.3833,  "India",        "Iron Ore"),
    "Kiriburu Iron Ore Mine":        (22.1333,  85.3000,  "India",        "Iron Ore"),
    "Meghahatuburu Iron Ore Mine":   (22.1500,  85.2833,  "India",        "Iron Ore"),
    "Gua Iron Ore Mines":            (22.2167,  85.3833,  "India",        "Iron Ore"),
    "Noamundi Iron Ore Mine":        (22.1667,  85.5000,  "India",        "Iron Ore"),
    "Chiria Iron Ore Mines":         (22.3000,  85.2167,  "India",        "Iron Ore"),
    "Carajas Mine":                  (-6.0667, -50.2667,  "Brazil",       "Iron Ore"),
    "Itabira Mine Complex":          (-19.6167,-43.2333,  "Brazil",       "Iron Ore"),
    "Minas Centrais Complex":        (-20.3167,-43.7833,  "Brazil",       "Iron Ore"),
    "Brucutu Mine":                  (-19.9167,-43.6167,  "Brazil",       "Iron Ore"),
    "Conceicao Mine":                (-19.4667,-43.4167,  "Brazil",       "Iron Ore"),
    "Fabrica Nova Mine":             (-20.0833,-43.8500,  "Brazil",       "Iron Ore"),
    "Alegria Mine":                  (-19.8333,-43.4833,  "Brazil",       "Iron Ore"),
    "Capao Xavier Mine":             (-19.9500,-43.8667,  "Brazil",       "Iron Ore"),
    "Mount Whaleback Mine":          (-23.3667, 119.6667, "Australia",    "Iron Ore"),
    "Tom Price Mine":                (-22.6833, 117.7833, "Australia",    "Iron Ore"),
    "Paraburdoo Mine":               (-23.1667, 117.6667, "Australia",    "Iron Ore"),
    "Yandicoogina Mine":             (-22.7000, 119.0833, "Australia",    "Iron Ore"),
    "Marandoo Mine":                 (-22.6167, 118.1000, "Australia",    "Iron Ore"),
    "Nammuldi Mine":                 (-22.6667, 117.9167, "Australia",    "Iron Ore"),
    "Cloudbreak Mine":               (-22.3000, 119.4500, "Australia",    "Iron Ore"),
    "Christmas Creek Mine":          (-22.1167, 119.5333, "Australia",    "Iron Ore"),
    "West Angelas Mine":             (-23.1167, 118.6833, "Australia",    "Iron Ore"),
    "Jimblebar Mine":                (-23.3333, 119.6167, "Australia",    "Iron Ore"),
    "Koodaideri Mine":               (-22.4500, 119.5000, "Australia",    "Iron Ore"),
    "Sishen Mine":                   (-27.6500,  23.0167, "South Africa", "Iron Ore"),
    "Kolomela Mine":                 (-28.3833,  22.8833, "South Africa", "Iron Ore"),
    "Thabazimbi Mine":               (-24.5833,  27.4167, "South Africa", "Iron Ore"),
    "Kiruna Mine":                   (67.8556,   20.2253, "Sweden",       "Iron Ore"),
    "Malmberget Mine":               (67.1833,   20.6667, "Sweden",       "Iron Ore"),
    "Lebedinsky Mine":               (50.9667,   37.6167, "Russia",       "Iron Ore"),
    "Stoilensky Mine":               (50.8000,   37.9000, "Russia",       "Iron Ore"),
    "Mikhailovsky Mine":             (51.6833,   35.2667, "Russia",       "Iron Ore"),
    "Kachkanarsky Mine":             (58.7000,   59.4833, "Russia",       "Iron Ore"),
    "Anshan Mine Complex":           (41.1083,  122.9900, "China",        "Iron Ore"),
    "Qidashan Mine":                 (41.0833,  123.0833, "China",        "Iron Ore"),
    "Dagushan Mine":                 (41.0167,  122.8833, "China",        "Iron Ore"),
    "Gongchangling Mine":            (40.9833,  123.2000, "China",        "Iron Ore"),
    "Kryvyi Rih Mining District":    (47.9108,   33.3917, "Ukraine",      "Iron Ore"),
    "Mary River Mine":               (71.2833,  -78.9833, "Canada",       "Iron Ore"),
    "IOC Mine":                      (52.9500,  -66.8667, "Canada",       "Iron Ore"),
    "Hibbing Taconite Mine":         (47.4271,  -92.9377, "USA",          "Iron Ore"),
    "Minntac Mine":                  (47.5333,  -92.7000, "USA",          "Iron Ore"),
    "United Taconite Mine":          (47.5167,  -92.3500, "USA",          "Iron Ore"),
    "Keetac Mine":                   (47.4000,  -92.8833, "USA",          "Iron Ore"),
    "Guelbs Mine":                   (22.7167,  -12.5833, "Mauritania",   "Iron Ore"),
    "MHaoudat Mine":                 (22.6833,  -12.7000, "Mauritania",   "Iron Ore"),
    "Bong Mine":                     (6.8833,   -10.0500, "Liberia",      "Iron Ore"),
    "Nimba Mine":                    (7.5833,    -8.5167, "Liberia",      "Iron Ore"),
    "Gol-e-Gohar Mine":              (29.1667,   57.3833, "Iran",         "Iron Ore"),
    "Chadormalu Mine":               (32.4833,   55.6500, "Iran",         "Iron Ore"),
    "Sokolov-Sarbai Mine":           (52.8833,   62.9500, "Kazakhstan",   "Iron Ore"),
    "Lisakovsk Mine":                (52.5333,   62.5000, "Kazakhstan",   "Iron Ore"),

    # ==================== ALUMINUM / BAUXITE MINES ====================
    "Weipa Bauxite Mine":            (-12.6667, 141.8667, "Australia",   "Bauxite/Aluminum"),
    "Gove Bauxite Mine":             (-12.2667, 136.8167, "Australia",   "Bauxite/Aluminum"),
    "Huntly Bauxite Mine":           (-32.5833, 116.0167, "Australia",   "Bauxite/Aluminum"),
    "Willowdale Bauxite Mine":       (-32.7167, 116.0500, "Australia",   "Bauxite/Aluminum"),
    "Boddington Bauxite Mine":       (-32.8000, 116.4667, "Australia",   "Bauxite/Aluminum"),
    "Sangaredi Bauxite Mine":        (11.1333,  -13.7333, "Guinea",      "Bauxite/Aluminum"),
    "Boke Bauxite Mine":             (10.9500,  -14.2833, "Guinea",      "Bauxite/Aluminum"),
    "Kamsar Bauxite Mine":           (10.6500,  -14.6167, "Guinea",      "Bauxite/Aluminum"),
    "Dian-Dian Bauxite Mine":        (11.2000,  -13.6500, "Guinea",      "Bauxite/Aluminum"),
    "Paragominas Bauxite Mine":      (-3.0000,  -47.5000, "Brazil",      "Bauxite/Aluminum"),
    "Porto Trombetas Bauxite Mine":  (-1.4667,  -56.3833, "Brazil",      "Bauxite/Aluminum"),
    "Juruti Bauxite Mine":           (-2.1500,  -56.0833, "Brazil",      "Bauxite/Aluminum"),
    "Miraí Bauxite Mine":            (-20.8667, -42.6167, "Brazil",      "Bauxite/Aluminum"),
    "Pocos de Caldas Bauxite Mine":  (-21.7833, -46.5667, "Brazil",      "Bauxite/Aluminum"),
    "Guangxi Bauxite District":      (23.7333,  106.6167, "China",       "Bauxite/Aluminum"),
    "Shanxi Bauxite District":       (37.8667,  112.5500, "China",       "Bauxite/Aluminum"),
    "Henan Bauxite District":        (34.7667,  113.6500, "China",       "Bauxite/Aluminum"),
    "Guizhou Bauxite Mine":          (26.5833,  106.7167, "China",       "Bauxite/Aluminum"),
    "Odisha Bauxite Mines":          (20.2667,   85.8333, "India",       "Bauxite/Aluminum"),
    "Gujarat Bauxite Mines":         (21.5167,   73.2167, "India",       "Bauxite/Aluminum"),
    "Jharkhand Bauxite Mines":       (23.3500,   85.3333, "India",       "Bauxite/Aluminum"),
    "Chhattisgarh Bauxite Mines":    (21.2500,   81.6333, "India",       "Bauxite/Aluminum"),
    "Amarkantak Bauxite Mine":       (22.6667,   81.7500, "India",       "Bauxite/Aluminum"),
    "Clarendon Bauxite Mine":        (17.9667,  -77.2500, "Jamaica",     "Bauxite/Aluminum"),
    "St. Ann Bauxite Mine":          (18.4333,  -77.2000, "Jamaica",     "Bauxite/Aluminum"),
    "Manchester Bauxite Mine":       (18.0500,  -77.5167, "Jamaica",     "Bauxite/Aluminum"),
    "North Urals Bauxite Mine":      (59.5000,   60.2000, "Russia",      "Bauxite/Aluminum"),
    "Srednetimanskoe Bauxite Mine":  (65.3000,   57.2500, "Russia",      "Bauxite/Aluminum"),
    "Ural Bauxite Deposit":          (58.0000,   59.5000, "Russia",      "Bauxite/Aluminum"),
    "Central Highlands Bauxite":     (12.6667,  108.0333, "Vietnam",     "Bauxite/Aluminum"),
    "Dak Nong Bauxite Mine":         (12.2500,  107.7000, "Vietnam",     "Bauxite/Aluminum"),
    "Bintan Bauxite Mine":           (1.0500,   104.4500, "Indonesia",   "Bauxite/Aluminum"),
    "Riau Islands Bauxite":          (0.9000,   104.4500, "Indonesia",   "Bauxite/Aluminum"),
    "Pahang Bauxite District":       (3.8000,   103.3200, "Malaysia",    "Bauxite/Aluminum"),
    "Lelydorp Bauxite Mine":         (5.7000,   -55.2333, "Suriname",    "Bauxite/Aluminum"),
    "Paranam Bauxite Mine":          (5.6167,   -55.0667, "Suriname",    "Bauxite/Aluminum"),
    "Parnassos-Giona Bauxite":       (38.5333,   22.6167, "Greece",      "Bauxite/Aluminum"),

    # ==================== COPPER MINES ====================
    "Escondida Copper Mine":         (-24.2667,  -69.0833, "Chile",       "Copper"),
    "Collahuasi Copper Mine":        (-20.9667,  -68.7167, "Chile",       "Copper"),
    "El Teniente Copper Mine":       (-34.0833,  -70.3667, "Chile",       "Copper"),
    "Los Bronces Copper Mine":       (-33.1500,  -70.3000, "Chile",       "Copper"),
    "Chuquicamata Copper Mine":      (-22.3000,  -68.9000, "Chile",       "Copper"),
    "Radomiro Tomic Copper Mine":    (-22.4500,  -68.8333, "Chile",       "Copper"),
    "Ministro Hales Copper Mine":    (-22.3500,  -68.9500, "Chile",       "Copper"),
    "Los Pelambres Copper Mine":     (-31.7833,  -70.5500, "Chile",       "Copper"),
    "Andina Copper Mine":            (-32.8500,  -70.2500, "Chile",       "Copper"),
    "Centinela Copper Mine":         (-23.9667,  -69.4500, "Chile",       "Copper"),
    "Antamina Copper Mine":          (-9.3500,   -77.1000, "Peru",        "Copper"),
    "Cerro Verde Copper Mine":       (-16.5167,  -71.5833, "Peru",        "Copper"),
    "Las Bambas Copper Mine":        (-14.1833,  -72.2333, "Peru",        "Copper"),
    "Toromocho Copper Mine":         (-11.5167,  -76.1167, "Peru",        "Copper"),
    "Antapaccay Copper Mine":        (-14.3667,  -71.2833, "Peru",        "Copper"),
    "Toquepala Copper Mine":         (-17.2667,  -70.6167, "Peru",        "Copper"),
    "Cuajone Copper Mine":           (-17.0333,  -70.7167, "Peru",        "Copper"),
    "Bingham Canyon Copper Mine":    (40.5250,  -112.1500, "USA",         "Copper"),
    "Morenci Copper Mine":           (33.0500,  -109.3667, "USA",         "Copper"),
    "Bagdad Copper Mine":            (34.5833,  -113.1833, "USA",         "Copper"),
    "Sierrita Copper Mine":          (31.8167,  -111.0500, "USA",         "Copper"),
    "Ray Copper Mine":               (33.1833,  -110.9833, "USA",         "Copper"),
    "Miami Copper Mine":             (33.3833,  -110.8667, "USA",         "Copper"),
    "Safford Copper Mine":           (32.8167,  -109.7167, "USA",         "Copper"),
    "Grasberg Copper Mine":          (-4.0500,   137.1167, "Indonesia",   "Copper"),
    "Batu Hijau Copper Mine":        (-8.9833,   116.8833, "Indonesia",   "Copper"),
    "Olympic Dam Copper Mine":       (-30.4333,  136.8833, "Australia",   "Copper"),
    "Mount Isa Copper Mine":         (-20.7333,  139.4833, "Australia",   "Copper"),
    "Ernest Henry Copper Mine":      (-20.4500,  140.7167, "Australia",   "Copper"),
    "Cadia-Ridgeway Copper Mine":    (-33.4500,  148.9667, "Australia",   "Copper"),
    "Prominent Hill Copper Mine":    (-29.7167,  135.5333, "Australia",   "Copper"),
    "Kansanshi Copper Mine":         (-12.0833,   26.4333, "Zambia",      "Copper"),
    "Lumwana Copper Mine":           (-12.3167,   25.8167, "Zambia",      "Copper"),
    "Konkola Copper Mine":           (-12.4000,   27.8833, "Zambia",      "Copper"),
    "Mopani Copper Mine":            (-12.8000,   28.2000, "Zambia",      "Copper"),
    "Tenke Fungurume Copper Mine":   (-10.6000,   26.1000, "DR Congo",    "Copper"),
    "Kamoa-Kakula Copper Mine":      (-10.7667,   25.8000, "DR Congo",    "Copper"),
    "Mutanda Copper Mine":           (-10.9333,   27.5667, "DR Congo",    "Copper"),
    "Kamoto Copper Mine":            (-10.7167,   26.4000, "DR Congo",    "Copper"),
    "Oyu Tolgoi Copper Mine":        (43.0000,   106.8500, "Mongolia",    "Copper"),
    "Erdenet Copper Mine":           (49.0333,   104.0667, "Mongolia",    "Copper"),
    "Norilsk Copper District":       (69.3500,    88.2000, "Russia",      "Copper"),
    "Udokan Copper Deposit":         (56.5333,   118.2500, "Russia",      "Copper"),
    "Kounrad Copper Mine":           (47.6333,    74.9833, "Kazakhstan",  "Copper"),
    "Buenavista Copper Mine":        (30.3167,  -109.7333, "Mexico",      "Copper"),
    "La Caridad Copper Mine":        (30.1167,  -109.4833, "Mexico",      "Copper"),
    "Lubin Copper Mine":             (51.4000,    16.2000, "Poland",      "Copper"),
    "Rudna Copper Mine":             (51.5167,    16.2667, "Poland",      "Copper"),
    "Highland Valley Copper Mine":   (50.4833,  -121.0333, "Canada",      "Copper"),
    "Mount Polley Copper Mine":      (52.5500,  -121.6167, "Canada",      "Copper"),
    "Cobre Panama Mine":             (8.6500,    -80.6167, "Panama",      "Copper"),
    "Sarcheshmeh Copper Mine":       (29.5500,    55.7667, "Iran",        "Copper"),
    "Las Cruces Copper Mine":        (37.5500,    -6.2333, "Spain",       "Copper"),
    "Tampakan Copper Deposit":       (6.3833,    125.0667, "Philippines", "Copper"),
    "Cayeli Copper Mine":            (41.0833,    40.7333, "Turkey",      "Copper"),

    # ==================== LIMESTONE MINES ====================
    # USA
    "Indiana Limestone Quarry":      (38.9167,  -86.5167, "USA",          "Limestone"),
    "Lehigh Portland Cement":        (40.6833,  -75.5167, "USA",          "Limestone"),
    "Texas Limestone Quarry":        (30.3500,  -97.9833, "USA",          "Limestone"),
    "Florida Limestone District":    (25.7833,  -80.3000, "USA",          "Limestone"),
    "Ames Limestone Quarry":         (41.9667,  -93.6167, "USA",          "Limestone"),
    # INDIA
    "Maihar Cement Limestone":       (24.2667,   80.7833, "India",        "Limestone"),
    "Ariyalur Limestone Mines":      (11.1500,   79.0833, "India",        "Limestone"),
    "Satna Limestone District":      (24.6000,   80.8333, "India",        "Limestone"),
    "Gulbarga Limestone Mines":      (17.3333,   76.8167, "India",        "Limestone"),
    "Rajasthan Limestone Belt":      (25.0833,   74.6167, "India",        "Limestone"),
    # CHINA
    "Guangdong Limestone District":  (23.5000,  113.2333, "China",        "Limestone"),
    "Sichuan Limestone Quarries":    (29.6500,  104.0667, "China",        "Limestone"),
    "Yunnan Limestone District":     (25.0500,  102.7167, "China",        "Limestone"),
    # TURKEY
    "Afyonkarahisar Marble Belt":    (38.7500,   30.5333, "Turkey",       "Limestone"),
    "Bilecik Limestone Quarry":      (40.1500,   29.9833, "Turkey",       "Limestone"),
    # EGYPT
    "Minya Limestone Quarries":      (28.1000,   30.7500, "Egypt",        "Limestone"),
    "Qena Limestone District":       (26.1667,   32.7333, "Egypt",        "Limestone"),
    # BRAZIL
    "Minas Gerais Limestone":        (-19.4833,  -44.1667, "Brazil",      "Limestone"),
    "Pedro Leopoldo Limestone":      (-19.6167,  -44.0333, "Brazil",      "Limestone"),
    # GERMANY
    "Ruedersdorf Limestone":         (52.4667,   13.8000, "Germany",      "Limestone"),
    "Eifel Limestone District":      (50.3333,    6.9333, "Germany",      "Limestone"),
    # POLAND
    "Kielce Limestone Region":       (50.8500,   20.6333, "Poland",       "Limestone"),
    # VIETNAM
    "Ha Long Bay Limestone":         (20.9167,  107.1667, "Vietnam",      "Limestone"),
    "Ninh Binh Limestone":           (20.2500,  105.9667, "Vietnam",      "Limestone"),
    # MALAYSIA
    "Ipoh Limestone Quarries":       (4.5833,   101.0833, "Malaysia",     "Limestone"),
    # AUSTRALIA
    "Portsea Limestone Quarry":      (-38.3167,  144.7167,"Australia",    "Limestone"),
    "Napier Downs Limestone":        (-17.5000,  124.9167,"Australia",    "Limestone"),

    # ── GOLD ──────────────────────────────────────────────────────────────────
    "Hutti Gold Mine":                  (16.2200,  76.6300, "India",       "Gold"),
    "Kolar Gold Fields":                (12.9200,  78.2700, "India",       "Gold"),
    "Dharwar Gold Belt":                (15.4600,  75.0100, "India",       "Gold"),
    "Muruntau Gold Mine":               (41.5500,  64.5700, "Uzbekistan",  "Gold"),
    "Kibali Gold Mine":                 (3.6000,   29.6000, "DRC",         "Gold"),
    "Loulo-Gounkoto Gold Mine":         (13.9000,  -9.3400, "Mali",        "Gold"),
    "Lihir Gold Mine":                  (-3.1200, 152.6400, "Papua New Guinea","Gold"),
    "Porgera Gold Mine":                (-5.4700, 143.1300, "Papua New Guinea","Gold"),
    "Boddington Gold Mine":             (-32.7900, 116.3700,"Australia",   "Gold"),
    "Superpit Gold Mine (Kalgoorlie)":  (-30.7800, 121.5000,"Australia",   "Gold"),
    "Newmont Nevada (Carlin Trend)":    (40.7200, -116.4800,"USA",         "Gold"),
    "Fort Knox Gold Mine":              (64.8200, -147.2900,"USA",         "Gold"),
    "Red Lake Gold Mine":               (51.0200,  -93.7900,"Canada",      "Gold"),
    "Mponeng Gold Mine":                (-26.4800,  27.4600,"South Africa","Gold"),
    "South Deep Gold Mine":             (-26.4200,  27.3900,"South Africa","Gold"),
    "Yanacocha Gold Mine":              (-6.9500,  -78.5300,"Peru",        "Gold"),
    "Pueblo Viejo Gold Mine":           (19.0200,  -70.1000,"Dominican Republic","Gold"),
    "Detour Lake Gold Mine":            (49.7800,  -79.6900,"Canada",      "Gold"),
    "Tarkwa Gold Mine":                 (5.2900,   -2.0000, "Ghana",       "Gold"),
    "Obuasi Gold Mine":                 (6.2000,   -1.6700, "Ghana",       "Gold"),
    "Geita Gold Mine":                  (-2.8700,  32.2300, "Tanzania",    "Gold"),
    "Grasberg Gold (joint)":            (-4.0500, 137.1100, "Indonesia",   "Precious Metal"),
    "Olimpiada Gold Mine":              (59.1700,  92.7300, "Russia",      "Gold"),
    "Kumtor Gold Mine":                 (41.8600,  78.1800, "Kyrgyzstan",  "Gold"),
    "Cripple Creek Gold":               (38.7400, -105.1800,"USA",         "Gold"),

    # ── NICKEL ────────────────────────────────────────────────────────────────
    "Sukinda Chromite-Nickel Belt":     (21.0000,  85.8000, "India",       "Nickel"),
    "Norilsk Nickel":                   (69.3400,  88.2000, "Russia",      "Nickel"),
    "Sudbury Nickel Basin":             (46.4900,  -80.9900,"Canada",      "Nickel"),
    "Thompson Nickel Mine":             (55.7400,  -97.8500,"Canada",      "Nickel"),
    "Raglan Nickel Mine":               (61.6900,  -73.6500,"Canada",      "Nickel"),
    "Voisey's Bay Nickel":              (56.4700,  -62.0700,"Canada",      "Nickel"),
    "Jinchuan Nickel Mine":             (38.5200, 102.1700, "China",       "Nickel"),
    "Vale Onca Puma":                   (-6.4200,  -51.3800,"Brazil",      "Nickel"),
    "PT Vale Sorowako":                 (-2.5500, 121.3800, "Indonesia",   "Nickel"),
    "Goro Nickel Mine":                 (-22.2700, 166.9700,"New Caledonia","Nickel"),
    "Koniambo Nickel":                  (-20.9000, 164.4000,"New Caledonia","Nickel"),
    "Loma de Niquel":                   (9.7100,  -65.6500, "Venezuela",   "Nickel"),
    "Barro Alto Nickel":                (-14.9500, -48.9300,"Brazil",      "Nickel"),
    "Ambatovy Nickel Mine":             (-18.7600,  48.4100,"Madagascar",  "Nickel"),
    "Nikkelverk Nickel (Kristiansand)": (58.1500,   7.9600, "Norway",      "Nickel"),
    "Tati Nickel Mine":                 (-21.0300,  27.4500,"Botswana",    "Nickel"),

    # ── ZINC ──────────────────────────────────────────────────────────────────
    "Rampura Agucha Zinc Mine":         (24.6300,  74.6700, "India",       "Zinc"),
    "Sindesar Khurd Zinc Mine":         (25.5300,  73.6700, "India",       "Zinc"),
    "Rajpura Dariba Zinc Mine":         (25.6700,  74.2700, "India",       "Zinc"),
    "Zawar Zinc Mines":                 (24.3500,  73.6800, "India",       "Zinc"),
    "Red Dog Zinc Mine":                (68.0600, -162.8900,"USA",         "Zinc"),
    "Century Zinc Mine":                (-18.7200, 139.6200,"Australia",   "Zinc"),
    "McArthur River Zinc Mine":         (-16.4400, 136.0900,"Australia",   "Zinc"),
    "Cannington Silver-Zinc Mine":      (-22.3200, 140.7700,"Australia",   "Zinc"),
    "Brunswick Zinc Mine":              (47.4400,  -65.5200,"Canada",      "Zinc"),
    "Antamina Zinc-Copper Mine":        (-9.5300,  -77.0500,"Peru",        "Zinc"),
    "San Cristobal Zinc Mine":          (-21.8900,  -66.8200,"Bolivia",    "Zinc"),
    "Tara Zinc Mine":                   (53.4500,   -6.9100,"Ireland",     "Zinc"),
    "Neves-Corvo Zinc Mine":            (37.7000,   -7.9700,"Portugal",    "Zinc"),
    "Vazante Zinc Mine":                (-17.9900, -46.9100,"Brazil",      "Zinc"),
    "Gamsberg Zinc Mine":               (-29.2000,  18.6000,"South Africa","Zinc"),
    "Lennard Shelf Zinc":               (-18.5000, 125.4000,"Australia",   "Zinc"),
    "Myra Falls Zinc Mine":             (49.6000, -125.5500,"Canada",      "Zinc"),
    "Dugald River Zinc Mine":           (-19.9200, 139.7000,"Australia",   "Zinc"),
    "Idarado Zinc Mine":                (37.9000, -107.7000,"USA",         "Zinc"),

    # ── POLYMETALLIC (multi-mineral) ──────────────────────────────────────────
    "Neves-Corvo Polymetallic":         (37.7200,  -7.9500, "Portugal",    "Polymetallic"),
    "Broken Hill Polymetallic":         (-31.9500, 141.4700,"Australia",   "Polymetallic"),
    "Cerro de Pasco Polymetallic":      (-10.6900, -76.2600,"Peru",        "Polymetallic"),
    "Bayan Obo Polymetallic":           (41.8200, 110.0200, "China",       "Polymetallic"),
    "Mount Isa Copper-Zinc":            (-20.7200, 139.4900,"Australia",   "Polymetallic"),
    # ==================== MANGANESE MINES ====================
    # AUSTRALIA
    "Groote Eylandt Manganese":      (-14.0000,  136.5000, "Australia",  "Manganese"),
    "Woodie Woodie Manganese":       (-22.5333,  121.2333, "Australia",  "Manganese"),
    # SOUTH AFRICA
    "Hotazel Manganese Mines":       (-27.2333,   22.9833, "South Africa","Manganese"),
    "Mamatwan Mine":                 (-27.3667,   22.9167, "South Africa","Manganese"),
    "Wessels Mine":                  (-27.2167,   22.9000, "South Africa","Manganese"),
    "Nchwaning Mine":                (-27.3833,   22.8833, "South Africa","Manganese"),
    # GABON
    "Moanda Manganese Mine":         (-1.5667,    13.2000, "Gabon",       "Manganese"),
    "Bangombe Manganese":            (-1.4833,    13.0833, "Gabon",       "Manganese"),
    # BRAZIL
    "Morro da Mina Manganese":       (-20.5833,  -43.7167, "Brazil",      "Manganese"),
    "Corumba Manganese":             (-19.0167,  -57.6500, "Brazil",      "Manganese"),
    "Azul Manganese Mine":           (-6.0833,   -50.0500, "Brazil",      "Manganese"),
    # INDIA
    "Balaghat Manganese Mines":      (21.8167,    80.1833, "India",       "Manganese"),
    "Vizag Manganese District":      (17.6833,    83.2167, "India",       "Manganese"),
    "Sandur Manganese Mine":         (15.0833,    76.5500, "India",       "Manganese"),
    "Nagpur Manganese District":     (21.1500,    79.0833, "India",       "Manganese"),
    # UKRAINE
    "Nikopol Manganese Basin":       (47.5667,    34.3833, "Ukraine",     "Manganese"),
    "Marganets Manganese Mine":      (47.6500,    34.6333, "Ukraine",     "Manganese"),
    # CHINA
    "Guizhou Manganese District":    (27.0000,   107.5000, "China",       "Manganese"),
    "Guangxi Manganese Mines":       (23.3167,   107.6833, "China",       "Manganese"),
    "Hunan Manganese Belt":          (28.2333,   112.9333, "China",       "Manganese"),
    # GHANA
    "Nsuta Manganese Mine":          (5.2167,     -1.9500, "Ghana",       "Manganese"),
    # KAZAKHSTAN
    "Zhairem Manganese Mine":        (47.3167,    66.0500, "Kazakhstan",  "Manganese"),
    # MEXICO
    "Molango Manganese Deposit":     (20.7833,  -98.7333,  "Mexico",      "Manganese"),
}


def get_mines_by_type(mineral_type):
    return {n: d for n, d in LEGAL_MINING_AREAS.items() if d[3] == mineral_type}


def get_mine_count():
    counts = {}
    for d in LEGAL_MINING_AREAS.values():
        counts[d[3]] = counts.get(d[3], 0) + 1
    return counts


def get_mines_by_country(country):
    return {n: d for n, d in LEGAL_MINING_AREAS.items() if d[2] == country}


def get_all_countries():
    return sorted(set(d[2] for d in LEGAL_MINING_AREAS.values()))


def get_total_count():
    return len(LEGAL_MINING_AREAS)


if __name__ == "__main__":
    print("=" * 60)
    print("LEGAL MINING AREAS DATABASE")
    print("=" * 60)
    counts = get_mine_count()
    print("\nMines by Type:")
    for t, c in counts.items():
        print(f"   {t}: {c} mines")
    print(f"\nTotal Mines: {get_total_count()}")
    print(f"Countries:   {len(get_all_countries())}")