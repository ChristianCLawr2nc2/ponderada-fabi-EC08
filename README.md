# Culling Games — Navegação Autônoma

Workspace ROS 2 com o simulador [culling_games](https://github.com/rmnicola/culling_games) e a solução da ponderada em duas partes:

1. **Parte 1:** mapa completo via `/get_map` + caminho mínimo (BFS/A*) + execução
2. **Parte 2:** exploração cega com sensores (DFS + backtracking), construção do mapa, reset e rota ótima

---

## Estrutura

```
├── src/
│   ├── cg/                 # Simulador (mapa + Pygame)
│   ├── cg_interfaces/      # msgs/srvs
│   ├── cg_teleop/          # teleop por teclado
│   └── cg_solver/          # ← nossa solução (parte1 / parte2)
│       └── cg_solver/
│           ├── grid.py         # constantes e utilitários da grade
│           ├── pathfinding.py  # BFS / A*
│           ├── exploration.py  # DFS + mapa por sensores
│           ├── parte1_node.py
│           └── parte2_node.py
├── simulator/              # Validação local sem ROS 2 (Windows/Linux)
├── tests/
└── README.md
```


---

## Requisitos (ROS 2)

- Ubuntu + ROS 2 (Humble/Jazzy)
- `python3-pygame`
- `colcon`

```bash
sudo apt install python3-pygame
```

---

## Build e execução com ROS 2

```bash
cd ~/caminho/para/ponderada-fabi
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build
source install/setup.bash
```

### Terminal 1 — simulador

```bash
ros2 run cg maze -- --map test.csv
# ou: ros2 run cg maze -- --map 1.csv
# ou: ros2 run cg maze -- --generate
```

### Terminal 2 — Parte 1 (mapa conhecido)

```bash
source install/setup.bash
ros2 run cg_solver parte1
# opcional: algoritmo A*
ros2 run cg_solver parte1 --ros-args -p algorithm:=astar
```

### Terminal 2 — Parte 2 (exploração + navegação)

Com o simulador ainda aberto (reinicie o mapa se necessário):

```bash
ros2 service call /reset cg_interfaces/srv/Reset "{is_random: false}"
ros2 run cg_solver parte2
```

A Parte 2 salva o mapa descoberto em `mapa_descoberto.csv` (cwd do processo).

---

## Validação sem ROS 2 (já testado neste PC)

Útil no Windows, onde o ROS 2 normalmente roda via WSL/Ubuntu.

```bash
# Parte 1 — test.csv → 25 movimentos
python simulator/run_parte1.py --map src/cg/maps/test.csv

# Parte 1 — 1.csv → 102 movimentos
python simulator/run_parte1.py --map src/cg/maps/1.csv

# Parte 2 — exploração + mesma rota ótima
python simulator/run_parte2.py --map src/cg/maps/test.csv
python simulator/run_parte2.py --map src/cg/maps/1.csv
```

### Resultados observados

| Mapa | Parte 1 (BFS) | Parte 2 (após DFS) |
|------|---------------|--------------------|
| `test.csv` | 25 movimentos | mesma rota (25) |
| `1.csv` | 102 movimentos | mesma rota (102) |

No `test.csv`, a exploração registrou 841 células conhecidas, 728 visitadas e 1454 movimentos de ida/volta antes do planejamento.

---

## Como funciona (resumo)

### Parte 1
1. Chama `/get_map`
2. Monta a grade 2D
3. BFS (ou A*) de `r` até `t`
4. Envia cada direção em `/move_command`

### Parte 2
1. Assina `/culling_games/robot_sensors`
2. DFS: anda para vizinhos livres não visitados; backtrack com direção oposta
3. Nunca pisa no `t` durante a exploração
4. Salva o mapa, chama `/reset`, planeja BFS e executa a rota

---

## Teleoperação (opcional)

```bash
ros2 run cg_teleop teleop_keyboard
```

Teclas: `w/a/s/d` ou setas; `r` reset; `n` mapa aleatório.

---

## Tutorial original do simulador

O simulador original documenta serviços, sensores e opções de mapa. Veja também a seção de estudo em [`docs/ESTUDO_PROVA.md`](docs/ESTUDO_PROVA.md) para BFS, DFS, A* e armadilhas típicas de prova.
