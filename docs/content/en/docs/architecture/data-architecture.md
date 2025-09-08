# Data Architecture

This document details the data architecture, flow, storage systems, and management strategies used in Project AIRI.

## Data Architecture Overview

Project AIRI employs a sophisticated data architecture designed to handle real-time interactions, persistent memory, and complex AI processing workflows.

```mermaid
%%{ init: { 'flowchart': { 'curve': 'catmullRom' } } }%%

graph TB
    subgraph DataSources["Data Sources"]
        UserInput["User Input<br/>(Text, Voice, Actions)"]
        ExternalAPIs["External APIs<br/>(LLMs, TTS, Games)"]
        SystemEvents["System Events<br/>(Logs, Metrics, Errors)"]
        MediaContent["Media Content<br/>(Audio, Video, Images)"]
    end
    
    subgraph ProcessingLayer["Data Processing Layer"]
        InputProcessor["Input Processor"]
        AudioProcessor["Audio Processor"]
        AIProcessor["AI/LLM Processor"]
        EventProcessor["Event Processor"]
    end
    
    subgraph StorageLayer["Storage Layer"]
        MemoryDB["Memory Database<br/>(DuckDB WASM)"]
        VectorStore["Vector Store<br/>(Embeddings)"]
        LocalStorage["Browser/Local Storage"]
        FileSystem["File System<br/>(Desktop only)"]
    end
    
    subgraph DataConsumers["Data Consumers"]
        UIComponents["UI Components"]
        AIModels["AI Models"]
        ExternalServices["External Services"]
        Analytics["Analytics Systems"]
    end
    
    UserInput --> InputProcessor
    ExternalAPIs --> AIProcessor
    SystemEvents --> EventProcessor
    MediaContent --> AudioProcessor
    
    InputProcessor --> MemoryDB
    AudioProcessor --> VectorStore
    AIProcessor --> MemoryDB
    EventProcessor --> LocalStorage
    
    MemoryDB --> UIComponents
    VectorStore --> AIModels
    LocalStorage --> ExternalServices
    FileSystem --> Analytics
    
    style DataSources fill:#e8f5e8
    style ProcessingLayer fill:#fff3e0
    style StorageLayer fill:#e3f2fd
    style DataConsumers fill:#f3e5f5
```

## Data Models

### Core Data Entities

```mermaid
erDiagram
    Character {
        string id PK
        string name
        string personality
        jsonb traits
        timestamp created_at
        timestamp updated_at
    }
    
    Conversation {
        string id PK
        string character_id FK
        string context
        jsonb metadata
        timestamp started_at
        timestamp ended_at
    }
    
    Message {
        string id PK
        string conversation_id FK
        string content
        string type
        string sender
        jsonb embeddings
        timestamp created_at
    }
    
    Memory {
        string id PK
        string character_id FK
        string content
        string type
        float importance
        vector embeddings
        timestamp created_at
        timestamp accessed_at
    }
    
    GameSession {
        string id PK
        string character_id FK
        string game_type
        jsonb game_state
        jsonb actions
        timestamp started_at
        timestamp ended_at
    }
    
    AudioSegment {
        string id PK
        string conversation_id FK
        blob audio_data
        string transcription
        jsonb features
        timestamp created_at
    }
    
    Character ||--o{ Conversation : has
    Conversation ||--o{ Message : contains
    Character ||--o{ Memory : stores
    Character ||--o{ GameSession : plays
    Conversation ||--o{ AudioSegment : includes
```

### Memory System Data Model

```mermaid
graph TD
    subgraph MemoryTypes["Memory Types"]
        ShortTerm["Short-term Memory<br/>(Working Context)"]
        Episodic["Episodic Memory<br/>(Life Events)"]
        Semantic["Semantic Memory<br/>(Knowledge)"]
        Procedural["Procedural Memory<br/>(Skills)"]
    end
    
    subgraph StorageStrategy["Storage Strategy"]
        InMemory["In-Memory Cache"]
        DuckDB["DuckDB Tables"]
        VectorDB["Vector Database"]
        LongTermStorage["Long-term Storage"]
    end
    
    ShortTerm --> InMemory
    Episodic --> DuckDB
    Semantic --> VectorDB
    Procedural --> LongTermStorage
    
    style MemoryTypes fill:#e1f5fe
    style StorageStrategy fill:#f3e5f5
```

## Data Flow Architecture

### Real-time Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Core
    participant Memory
    participant AI
    participant Storage
    
    User->>Frontend: Input (text/voice)
    Frontend->>Core: Process Input
    
    Note over Core: Input Validation & Sanitization
    
    Core->>Memory: Retrieve Context
    Memory->>Storage: Query Recent Interactions
    Storage-->>Memory: Return Context Data
    Memory-->>Core: Contextualized Data
    
    Core->>AI: Generate Response
    AI-->>Core: Response + Metadata
    
    Core->>Memory: Store Interaction
    Memory->>Storage: Persist Data
    
    Core->>Frontend: Send Response
    Frontend-->>User: Display/Play Response
    
    Note over Storage: Background: Update Embeddings, Consolidate Memory
```

### Audio Data Processing Flow

```mermaid
graph LR
    subgraph AudioFlow["Audio Data Flow"]
        Capture["Audio Capture"]
        VAD["Voice Activity Detection"]
        STT["Speech-to-Text"]
        Embedding["Audio Embeddings"]
        Storage["Audio Storage"]
        TTS["Text-to-Speech"]
        Playback["Audio Playback"]
    end
    
    Capture --> VAD
    VAD --> STT
    STT --> Embedding
    Embedding --> Storage
    Storage --> TTS
    TTS --> Playback
    
    style AudioFlow fill:#ffecb3
```

### Game Data Integration Flow

```mermaid
graph TB
    subgraph GameData["Game Data Integration"]
        GameAPI["Game API"]
        StateTracker["State Tracker"]
        ActionPlanner["Action Planner"]
        DecisionEngine["Decision Engine"]
        GameMemory["Game Memory"]
    end
    
    GameAPI --> StateTracker
    StateTracker --> ActionPlanner
    ActionPlanner --> DecisionEngine
    DecisionEngine --> GameMemory
    GameMemory --> ActionPlanner
    
    style GameData fill:#c8e6c9
```

## Storage Systems

### DuckDB WASM Database

**Primary Use Cases**:
- Structured data storage
- Complex analytical queries
- Time-series data analysis
- Conversation history

**Schema Design**:
```sql
-- Conversations table
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,
    character_id VARCHAR NOT NULL,
    context TEXT,
    metadata JSON,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Messages table  
CREATE TABLE messages (
    id VARCHAR PRIMARY KEY,
    conversation_id VARCHAR REFERENCES conversations(id),
    content TEXT NOT NULL,
    message_type VARCHAR NOT NULL,
    sender VARCHAR NOT NULL,
    embeddings FLOAT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Memory table
CREATE TABLE memories (
    id VARCHAR PRIMARY KEY,
    character_id VARCHAR NOT NULL,
    content TEXT NOT NULL,
    memory_type VARCHAR NOT NULL,
    importance FLOAT DEFAULT 0.5,
    embeddings FLOAT[],
    created_at TIMESTAMP DEFAULT NOW(),
    accessed_at TIMESTAMP DEFAULT NOW()
);
```

### Vector Storage System

**Implementation**: Custom vector store with similarity search capabilities

```mermaid
graph LR
    subgraph VectorSystem["Vector Storage System"]
        Embedder["Text Embedder"]
        VectorIndex["Vector Index"]
        SimilaritySearch["Similarity Search"]
        MemoryRetrieval["Memory Retrieval"]
    end
    
    Embedder --> VectorIndex
    VectorIndex --> SimilaritySearch
    SimilaritySearch --> MemoryRetrieval
    
    style VectorSystem fill:#e1bee7
```

**Key Features**:
- Semantic similarity search
- Efficient vector indexing
- Real-time embedding generation
- Memory consolidation algorithms

### Local Storage Strategy

```mermaid
graph TD
    subgraph LocalStorage["Local Storage Strategy"]
        BrowserStorage["Browser Storage"]
        FileSystemStorage["File System Storage"]
        MemoryCache["In-Memory Cache"]
        TemporaryStorage["Temporary Storage"]
    end
    
    subgraph DataTypes["Data Types by Storage"]
        Settings["User Settings"]
        Cache["Cache Data"]
        Files["Media Files"]
        Temp["Processing Data"]
    end
    
    Settings --> BrowserStorage
    Cache --> MemoryCache
    Files --> FileSystemStorage
    Temp --> TemporaryStorage
    
    style LocalStorage fill:#fff9c4
    style DataTypes fill:#f8bbd9
```

## Data Processing Pipelines

### Input Processing Pipeline

```mermaid
graph LR
    subgraph InputPipeline["Input Processing Pipeline"]
        Raw["Raw Input"]
        Validate["Validation"]
        Normalize["Normalization"]
        Enrich["Enrichment"]
        Store["Storage"]
    end
    
    Raw --> Validate
    Validate --> Normalize
    Normalize --> Enrich
    Enrich --> Store
    
    style InputPipeline fill:#ffcdd2
```

**Processing Steps**:
1. **Validation**: Input sanitization and format validation
2. **Normalization**: Text normalization, encoding standardization
3. **Enrichment**: Context addition, metadata extraction
4. **Storage**: Persistent storage with indexing

### Memory Consolidation Pipeline

```mermaid
graph TB
    subgraph Consolidation["Memory Consolidation Pipeline"]
        Recent["Recent Memories"]
        Importance["Importance Scoring"]
        Clustering["Semantic Clustering"]
        Compression["Memory Compression"]
        LongTerm["Long-term Storage"]
    end
    
    Recent --> Importance
    Importance --> Clustering
    Clustering --> Compression
    Compression --> LongTerm
    
    style Consolidation fill:#e8f5e8
```

**Consolidation Process**:
- **Importance Scoring**: Relevance and emotional weight calculation
- **Semantic Clustering**: Grouping related memories
- **Compression**: Redundant information removal
- **Long-term Storage**: Persistent memory formation

## Data Privacy and Security

### Privacy-First Design

```mermaid
graph LR
    subgraph Privacy["Privacy Measures"]
        LocalProcessing["Local Processing"]
        Encryption["Data Encryption"]
        Anonymization["Data Anonymization"]
        Retention["Retention Policies"]
    end
    
    subgraph Security["Security Measures"]
        AccessControl["Access Control"]
        InputSanitization["Input Sanitization"]
        SecureTransport["Secure Transport"]
        AuditLogging["Audit Logging"]
    end
    
    LocalProcessing --> AccessControl
    Encryption --> SecureTransport
    Anonymization --> AuditLogging
    Retention --> InputSanitization
    
    style Privacy fill:#e8f5e8
    style Security fill:#ffebee
```

### Data Encryption Strategy

**Encryption at Rest**:
- Local database encryption
- Sensitive data field-level encryption
- Key derivation from user credentials

**Encryption in Transit**:
- HTTPS/WSS for all communications
- End-to-end encryption for sensitive data
- Certificate pinning for API connections

## Performance Optimization

### Data Access Patterns

```mermaid
graph TD
    subgraph AccessPatterns["Data Access Optimization"]
        Caching["Multi-level Caching"]
        Indexing["Smart Indexing"]
        Batching["Batch Operations"]
        Streaming["Data Streaming"]
    end
    
    subgraph Performance["Performance Strategies"]
        LazyLoading["Lazy Loading"]
        Pagination["Pagination"]
        Compression["Data Compression"]
        Partitioning["Data Partitioning"]
    end
    
    Caching --> LazyLoading
    Indexing --> Pagination
    Batching --> Compression
    Streaming --> Partitioning
    
    style AccessPatterns fill:#e3f2fd
    style Performance fill:#f3e5f5
```

### Memory Management

**Memory Usage Optimization**:
- Automatic garbage collection
- Memory-mapped file access
- Efficient data structures
- Resource pooling

**Performance Metrics**:
- Query execution time
- Memory usage patterns
- Cache hit rates
- Storage I/O operations

## Data Migration and Versioning

### Schema Evolution

```mermaid
graph LR
    subgraph SchemaEvolution["Schema Evolution Strategy"]
        V1["Schema v1.0"]
        Migration["Migration Scripts"]
        V2["Schema v2.0"]
        Validation["Data Validation"]
    end
    
    V1 --> Migration
    Migration --> V2
    V2 --> Validation
    
    style SchemaEvolution fill:#fff3e0
```

**Migration Strategy**:
- Forward-compatible schema changes
- Automated migration scripts
- Data integrity validation
- Rollback capabilities

## Analytics and Monitoring

### Data Analytics Pipeline

```mermaid
graph TB
    subgraph Analytics["Analytics Pipeline"]
        Collection["Data Collection"]
        Aggregation["Data Aggregation"]
        Analysis["Real-time Analysis"]
        Visualization["Data Visualization"]
        Alerts["Automated Alerts"]
    end
    
    Collection --> Aggregation
    Aggregation --> Analysis
    Analysis --> Visualization
    Analysis --> Alerts
    
    style Analytics fill:#c8e6c9
```

**Monitoring Metrics**:
- System performance metrics
- User interaction patterns
- Memory usage analytics
- Error tracking and analysis

This data architecture ensures efficient, secure, and scalable data management while maintaining privacy and providing real-time performance for AIRI's complex AI interactions.