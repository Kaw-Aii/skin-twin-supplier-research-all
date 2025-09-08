# Component Architecture

This document provides detailed information about each major component in Project AIRI's architecture.

## Component Overview

Project AIRI consists of multiple interconnected components organized in different layers. Each component has specific responsibilities and well-defined interfaces.

```mermaid
%%{ init: { 'flowchart': { 'curve': 'catmullRom' } } }%%

graph TD
    subgraph Apps["Applications"]
        StageWeb["@proj-airi/stage-web"]
        StageTamagotchi["@proj-airi/stage-tamagotchi"]
        Playground["@proj-airi/playground-prompt-engineering"]
        RealtimeAudio["@proj-airi/realtime-audio"]
    end
    
    subgraph Packages["Core Packages"]
        StageUI["@proj-airi/stage-ui"]
        UI["@proj-airi/ui"]
        Audio["@proj-airi/audio"]
        ServerRuntime["@proj-airi/server-runtime"]
        ServerSDK["@proj-airi/server-sdk"]
        Memory["@proj-airi/memory-pgvector"]
        DuckDBWasm["@proj-airi/duckdb-wasm"]
        DrizzleDuckDB["@proj-airi/drizzle-duckdb-wasm"]
    end
    
    subgraph Services["External Services"]
        DiscordBot["services/discord-bot"]
        MinecraftBot["services/minecraft"]
        TelegramBot["services/telegram-bot"]
        TwitterServices["services/twitter-services"]
    end
    
    subgraph Crates["Rust Crates"]
        TauriMCP["tauri-plugin-mcp"]
        TauriRdev["tauri-plugin-rdev"]
        TauriAudio["tauri-plugin-ipc-audio-*"]
        TauriWindow["tauri-plugin-window-*"]
    end
    
    StageWeb --> StageUI
    StageTamagotchi --> StageUI
    StageUI --> UI
    
    StageWeb --> Audio
    StageTamagotchi --> Audio
    RealtimeAudio --> Audio
    
    StageWeb --> ServerRuntime
    StageTamagotchi --> ServerRuntime
    ServerRuntime --> ServerSDK
    
    ServerRuntime --> Memory
    Memory --> DuckDBWasm
    DuckDBWasm --> DrizzleDuckDB
    
    StageTamagotchi --> TauriMCP
    StageTamagotchi --> TauriRdev
    StageTamagotchi --> TauriAudio
    StageTamagotchi --> TauriWindow
    
    ServerRuntime --> DiscordBot
    ServerRuntime --> MinecraftBot
    ServerRuntime --> TelegramBot
    ServerRuntime --> TwitterServices
    
    style Apps fill:#e3f2fd
    style Packages fill:#f3e5f5
    style Services fill:#fff3e0
    style Crates fill:#e8f5e8
```

## Application Components

### Stage Web (`@proj-airi/stage-web`)
Browser-based frontend application providing the main AIRI interface.

**Technologies**: Vue 3, TypeScript, Vite, UnoCSS
**Key Features**:
- Real-time character interaction
- WebGPU-accelerated rendering
- Progressive Web App support
- Cross-browser compatibility

```mermaid
graph LR
    subgraph StageWeb["Stage Web Architecture"]
        Router["Vue Router"]
        Store["Pinia Store"]
        Components["Vue Components"]
        WebGL["WebGL/WebGPU"]
        WebAudio["Web Audio API"]
        Workers["Web Workers"]
    end
    
    Router --> Components
    Store --> Components
    Components --> WebGL
    Components --> WebAudio
    Components --> Workers
    
    style StageWeb fill:#e1f5fe
```

### Stage Tamagotchi (`@proj-airi/stage-tamagotchi`)
Desktop application built with Tauri, providing native OS integration.

**Technologies**: Tauri, Rust, Vue 3, Native APIs
**Key Features**:
- Native desktop integration
- Hardware acceleration
- Local file system access
- System-level audio/video processing

```mermaid
graph TB
    subgraph Tamagotchi["Stage Tamagotchi Architecture"]
        TauriCore["Tauri Core"]
        RustBackend["Rust Backend"]
        VueFramework["Vue Frontend"]
        NativeAPIs["Native APIs"]
        Plugins["Custom Plugins"]
    end
    
    TauriCore --> RustBackend
    TauriCore --> VueFramework
    RustBackend --> NativeAPIs
    RustBackend --> Plugins
    
    style Tamagotchi fill:#f3e5f5
```

## Core Package Components

### Stage UI (`@proj-airi/stage-ui`)
Comprehensive UI component library specifically designed for AIRI's interface.

**Key Components**:
- Character display and animation
- Chat interfaces
- Settings panels
- Loading screens
- Transition effects

```mermaid
graph TD
    subgraph StageUIComponents["Stage UI Components"]
        CharacterRenderer["Character Renderer"]
        ChatInterface["Chat Interface"]
        SettingsPanel["Settings Panel"]
        LoadingScreens["Loading Screens"]
        Transitions["UI Transitions"]
        ThemeSystem["Theme System"]
    end
    
    CharacterRenderer --> ThemeSystem
    ChatInterface --> ThemeSystem
    SettingsPanel --> ThemeSystem
    LoadingScreens --> ThemeSystem
    Transitions --> ThemeSystem
    
    style StageUIComponents fill:#f8bbd9
```

### Audio System (`@proj-airi/audio`)
Comprehensive audio processing pipeline for real-time voice interaction.

**Key Features**:
- Voice Activity Detection (VAD)
- Speech Recognition (STT)
- Text-to-Speech (TTS)
- Audio streaming and effects
- Real-time processing

```mermaid
graph LR
    subgraph AudioPipeline["Audio Processing Pipeline"]
        Input["Audio Input"]
        VAD["Voice Activity Detection"]
        STT["Speech to Text"]
        Processing["Audio Processing"]
        TTS["Text to Speech"]
        Output["Audio Output"]
    end
    
    Input --> VAD
    VAD --> STT
    STT --> Processing
    Processing --> TTS
    TTS --> Output
    
    style AudioPipeline fill:#ffecb3
```

### Server Runtime (`@proj-airi/server-runtime`)
Core server-side runtime managing AIRI's behavior and state.

**Responsibilities**:
- Character state management
- Service coordination
- Real-time decision making
- Memory management
- External service integration

```mermaid
graph TB
    subgraph ServerRuntime["Server Runtime Components"]
        StateManager["State Manager"]
        ServiceCoordinator["Service Coordinator"]
        DecisionEngine["Decision Engine"]
        MemoryManager["Memory Manager"]
        ServiceIntegrations["Service Integrations"]
    end
    
    StateManager --> DecisionEngine
    ServiceCoordinator --> StateManager
    DecisionEngine --> MemoryManager
    DecisionEngine --> ServiceIntegrations
    ServiceCoordinator --> ServiceIntegrations
    
    style ServerRuntime fill:#c8e6c9
```

### Memory System (`@proj-airi/memory-pgvector`)
Advanced memory management system for persistent character memory.

**Features**:
- Vector-based semantic search
- Episodic memory storage
- Context-aware retrieval
- Memory consolidation
- Privacy-preserving storage

```mermaid
graph TD
    subgraph MemorySystem["Memory System Architecture"]
        EpisodicMemory["Episodic Memory"]
        SemanticMemory["Semantic Memory"]
        VectorStore["Vector Store"]
        MemoryRetrieval["Memory Retrieval"]
        ContextManager["Context Manager"]
    end
    
    EpisodicMemory --> VectorStore
    SemanticMemory --> VectorStore
    VectorStore --> MemoryRetrieval
    MemoryRetrieval --> ContextManager
    
    style MemorySystem fill:#e1bee7
```

### Database Layer (`@proj-airi/duckdb-wasm` & `@proj-airi/drizzle-duckdb-wasm`)
High-performance embedded database system running in WebAssembly.

**Key Features**:
- In-browser SQL analytics
- Type-safe database operations
- High-performance queries
- Zero-config embedded database
- Cross-platform compatibility

```mermaid
graph LR
    subgraph DatabaseLayer["Database Layer"]
        DrizzleORM["Drizzle ORM"]
        DuckDBWasm["DuckDB WASM"]
        QueryEngine["Query Engine"]
        DataTypes["Type System"]
    end
    
    DrizzleORM --> DuckDBWasm
    DuckDBWasm --> QueryEngine
    DrizzleORM --> DataTypes
    
    style DatabaseLayer fill:#fff9c4
```

## Service Components

### Discord Bot Service
Comprehensive Discord integration providing voice and text interaction.

**Key Features**:
- Voice channel participation
- Slash command support
- Message handling
- Audio streaming
- User interaction tracking

```mermaid
graph TB
    subgraph DiscordBot["Discord Bot Components"]
        CommandHandler["Command Handler"]
        VoiceManager["Voice Manager"]
        MessageProcessor["Message Processor"]
        AudioStreaming["Audio Streaming"]
        UserTracker["User Tracker"]
    end
    
    CommandHandler --> MessageProcessor
    VoiceManager --> AudioStreaming
    MessageProcessor --> UserTracker
    AudioStreaming --> UserTracker
    
    style DiscordBot fill:#7289da,color:#fff
```

### Minecraft Service
Intelligent Minecraft gameplay automation and interaction.

**Technologies**: Mineflayer, JavaScript, Minecraft Protocol
**Key Features**:
- Autonomous gameplay
- Chat interaction
- World exploration
- Task execution
- Player collaboration

```mermaid
graph LR
    subgraph MinecraftBot["Minecraft Bot Components"]
        Mineflayer["Mineflayer Client"]
        ActionPlanner["Action Planner"]
        ChatHandler["Chat Handler"]
        WorldAnalyzer["World Analyzer"]
        TaskExecutor["Task Executor"]
    end
    
    Mineflayer --> ActionPlanner
    Mineflayer --> ChatHandler
    Mineflayer --> WorldAnalyzer
    ActionPlanner --> TaskExecutor
    WorldAnalyzer --> ActionPlanner
    
    style MinecraftBot fill:#8bc34a
```

### Factorio Service
Advanced Factorio automation and base management.

**Technologies**: Factorio RCON, TypeScript, Autorio library
**Key Features**:
- Factory automation
- Resource management
- Base planning
- Production optimization
- Real-time monitoring

```mermaid
graph TD
    subgraph FactorioBot["Factorio Bot Components"]
        RCONClient["RCON Client"]
        AutorioLib["Autorio Library"]
        BaseManager["Base Manager"]
        ProductionPlanner["Production Planner"]
        ResourceTracker["Resource Tracker"]
    end
    
    RCONClient --> AutorioLib
    AutorioLib --> BaseManager
    BaseManager --> ProductionPlanner
    ProductionPlanner --> ResourceTracker
    
    style FactorioBot fill:#ff9800
```

## Tauri Plugin Components

### MCP Plugin (`tauri-plugin-mcp`)
Model Context Protocol integration for AI model management.

**Features**:
- Model lifecycle management
- Context sharing
- Plugin communication
- Resource management

### Audio Plugins (`tauri-plugin-ipc-audio-*`)
Native audio processing plugins for desktop application.

**Components**:
- `tauri-plugin-ipc-audio-transcription-ort`: Speech recognition
- `tauri-plugin-ipc-audio-vad-ort`: Voice activity detection

### Window Management Plugins
Advanced window behavior and interaction plugins.

**Components**:
- `tauri-plugin-window-pass-through-on-hover`: Transparent window interaction
- `tauri-plugin-window-router-link`: Router integration
- `tauri-plugin-rdev`: Input device monitoring

## Component Communication

### Inter-Component Communication Patterns

```mermaid
graph TB
    subgraph CommunicationPatterns["Communication Patterns"]
        EventBus["Event Bus"]
        MessageQueue["Message Queue"]
        DirectCall["Direct Function Calls"]
        WebSockets["WebSocket Connections"]
        IPC["Inter-Process Communication"]
    end
    
    EventBus --> |"Vue Components"| DirectCall
    MessageQueue --> |"Services"| WebSockets
    IPC --> |"Tauri Plugins"| DirectCall
    
    style CommunicationPatterns fill:#ffcdd2
```

### Data Flow Between Components

```mermaid
sequenceDiagram
    participant UI as Frontend UI
    participant Core as Core Engine
    participant Memory as Memory System
    participant Service as External Service
    participant DB as Database
    
    UI->>Core: User Input
    Core->>Memory: Retrieve Context
    Memory->>DB: Query Data
    DB-->>Memory: Return Data
    Memory-->>Core: Context Data
    Core->>Service: Execute Action
    Service-->>Core: Action Result
    Core->>Memory: Store Result
    Memory->>DB: Save Data
    Core-->>UI: Response + State Update
```

## Component Dependencies

### Dependency Graph

```mermaid
graph TD
    Apps --> Packages
    Packages --> Services
    Apps --> Crates
    Services --> External["External APIs"]
    Crates --> System["System APIs"]
    
    subgraph Legend
        A["High Level"]
        B["Medium Level"]
        C["Low Level"]
        D["External"]
    end
    
    style Apps fill:#e3f2fd
    style Packages fill:#f3e5f5
    style Services fill:#fff3e0
    style Crates fill:#e8f5e8
    style External fill:#ffebee
    style System fill:#f1f8e9
```

This component architecture ensures modularity, testability, and maintainability while providing the flexibility needed for AIRI's complex requirements.