```mermaid

sequenceDiagram
    participant K as Kyrksal
    participant A as nginx rtmp server
    participant English as merge 3las audio to rtmp
    participant InterpretEng as 3LAS server eng

    K->>A: start stream
    A->>English: start merger

    InterpretEng->>English: stream

            

```