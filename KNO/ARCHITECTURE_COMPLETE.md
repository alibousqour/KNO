# KNO v5.0 - COMPLETE ARCHITECTURE DIAGRAM
## النظام المعماري الشامل - Complete System Architecture

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                     KNO v5.0 SYSTEM ARCHITECTURE                         ║
║                    نظام KNO v5.0 المعماري الكامل                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│                     🎨 PRESENTATION LAYER (GUI)                        │
│         ┌────────────────────────────────────────────────────┐         │
│         │  KNOAgent Window (900x700)                         │         │
│         │  ┌──────────────────────────────────────────────┐ │         │
│         │  │  Menu Bar                                    │ │         │
│         │  ├──────────────────────────────────────────────┤ │         │
│         │  │  NeonLabel("Welcome")  (Cyan Neon)          │ │         │
│         │  │  ┌─────────────────────────────────────────┐│ │         │
│         │  │  │  GradientFrame (Neon Gradient)          ││ │         │
│         │  │  │  ┌─── Listen Button ────┐               ││ │         │
│         │  │  │  │ (Magenta Theme)      │               ││ │         │
│         │  │  └─────────────────────────────────────────┘│ │         │
│         │  │                                              │ │         │
│         │  │  Text Output Area (Scrollable)              │ │         │
│         │  │  ────────────────────────────────────────── │ │         │
│         │  │  Response text here...                       │ │         │
│         │  │                                              │ │         │
│         │  │  Status Bar: Ready | Cache: 72% | Mem: 85MB│ │         │
│         │  └──────────────────────────────────────────────┘ │         │
│         └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │
                          (Update Display)
                                 │
┌─────────────────────────────────────────────────────────────────────────┐
│                    🎛️  CONTROLLER LAYER                                │
│         ┌──────────────────────────────────────────────────┐           │
│         │           KNOAgent (Main Controller)            │           │
│         ├──────────────────────────────────────────────────┤           │
│         │  ├─ _on_listen()      (Event Handler)           │           │
│         │  ├─ _on_think()       (LLM Processing)          │           │
│         │  ├─ _on_save_config() (Configuration)           │           │
│         │  ├─ _update_status()  (UI Updates)              │           │
│         │  └─ error_handler()   (Error Management)        │           │
│         └──────────────────────────────────────────────────┘           │
│                 ▲ Controls                    ▼ Uses                    │
│                 │                             │                        │
│     ┌───────────┴─────────────┬───────────────┴──────────────┐         │
│     │                         │                              │         │
└─────────────────────────────────────────────────────────────────────────┘
      │                       │                              │
      ▼                       ▼                              ▼
┌──────────────┐      ┌──────────────┐           ┌──────────────────┐
│   MODEL      │      │  UTILITIES   │           │  CONFIGURATION   │
│   LAYER      │      │   MODULES    │           │     LAYER        │
└──────────────┘      └──────────────┘           └──────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                    📊 MODEL/DATA LAYER                                  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ AudioProcessor                                                   │  │
│  │ ├─ record_audio(output_file, timeout)                           │  │
│  │ │  └─ Returns: (success: bool, error: str)                      │  │
│  │ │                                                                │  │
│  │ └─ transcribe_audio(audio_file)                                 │  │
│  │    ├─ Whisper CLI (Local)     ┐                                 │  │
│  │    ├─ SpeechRecognition       ├─ 3 Fallback Methods             │  │
│  │    └─ Cloud LLM Bridge        ┘                                 │  │
│  │    Returns: transcribed_text or error                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ ErrorRecoveryManager                                             │  │
│  │ ├─ log_error(component, message, exception)                      │  │
│  │ ├─ should_retry(component, max_retries=3)                        │  │
│  │ ├─ reset_component(component)                                    │  │
│  │ └─ get_recovery_stats()                                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ SmartCache (Performance)                                         │  │
│  │ ├─ set(key, value, ttl)              [Store with TTL]           │  │
│  │ ├─ get(key)                          [Retrieve if valid]        │  │
│  │ ├─ clear()                           [Clear all]                │  │
│  │ └─ get_stats()                       [Hit rate, size, etc]      │  │
│  │                                                                   │  │
│  │ Features: LRU Eviction | Thread-safe | Memory efficient          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ @cached Decorator                                                │  │
│  │ ├─ Automatically caches function results                         │  │
│  │ ├─ Optional custom TTL                                           │  │
│  │ └─ Transparent to caller                                         │  │
│  │                                                                   │  │
│  │ Usage: @cached(ttl=3600)                                         │  │
│  │        def expensive_operation(data):                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ RateLimiter (Security)                                           │  │
│  │ ├─ is_allowed(endpoint)        [Check if request allowed]       │  │
│  │ ├─ wait_if_needed(endpoint)    [Wait & return wait time]        │  │
│  │ └─ get_stats(endpoint)         [Token bucket status]            │  │
│  │                                                                   │  │
│  │ Algorithm: Token Bucket | Per-endpoint tracking                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ SessionManager (Sessions)                                        │  │
│  │ ├─ create_session(id, data)            [Create new session]     │  │
│  │ ├─ get_session(id)                     [Get if valid/not expired]│ │
│  │ ├─ update_session(id, data)            [Update data]            │  │
│  │ ├─ destroy_session(id)                 [Delete session]         │  │
│  │ └─ cleanup_expired()                   [Remove expired]         │  │
│  │                                                                   │  │
│  │ Features: Timeout management | Auto-cleanup | Thread-safe       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ BackupManager (Data Safety)                                      │  │
│  │ ├─ backup(source_file, backup_name)    [Create versioned backup]│  │
│  │ ├─ restore(backup_path, target_file)   [Restore from backup]    │  │
│  │ └─ cleanup_old_backups()               [Keep last N versions]   │  │
│  │                                                                   │  │
│  │ Features: Automatic cleanup | Version management | Safe restore  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ DataEncryption (Security)                                        │  │
│  │ ├─ encrypt(data, key)                  [Encrypt with SHA256+XOR] │  │
│  │ ├─ decrypt(encrypted_data, key)        [Decrypt data]           │  │
│  │ └─ Symmetric encryption                [AES-ready]              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ PerformanceMonitor (Metrics)                                     │  │
│  │ ├─ record(metric_name, value)          [Log metric]             │  │
│  │ ├─ get_stats(metric_name)              [Min/max/avg/count]      │  │
│  │ └─ report()                            [Generate report]        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                    ⚙️ CONFIGURATION LAYER                               │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ ConfigManager (Dynamic Configuration)                           │  │
│  │                                                                   │  │
│  │  Hierarchy:                                                      │  │
│  │  ConfigManager                                                   │  │
│  │  ├─ .api (APIConfig)                                            │  │
│  │  │  ├─ gemini_key, openai_key, deepseek_key                     │  │
│  │  │  ├─ default_model: "gemini-pro"                              │  │
│  │  │  ├─ timeout_seconds: 30                                      │  │
│  │  │  └─ max_retries: 3                                           │  │
│  │  │                                                               │  │
│  │  ├─ .audio (AudioConfig)                                        │  │
│  │  │  ├─ sample_rate: 16000 Hz                                    │  │
│  │  │  ├─ channels: 1 (mono)                                       │  │
│  │  │  ├─ max_duration: 300s                                       │  │
│  │  │  └─ use_whisper, use_google_speech                           │  │
│  │  │                                                               │  │
│  │  ├─ .ui (UIConfig)                                              │  │
│  │  │  ├─ theme: "dark"                                            │  │
│  │  │  ├─ accent_color: "#00D9FF" (Neon Cyan)                     │  │
│  │  │  ├─ window_width: 900, window_height: 700                    │  │
│  │  │  └─ animation_enabled: True                                  │  │
│  │  │                                                               │  │
│  │  ├─ .logging (LoggingConfig)                                    │  │
│  │  │  ├─ log_level: "INFO"                                        │  │
│  │  │  ├─ log_file: "logs/kno.log"                                 │  │
│  │  │  ├─ max_file_size: 10MB (Rotation)                           │  │
│  │  │  └─ backup_count: 5                                          │  │
│  │  │                                                               │  │
│  │  ├─ .cache (CacheConfig)                                        │  │
│  │  │  ├─ enabled: True                                            │  │
│  │  │  ├─ max_size: 100                                            │  │
│  │  │  ├─ ttl_seconds: 3600                                        │  │
│  │  │  └─ eviction_policy: "lru"                                   │  │
│  │  │                                                               │  │
│  │  ├─ .security (SecurityConfig)                                  │  │
│  │  │  ├─ enable_encryption: True                                  │  │
│  │  │  ├─ api_rate_limit: 60 req/min                               │  │
│  │  │  ├─ session_timeout_minutes: 60                              │  │
│  │  │  └─ auto_backup_enabled: True                                │  │
│  │  │                                                               │  │
│  │  └─ .performance (PerformanceConfig)                            │  │
│  │     ├─ async_enabled: True                                      │  │
│  │     ├─ thread_pool_size: 4                                      │  │
│  │     ├─ lazy_load_modules: True                                  │  │
│  │     └─ memory_limit_mb: 512                                     │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Sources (Priority):                                                    │
│  1. config.json (File-based, persistent)                              │
│  2. .env (Environment variables, secrets)                             │
│  3. Defaults (Hardcoded, fallback)                                    │
│                                                                         │
│  Features: Validation | Hot reloading | Dynamic updates               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                 🔄 DATA FLOW & INTERACTION PATTERNS                     │
│                                                                         │
│  PATTERN 1: Audio Recording & Transcription Flow                       │
│  ═════════════════════════════════════════════════════════════════════  │
│                                                                         │
│    User clicks "Listen"                                                │
│         ▽                                                               │
│    KNOAgent._on_listen()                                               │
│         ▽                                                               │
│    AudioProcessor.record_audio()                                       │
│    ├─ Record from microphone (timeout=300s)                            │
│    ├─ Handle timeout + errors                                          │
│    └─ Return (success: bool, error: str)                               │
│         ▽                                                               │
│    If success:                                                          │
│    AudioProcessor.transcribe_audio()                                   │
│    ├─ Check @cached result                                             │
│    ├─ If hit: return cached text → 1ms                                 │
│    ├─ If miss: Try Whisper CLI                                         │
│    ├─ If fail: Try SpeechRecognition (Google)                          │
│    ├─ If fail: Try Cloud LLM Bridge                                    │
│    └─ Return transcribed_text or error                                │
│         ▽                                                               │
│    Send to LLM for processing                                          │
│    ├─ RateLimiter.is_allowed() → proceed if allowed                    │
│    ├─ LLM processing (with timeout)                                    │
│    └─ SmartCache.set() → cache response                                │
│         ▽                                                               │
│    Update UI                                                            │
│    ├─ NeonLabel animation                                              │
│    ├─ GradientFrame update                                             │
│    ├─ ToastNotification display                                        │
│    └─ Status bar refresh                                               │
│                                                                         │
│                                                                         │
│  PATTERN 2: Error Detection & Recovery Flow                            │
│  ═════════════════════════════════════════════════════════════════════  │
│                                                                         │
│    Exception Detected                                                  │
│         ▽                                                               │
│    ErrorRecoveryManager.log_error()                                    │
│    ├─ Record: component, message, exception type                       │
│    ├─ Store in component-specific tracker                              │
│    └─ Write to logs/kno.log                                            │
│         ▽                                                               │
│    ErrorRecoveryManager.should_retry()                                 │
│    ├─ Check retry count for component                                  │
│    ├─ If < max_retries: return True                                    │
│    └─ If >= max_retries: return False → use fallback                   │
│         ▽                                                               │
│    If retry: Execute retry logic                                       │
│    ├─ Exponential backoff (1s → 2s → 4s → ...)                         │
│    ├─ Alternative strategy                                             │
│    └─ Re-attempt operation                                             │
│         ▽                                                               │
│    If fallback: Use alternative method                                 │
│    ├─ Switch to backup transcription method                            │
│    ├─ Use cached result if available                                   │
│    └─ Display to user gracefully                                       │
│         ▽                                                               │
│    Resolution                                                          │
│    ├─ Log resolution success                                           │
│    ├─ Update UI status                                                 │
│    └─ Continue normal operation                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                 📁 DEPENDENCY RELATIONSHIPS                             │
│                                                                         │
│   agent_refactored_v5.py                                               │
│   ├─ imports: kno_config_v5 (ConfigManager)                            │
│   ├─ imports: kno_utils (SmartCache, ErrorRecoveryManager, etc)        │
│   ├─ imports: customtkinter (GUI)                                      │
│   ├─ imports: PIL (Graphics)                                           │
│   ├─ imports: logging (Centralized logging)                            │
│   └─ uses: config.json + .env (Configuration)                          │
│                                                                         │
│   kno_utils.py                                                         │
│   ├─ imports: time, hashlib, json (Standard library)                   │
│   ├─ imports: threading, collections (Thread-safety)                   │
│   ├─ imports: logging (Event logging)                                  │
│   └─ No external dependencies                                          │
│                                                                         │
│   kno_config_v5.py                                                     │
│   ├─ imports: json, logging (Standard library)                         │
│   ├─ imports: pathlib (File system)                                    │
│   ├─ imports: python-dotenv (.env support)                             │
│   ├─ uses: .env (Environment variables)                                │
│   └─ uses: config.json (Configuration file)                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│            💻 DEPLOYMENT ARCHITECTURE                                  │
│                                                                         │
│   Development Environment                                              │
│   ┌──────────────────────────────────────────────┐                     │
│   │  Python 3.9+                                 │                     │
│   │  Virtual Environment (venv/)                 │                     │
│   │                                              │                     │
│   │  Dependencies:                               │                     │
│   │  ├─ customtkinter (GUI framework)            │                     │
│   │  ├─ pillow (Image processing)                │                     │
│   │  ├─ requests (HTTP client)                   │                     │
│   │  ├─ SpeechRecognition (Audio)                │                     │
│   │  ├─ python-dotenv (Config)                   │                     │
│   │  ├─ pytest (Testing)                         │                     │
│   │  └─ pyttsx3 (TTS)                            │                     │
│   │                                              │                     │
│   │  Configuration:                              │                     │
│   │  ├─ .env (API keys, secrets)                 │                     │
│   │  ├─ config.json (Runtime settings)           │                     │
│   │  └─ logs/ (Application logs)                 │                     │
│   │                                              │                     │
│   │  Data:                                       │                     │
│   │  ├─ backups/ (Automatic backups)             │                     │
│   │  ├─ memory.json (Cached responses)           │                     │
│   │  └─ experience.json (Learning data)          │                     │
│   └──────────────────────────────────────────────┘                     │
│                  ▼ Deploy                                              │
│   Production Environment                                               │
│   ┌──────────────────────────────────────────────┐                     │
│   │  Docker Container (Optional)                 │                     │
│   │  ┌──────────────────────────────────────────┐│                     │
│   │  │  Python Runtime                          ││                     │
│   │  │  + Application Code                      ││                     │
│   │  │  + Dependencies                          ││                     │
│   │  │  + Configuration Management              ││                     │
│   │  │                                          ││                     │
│   │  │  Volumes:                                ││                     │
│   │  │  ├─ /app/config → config.json            ││                     │
│   │  │  ├─ /app/logs → Persistent logs          ││                     │
│   │  │  └─ /app/data → Backups & caches         ││                     │
│   │  └──────────────────────────────────────────┘│                     │
│   │                                              │                     │
│   │  Environment Variables (from .env):          │                     │
│   │  ├─ GEMINI_API_KEY                           │                     │
│   │  ├─ OPENAI_API_KEY                           │                     │
│   │  ├─ DEEPSEEK_API_KEY                         │                     │
│   │  ├─ ENCRYPTION_KEY                          │                     │
│   │  └─ ...                                      │                     │
│   └──────────────────────────────────────────────┘                     │
│                                                                         │
│   Monitoring & Logging                                                  │
│   ┌──────────────────────────────────────────────┐                     │
│   │  logs/kno.log                                │                     │
│   │  ├─ INFO: Normal operation                   │                     │
│   │  ├─ WARNING: Non-critical issues             │                     │
│   │  ├─ ERROR: Failures with recovery            │                     │
│   │  └─ DEBUG: Detailed trace information        │                     │
│   │                                              │                     │
│   │  Metrics:                                    │                     │
│   │  ├─ Performance (response time, memory)      │                     │
│   │  ├─ Reliability (error rate, recovery)       │                     │
│   │  ├─ Usage (API calls, cache hits)            │                     │
│   │  └─ Security (rate limit hits, sessions)     │                     │
│   └──────────────────────────────────────────────┘                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════════════╗
║                        END OF ARCHITECTURE DIAGRAM                        ║
║                                                                           ║
║  This diagram represents the complete KNO v5.0 system architecture,     ║
║  showing:                                                                 ║
║  • Layered design (Presentation, Controller, Model, Data)                ║
║  • Component relationships and interactions                              ║
║  • Data flow patterns (audio processing, error recovery)                 ║
║  • Deployment architecture                                               ║
║  • Configuration management                                              ║
║  • Monitoring and logging infrastructure                                 ║
║  • Security and fault tolerance mechanisms                               ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## 📊 COMPONENT INTERACTION MATRIX

```
                    │ Audio │ Error │ Config│ Cache │ Rate  │
                    │Process│Recov │Mgr   │      │Limit  │
────────────────────┼───────┼───────┼───────┼───────┼────────
KNOAgent (Control)  │  ✓✓   │  ✓✓  │  ✓   │  ✓   │   ✓   │
AudioProcessor      │  ──   │  ✓   │  ✓   │  ✓   │   ➜   │
ErrorRecovery       │  ✓    │  ──  │  ✓   │  ✓   │   ✓   │
ConfigManager       │  ✓    │  ✓   │  ──  │  ✓   │   ✓   │
SmartCache          │  ✓✓   │  ✓   │  ✓   │  ──  │   ✓   │
RateLimiter         │  ✓    │  ✓   │  ✓   │  ✓   │   ──  │
SessionManager      │  ──   │  ✓   │  ✓   │  ✓   │   ➜   │
BackupManager       │  ✓    │  ✓   │  ✓   │  ✓   │   ──  │
PerformanceMonitor  │  ✓    │  ✓   │  ✓   │  ✓   │   ✓   │

Legend:
✓✓  = High interaction (multiple calls)
✓   = Direct interaction
➜   = Optional/conditional interaction
──  = Does not interact
```

---

## 🔗 Service Dependencies

```
External Services:
├─ Gemini API (Google ML)
│  └─ Used by: KNOAgent, LLM processing
│
├─ OpenAI API (ChatGPT)
│  └─ Used by: KNOAgent, Fallback LLM
│
├─ DeepSeek API
│  └─ Used by: KNOAgent, Fallback LLM
│
├─ Google Cloud Speech
│  └─ Used by: AudioProcessor.transcribe_audio()
│
├─ Whisper (OpenAI)
│  └─ Used by: AudioProcessor.transcribe_audio() [Local]
│
└─ File System
   ├─ Read: config.json, .env
   ├─ Write: logs/kno.log
   └─ Write: backups/*, memory.json

Internal Service Chain:
┌─────────────────────────────────────────────┐
│              User Input                     │
└────────────────────┬────────────────────────┘
                     ▼
         ┌──────────────────────┐
         │   KNOAgent (GUI)     │
         └──────────┬───────────┘
                    ▼
      ┌─────────────────────────┐
      │   AudioProcessor        │
      │  - Record               │
      │  - Transcribe           │
      └──────────┬──────────────┘
                 ▼
   ┌─────────────────────────────┐
   │  Error Recovery Manager     │
   │  - Track errors             │
   │  - Manage retries           │
   │  - Fallbacks                │
   └──────────┬──────────────────┘
              ▼
   ┌────────────────────────────┐
   │   RateLimiter              │
   │  - Check quota             │
   │  - Queue requests          │
   └──────────┬─────────────────┘
              ▼
    ┌────────────────────────┐
    │   LLM APIs             │
    │ - Process text         │
    │ - Generate response    │
    └──────────┬─────────────┘
               ▼
     ┌──────────────────────┐
     │   SmartCache         │
     │ - Store result       │
     │ - Return cached      │
     └──────────┬───────────┘
                ▼
        ┌──────────────────┐
        │  BackupManager   │
        │ - Auto-backup    │
        └──────────┬───────┘
                   ▼
          ┌────────────────┐
          │   User Output  │
          └────────────────┘
```
