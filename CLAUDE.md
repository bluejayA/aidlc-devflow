# aidlc-devflow 프로젝트 규칙

## 백로그-GitHub 이슈 연동 (필수)

### 백로그 등록 시
- `memory/backlog_aidlc.md`에 항목 추가
- GitHub 이슈를 `enhancement` 라벨로 동시 생성 (`bluejayA/aidlc-devflow`)
- 백로그에 이슈 번호와 링크 기록

### 백로그 구현 시
백로그 항목을 구현하여 커밋할 때, 연결된 GitHub 이슈와 반드시 연동한다.

1. **커밋 메시지에 이슈 번호 포함**
   - 진행 중: `refs #N`
   - 완료 시: `closes #N` (머지 시 이슈 자동 클로즈)
   - 예: `feat: workspace-detection에 사용자 질문 분기 추가 (closes #1)`

2. **GitHub 이슈에 진행 코멘트 남기기**
   - 구현 시작 시: 간략한 접근 방식 코멘트
   - 커밋 완료 시: 변경 내용 요약 + 커밋 해시 코멘트

3. **백로그 파일 상태 동기화**
   - 구현 완료 시 `backlog_aidlc.md`의 상태를 `Done`으로 변경
