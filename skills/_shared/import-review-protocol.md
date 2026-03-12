# Import-Review Protocol

<!-- GENERATE/IMPORT 모드 + Hold/Skip 공유 프로토콜 -->
<!-- 참조하는 스킬: aidlc-user-stories, aidlc-nfr-requirements -->

## 두 가지 모드

| 모드 | 주체 | 흐름 |
|------|------|------|
| **GENERATE** | Claude | 질문 → 수집 → 생성 → 리뷰 |
| **IMPORT** | 사용자 | 파일 수신 → 검증 → 피드백 → 확정 |

모드는 오케스트레이터가 호출 시 인라인 신호로 전달: `"Mode: GENERATE"` 또는 `"Mode: IMPORT"`

## IMPORT Mode 프로세스

```
1. 파일 수신: 사용자가 경로 전달 또는 내용 붙여넣기
2. 형식 검증: 필수 섹션 존재 여부 확인
3. 내용 검토: 누락/모순/모호한 항목 식별
4. 피드백 제시:
   - ✅ 충분한 항목
   - ⚠️ 보완 권장 항목 (이유 포함)
   - ❌ 누락/모순 항목 (이유 포함)
5. 사용자 확정: 피드백 반영 여부는 사용자 결정
```

## Hold/Skip Signal

Pre-Planning 스테이지(user-stories, nfr-requirements)에서 실행 중 중단하거나 건너뛸 수 있다.
오케스트레이터가 H(Hold) 또는 S(Skip) 선택을 감지하면 아래 형식으로 산출물을 저장한다.

### Hold

진행 중인 작업을 중단하고 나중에 재개.

```markdown
## Status: HELD
**Held at**: [중단 시점]
**Reason**: [사용자 제공 이유]
**Completed sections**: [완료된 부분]
**Remaining**: [남은 부분]
```

### Skip

이 스테이지를 완전히 건너뜀.

```markdown
## Status: SKIPPED
**Reason**: [사용자 제공 이유]
```

오케스트레이터는 HELD/SKIPPED 상태를 devflow-state에 기록하고 다음 스테이지로 진행한다.
