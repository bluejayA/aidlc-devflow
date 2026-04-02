# 스킬 정합성 체크리스트

> 백로그 작업 시 해당 스킬/파일을 수정하면 여기서 관련 이슈를 확인하고 함께 수정한다.
> 수정 완료 시 `[x]`로 체크.


## 상시 체크 — 메타 태그 동기화

> 오케스트레이터 SKILL.md 수정 시 반드시 확인.

메타 태그(`@gate`, `@gate-option`, `@step`, `@condition`, `@state-update`, `@resume-rules`)가 삽입된 파일을 수정할 때:

- [ ] 게이트 추가/삭제 시 `@gate` + `@gate-option` 태그도 함께 수정했는가
- [ ] 스텝 순서 변경 시 `@step` 번호를 재조정했는가
- [ ] 조건 분기 변경 시 `@condition` 태그를 업데이트했는가
- [ ] devflow-state 업데이트 지점 변경 시 `@state-update` 주석을 동기화했는가
- [ ] Resume Flow 분기 변경 시 `@resume-rules` 주석 블록을 업데이트했는가
- [ ] `bash tests/run-all.sh` 실행 시 전체 통과하는가

**검증 방법**: `bash tests/run-all.sh` — 269개 테스트가 불일치를 자동 검출
**규격 참조**: `_shared/patterns/meta-tag-standard.md` → Maintenance 섹션
