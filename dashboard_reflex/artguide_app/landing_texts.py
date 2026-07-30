"""Marketing copy for the landing page, in the three supported languages.

Headings are split into a plain part and an `_em` part rendered in italic rust.
`hero_lines` are explicit line breaks so the masked line-by-line reveal works.
"""

LANDING = {
    "es": {
        "nav": ["Cómo funciona", "Personalización", "Casos de uso", "FAQ"],
        "nav_cta": "Solicitar una demo",
        "open_app": "Probar ArtGuide",
        # Hero
        "hero_eyebrow": "Una cámara. Una historia por obra.",
        "hero_lines": ["Reconoce cada obra al instante", "y escucha su historia con"],
        "hero_em": "voz natural.",
        "hero_sub": (
            "ArtGuide identifica una obra de arte en segundos y genera una descripción "
            "completa, personalizada por idioma, duración y enfoque — sin instalación "
            "ni equipos adicionales."
        ),
        "hero_cta": "Solicitar una demo",
        "hero_ghost": "Ver cómo funciona →",
        "hero_frame": "[ montaje de exposición — placeholder ]",
        # Problem
        "problem_eyebrow": "El problema",
        "problem_heading": "Tener audioguía lista para cada exposición sigue siendo ",
        "problem_em": "caro y lento",
        "problem_cards": [
            "Los dispositivos de audioguía física son caros de comprar, mantener y reponer.",
            "Contratar guías o grabar audioguías en cada idioma nuevo lleva semanas.",
            "Cada vez que cambia una pieza de la exposición, hay que regrabar o reimprimir contenido.",  # noqa
            "El visitante espera algo moderno: sin colas para recoger un aparato, y con la posibilidad de elegir idioma y nivel de detalle.",  # noqa
        ],
        # How it works
        "how_eyebrow": "Cómo funciona",
        "how_heading": "Del catálogo a la voz, ",
        "how_em": "en cuatro pasos",
        "how_steps": [
            ("Sube el catálogo de obras", "Fotografías, sin formato especial."),
            ("El sistema las indexa", "Reconocimiento automático, listo en minutos."),
            ("El visitante enfoca la obra", "Desde el navegador del móvil, sin apps."),
            (
                "Escucha su audioguía",
                "En su idioma y duración elegidos, y enfoque temático (bajo demanda).",
            ),
        ],
        # Personalisation
        "pers_eyebrow": "Personalización",
        "pers_heading": "Cada visitante vive una experiencia ",
        "pers_em": "adaptada a lo que le interesa",
        "pers_sub": "Algo que ninguna audioguía física puede ofrecer.",
        "pers_cards": [
            ("Idioma", "Castellano · Catalán · Inglés", "Ampliable a demanda."),
            ("Duración", "Breve · Media · Extendida", "Según el tiempo del visitante."),
            (
                "Enfoque temático (bajo demanda)",
                "Historia · Historia del arte · Curiosidades",
                "La misma obra, contada distinto.",
            ),
        ],
        # Benefits
        "ben_eyebrow": "Beneficios clave",
        "ben_heading": "Pensado para exposiciones ",
        "ben_em": "que no se quedan quietas",
        "ben_items": [
            ("Montaje rápido", "Sube tus obras y el sistema las indexa automáticamente."),
            (
                "Sin inversión en hardware",
                "Cero dispositivos que comprar, mantener o desinfectar.",
            ),
            ("Flexible por naturaleza", "Ideal para exposiciones que cambian cada pocos meses."),
            (
                "Personalización real",
                "Idioma, duración y enfoque (bajo demanda) a elección del visitante.",
            ),
            ("Escalable", "Funciona igual con una sala que con una colección completa."),
        ],
        # Use cases
        "uc_eyebrow": "Casos de uso",
        "uc_heading": "Una misma guía, ",
        "uc_em": "para cada formato de exhibición",
        "uc_cards": [
            (
                "Museos y colecciones permanentes",
                "La colección permanente incorpora piezas nuevas sin rehacer la audioguía entera.",
            ),
            (
                "Exposiciones temporales",
                "La audioguía se monta al mismo ritmo que se monta la exposición.",
            ),
            ("Muestras itinerantes", "El catálogo viaja con la exposición, sin reinstalar nada."),
            ("Galerías y espacios efímeros", "Ideal para montajes breves con recursos ajustados."),
            ("Ferias y bienales de arte", "Múltiples obras y artistas, un único punto de acceso."),
            ("Centros cívicos y bibliotecas", "Cultura accesible en espacios no museísticos."),
        ],
        # Technology
        "tech_eyebrow": "Cómo lo hacemos posible",
        "tech_heading": "Detrás de cada audioguía, ",
        "tech_em": "tres tecnologías",
        "tech_sub": (
            "Tres piezas que trabajan juntas para que el visitante enfoque una obra y "
            "escuche su historia — sin fricción."
        ),
        "tech_rows": [
            (
                "Reconocimiento",
                "Visual, en tiempo real.",
                "El sistema identifica la obra directamente desde la cámara, sobre el "
                "catálogo de tu colección o muestra.",
            ),
            (
                "Voz",
                "Síntesis neuronal de alta fidelidad.",
                "Voces naturales en castellano, catalán e inglés, ampliables a demanda "
                "según la exposición.",
            ),
            (
                "Infraestructura",
                "Propia y privada.",
                "Alojada en nuestros servidores: privacidad para tus obras y respuesta sin "
                "depender de terceros. Alojamiento on-premise, bajo demanda.",
            ),
        ],
        # FAQ
        "faq_eyebrow": "Preguntas frecuentes",
        "faq_heading": "Todo lo que necesitas saber ",
        "faq_em": "antes de una demo",
        "faq_sub_before": "Si te queda alguna pregunta sin responder, ",
        "faq_sub_link": "escríbenos directamente",
        "faq_sub_after": " y te contestamos personalmente.",
        "faq": [
            (
                "¿Qué hace falta para dar de alta una nueva exposición?",
                "Nos envías las fotografías de las obras y preparamos el catálogo contigo. "
                "Sin instalación ni dispositivos que repartir.",
            ),
            (
                "¿Podemos cambiar las obras a mitad de exposición?",
                "Sí — el catálogo se actualiza de forma rápida, sin reinstalar nada ni "
                "esperar un nuevo lote de dispositivos.",
            ),
            (
                "¿Qué pasa cuando termina la exposición, se borran los datos?",
                "Tú decides: puedes archivar el catálogo para reutilizarlo en la próxima "
                "muestra o eliminarlo por completo.",
            ),
            (
                "¿El visitante necesita descargar una app?",
                "No. Se accede desde el navegador del móvil, sin descargas ni registro.",
            ),
        ],
        # CTA + footer
        "cta_eyebrow": "Hablemos",
        "cta_heading": "Hablemos de ",
        "cta_em": "tu próximo proyecto",
        "cta_sub": "Contáctanos y te mostramos ArtGuide funcionando con tus propias obras.",
        "cta_button": "Contactar",
        "footer": "© 2026 ArtGuide — Una cámara. Una historia por obra.",
    },
    "ca": {
        "nav": ["Com funciona", "Personalització", "Casos d'ús", "FAQ"],
        "nav_cta": "Sol·licitar una demo",
        "open_app": "Provar ArtGuide",
        # Hero
        "hero_eyebrow": "Una càmera. Una història per obra.",
        "hero_lines": ["Reconeix cada obra a l'instant", "i n'escolta la història amb"],
        "hero_em": "veu natural.",
        "hero_sub": (
            "ArtGuide identifica una obra d'art en segons i genera una descripció "
            "completa, personalitzada per idioma, durada i enfocament — sense "
            "instal·lació ni equips addicionals."
        ),
        "hero_cta": "Sol·licitar una demo",
        "hero_ghost": "Veure com funciona →",
        "hero_frame": "[ muntatge d'exposició — placeholder ]",
        # Problem
        "problem_eyebrow": "El problema",
        "problem_heading": "Tenir una audioguia a punt per a cada exposició continua sent ",
        "problem_em": "car i lent",
        "problem_cards": [
            "Els dispositius d'audioguia física són cars de comprar, mantenir i reposar.",
            "Contractar guies o gravar audioguies en cada idioma nou triga setmanes.",
            "Cada vegada que canvia una peça de l'exposició, cal regravar o reimprimir contingut.",
            "El visitant espera alguna cosa moderna: sense cues per recollir un aparell, i amb la possibilitat de triar idioma i nivell de detall.", # noqa
        ],
        # How it works
        "how_eyebrow": "Com funciona",
        "how_heading": "Del catàleg a la veu, ",
        "how_em": "en quatre passos",
        "how_steps": [
            ("Puja el catàleg d'obres", "Fotografies, sense format especial."),
            ("El sistema les indexa", "Reconeixement automàtic, a punt en minuts."),
            ("El visitant enfoca l'obra", "Des del navegador del mòbil, sense apps."),
            (
                "Escolta la seva audioguia",
                "En el seu idioma i durada triats, i enfocament temàtic (sota demanda).",
            ),
        ],
        # Personalisation
        "pers_eyebrow": "Personalització",
        "pers_heading": "Cada visitant viu una experiència ",
        "pers_em": "adaptada al que li interessa",
        "pers_sub": "Alguna cosa que cap audioguia física pot oferir.",
        "pers_cards": [
            ("Idioma", "Castellà · Català · Anglès", "Ampliable a demanda."),
            ("Durada", "Breu · Mitjana · Extensa", "Segons el temps del visitant."),
            (
                "Enfocament temàtic (sota demanda)",
                "Història · Història de l'art · Curiositats",
                "La mateixa obra, explicada de manera diferent.",
            ),
        ],
        # Benefits
        "ben_eyebrow": "Beneficis clau",
        "ben_heading": "Pensat per a exposicions ",
        "ben_em": "que no s'estan quietes",
        "ben_items": [
            ("Muntatge ràpid", "Puja les teves obres i el sistema les indexa automàticament."),
            (
                "Sense inversió en maquinari",
                "Zero dispositius per comprar, mantenir o desinfectar.",
            ),
            ("Flexible per naturalesa", "Ideal per a exposicions que canvien cada pocs mesos."),
            (
                "Personalització real",
                "Idioma, durada i enfocament (sota demanda) a elecció del visitant.",
            ),
            ("Escalable", "Funciona igual amb una sala que amb una col·lecció completa."),
        ],
        # Use cases
        "uc_eyebrow": "Casos d'ús",
        "uc_heading": "Una mateixa guia, ",
        "uc_em": "per a cada format d'exhibició",
        "uc_cards": [
            (
                "Museus i col·leccions permanents",
                "La col·lecció permanent incorpora peces noves sense refer l'audioguia sencera.",
            ),
            (
                "Exposicions temporals",
                "L'audioguia es munta al mateix ritme que es munta l'exposició.",
            ),
            ("Mostres itinerants", "El catàleg viatja amb l'exposició, sense reinstal·lar res."),
            ("Galeries i espais efímers", "Ideal per a muntatges breus amb recursos ajustats."),
            ("Fires i biennals d'art", "Múltiples obres i artistes, un únic punt d'accés."),
            ("Centres cívics i biblioteques", "Cultura accessible en espais no museístics."),
        ],
        # Technology
        "tech_eyebrow": "Com ho fem possible",
        "tech_heading": "Darrere de cada audioguia, ",
        "tech_em": "tres tecnologies",
        "tech_sub": (
            "Tres peces que treballen juntes perquè el visitant enfoqui una obra i "
            "n'escolti la història — sense fricció."
        ),
        "tech_rows": [
            (
                "Reconeixement",
                "Visual, en temps real.",
                "El sistema identifica l'obra directament des de la càmera, sobre el "
                "catàleg de la teva col·lecció o mostra.",
            ),
            (
                "Veu",
                "Síntesi neuronal d'alta fidelitat.",
                "Veus naturals en castellà, català i anglès, ampliables a demanda "
                "segons l'exposició.",
            ),
            (
                "Infraestructura",
                "Pròpia i privada.",
                "Allotjada als nostres servidors: privacitat per a les teves obres i "
                "resposta sense dependre de tercers. Allotjament on-premise, sota demanda.",
            ),
        ],
        # FAQ
        "faq_eyebrow": "Preguntes freqüents",
        "faq_heading": "Tot el que necessites saber ",
        "faq_em": "abans d'una demo",
        "faq_sub_before": "Si et queda algun dubte, ",
        "faq_sub_link": "escriu-nos directament",
        "faq_sub_after": " i et contestem personalment.",
        "faq": [
            (
                "Què cal per donar d'alta una nova exposició?",
                "Ens envies les fotografies de les obres i preparem el catàleg amb tu. "
                "Sense instal·lació ni dispositius per repartir.",
            ),
            (
                "Podem canviar les obres a mitja exposició?",
                "Sí — el catàleg s'actualitza de forma ràpida, sense reinstal·lar res "
                "ni esperar un nou lot de dispositius.",
            ),
            (
                "Què passa quan acaba l'exposició, s'esborren les dades?",
                "Tu decideixes: pots arxivar el catàleg per reutilitzar-lo a la propera "
                "mostra o eliminar-lo del tot.",
            ),
            (
                "El visitant necessita descarregar una app?",
                "No. S'hi accedeix des del navegador del mòbil, sense descàrregues ni registre.",
            ),
        ],
        # CTA + footer
        "cta_eyebrow": "Parlem-ne",
        "cta_heading": "Parlem del ",
        "cta_em": "teu proper projecte",
        "cta_sub": "Contacta'ns i et mostrem ArtGuide funcionant amb les teves pròpies obres.",
        "cta_button": "Contactar",
        "footer": "© 2026 ArtGuide — Una càmera. Una història per obra.",
    },
    "en": {
        "nav": ["How it works", "Personalization", "Use cases", "FAQ"],
        "nav_cta": "Request a demo",
        "open_app": "Try ArtGuide",
        # Hero
        "hero_eyebrow": "One camera. One story per artwork.",
        "hero_lines": ["Recognizes each artwork instantly", "and tells its story in"],
        "hero_em": "a natural voice.",
        "hero_sub": (
            "ArtGuide identifies an artwork in seconds and generates a complete "
            "description, personalized by language, length, and focus — no "
            "installation or extra equipment required."
        ),
        "hero_cta": "Request a demo",
        "hero_ghost": "See how it works →",
        "hero_frame": "[ exhibition mockup — placeholder ]",
        # Problem
        "problem_eyebrow": "The problem",
        "problem_heading": "Having an audio guide ready for every exhibition is still ",
        "problem_em": "expensive and slow",
        "problem_cards": [
            "Physical audio guide devices are expensive to buy, maintain, and replace.",
            "Hiring guides or recording audio guides for a new language takes weeks.",
            "Every time a piece in the exhibition changes, content has to be re-recorded or reprinted.",  # noqa
            "Visitors expect something modern: no queuing for a device, and the ability to choose language and level of detail.",  # noqa
        ],
        # How it works
        "how_eyebrow": "How it works",
        "how_heading": "From catalog to voice, ",
        "how_em": "in four steps",
        "how_steps": [
            ("Upload the catalog of artworks", "Photographs, no special format."),
            ("The system indexes them", "Automatic recognition, ready in minutes."),
            ("The visitor points at the artwork", "From their phone's browser, no apps."),
            (
                "They listen to their audio guide",
                "In their chosen language and length, with thematic focus (on request).",
            ),
        ],
        # Personalisation
        "pers_eyebrow": "Personalization",
        "pers_heading": "Every visitor gets an experience ",
        "pers_em": "tailored to what interests them",
        "pers_sub": "Something no physical audio guide can offer.",
        "pers_cards": [
            ("Language", "Spanish · Catalan · English", "Expandable on request."),
            ("Length", "Short · Medium · Extended", "Based on the visitor's time."),
            (
                "Thematic focus (on request)",
                "History · Art history · Trivia",
                "The same artwork, told differently.",
            ),
        ],
        # Benefits
        "ben_eyebrow": "Key benefits",
        "ben_heading": "Built for exhibitions ",
        "ben_em": "that don't stand still",
        "ben_items": [
            ("Fast setup", "Upload your artworks and the system indexes them automatically."),
            (
                "No investment in hardware",
                "Zero devices to buy, maintain, or disinfect.",
            ),
            ("Flexible by design", "Ideal for exhibitions that change every few months."),
            (
                "Real personalization",
                "Language, length, and focus (on request), chosen by the visitor.",
            ),
            ("Scalable", "Works the same for a single room as for a full collection."),
        ],
        # Use cases
        "uc_eyebrow": "Use cases",
        "uc_heading": "One guide, ",
        "uc_em": "for every exhibition format",
        "uc_cards": [
            (
                "Museums and permanent collections",
                "The permanent collection adds new pieces without rebuilding the whole audio guide.", # noqa
            ),
            (
                "Temporary exhibitions",
                "The audio guide comes together at the same pace as the exhibition.",
            ),
            (
                "Touring exhibitions",
                "The catalog travels with the exhibition, nothing to reinstall.",
            ),
            ("Galleries and pop-up spaces", "Ideal for short setups with limited resources."),
            ("Art fairs and biennials", "Multiple artworks and artists, a single point of access."),
            ("Civic centers and libraries", "Culture made accessible outside museum spaces."),
        ],
        # Technology
        "tech_eyebrow": "How we make it possible",
        "tech_heading": "Behind every audio guide, ",
        "tech_em": "three technologies",
        "tech_sub": (
            "Three pieces working together so the visitor can point at an artwork and "
            "hear its story — with no friction."
        ),
        "tech_rows": [
            (
                "Recognition",
                "Visual, in real time.",
                "The system identifies the artwork directly from the camera, against "
                "your collection or exhibition catalog.",
            ),
            (
                "Voice",
                "High-fidelity neural synthesis.",
                "Natural voices in Spanish, Catalan, and English, expandable on request "
                "depending on the exhibition.",
            ),
            (
                "Infrastructure",
                "Our own, private.",
                "Hosted on our own servers: privacy for your artworks and fast responses "
                "with no third-party dependency. On-premise hosting, on request.",
            ),
        ],
        # FAQ
        "faq_eyebrow": "Frequently asked questions",
        "faq_heading": "Everything you need to know ",
        "faq_em": "before a demo",
        "faq_sub_before": "If you still have a question, ",
        "faq_sub_link": "write to us directly",
        "faq_sub_after": " and we'll get back to you personally.",
        "faq": [
            (
                "What do we need to onboard a new exhibition?",
                "You send us the photographs of the artworks and we put the catalog "
                "together with you. No installation or devices to hand out.",
            ),
            (
                "Can we change the artworks partway through the exhibition?",
                "Yes — the catalog updates quickly, with nothing to reinstall and no "
                "waiting on a new batch of devices.",
            ),
            (
                "What happens to the data when the exhibition ends — is it deleted?",
                "You decide: you can archive the catalog to reuse for the next "
                "exhibition, or delete it entirely.",
            ),
            (
                "Does the visitor need to download an app?",
                "No. It's accessed from the phone's browser, no downloads or sign-up.",
            ),
        ],
        # CTA + footer
        "cta_eyebrow": "Let's talk",
        "cta_heading": "Let's talk about ",
        "cta_em": "your next project",
        "cta_sub": "Get in touch and we'll show you ArtGuide working with your own artworks.",
        "cta_button": "Contact us",
        "footer": "© 2026 ArtGuide — AI-powered audio guides for exhibitions",
    },
}

REPO_URL = "https://github.com/annafalpi27/artguide/tree/main"


# Rotating lines shown on the desktop side panel while the agent works.
# Each entry is (before, emphasis, after) — the emphasis renders italic rust.
WAITING_PHRASES = {
    "es": [
        ("Cada obra tiene una ", "historia detrás", ". Nosotros la contamos."),
        ("Reconocemos ", "miles de obras", " en tres idiomas."),
        ("Tú eliges el ", "idioma y la duración", " — misma obra, otra voz."),
    ],
    "ca": [
        ("Cada obra té una ", "història al darrere", ". Nosaltres l'expliquem."),
        ("Reconeixem ", "milers d'obres", " en tres idiomes."),
        ("Tu tries l'", "idioma i la durada", " — mateixa obra, una altra veu."),
    ],
    "en": [
        ("Every artwork has a ", "story behind it", ". We tell it."),
        ("We recognise ", "thousands of artworks", " in three languages."),
        ("You choose the ", "language and length", " — One camera. One story per artwork."),
    ],
}
