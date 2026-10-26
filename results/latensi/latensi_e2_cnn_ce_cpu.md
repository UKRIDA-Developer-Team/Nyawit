### Latensi e2_cnn_ce (cpu)

| Parameter | Ukuran checkpoint | Median (ms) | P90 (ms) | FPS | Pra-pemrosesan (ms) | Perangkat |
|---|---|---|---|---|---|---|
| 4.01 M | 16.3 MB | 12.3 | 12.8 | 81.0 | 1.9 | Linux-7.2.4-3-cachyos-x86_64-with-glibc2.44, 6 thread |

Prosedur: batch 1, input 1x3x224x224, 10 iterasi pemanasan, 100 iterasi diukur, forward pass saja.
