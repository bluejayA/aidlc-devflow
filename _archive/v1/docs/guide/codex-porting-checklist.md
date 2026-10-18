# Codex 포팅 체크리스트

이 문서는 `aidlc-devflow` 같은 Claude 중심 스킬 저장소를 Codex에서 재사용할 때 필요한 최소 작업을 정리한다.

## 1) 포팅 목표 확정

- [ ] 목표를 결정한다:
  - A. 빠른 실행: 핵심 스킬만 Codex에서 사용
  - B. 전체 이관: 오케스트레이터 + 전 스킬 + 문서까지 Codex 대응
- [ ] 대상 브랜치를 분리한다 (예: `codex/port-skill-pack`).

## 2) 호스트 의존 요소 식별

아래 파일은 Claude 전용 엔트리/UX에 의존한다.

- [ ] `.claude-plugin/plugin.json`
- [ ] `hooks/hooks.json`
- [ ] `hooks/session-start`
- [ ] 문서 내 `/aidlc:skill-name` 호출 문법

권장 원칙:
- 런타임 핵심은 `skills/`로 두고, 호스트별 엔트리(`.claude-plugin`, `hooks`)는 분리 유지한다.

## 3) 경로 정규화 (`_shared`)

현재 스킬 다수는 `_shared/...`를 참조한다. Codex에서 파일 기준 상대경로 해석 시 실패할 수 있으므로, 아래처럼 정규화한다.

- Before: ``_shared/patterns/xxx.md``
- After: ``../_shared/patterns/xxx.md``

## 4) 자동 변환 스크립트 실행

저장소 루트에서 실행:

```bash
# 1) 변경 예상치 확인
python3 scripts/port_to_codex.py --root .

# 2) 실제 적용
python3 scripts/port_to_codex.py --root . --apply
```

옵션:

```bash
# _shared 경로만 변환
python3 scripts/port_to_codex.py --root . --apply --no-rewrite-invocations

# slash 호출 문법만 변환
python3 scripts/port_to_codex.py --root . --apply --no-rewrite-shared
```

## 5) 수동 점검 (필수)

- [ ] `skills/*/SKILL.md`에서 `_shared` 참조가 모두 `../_shared`로 바뀌었는지 확인
- [ ] `/aidlc:...` 호출이 `$skill-name` 또는 자연어 호출 가이드로 변경됐는지 확인
- [ ] Claude 전용 문구(예: SessionStart, Claude plugin host)를 Codex 안내로 재작성

추천 점검 명령:

```bash
rg -n '_shared/|skills/_shared/|/aidlc:' skills docs README* hooks -S
```

## 6) 오케스트레이터 동작 검증

- [ ] `aidlc-using-devflow` 진입 테스트
- [ ] `aidlc-inception-orchestrator`의 게이트 분기 테스트
- [ ] `aidlc-construction-orchestrator`의 Plan→Generate→Build/Test 루프 테스트
- [ ] `devflow-docs/devflow-state.md` 갱신과 resume 시나리오 테스트

## 7) 테스트 파이프라인 유지

기존 메타태그 검증은 Codex에서도 그대로 유효하다.

```bash
bash tests/run-all.sh
```

필요 조건:
- Node.js (parse-skills)
- Python + pytest + pyyaml (`uv sync` 또는 동등 환경)

## 8) 배포 방식 선택

- [ ] 단일 저장소 유지: Claude/Codex 공용 코어 + 엔트리만 분기
- [ ] Codex 전용 포크: 문서/호출문법/운영규약까지 완전 분리

권장:
- 초기에는 공용 코어(`skills/`)를 유지하고, 호스트 엔트리만 분기한다.

## 9) 릴리즈 체크

- [ ] 변경 요약 문서화 (`docs/guide/codex-porting-checklist.md` 링크)
- [ ] 버전 태그 정책 확정 (`vX.Y.Z-codex.N` 등)
- [ ] 설치/온보딩 문서에 Codex 사용 예시 추가
