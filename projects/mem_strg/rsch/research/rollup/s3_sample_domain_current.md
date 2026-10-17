# 도메인 CURRENT — 생성 2026-10-17 23:59 (직접 고치지 않음)

| 역할 | 세션 | 상태 | 지금 | 다음 | 기다리는 대상 | Owner 대기 | 갱신 |
|---|---|---|---|---|---|---|---|
| rhs/order/arch | RHS/ORDER/ARCH | IDLE | seeded | - | - | - | 09:00 |
| rhs/order/pln | RHS/ORDER/PLN | WAITING | PMOV H3d PASS | accept after PMO freeze | role:rhs/order/pmo | - | 14:00 |
| rhs/order/pmo | RHS/ORDER/PMO | DONE | F2 frozen 4da7fd5 | - | - | - | 15:00 |
| rhs/order/rsch | RHS/ORDER/RSCH | IDLE | seeded | - | - | - | 09:00 |
| rhs/sim/arch | RHS/SIM/ARCH | IDLE | seeded | - | - | - | 09:00 |
| rhs/sim/pln | RHS/SIM/PLN | ACTIVE | E-1 found: spot buy fee in base asset | tell order PLN | - | - | 12:00 |
| rhs/sim/pmo | RHS/SIM/PMO | IDLE | seeded | - | - | - | 09:00 |
| rhs/sim/rsch | RHS/SIM/RSCH | IDLE | seeded | - | - | - | 09:00 |

## 표시
- STALE rhs/order/pln (WAITING 10h) → 확인: RHS/ORDER/PLN
- CONFLICT rhs/order/pln가 rhs/order/pmo를 기다리지만 rhs/order/pmo는 DONE → 확인: RHS/ORDER/PLN
- STALE rhs/sim/pln (ACTIVE 12h) → 확인: RHS/SIM/PLN
- CROSS_ONE_SIDED RHS-X-001: sim 쪽에만 있음
