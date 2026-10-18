#!/bin/bash
# 스킬 구조 검증 스크립트
# 사용법: ./tests/validate-skills.sh [skills_dir]
# 종료코드: 0 (통과), 1 (이슈 발견)

SKILLS_DIR="${1:-skills}"
ERRORS=0
WARNINGS=0

RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

error() { echo -e "${RED}  ❌ $1${NC}"; ((ERRORS++)); }
warn()  { echo -e "${YELLOW}  ⚠️  $1${NC}"; ((WARNINGS++)); }
ok()    { echo -e "${GREEN}  ✅ $1${NC}"; }

echo "=== AIDLC 스킬 구조 검증 ==="
echo ""

# 모든 SKILL.md 파일 수집
SKILL_FILES=$(find "$SKILLS_DIR" -name "SKILL.md" -type f | sort)

for SKILL_FILE in $SKILL_FILES; do
    SKILL_DIR=$(dirname "$SKILL_FILE")
    SKILL_NAME=$(basename "$SKILL_DIR")
    echo "[$SKILL_NAME]"

    # 1. frontmatter 존재 확인
    if ! head -1 "$SKILL_FILE" | grep -q "^---"; then
        error "frontmatter 없음"
        echo ""
        continue
    fi

    # frontmatter 추출 (첫 번째 --- 와 두 번째 --- 사이)
    FRONTMATTER=$(awk 'NR==1{next} /^---$/{exit} {print}' "$SKILL_FILE")

    # 2. name 필드
    FM_NAME=$(echo "$FRONTMATTER" | grep "^name:" | sed 's/name: *//')
    if [ -z "$FM_NAME" ]; then
        error "name 필드 누락"
    elif [ "$FM_NAME" != "$SKILL_NAME" ]; then
        error "name 불일치: frontmatter='$FM_NAME' vs 디렉토리='$SKILL_NAME'"
    else
        ok "name: $FM_NAME"
    fi

    # 3. description 필드 + CSO 확인
    DESC=$(echo "$FRONTMATTER" | grep "^description:" | sed 's/description: *//')
    if [ -z "$DESC" ]; then
        error "description 누락"
    elif echo "$DESC" | grep -qi "^use when"; then
        ok "description CSO 준수"
    else
        warn "description이 'Use when...'으로 시작하지 않음"
    fi

    # 4. metadata 필수 필드
    for FIELD in version author category; do
        if echo "$FRONTMATTER" | grep -q "$FIELD:"; then
            ok "metadata.$FIELD 존재"
        else
            error "metadata.$FIELD 누락"
        fi
    done

    # 5. invoke_mode
    if echo "$FRONTMATTER" | grep -q "invoke_mode:"; then
        ok "invoke_mode 존재"
    else
        error "invoke_mode 누락"
    fi

    # 6. return_behavior
    if echo "$FRONTMATTER" | grep -q "return_behavior:"; then
        ok "return_behavior 존재"
    else
        warn "return_behavior 누락"
    fi

    # 7. 줄 수 (500줄 가이드라인)
    LINE_COUNT=$(wc -l < "$SKILL_FILE" | tr -d ' ')
    if [ "$LINE_COUNT" -gt 500 ]; then
        warn "SKILL.md ${LINE_COUNT}줄 — 500줄 가이드라인 초과"
    else
        ok "${LINE_COUNT}줄"
    fi

    # 8. description 길이 (1024자)
    DESC_LEN=${#DESC}
    if [ "$DESC_LEN" -gt 1024 ]; then
        warn "description ${DESC_LEN}자 — 1024자 초과"
    fi

    # 9. _shared/ 참조 유효성
    REFS=$(grep -oE '_shared/[a-zA-Z0-9_/-]+\.md' "$SKILL_FILE" | sort -u)
    for REF in $REFS; do
        if [ -f "$SKILLS_DIR/$REF" ]; then
            ok "참조 유효: $REF"
        else
            error "참조 파일 없음: $REF"
        fi
    done

    echo ""
done

echo "=== 결과 ==="
echo "  에러: $ERRORS건"
echo "  경고: $WARNINGS건"

if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}FAIL${NC} — 에러를 수정하세요"
    exit 1
else
    echo -e "${GREEN}PASS${NC}"
    exit 0
fi
