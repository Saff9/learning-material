---
title: "UML Cheat Sheet"
tags:
  - oop
  - cheatsheet
  - uml
  - mermaid
  - reference-card
aliases:
  - UML Quick Reference
  - Mermaid Cheat Sheet
  - UML Card
created: 2025-01-20
---

# 📐 UML Cheat Sheet

> [!tip] How to use this card
> Keep this open when drawing diagrams. Every section has the Mermaid syntax for copy-paste. Click wikilinks for the full diagram deep-dive.

Deep dives: [[uml-overview]] · [[class-diagrams]] · [[object-diagrams]] · [[sequence-diagrams]] · [[state-and-activity-diagrams]] · [[use-case-and-package-diagrams]] · [[mermaid-cheatsheet]].

---

## 🧭 The 14 UML Diagram Types (and which matter)

| Category | Diagrams | Priority for OOP |
|---|---|:---:|
| **Structure** (7) | Class, Object, Component, Composite Structure, Deployment, Package, Profile | Class ★★★ · Object ★★ · Package ★ · Component ★ |
| **Behavior** (7) | Use Case, Activity, State, Sequence, Communication, Interaction Overview, Timing | Sequence ★★★ · State ★★ · Activity ★★ · Use Case ★ |

> [!success] If you only learn 6…
> Class · Object · Sequence · State · Activity · Use Case. These cover ~95% of OOP design needs.

```mermaid
mindmap
  root((UML))
    Structural
      Class
      Object
      Package
      Component
      Composite
      Deployment
      Profile
    Behavioral
      Sequence
      State
      Activity
      Use Case
      Communication
      Timing
      Interaction Overview
```

See [[uml-overview]].

---

## 🏛️ Class Diagram Anatomy

Three compartments, top to bottom:

```
┌─────────────────────┐
│      ClassName       │  ← Name (italic if abstract)
├─────────────────────┤
│ +publicAttr: Type    │  ← Attributes
│ -privateAttr: Type   │
│ #protectedAttr: Type │
│ ~packageAttr: Type   │
├─────────────────────┤
│ +method(): RetType   │  ← Operations
│ #protectedMethod()   │
│ -privateMethod()     │
│ {abstract} method()  │  ← italic or {abstract}
└─────────────────────┘
```

### Visibility markers

| Marker | Meaning | Python equivalent |
|:---:|---|---|
| `+` | Public | (no underscore) `name` |
| `-` | Private | `__name` (mangled) |
| `#` | Protected | `_name` (by convention) |
| `~` | Package | (no Python equivalent) |

### Other markers

| Marker | Meaning |
|---|---|
| *italic name* | Abstract class |
| `{abstract}` | Abstract method (alternative) |
| `<<interface>>` | Stereotype: interface |
| `<<protocol>>` | Stereotype: Protocol |
| `static` | Underlined attribute/method |
| `: Type` | Type annotation |
| `= value` | Default value |

### Minimal Mermaid class diagram

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +speak() String*
        #sleep()
    }
    class Dog {
        +speak() String
        -barkVolume: int
    }
    Animal <|-- Dog
```

> [!note] `*` after a method name = abstract method. `+`/`-`/`#` = visibility.

See [[class-diagrams]].

---

## 🔗 The 6 Relationships (with Mermaid)

| Relationship | UML Symbol | Mermaid syntax | Meaning | Real-world analogy |
|---|:---:|---|---|---|
| **Inheritance** | `──▷` | `Parent <\|-- Child` | "is-a" | Dog is an Animal |
| **Realization** | `┄┄▷` | `Protocol <\|.. Class` | "implements" | Circle implements Shape |
| **Composition** | `──◆` | `Car *-- Engine` | "owns" (lifecycle bound) | House owns Rooms |
| **Aggregation** | `──◇` | `Team o-- Player` | "has-a" (shared) | Team has Players (they exist on their own) |
| **Association** | `──` | `A --> B` | "uses" (long-term) | Teacher uses Classroom |
| **Dependency** | `┄┄>` | `A ..> B` | "temporarily uses" | Chef uses Recipe during cooking |

### Full Mermaid demonstration

```mermaid
classDiagram
    class Animal {
        +speak() String
    }
    class Mammal {
        +furColor: String
    }
    class Dog {
        +fetch()
    }
    class Tail {
        +wag()
    }
    class Owner {
        +name: String
    }
    class Food {
        +calories: int
    }
    Animal <|-- Mammal         %% inheritance (is-a)
    Mammal <|-- Dog            %% inheritance (is-a)
    Dog *-- Tail               %% composition (owns lifecycle)
    Dog o-- Owner              %% aggregation (shared)
    Dog --> Food : eats        %% association (uses)
    Dog ..> Food : feeds       %% dependency (temporarily)
```

### Composition vs Aggregation — the line that confuses everyone

| Question | Composition | Aggregation |
|---|---|---|
| If the container is destroyed, are the parts destroyed too? | Yes | No |
| Are the parts shared with other containers? | No | Yes |
| Created by the container? | Yes | No (passed in) |
| Python code | `self.engine = Engine()` | `self.driver = driver` (passed in `__init__`) |

See [[class-diagrams]].

---

## 🔢 Multiplicity Table

| Marker | Meaning | Example |
|:---:|---|---|
| `1` | Exactly one | `1` Person has `1` Heart |
| `0..1` | Zero or one (optional) | `0..1` Person has `0..1` Spouse |
| `0..*` or `*` | Zero or more | `0..*` Order has `0..*` Items |
| `1..*` | One or more (required, multiple) | `1..*` Department has `1..*` Employees |
| `n` | Exactly n | `4` Car has `4` Wheels |
| `n..m` | Between n and m | `2..5` Meeting has `2..5` Participants |

### Mermaid syntax for multiplicity

```mermaid
classDiagram
    Person "1" --> "0..1" Spouse : married_to
    Order "1" --> "1..*" Item : contains
    Team "1" o-- "5..11" Player : fields
    Library "1" *-- "0..*" Book : owns
```

See [[class-diagrams]].

---

## 🎬 Sequence Diagram Syntax Cheat-Sheet

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant C as Cart
    participant I as Inventory
    participant P as Payment

    U->>C: addItem(sku, qty)
    C->>I: checkStock(sku, qty)
    I-->>C: inStock: true
    C-->>U: ok

    U->>C: checkout()
    C->>P: charge(amount)
    alt success
        P-->>C: paid
        C-->>U: confirmed
    else declined
        P-->>C: declined
        C-->>U: error
    end

    loop retry 3x
        C->>P: charge(amount)
    end
```

### Sequence diagram elements

| Element | Mermaid syntax | Meaning |
|---|---|---|
| Participant | `participant A as Alias` | A lifeline |
| Sync message | `A->>B: msg` | Solid arrow with filled head |
| Async message | `A--)B: msg` | Solid arrow with open head |
| Return message | `B-->>A: result` | Dashed arrow |
| Self message | `A->>A: msg` | Loop on same lifeline |
| Note | `Note over A: text` or `Note right of A: text` | Sticky note |
| Activation | `activate A` / `deactivate A` | Vertical bar on lifeline |
| `alt`/`else`/`end` | conditional | Alternative branches |
| `opt`/`end` | optional | Optional fragment |
| `loop`/`end` | iteration | Loop fragment |
| `par`/`and`/`end` | parallel | Concurrent fragments |
| `autonumber` | auto numbering | Auto-number messages |

See [[sequence-diagrams]].

---

## 🚦 State Diagram Syntax Cheat-Sheet (stateDiagram-v2)

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> HasCoin: insertCoin
    HasCoin --> Dispensing: selectItem
    Dispensing --> Idle: dispenseItem
    HasCoin --> Idle: cancel
    Dispensing --> OutOfStock: empty
    OutOfStock --> [*]
    Idle --> [*]: powerOff

    note right of HasCoin
        user has inserted coin,
        can select item or cancel
    end note
```

### State diagram elements

| Element | Mermaid syntax | Meaning |
|---|---|---|
| Initial state | `[*]` | Black circle |
| Final state | `[*]` (different arrow target) | Bullseye |
| State | `StateName` | A vertex |
| Transition | `A --> B: event` | Edge with optional label |
| Guard | `A --> B: event [guard]` | Conditional transition |
| Action | `A --> B: event / action` | Triggered action |
| Composite state | `state X { ... }` | Nested states |
| Fork/Join | `state fork <<fork>>` | Parallel split/join |
| Note | `note left of A: text` | Annotation |

See [[state-and-activity-diagrams]].

---

## 🌊 Activity Diagram Syntax (via flowchart)

Mermaid doesn't have a true activity diagram. Use `flowchart`:

```mermaid
flowchart TD
    S([Start]) --> A[User submits form]
    A --> B{Valid?}
    B -- No --> C[Show errors]
    C --> A
    B -- Yes --> D[Save to DB]
    D --> E[Send email]
    D --> F[Send SMS]
    E --> G([End])
    F --> G
```

### Activity elements via flowchart

| Concept | Flowchart syntax |
|---|---|
| Start / End | `([Start])` (rounded) |
| Action | `[Do something]` |
| Decision | `{Condition?}` |
| Fork / Join | Use multiple edges in/out of a node, or `subgraph` |
| Swimlane | `subgraph LaneName ... end` |

See [[state-and-activity-diagrams]].

---

## 🧭 Mermaid Syntax Quick Reference

### `classDiagram`

```mermaid
classDiagram
    class ClassName {
        +publicAttr: Type
        -privateAttr: Type
        #protectedAttr: Type
        ~packageAttr: Type
        +method() ReturnType
        -privateMethod()
        {abstract} abstractMethod()
    }
    Parent <|-- Child          %% inheritance
    Interface <|.. Class       %% realization
    Container *-- Part         %% composition
    Container o-- Part         %% aggregation
    A --> B : label            %% association
    A ..> B : label            %% dependency
    class StereotypeClass {
        <<interface>>
    }
```

### `sequenceDiagram`

```mermaid
sequenceDiagram
    autonumber
    participant A
    participant B
    A->>B: sync
    B-->>A: reply
    A-)B: async
    Note over A,B: span
    loop 3 times
        A->>B: retry
    end
```

### `stateDiagram-v2`

```mermaid
stateDiagram-v2
    direction LR
    [*] --> A
    A --> B: trigger [guard] / action
    B --> [*]
    state C {
        [*] --> C1
        C1 --> C2
    }
```

### `flowchart`

```mermaid
flowchart TD
    A[Start] --> B{Choice?}
    B -- Yes --> C[Do thing]
    B -- No --> D[Do other]
    C --> E([End])
    D --> E
```

### `mindmap`

```mermaid
mindmap
    root((Topic))
        Branch A
            Leaf 1
            Leaf 2
        Branch B
            Leaf 3
```

### `erDiagram`

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    CUSTOMER {
        int id PK
        string name
    }
```

### `timeline`

```mermaid
timeline
    title OOP History
    1967 : Simula
    1970s : Smalltalk
    1985 : C++
    1995 : Java
    2000s : Python OOP matures
```

### `gitGraph`

```mermaid
gitGraph
    commit
    commit
    branch feature
    checkout feature
    commit
    checkout main
    merge feature
```

See [[mermaid-cheatsheet]] for the full reference.

---

## 🎯 "I Want to Show X, Use Y" Lookup

| You want to show… | Use this diagram |
|---|---|
| The structure of a system at rest (classes + relationships) | **Class diagram** — [[class-diagrams]] |
| A snapshot of instances and links at one moment | **Object diagram** — [[object-diagrams]] |
| The order of messages between objects over time | **Sequence diagram** — [[sequence-diagrams]] |
| The lifecycle of one object (state transitions) | **State diagram** — [[state-and-activity-diagrams]] |
| A workflow or algorithm flow | **Activity diagram** — [[state-and-activity-diagrams]] |
| What the system does, from outside (actors + goals) | **Use case diagram** — [[use-case-and-package-diagrams]] |
| How packages/modules depend on each other | **Package diagram** — [[use-case-and-package-diagrams]] |
| Deployment of components to hardware | **Deployment diagram** — (rare in OOP) |
| A brainstorm / taxonomy of concepts | **Mindmap** — [[mermaid-cheatsheet]] |
| A decision procedure | **Flowchart** — [[mermaid-cheatsheet]] |
| A historical sequence of events | **Timeline** — [[mermaid-cheatsheet]] |
| Database schema | **ER diagram** — [[mermaid-cheatsheet]] |
| Branching/merging history | **Git graph** — [[mermaid-cheatsheet]] |

---

## 🧪 Common Mermaid Pitfalls (Quick Fix)

| Symptom | Fix |
|---|---|
| Diagram won't render | Check for unescaped special chars (`<`, `>`, `&`) — use `&lt;`, `&gt;`, `&amp;` |
| `classDiagram` confusion between `<\|--` and `<\|..` | `<\|--` = solid (inheritance); `<\|..` = dashed (realization) |
| Labels with spaces break arrows | Wrap label in quotes: `A --> B: "has many"` |
| State diagram notes don't render | Use `note right of StateName` exactly; Mermaid is finicky |
| `mindmap` branches look weird | Indentation must be **consistent** (tabs or spaces, not mixed) |
| `flowchart TD` edges overlap | Add direction `TD`/`LR`; use `subgraph` to cluster |
| Sequence diagram async arrows | `--)` not `-)-` — Mermaid's parser is strict |
| `classDiagram` doesn't show visibility `~` | Mermaid supports `+`, `-`, `#` only; `~` (package) not rendered |
| Diagram is too wide for screen | Use `direction LR` or split into multiple smaller diagrams |
| `%% comment` breaks inside `{}` block | Use `%%` only on its own line |

See [[mermaid-cheatsheet]].

---

## 🎨 Visual Conventions Summary

### Arrow style

| Style | Meaning |
|:---:|---|
| `──` solid | Permanent relationship (inheritance, association, composition) |
| `┄┄` dashed | Temporary / realization / dependency / return |

### Arrow head

| Head | Meaning |
|:---:|---|
| `▷` open triangle | "is-a" / "implements" |
| `◆` filled diamond | Composition |
| `◇` open diamond | Aggregation |
| `>` open arrow | Navigability / direction |
| `▷▷` or `▷` (filled) | Stronger relationship |

### Line labels

- Place **above** the line.
- Format: `event [guard] / action` for state transitions.
- Format: `multiplicity : role` for associations.

---

## 📦 A Compact Library System (All-in-One Example)

```mermaid
classDiagram
    class Library {
        +name: String
        +books: List~Book~
        +addBook(b: Book)
        +findBook(isbn: String) Book
    }
    class Book {
        +isbn: String
        +title: String
        +available: bool
        +checkout() void
        +return() void
    }
    class Member {
        +id: String
        +name: String
        +borrow(b: Book)
    }
    class Loan {
        +due: Date
        +returned: Date
    }
    class Catalog {
        +search(q: String) List~Book~
    }
    Library *-- Book : owns
    Library o-- Member : registers
    Member --> Loan : has
    Book --> Loan : part of
    Library --> Catalog : uses
    Loan ..> Book : references
```

> [!example] Try redrawing this from memory
> After 10 minutes with [[class-diagrams]], sketch this diagram on paper. Compare. The gaps are what you didn't actually learn yet.

---

## 🔑 Key Takeaways

- **6 of the 14 UML diagram types** cover ~95% of OOP needs: Class, Object, Sequence, State, Activity, Use Case.
- **Class diagrams** have 3 compartments (name, attributes, operations) and 4 visibility markers (`+`, `-`, `#`, `~`).
- **The 6 relationships** are: inheritance `──▷`, realization `┄┄▷`, composition `──◆`, aggregation `──◇`, association `──`, dependency `┄┄>`.
- **Composition ≠ Aggregation**: lifecycle-bound vs shared. When in doubt, ask "if the container dies, do the parts die too?"
- **Multiplicity**: `1`, `0..1`, `*`, `1..*`, `n`, `n..m`.
- **Sequence diagrams** show messages over time; use `alt`/`opt`/`loop`/`par` for control flow.
- **State diagrams** (`stateDiagram-v2`) show object lifecycles with `[*]` for start/end.
- Mermaid supports `classDiagram`, `sequenceDiagram`, `stateDiagram-v2`, `flowchart`, `mindmap`, `erDiagram`, `timeline`, `gitGraph` — all render natively in Obsidian.
- Use the **"I want to show X, use Y"** table to pick the right diagram type.
- Mermaid is finicky — common fixes are escaping `<`/`>`/`&`, wrapping labels in quotes, and consistent indentation in mindmaps.
- Every diagram type in this card has a full deep-dive note behind it.

---

*See also: [[oop-quick-reference]] · [[mermaid-cheatsheet]] · [[class-diagrams]] · [[sequence-diagrams]] · [[state-and-activity-diagrams]] · [[object-diagrams]] · [[use-case-and-package-diagrams]] · [[uml-overview]]*
