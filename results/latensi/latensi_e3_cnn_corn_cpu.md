### Latensi e3_cnn_corn (cpu)

| Parameter | Ukuran checkpoint | Median (ms) | P90 (ms) | FPS | Pra-pemrosesan (ms) | Perangkat |
|---|---|---|---|---|---|---|
| 4.01 M | 16.3 MB | 12.6 | 13.0 | 79.6 | 1.9 | Linux-7.2.4-3-cachyos-x86_64-with-glibc2.44, 6 thread |

Prosedur: batch 1, input 1x3x224x224, 10 iterasi pemanasan, 100 iterasi diukur, forward pass saja.
