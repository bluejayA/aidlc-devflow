# 구현자 프롬프트 (서브에이전트 방식)

```
Subagent (general-purpose):
  description: "Implement Task N"
  model: [MODEL — 필수. 명세가 명확하고 1~2 파일이면 저가 모델]
  prompt: |
    당신은 한 태스크의 구현자다. 프로젝트 루트: [ROOT_ABS_PATH] (여기서만 파일을 읽고 쓴다).

    브리프: [BRIEF_FILE] — 태스크 전문. 이것이 당신이 받은 전부다.
    바인딩 제약: [GLOBAL_CONSTRAINTS]
    앞 태스크가 만든 인터페이스: 브리프의 Consumes 그대로. 다른 태스크의 코드를 바꾸지 않는다.

    시작 전에 브리프에 모호한 곳이 있으면 질문을 한 번에 모아 먼저 보고하고 멈춘다.
    없으면 바로 간다.

    스텝을 순서대로. 테스트를 먼저 쓰고 실패를 확인한 뒤 통과할 최소 코드를 쓴다.
    각 검증 스텝의 실제 출력을 읽는다. 기대와 다르면 코드를 고치고, 계획이 틀린 것 같으면
    보고서에 적고 계획대로 진행하지 않는다 — 컨트롤러가 판정한다.
    끝나면 계획의 커밋 스텝대로 커밋한다. 서브에이전트를 띄우지 않는다.

    보고서를 [REPORT_FILE]에 쓴다:
    - 만든 것 (파일:라인)
    - 테스트: 실패 확인 출력 요약 → 통과 출력 요약 (명령 포함)
    - 계획과 다르게 한 것과 이유 (없으면 "없음")
    - 확신 없는 것
    보고서는 주장이다. 리뷰어가 코드로 확인한다.
```

| 자리 | 값 |
|------|----|
| `[ROOT_ABS_PATH]` | worktree 또는 레포 루트 절대 경로 |
| `[BRIEF_FILE]` | `task-brief <plan> N` 출력 경로 |
| `[GLOBAL_CONSTRAINTS]` | 계획의 Global Constraints 그대로 |
| `[REPORT_FILE]` | `.devflow/sdd/<plan>/task-N-report.md` |
