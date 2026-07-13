# kdailymart-automation

kdailymart SG(운영중)/MY(신규) 매장의 "매일 10개 상품 자동화" 파이프라인 스캐폴딩.

## 현재 상태: 스캐폴딩만 완료, 실행 불가

이 폴더는 [`kdailymart_자동화_파이프라인_설계서_v1.md`]의 5번 섹션 구조를 그대로 코드로
옮긴 **뼈대**입니다. 아래는 아직 되어 있지 않습니다.

- 크리덴셜/API 키 연결 (도매꾹/쿠팡/네이버, 이미지 생성, 번역, 쇼피 셀러센터, SNS 채널 등) — 전혀 없음
- `agents/` 하위 9개 스크립트는 전부 **함수 시그니처 + docstring + TODO만 있는 스텁**이며,
  실제 호출 시 `NotImplementedError`를 던집니다.
- `rulebook/country_rules.json`, `rulebook/category_master.json`은 사람이 검수해야 하는 **초안(draft)**
  상태입니다 (실제 실행 전에 재검증 필요).
- 브라우저 자동화 방식(Playwright vs 쇼피 Open API 등) 등 핵심 아키텍처 결정이 아직 내려지지 않았습니다.

즉, **지금 이 저장소를 그대로 실행해도 아무 상품도 등록되지 않습니다.** 구조와 로직(각 단계가 무엇을
입력/출력하고 무엇을 근거로 승인/반려하는지)만 정리된 상태입니다.

## 폴더 구조

```
kdailymart-automation/
├── rulebook/
│   ├── country_rules.json       # SG/MY 금지카테고리, 수수료 가정 (draft)
│   └── category_master.json     # 카테고리ID, 속성 허용값 (draft, 2개 카테고리만 검증됨)
├── agents/
│   ├── sourcing.py              # 후보 10개 수집
│   ├── compliance.py            # 국가별 규제 필터
│   ├── margin.py                # 마진 스크리닝
│   ├── image.py                 # 이미지 가공/업로드
│   ├── localization.py          # 현지어 카피
│   ├── listing.py               # Global SKU 등록 -> Mass Upload -> Publish
│   ├── promo.py                 # 홍보 콘텐츠 제작
│   ├── distribution.py          # 채널 배정/스케줄링 (distribution-planner)
│   └── master_qa.py             # 전체 QA 게이트 + 일일 리포트
├── data/
│   ├── candidates/               # 일자별 후보 리스트
│   └── listed/                   # 등록 완료 상품 로그
├── logs/
│   └── master-qa/                # 일일 QA 리포트
└── outputs/
    ├── detail-pages/
    └── promo/
```

각 agent의 역할/입력/출력/반려조건은 해당 스크립트 상단 docstring과 설계서 1번 섹션 표를 참고하세요.

## 파이프라인 순서 (설계서 2번 섹션)

1. `sourcing` → 국가별 후보 10개
2. `compliance` → 규제 필터 (탈락분은 sourcing으로 반송)
3. `margin` → 마진 20% 미만 탈락 (Adjustment Rate 조정 후 1회 재시도)
4. `image` + `localization` (병렬)
5. `listing` → Global SKU=원가만 입력 → Mass Upload → 개별 Publish
6. `promo` + `distribution` (병렬)
7. `master_qa` → 전체 로그 검토 → 통과만 최종 승인, 문제 상품은 재작업 큐 등록

정지 조건: 3회 연속 반려되는 상품은 자동 재시도 중단, 사람 검토 큐로 이관.

## 다국가 확장 방침

SG 다음으로 신규 국가 상점을 빠르게 여는 것이 목표이며, 신규 국가는 "카테고리 무제한"으로
운영할 계획입니다. 단 이는 **사업 방침이지 법적 면제가 아닙니다.** SG의 HSA(뷰티), MY의
JAKIM(할랄)/NPRA(화장품) 사례처럼 어느 국가든 고유 규제가 있으므로, `rulebook/country_rules.json`의
`expansion_policy`에 정리된 순서(① 규제기관 리서치 → ② restricted_categories 채우기 →
③ 그 다음에야 카테고리 자유화)를 반드시 지킵니다. 규제 확인이 안 된 카테고리는
compliance-agent가 기본적으로 반려하도록 설계되어 있습니다 (미조사 카테고리에 대한 안전장치).

홍보 채널도 SG/MY처럼 국가별 노하우가 없는 상태로 시작하므로, `agents/distribution.py`에 정리된
공통 원칙(숏폼 영상형/로컬 커뮤니티형/비주얼 채널 3유형 우선 배정 후 실사용 데이터로 교체)을
기본값으로 삼습니다. 홍보 콘텐츠 포맷도 카드뉴스/인포그래픽에 한정하지 않고 `agents/promo.py`의
`ContentFormat`에 채널에 맞는 포맷을 추가해가는 방식입니다.

## 실제 가동까지 남은 단계

1. **MY 셀러센터 계정 개설 확정** — 아직 미확인. 미개설 시 MY 관련 전 단계가 진행 불가.
2. **브라우저 자동화 방식 결정** — Playwright/Selenium 직접 조작 vs 쇼피 Open API. `listing.py`,
   `distribution.py`의 실제 구현이 이 결정에 따라 완전히 달라짐.
3. **크리덴셜/API 키 확보**
   - 이미지 생성 API (예: OpenAI Images / Stability AI 등 택1)
   - 번역/카피라이팅 API 또는 LLM
   - GitHub 업로드 토큰 (기존 토큰은 룰북 v2 기준 revoke 대상 — 새 토큰 필요)
   - 쇼피 셀러센터 로그인/2FA 처리 방식
   - SNS 채널별 API (Threads, Meta Graph API, TikTok API 등) 또는 수동 게시로 범위 축소
   - 도매꾹/쿠팡/네이버 접근 방식 (공식 API 유무 확인, 계정/세션)
4. **`rulebook/category_master.json` 보강** — 현재 SG 2개 카테고리만 검증됨. 새 카테고리 추가 시
   HiddenCatProps / Pre-order DTS Range / Attribute value mapping / Template 4행을 전부 파싱해서 채울 것
   (마스터 원칙 #1, 운영 룰북 v2).
5. **마진계산기 공식 재설계** — Global SKU Price = 원가만 입력, Market Price Adjustment Rate로
   마진 조정하는 방식으로 전면 재검증 (기존 "판매가=원가" 전제는 틀렸던 것으로 확인됨).
6. **각 agent 스텁의 실제 로직 구현 + 단위 테스트** — `NotImplementedError`를 실제 구현으로 교체.
7. **1개 상품으로 사람 검토 하 E2E 드라이런** — 전 단계를 사람이 한 단계씩 확인하며 실행.
8. **무인 자동화 활성화 + 모니터링/알림 체계 구축** — master_qa 리포트를 사람에게 알리는 채널 연결.

## 참고 문서

- 설계서: `kdailymart_자동화_파이프라인_설계서_v1.md` (파이프라인 구조, 에이전트 구성)
- 운영 룰북 v2: Day 1 실전 검증 내용 (Global SKU=원가 공식, SG 4대 규제군, 검증된 카테고리 ID,
  실패 이력 등). 이 저장소의 draft 데이터는 대부분 이 문서에서 가져왔습니다.
