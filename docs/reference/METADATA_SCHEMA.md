# Evolve Consciousness Engine - Metadata Schema

**Version:** 1.0.0
**Last Updated:** November 30, 2025

Complete reference for all metadata fields in the Pinecone vector database.

---

## Table of Contents

- [Overview](#overview)
- [Core Fields](#core-fields)
- [Tagging Fields](#tagging-fields)
- [Primary Fields (Individual)](#primary-fields-individual)
- [Comprehensive Fields (All Detected)](#comprehensive-fields-all-detected)
- [Optional Fields](#optional-fields)
- [Field Categories](#field-categories)
- [Query Examples](#query-examples)
- [Best Practices](#best-practices)

---

## Overview

Every document chunk in Pinecone has metadata attached. This metadata powers semantic search and filtering.

**Total Metadata Fields:** 30+

**Field Types:**
- **string** - Single text value
- **number** - Integer or float
- **list[string]** - Array of text values
- **boolean** - True/false (rare in current schema)

**Data Flow:**
1. Document uploaded → chunked into ~1000 token pieces
2. Each chunk analyzed → tags generated (keyword or AI)
3. Metadata attached → stored in Pinecone alongside vector
4. Query time → filter by metadata to narrow search

---

## Core Fields

These fields exist on EVERY chunk in the database.

### `text`
- **Type:** string
- **Purpose:** The actual text content of the chunk
- **Example:** `"The heart chakra, or Anahata in Sanskrit, is the fourth primary chakra..."`
- **Populated:** Always (required for embedding)
- **Queryable:** No (use semantic search instead)
- **Notes:** Cleaned for UTF-8 compatibility, max ~1000 tokens

### `title`
- **Type:** string
- **Purpose:** Document title (unique identifier)
- **Example:** `"Heart Chakra Healing"`
- **Populated:** Always (required for upload)
- **Queryable:** Yes
- **Filter Example:**
  ```json
  {
    "title": "Heart Chakra Healing"
  }
  ```
- **Notes:** Used for document management (delete, duplicate check)

### `source`
- **Type:** string
- **Purpose:** Source identifier (file path, URL, etc.)
- **Example:** `"/content/intermediate/chakras.md"` or `"notion://page/abc123"`
- **Populated:** Always (defaults to "unknown" if not provided)
- **Queryable:** Yes
- **Filter Example:**
  ```json
  {
    "source": {"$regex": "/content/advanced/.*"}
  }
  ```

### `chunk_index`
- **Type:** number (integer)
- **Purpose:** Position of this chunk in the document (0-based)
- **Example:** `0`, `1`, `2`, etc.
- **Populated:** Always
- **Queryable:** Yes
- **Filter Example:**
  ```json
  {
    "chunk_index": 0
  }
  ```
- **Use Case:** Get only the first chunk of each document (introductions)

### `total_chunks`
- **Type:** number (integer)
- **Purpose:** Total number of chunks in the complete document
- **Example:** `47`
- **Populated:** Always
- **Queryable:** Yes
- **Filter Example:**
  ```json
  {
    "total_chunks": {"$lt": 10}
  }
  ```
- **Use Case:** Find short documents (fewer chunks)

---

## Tagging Fields

Core semantic tags generated for each chunk.

### `tags`
- **Type:** list[string]
- **Purpose:** Comprehensive list of detected concepts (up to 50)
- **Example:** `["heart", "anahata", "forgiveness", "love", "healing", "fourth_chakra"]`
- **Populated:** Always
- **Queryable:** Yes (with `$in` operator)
- **Filter Example:**
  ```json
  {
    "tags": {"$in": ["quantum", "photon"]}
  }
  ```
- **Notes:**
  - Generated from keyword matching or AI
  - Deduplicated, limited to 50 most relevant
  - Mix of specific terms and general concepts

### `primary_theme`
- **Type:** string
- **Purpose:** One-sentence summary of the chunk's main idea
- **Example:** `"Exploring the connection between heart chakra healing and forgiveness practices"`
- **Populated:** When `use_ai_tagging=true`
- **Queryable:** Yes (but usually use semantic search instead)
- **Notes:** Only available with AI tagging (Ollama or OpenAI)

### `consciousness_level`
- **Type:** string
- **Purpose:** Hawkins Scale consciousness level (20-1000)
- **Example:** `"love"`, `"acceptance"`, `"courage"`, `"fear"`, `"enlightenment"`
- **Populated:** Always (defaults to "neutrality" if not detected)
- **Queryable:** Yes
- **Possible Values:**
  - `shame` (20)
  - `guilt` (30)
  - `apathy` (50)
  - `grief` (75)
  - `fear` (100)
  - `desire` (125)
  - `anger` (150)
  - `pride` (175)
  - `courage` (200) ← Empowerment threshold
  - `neutrality` (250)
  - `willingness` (310)
  - `acceptance` (350)
  - `reason` (400)
  - `love` (500)
  - `joy` (540)
  - `peace` (600)
  - `enlightenment` (700-1000)
- **Filter Example:**
  ```json
  {
    "consciousness_level": {"$in": ["love", "joy", "peace"]}
  }
  ```
- **Use Case:** Find uplifting vs. healing content

### `emotions`
- **Type:** list[string]
- **Purpose:** Detected emotional content in the text
- **Example:** `["love", "peace", "joy"]` or `["fear", "anger", "shame"]`
- **Populated:** When emotions are detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `fear`
  - `anger`
  - `sadness`
  - `joy`
  - `love`
  - `shame`
  - `guilt`
  - `peace`
- **Filter Example:**
  ```json
  {
    "emotions": {"$in": ["love", "compassion"]}
  }
  ```

---

## Primary Fields (Individual)

Single "most prominent" value for each category. Use these for simple queries.

### `primary_chakra`
- **Type:** string
- **Purpose:** The main chakra discussed in this chunk
- **Example:** `"heart"`, `"crown"`, `"root"`
- **Populated:** When a chakra is detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `root` (Muladhara)
  - `sacral` (Svadhisthana)
  - `solar_plexus` (Manipura)
  - `heart` (Anahata)
  - `throat` (Vishuddha)
  - `third_eye` (Ajna)
  - `crown` (Sahasrara)
  - `soul_star` (8th chakra)
  - `earth_star` (below root)
- **Filter Example:**
  ```json
  {
    "primary_chakra": "heart"
  }
  ```
- **See Also:** `all_chakras` for chunks that mention multiple chakras

### `tradition`
- **Type:** string
- **Purpose:** Primary spiritual/esoteric tradition
- **Example:** `"vedic"`, `"buddhist"`, `"hermetic"`, `"sufi"`
- **Populated:** When a tradition is detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `hermetic`
  - `kabbalah`
  - `sufi`
  - `gnostic`
  - `rosicrucian`
  - `vedic`
  - `buddhist`
  - `taoist`
  - `shamanic`
  - `egyptian`
  - `hindu`
  - `christian_mysticism`
  - `essene`
- **Filter Example:**
  ```json
  {
    "tradition": {"$in": ["vedic", "hindu", "buddhist"]}
  }
  ```

### `teacher`
- **Type:** string
- **Purpose:** Primary esoteric teacher/philosopher mentioned
- **Example:** `"blavatsky"`, `"hawkins"`, `"dispenza"`, `"steiner"`
- **Populated:** When a teacher is detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `leadbeater` - Charles Leadbeater
  - `besant` - Annie Besant
  - `blavatsky` - Helena Blavatsky
  - `bailey` - Alice Bailey
  - `hall` - Manly P. Hall
  - `steiner` - Rudolf Steiner
  - `troward` - Thomas Troward
  - `holmes` - Ernest Holmes
  - `fleet` - Thurman Fleet
  - `goddard` - Neville Goddard
  - `murphy` - Joseph Murphy
  - `hawkins` - David Hawkins
  - `dispenza` - Joe Dispenza
  - `lipton` - Bruce Lipton
  - `eddy` - Mary Baker Eddy
  - `hopkins` - Emma Curtis Hopkins
  - `cady` - H. Emilie Cady
  - `fillmore` - Myrtle/Charles Fillmore
  - `fox` - Emmet Fox
- **Filter Example:**
  ```json
  {
    "teacher": "blavatsky"
  }
  ```

### `ascension_path`
- **Type:** string
- **Purpose:** Primary spiritual ascension/liberation path
- **Example:** `"12_step_ascension"`, `"buddhist_nirvana"`, `"kabbalistic_devekut"`
- **Populated:** When an ascension path is detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `12_step_ascension` - Recovery as spiritual path
  - `hindu_moksha` - Liberation, self-realization
  - `buddhist_nirvana` - Enlightenment, cessation
  - `kabbalistic_devekut` - Cleaving to God
  - `sufi_fana` - Annihilation in the divine
  - `christian_theosis` - Divinization, union with Christ
  - `rosicrucian_alchemy` - Spiritual transmutation
  - `taoist_immortality` - Golden elixir, inner alchemy
  - `yogic_samadhi` - Yogic enlightenment
- **Filter Example:**
  ```json
  {
    "ascension_path": "12_step_ascension"
  }
  ```

### `bridge_concept`
- **Type:** string
- **Purpose:** Primary consciousness-matter bridge concept
- **Example:** `"photon_consciousness"`, `"quantum_mind"`, `"addiction_ascension"`
- **Populated:** When a bridge concept is detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `photon_consciousness` - Light as awareness
  - `chakra_sephiroth` - Energy centers correspondence
  - `quantum_mind` - Consciousness field theory
  - `meridian_nadi` - Energy channel correspondence
  - `addiction_ascension` - Addiction as spiritual path
  - `neuroscience_mysticism` - Brain and consciousness
  - `quantum_spirituality` - Physics and consciousness
- **Filter Example:**
  ```json
  {
    "bridge_concept": "photon_consciousness"
  }
  ```
- **Use Case:** Find content that bridges science and spirituality

### `recovery_focus`
- **Type:** string
- **Purpose:** Primary addiction/recovery focus
- **Example:** `"alcohol"`, `"drugs"`, `"codependency"`
- **Populated:** When addiction content is detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `alcohol`
  - `drugs`
  - `gambling`
  - `sex`
  - `food`
  - `technology`
  - `codependency`
- **Filter Example:**
  ```json
  {
    "recovery_focus": "alcohol"
  }
  ```

### `healing_modality`
- **Type:** string
- **Purpose:** Primary healing modality mentioned
- **Example:** `"energy_healing"`, `"sound_healing"`, `"breathwork"`
- **Populated:** When a healing modality is detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `energy_healing` - Reiki, pranic healing, etc.
  - `sound_healing` - Singing bowls, tuning forks, etc.
  - `crystal_healing` - Gemstones, quartz, etc.
  - `breathwork` - Pranayama, holotropic, etc.
  - `meditation_type` - Vipassana, TM, zen, etc.
  - `bodywork` - Massage, rolfing, etc.
  - `plant_medicine` - Ayahuasca, psilocybin, etc.
- **Filter Example:**
  ```json
  {
    "healing_modality": "breathwork"
  }
  ```

---

## Comprehensive Fields (All Detected)

These fields contain ALL detected values, not just the primary one. Use for comprehensive queries.

### `all_chakras`
- **Type:** list[string]
- **Purpose:** ALL chakras mentioned in this chunk
- **Example:** `["heart", "crown", "third_eye"]`
- **Populated:** When chakras are detected (may be empty)
- **Queryable:** Yes
- **Filter Example:**
  ```json
  {
    "all_chakras": {"$in": ["crown", "third_eye"]}
  }
  ```
- **Difference from primary_chakra:**
  - `primary_chakra`: Just the main one → `"heart"`
  - `all_chakras`: All mentioned → `["heart", "throat", "crown"]`
- **Use Case:** Find content that discusses multiple chakras together

### `all_meridians`
- **Type:** list[string]
- **Purpose:** ALL meridians/acupuncture points mentioned
- **Example:** `["heart_meridian", "liver", "kidney"]`
- **Populated:** When meridians are detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `lung`
  - `large_intestine`
  - `stomach`
  - `spleen`
  - `heart_meridian`
  - `small_intestine`
  - `bladder`
  - `kidney`
  - `pericardium`
  - `triple_warmer`
  - `gallbladder`
  - `liver`
- **Filter Example:**
  ```json
  {
    "all_meridians": {"$in": ["heart_meridian", "pericardium"]}
  }
  ```

### `all_12_steps`
- **Type:** list[string]
- **Purpose:** ALL 12-step references in this chunk
- **Example:** `["step_1", "step_3", "step_11"]`
- **Populated:** When 12-step content is detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `step_1` - Powerlessness, unmanageable
  - `step_2` - Came to believe, higher power
  - `step_3` - Decision, turn over will
  - `step_4` - Moral inventory
  - `step_5` - Admitted wrongs
  - `step_6` - Ready, defects removed
  - `step_7` - Humbly asked
  - `step_8` - Amends list
  - `step_9` - Direct amends
  - `step_10` - Continued inventory
  - `step_11` - Prayer and meditation
  - `step_12` - Spiritual awakening, carry message
- **Filter Example:**
  ```json
  {
    "all_12_steps": {"$in": ["step_1", "step_2", "step_3"]}
  }
  ```
- **Use Case:** Find early steps vs. maintenance steps

### `all_consciousness_levels`
- **Type:** list[string]
- **Purpose:** ALL consciousness levels discussed
- **Example:** `["fear", "courage", "acceptance"]`
- **Populated:** When multiple levels are detected (may be empty)
- **Queryable:** Yes
- **See:** `consciousness_level` field for possible values
- **Filter Example:**
  ```json
  {
    "all_consciousness_levels": {"$in": ["love", "joy", "peace"]}
  }
  ```

### `all_traditions`
- **Type:** list[string]
- **Purpose:** ALL spiritual traditions mentioned
- **Example:** `["vedic", "buddhist", "taoist"]`
- **Populated:** When traditions are detected (may be empty)
- **Queryable:** Yes
- **See:** `tradition` field for possible values
- **Filter Example:**
  ```json
  {
    "all_traditions": {"$in": ["hermetic", "kabbalah", "gnostic"]}
  }
  ```
- **Use Case:** Find syncretic/comparative mysticism content

### `all_teachers`
- **Type:** list[string]
- **Purpose:** ALL teachers/philosophers mentioned
- **Example:** `["blavatsky", "bailey", "leadbeater"]`
- **Populated:** When teachers are detected (may be empty)
- **Queryable:** Yes
- **See:** `teacher` field for possible values
- **Filter Example:**
  ```json
  {
    "all_teachers": {"$in": ["blavatsky", "besant", "leadbeater"]}
  }
  ```
- **Use Case:** Find Theosophical Society connections

### `all_quantum_physics`
- **Type:** list[string]
- **Purpose:** ALL quantum physics concepts mentioned
- **Example:** `["quantum_field", "zero_point", "frequency"]`
- **Populated:** When quantum concepts are detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `quantum_physics`
  - `field_theory`
  - `frequency`
  - `neuroscience`
  - `epigenetics`
  - `biofield`
- **Filter Example:**
  ```json
  {
    "all_quantum_physics": {"$in": ["quantum_field", "zero_point"]}
  }
  ```

### `all_quantum_particles`
- **Type:** list[string]
- **Purpose:** ALL quantum particles/concepts mentioned
- **Example:** `["photons", "entanglement", "superposition"]`
- **Populated:** When quantum particles are detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `photons`
  - `bosons`
  - `fermions`
  - `entanglement`
  - `superposition`
  - `observer_effect`
  - `wave_particle`
  - `zero_point`
- **Filter Example:**
  ```json
  {
    "all_quantum_particles": {"$in": ["photons", "entanglement"]}
  }
  ```
- **Use Case:** Find specific quantum mechanics topics

### `all_ascension_paths`
- **Type:** list[string]
- **Purpose:** ALL ascension paths discussed
- **Example:** `["12_step_ascension", "buddhist_nirvana", "hindu_moksha"]`
- **Populated:** When ascension paths are detected (may be empty)
- **Queryable:** Yes
- **See:** `ascension_path` field for possible values
- **Filter Example:**
  ```json
  {
    "all_ascension_paths": {"$in": ["12_step_ascension", "christian_theosis"]}
  }
  ```

### `all_bridge_concepts`
- **Type:** list[string]
- **Purpose:** ALL bridge concepts mentioned
- **Example:** `["photon_consciousness", "quantum_mind", "chakra_sephiroth"]`
- **Populated:** When bridge concepts are detected (may be empty)
- **Queryable:** Yes
- **See:** `bridge_concept` field for possible values
- **Filter Example:**
  ```json
  {
    "all_bridge_concepts": {"$in": ["photon_consciousness", "quantum_spirituality"]}
  }
  ```

### `all_universal_laws`
- **Type:** list[string]
- **Purpose:** ALL universal laws/hermetic principles mentioned
- **Example:** `["law_of_attraction", "law_of_vibration", "law_of_correspondence"]`
- **Populated:** When universal laws are detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `law_of_one`
  - `law_of_attraction`
  - `law_of_vibration`
  - `law_of_correspondence` (as above, so below)
  - `law_of_cause_effect` (karma)
  - `law_of_rhythm`
  - `law_of_polarity`
  - `law_of_gender`
  - `law_of_mind`
- **Filter Example:**
  ```json
  {
    "all_universal_laws": {"$in": ["law_of_correspondence", "law_of_vibration"]}
  }
  ```

### `all_healing_modalities`
- **Type:** list[string]
- **Purpose:** ALL healing modalities mentioned
- **Example:** `["breathwork", "sound_healing", "energy_healing"]`
- **Populated:** When healing modalities are detected (may be empty)
- **Queryable:** Yes
- **See:** `healing_modality` field for possible values
- **Filter Example:**
  ```json
  {
    "all_healing_modalities": {"$in": ["breathwork", "meditation_type"]}
  }
  ```

### `all_sacred_geometry`
- **Type:** list[string]
- **Purpose:** ALL sacred geometry patterns/symbols mentioned
- **Example:** `["flower_of_life", "metatron", "fibonacci"]`
- **Populated:** When sacred geometry is detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - Patterns: `flower_of_life`, `metatron`, `sri_yantra`, `golden_ratio`, `fibonacci`, `vesica_piscis`
  - Platonic Solids: `tetrahedron`, `cube`, `octahedron`, `dodecahedron`, `icosahedron`
  - Symbols: `ankh`, `om`, `yin_yang`, `pentagram`, `hexagram`, `cross`, `spiral`
- **Filter Example:**
  ```json
  {
    "all_sacred_geometry": {"$in": ["flower_of_life", "metatron"]}
  }
  ```

### `all_subtle_bodies`
- **Type:** list[string]
- **Purpose:** ALL subtle bodies/energy bodies mentioned
- **Example:** `["etheric", "emotional", "mental"]`
- **Populated:** When subtle bodies are detected (may be empty)
- **Queryable:** Yes
- **Possible Values:**
  - `etheric` - Vital body, prana body
  - `emotional` - Astral body, desire body
  - `mental` - Thought body, lower mind
  - `causal` - Higher mental, soul body
  - `buddhic` - Intuitive body, Christ consciousness
  - `atmic` - Spiritual will, divine purpose
- **Filter Example:**
  ```json
  {
    "all_subtle_bodies": {"$in": ["etheric", "emotional"]}
  }
  ```

### `all_addiction_types`
- **Type:** list[string]
- **Purpose:** ALL addiction types discussed
- **Example:** `["alcohol", "drugs", "codependency"]`
- **Populated:** When addiction types are detected (may be empty)
- **Queryable:** Yes
- **See:** `recovery_focus` field for possible values
- **Filter Example:**
  ```json
  {
    "all_addiction_types": {"$in": ["alcohol", "codependency"]}
  }
  ```

---

## Optional Fields

Fields that may or may not be present.

### `program_level`
- **Type:** string
- **Purpose:** Content difficulty level for addiction recovery program
- **Example:** `"beginner"`, `"intermediate"`, `"advanced"`
- **Populated:** Only for addiction-specific content (detected from filename)
- **Queryable:** Yes
- **Possible Values:**
  - `beginner` - Early recovery, basic concepts
  - `intermediate` - Sustained recovery, deeper work
  - `advanced` - Long-term recovery, spiritual mastery
- **Filter Example:**
  ```json
  {
    "program_level": "beginner"
  }
  ```
- **Detection:** Title starts with "beginner", "intermediate", or "advanced"
- **Notes:** Most general consciousness content won't have this field

---

## Field Categories

### Quick Reference by Use Case

**Basic Document Info:**
- `title`, `source`, `text`, `chunk_index`, `total_chunks`

**Semantic Tags:**
- `tags`, `primary_theme`, `emotions`

**Energy Systems:**
- `primary_chakra`, `all_chakras`, `all_meridians`, `all_subtle_bodies`

**Spiritual Traditions:**
- `tradition`, `all_traditions`, `teacher`, `all_teachers`

**Quantum/Science:**
- `all_quantum_physics`, `all_quantum_particles`, `bridge_concept`, `all_bridge_concepts`

**Recovery/Addiction:**
- `recovery_focus`, `all_addiction_types`, `all_12_steps`, `program_level`

**Consciousness:**
- `consciousness_level`, `all_consciousness_levels`, `ascension_path`, `all_ascension_paths`

**Universal Laws:**
- `all_universal_laws`

**Healing:**
- `healing_modality`, `all_healing_modalities`

**Sacred Geometry:**
- `all_sacred_geometry`

---

## Query Examples

### Simple Queries

**Find all heart chakra content:**
```json
{
  "filters": {
    "primary_chakra": "heart"
  }
}
```

**Find content by a specific teacher:**
```json
{
  "filters": {
    "teacher": "blavatsky"
  }
}
```

**Find beginner-level content:**
```json
{
  "filters": {
    "program_level": "beginner"
  }
}
```

### Intermediate Queries

**Find content about multiple chakras:**
```json
{
  "filters": {
    "all_chakras": {"$in": ["crown", "third_eye"]}
  }
}
```

**Find content at high consciousness levels:**
```json
{
  "filters": {
    "consciousness_level": {"$in": ["love", "joy", "peace", "enlightenment"]}
  }
}
```

**Find Theosophical content:**
```json
{
  "filters": {
    "all_teachers": {"$in": ["blavatsky", "besant", "leadbeater", "bailey"]}
  }
}
```

**Find quantum physics content:**
```json
{
  "filters": {
    "all_quantum_physics": {"$in": ["quantum_field", "zero_point"]}
  }
}
```

### Advanced Queries

**Find content bridging photons and chakras:**
```json
{
  "filters": {
    "bridge_concept": "photon_consciousness",
    "all_chakras": {"$in": ["crown", "third_eye"]}
  }
}
```

**Find Eastern mysticism synthesis:**
```json
{
  "filters": {
    "all_traditions": {"$in": ["vedic", "buddhist", "taoist", "hindu"]}
  }
}
```

**Find early recovery content:**
```json
{
  "filters": {
    "program_level": "beginner",
    "all_12_steps": {"$in": ["step_1", "step_2", "step_3"]}
  }
}
```

**Find hermetic principles with quantum physics:**
```json
{
  "filters": {
    "tradition": "hermetic",
    "all_universal_laws": {"$in": ["law_of_correspondence", "law_of_vibration"]},
    "all_quantum_physics": {"$in": ["quantum_field", "frequency"]}
  }
}
```

**Find content about multiple ascension paths (comparative mysticism):**
```json
{
  "filters": {
    "all_ascension_paths": {"$in": ["12_step_ascension", "buddhist_nirvana", "hindu_moksha"]}
  }
}
```

### Complex Queries

**Find advanced content about photon consciousness, crown chakra, and enlightenment:**
```json
{
  "question": "How does light relate to enlightenment?",
  "filters": {
    "bridge_concept": "photon_consciousness",
    "all_chakras": {"$in": ["crown", "soul_star"]},
    "consciousness_level": {"$in": ["peace", "enlightenment"]},
    "program_level": "advanced"
  },
  "top_k": 10
}
```

**Find content synthesizing 12-step recovery with spiritual ascension:**
```json
{
  "question": "How is addiction recovery a spiritual path?",
  "filters": {
    "ascension_path": "12_step_ascension",
    "all_12_steps": {"$in": ["step_11", "step_12"]},
    "all_ascension_paths": {"$in": ["christian_theosis", "buddhist_nirvana"]}
  },
  "top_k": 8
}
```

**Find healing content with breathwork and specific chakras:**
```json
{
  "question": "Breathwork practices for opening upper chakras",
  "filters": {
    "healing_modality": "breathwork",
    "all_chakras": {"$in": ["throat", "third_eye", "crown"]}
  },
  "top_k": 7
}
```

**Find documents that are first chunks (introductions):**
```json
{
  "filters": {
    "chunk_index": 0,
    "tradition": "vedic"
  }
}
```

---

## Best Practices

### Filtering Strategy

**1. Use Primary Fields for Simple Queries**
```json
// Good - Fast and simple
{
  "primary_chakra": "heart"
}

// Overkill - Unnecessary complexity
{
  "all_chakras": {"$in": ["heart"]}
}
```

**2. Use "all_*" Fields for Comprehensive Queries**
```json
// Good - Find any content mentioning these chakras
{
  "all_chakras": {"$in": ["crown", "third_eye", "soul_star"]}
}

// Too restrictive - Only finds content where crown is PRIMARY
{
  "primary_chakra": "crown"
}
```

**3. Combine Fields for Precision**
```json
{
  "tradition": "hermetic",
  "all_universal_laws": {"$in": ["law_of_correspondence"]},
  "consciousness_level": {"$in": ["acceptance", "love"]}
}
```

**4. Don't Over-Filter**
```json
// Bad - Too restrictive, may return 0 results
{
  "tradition": "vedic",
  "teacher": "blavatsky",
  "primary_chakra": "heart",
  "healing_modality": "breathwork",
  "consciousness_level": "love"
}

// Better - Start broad, add filters if needed
{
  "tradition": "vedic",
  "all_chakras": {"$in": ["heart"]}
}
```

### Performance Tips

**1. Filter Before Semantic Search**
- Filters narrow the search space → faster queries
- Apply most restrictive filters first

**2. Use `top_k` Wisely**
- Default: 5 (good for most queries)
- High precision needed: 10-15
- Broad exploration: 20 (max recommended)

**3. Empty Filters**
If a field is empty (not detected), it won't match filters:
```json
// This will NOT match chunks where teacher wasn't detected
{
  "teacher": "blavatsky"
}

// Better - use all_teachers if you want comprehensive search
{
  "all_teachers": {"$in": ["blavatsky"]}
}
```

### Query Design Patterns

**Pattern 1: Discovery (Broad → Narrow)**
```python
# Step 1: Broad query
result = query(
    question="What is consciousness?",
    filters={}
)

# Step 2: Refine based on results
result = query(
    question="What is consciousness?",
    filters={
        "tradition": "vedic",  # Found in step 1 results
        "consciousness_level": {"$in": ["love", "peace"]}
    }
)
```

**Pattern 2: Precision (Start Specific)**
```python
# Use when you know exactly what you want
result = query(
    question="Explain photon consciousness",
    filters={
        "bridge_concept": "photon_consciousness",
        "all_quantum_particles": {"$in": ["photons"]}
    }
)
```

**Pattern 3: Comparative (Multiple Values)**
```python
# Compare different traditions
result = query(
    question="Compare Eastern and Western mysticism",
    filters={
        "all_traditions": {"$in": ["vedic", "buddhist", "hermetic", "kabbalah"]}
    },
    top_k=15
)
```

**Pattern 4: Progressive Levels**
```python
# For teaching/learning paths
beginner = query(
    question="Introduction to chakras",
    filters={"program_level": "beginner"},
    top_k=5
)

intermediate = query(
    question="How do chakras relate to quantum fields?",
    filters={"program_level": "intermediate"},
    top_k=5
)

advanced = query(
    question="Chakra-Sephiroth correspondence in advanced practice",
    filters={"program_level": "advanced"},
    top_k=5
)
```

### Common Mistakes

**1. Case Sensitivity**
```json
// Wrong - Values are lowercase
{"primary_chakra": "Heart"}

// Correct
{"primary_chakra": "heart"}
```

**2. Forgetting $in Operator for Lists**
```json
// Wrong - Won't work
{"all_chakras": "heart"}

// Correct
{"all_chakras": {"$in": ["heart"]}}
```

**3. Filtering on Empty Fields**
```json
// This might return 0 results if no healing modality was detected
{"healing_modality": "breathwork"}

// Better - combine with semantic search
// Let the question do the work, use filters as gentle guides
```

**4. Using `text` Field for Search**
```json
// Wrong - Don't filter on text content
{"text": {"$regex": "chakra"}}

// Correct - Use semantic search with tags
{"tags": {"$in": ["chakra"]}}
```

### Optimization Techniques

**1. Index Commonly-Filtered Fields**
Already indexed in Pinecone:
- `title`
- `primary_chakra`
- `tradition`
- `teacher`
- `program_level`

**2. Cache Common Queries**
If building a UI, cache results for:
- List of all teachers
- List of all traditions
- List of all chakras
- Available program levels

**3. Batch Similar Queries**
```python
# Bad - 3 separate API calls
heart = query(question="...", filters={"primary_chakra": "heart"})
crown = query(question="...", filters={"primary_chakra": "crown"})
root = query(question="...", filters={"primary_chakra": "root"})

# Better - 1 API call
all_chakras = query(
    question="...",
    filters={"all_chakras": {"$in": ["heart", "crown", "root"]}},
    top_k=15
)
# Then filter results client-side
```

---

## Field Relationships

### Hierarchies

**Chakra Hierarchy (Bottom → Top):**
1. Earth Star (grounding)
2. Root (survival)
3. Sacral (creativity)
4. Solar Plexus (power)
5. Heart (love)
6. Throat (expression)
7. Third Eye (intuition)
8. Crown (consciousness)
9. Soul Star (higher self)

**Consciousness Hierarchy (Hawkins Scale):**
- Below 200: Disempowering (shame → pride)
- 200+: Empowering (courage → enlightenment)
- 500+: Unconditional love territory
- 600+: Peace and transcendence

**Program Level Hierarchy:**
1. Beginner → Intermediate → Advanced
2. Maps to recovery stages: Early → Sustained → Spiritual Mastery

### Overlaps

**Fields that often appear together:**

**Photon Consciousness + Crown Chakra:**
```json
{
  "bridge_concept": "photon_consciousness",
  "all_chakras": {"$in": ["crown", "third_eye", "soul_star"]}
}
```

**12-Step + Spiritual Awakening:**
```json
{
  "all_12_steps": {"$in": ["step_11", "step_12"]},
  "ascension_path": "12_step_ascension",
  "consciousness_level": {"$in": ["acceptance", "love"]}
}
```

**Hermetic + Quantum:**
```json
{
  "tradition": "hermetic",
  "all_universal_laws": {"$in": ["law_of_correspondence", "law_of_vibration"]},
  "all_quantum_physics": {"$in": ["frequency", "quantum_field"]}
}
```

**Theosophy Teachers:**
```json
{
  "all_teachers": {"$in": ["blavatsky", "besant", "leadbeater", "bailey"]}
}
```

---

## Metadata Generation

### Keyword-Based Tagging (Free)

**How it works:**
1. Text converted to lowercase
2. Keyword patterns matched against comprehensive dictionaries
3. Multiple keywords → added to appropriate category
4. First match becomes "primary" field
5. All matches added to "all_*" list

**Pros:**
- Instant results
- No API costs
- Consistent categorization
- Good for bulk uploads

**Cons:**
- May miss nuanced concepts
- Relies on exact keyword matches
- No semantic understanding

### AI-Enhanced Tagging (Paid/Free)

**Ollama (Free, Local):**
- Requires: `brew install ollama && ollama serve`
- Model: llama3.1 (default) or others
- Speed: ~3-5 seconds per chunk
- Quality: Good semantic understanding

**OpenAI (Paid):**
- Cost: ~$0.40 per 1000 documents
- Speed: ~1-2 seconds per chunk
- Quality: Excellent semantic understanding

**How it works:**
1. Chunk sent to AI with category definitions
2. AI identifies relevant tags semantically
3. Results merged with keyword-based tags
4. Primary theme generated (AI-only feature)

**When to use AI tagging:**
- High-quality content library
- Nuanced/esoteric material
- Building a curated collection
- Budget allows for it

**When to use keyword tagging:**
- Bulk uploads
- Budget-conscious
- Well-structured content (clear keyword usage)
- Speed is priority

---

## Future Enhancements

### Planned Fields

**Coming Soon:**
- `language` - Detected language (English, Sanskrit, Hebrew, etc.)
- `original_author` - Original author if known
- `publication_date` - When content was created
- `quality_score` - Content quality rating (1-10)
- `user_ratings` - Aggregate user ratings
- `related_documents` - Cross-references to similar content

### Relationship Fields

**Planned:**
- `precursor_to` - Documents that should be read first
- `follows_from` - Documents that come before this
- `synthesizes` - Other documents this combines
- `contradicts` - Opposing viewpoints

---

## Support

**Documentation:**
- [API Reference](API_REFERENCE.md) - Complete endpoint documentation
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

**Field Questions:**
- Check this document first
- Test queries at: `POST /query` endpoint
- Use `GET /uploaded-documents` to see actual metadata

**Adding New Fields:**
- Edit `/backend/tagging.py`
- Add keyword dictionary or AI prompt
- Update upload logic in `/backend/main.py`
- Re-upload documents to populate new fields

---

**Last Updated:** November 30, 2025
**Schema Version:** 1.0.0
