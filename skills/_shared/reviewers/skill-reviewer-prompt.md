# Skill Reviewer Prompt Template

**Purpose:** 스킬 SKILL.md가 구조적으로 완전하고, 내용이 구체적이며, CSO가 올바른지 검증한다.

**Dispatch timing:** writing-skills 3단계(REFACTOR)에서 Standard/Comprehensive depth일 때 자동 dispatch. Minimal depth에서는 스킵.

**Dispatch method:** Agent tool (general-purpose type)

```
Agent tool (general-purpose):
  description: "Review skill SKILL.md"
  prompt: |
    You are a skill reviewer. Verify this SKILL.md is structurally complete, content is concrete, and CSO is correct.

    **Skill to review:** [SKILL_FILE_PATH]
    **Reference standards:**
    - Reference: skills/_shared/patterns/skill-writing-guide.md

    ## 1. 구조 검증 (skill-writing-guide.md 기준)

    | 항목 | 검증 기준 |
    |------|----------|
    | frontmatter | name, description, metadata (version, author, category) 필수 필드 존재 |
    | name | 디렉토리명과 일치하는가 |
    | description 시작 | "Use when..."으로 시작하는가 |
    | description 내용 | 워크플로우 요약이 포함되어 있지 않은가 (트리거 조건만 기술) |
    | description 길이 | 1024자 이하인가 |
    | 필수 섹션 | Trigger, Examples (2개 이상), Troubleshooting (2개 이상) 존재하는가 |
    | 줄 수 | 500줄 이하인가 (초과 시 분리 권고) |

    ## 2. 내용 검증 (skill-writing-guide.md 기준)

    | 항목 | 검증 기준 |
    |------|----------|
    | 구체성 | "잘 처리한다", "적절히 대응한다" 같은 모호 표현이 없는가 |
    | 압박 시나리오 | 압박 시나리오 커버리지가 충분한가 (최소 2가지 압력 조합) |
    | standalone 동작 | 이 스킬만 읽고도 워크플로우를 실행할 수 있는가 (외부 참조 없이 핵심 흐름 완결) |
    | 예시 유용성 | Examples가 실제 사용 상황을 반영하며, 에이전트가 행동을 결정하는 데 도움이 되는가 |
    | Troubleshooting | 실제 발생 가능한 문제를 다루는가 (가상의 문제가 아닌 현실적 시나리오) |

    ## 3. CSO 검증

    | 항목 | 검증 기준 |
    |------|----------|
    | 트리거 명확성 | description이 "무엇을 하는가" + "언제 사용하는가"를 명확히 전달하는가 |
    | 키워드 풍부성 | 한국어/영어 동의어, 사용자 관점 키워드가 충분히 포함되어 있는가 |
    | 경계 명확성 | 유사 스킬과의 상호 배타 조건이 명확한가 (키워드 중복으로 잘못된 스킬이 선택될 여지가 없는가) |

    ## CRITICAL

    다음을 특히 엄격하게 확인한다:
    - description에 내부 구현 상세(파일 경로, 위임 체인, 실행 순서)가 노출되어 있지 않은가
    - 모호한 표현("잘", "적절히", "필요 시")이 핵심 지시에 사용되어 있지 않은가
    - 500줄을 초과하면서 분리 가능한 섹션(템플릿, 체크리스트)이 인라인에 남아 있지 않은가
    - Troubleshooting이 형식적이지 않고 실제 디버깅에 도움이 되는가

    ## Output Format

    ## Skill Review

    **Status:** ✅ Approved | ❌ Issues Found

    **Issues (if any):**
    - [검증 영역] [항목]: [구체적 문제] — [왜 문제인지]

    **Recommendations (advisory):**
    - [승인을 차단하지 않는 개선 제안]
```

**Reviewer returns:** Status, Issues (if any), Recommendations
