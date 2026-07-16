# kdailymart-automation

kdailymart SG(운영중)/MY(신규) 매장의 "매일 10개 상품 자동화" 파이프라인 스캐폴딩.

## 현재 상태: 크리덴셜 없이 되는 로직만 실구현, 실제 판매는 아직 불가

이 폴더는 [`kdailymart_자동화_파이프라인_설계서_v1.md`]의 5번 섹션 구조를 그대로 코드로
옮긴 뼈대에서 출발해, 외부 API/계정 없이도 동작 가능한 부분부터 하나씩 실구현하는 중입니다.

- **실구현 완료** (외부 크리덴셜 불필요, 실제 동작함):
  - `compliance.py` — 키워드 기반 v0 분류기로 규제 카테고리 승인/반려 판정 (`country_rules.json` 대조)
  - `margin.py` — Adjustment Rate 공식으로 순마진 계산/재시도 (SG는 실증됨, MY는 `formula_verified=False`로
    표시되는 보수적 추정치)
  - `listing.py`의 `build_mass_upload_row()` / `generate_mass_upload_file()` — 쇼피 로그인 자동화 없이,
    사람이 셀러센터에 직접 업로드할 **대용량업로드 .xlsx 파일을 실제로 생성**한다 (Phase 1 방식,
    아래 "등록 방식" 참고). `mass_upload()`/`publish_individually()`(브라우저자동화로 직접 올리는
    Phase 2)는 Phase 1이 병목으로 확인되기 전까지는 스텁으로 남겨둠.
- **아직 스텁** (`NotImplementedError`, 아래 크리덴셜/결정이 필요): `sourcing.py`, `image.py`,
  `localization.py`, `exposure.py`, `promo.py`, `distribution.py`, `cs.py`, `master_qa.py`
- 크리덴셜/API 키 연결 (도매꾹/쿠팡/네이버, 이미지 생성, 번역, SNS 채널 등) — 전혀 없음. (쇼피 셀러센터
  로그인은 Phase 1 방식 채택으로 당장은 불필요.)
- `rulebook/country_rules.json`, `rulebook/category_master.json`은 사람이 검수해야 하는 **초안(draft)**
  상태입니다 (실제 실행 전에 재검증 필요). `category_master.json`에 SG 2개 카테고리만 채워져 있어,
  그 외 카테고리로 상품을 등록하려면 실제 쇼피 대용량업로드 템플릿을 먼저 파싱해서 채워야 함.

즉, **지금 이 저장소를 그대로 실행해도 아무 상품도 등록되지 않습니다.** compliance/margin/listing(파일
생성)은 실제로 돌아가지만, 그 앞뒤(소싱/이미지/카피/CS/노출)는 여전히 크리덴셜과 결정을 기다리는
스텁이고, 생성된 파일을 실제로 쇼피에 올리는 마지막 클릭은 여전히 사람이 합니다.

## 등록 방식: Phase 1 (사람이 업로드) vs Phase 2 (완전 자동화)

쇼피 로그인 자동화(브라우저자동화/Open API)는 크리덴셜·2FA·플랫폼 승인 절차가 걸려있어 당장
가장 큰 병목이었습니다. 그래서 1단계는 로그인을 아예 자동화하지 않는 방식으로 갑니다:

1. 파이프라인이 상품 데이터를 조립해 쇼피 "대용량업로드" 형식의 `.xlsx` 파일을 만든다
   (`listing.build_mass_upload_row` + `listing.generate_mass_upload_file`, 실구현 완료)
2. **사람이** 그 파일을 쇼피 셀러센터에 직접 첨부해서 업로드하고, 개별 Publish 버튼을 누른다
3. 이 수동 단계 자체가 병목이 되면 (예: 매일 10개씩 반복하기 번거로워지면) 그때 브라우저자동화
   Phase 2(`mass_upload`/`publish_individually`)를 고려한다

⚠️ 지금 `generate_mass_upload_file()`은 템플릿 파일 없이 컬럼 문자만으로 새 엑셀을 만드는
**데모 모드**다. 실제 쇼피 대용량업로드 템플릿(.xlsx)을 셀러센터에서 다운받아 넘겨주면
그 파일 위에 값만 채우는 방식으로 바꿀 수 있고, 이게 되어야 실제로 업로드 가능한 파일이 나온다.

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
│   ├── exposure.py              # 노출/랭킹 모니터링 + 원인 후보 산출
│   ├── promo.py                 # 홍보 콘텐츠 제작
│   ├── distribution.py          # 채널 배정/스케줄링 (distribution-planner)
│   ├── cs.py                    # 고객 문의 응대/에스컬레이션
│   └── master_qa.py             # 전체 QA 게이트 + 운영 오버사이트 + 일일 리포트
├── data/
│   ├── candidates/               # 일자별 후보 리스트
│   ├── listed/                   # 등록 완료 상품 로그
│   └── exposure/                 # 노출 점검 로그
├── logs/
│   ├── master-qa/                # 일일 QA 리포트 + 운영 오버사이트 리포트
│   └── cs/                       # CS 응대 로그
└── outputs/
    ├── detail-pages/
    └── promo/
```

각 agent의 역할/입력/출력/반려조건은 해당 스크립트 상단 docstring과 설계서 1번 섹션 표를 참고하세요.

## 팀 구조 ↔ agent 매핑

실제 조직은 5개 팀(기획/디자인/개발/홍보/CS) + 이를 총괄하는 마스터로 운영할 계획입니다.
이 스캐폴딩의 파일과 매핑하면:

| 팀 | 역할 | 담당 agent |
|---|---|---|
| 기획팀 | 쿠팡/네이버 등에서 동남아 트렌드 상품 소싱·선정, 노출 저조 시 대체상품 검토 | `sourcing.py` (+ `exposure.py`의 원인 후보를 받아 대응) |
| 디자인팀 | 판매국 언어로 상세페이지 제작 (누끼/착용샷 + 카피) | `image.py`, `localization.py` |
| 개발팀 | 매일 만들어지는 상품 업로드 + 노출 체크 | `listing.py`, `exposure.py` |
| 홍보팀 | 카드뉴스/숏폼 등 홍보 콘텐츠 제작, 국가별 채널 리서치(기획팀과 협업) | `promo.py`, `distribution.py` |
| CS팀 | 구매자 문의 응대, 분쟁 소지 있는 건은 사람에게 이관 | `cs.py` |
| 마스터 | 5개 팀 전체 로그를 대조해 오류를 잡고 수정지시 (신규 상품 QA + 상시 운영 오버사이트 2개 트랙) | `master_qa.py` |

`compliance.py`/`margin.py`는 특정 팀 소속이라기보다, 기획팀이 상품을 고른 직후 마스터 룰북
기준으로 통과시켜야 하는 자동 관문(gate)에 가깝습니다.

## 파이프라인 순서 (설계서 2번 섹션)

1. `sourcing` → 국가별 후보 10개
2. `compliance` → 규제 필터 (탈락분은 sourcing으로 반송)
3. `margin` → 마진 20% 미만 탈락 (Adjustment Rate 조정 후 1회 재시도)
4. `image` + `localization` (병렬)
5. `listing` → Global SKU=원가만 입력 → Mass Upload → 개별 Publish
6. `promo` + `distribution` (병렬)
7. `master_qa` → 전체 로그 검토 → 통과만 최종 승인, 문제 상품은 재작업 큐 등록

정지 조건: 3회 연속 반려되는 상품은 자동 재시도 중단, 사람 검토 큐로 이관.

위 7단계는 "오늘 만든 상품"을 처리하는 트랙입니다. 이와 별개로 **상시 운영 트랙**이 있습니다:
- `cs` — 문의가 들어올 때마다 응대 (일일 파이프라인과 무관하게 계속 실행)
- `exposure` — 등록된 상품이 잘 노출되는지 주기적으로 점검, 저조하면 기획팀/홍보팀에 전달
- `master_qa` — 두 트랙 전부(신규 상품 QA + 운영 오버사이트)를 총괄 감시

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
