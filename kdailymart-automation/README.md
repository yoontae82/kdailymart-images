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
    **실제 쇼피 대용량업로드 템플릿 파일에 실제 값을 채운 진짜 .xlsx 파일을 생성**한다 (Phase 1 방식,
    아래 "등록 방식" 참고. 실제 템플릿으로 검증 완료 - 2026-07-16). `mass_upload()`/`publish_individually()`
    (브라우저자동화로 직접 올리는 Phase 2)는 Phase 1이 병목으로 확인되기 전까지는 스텁으로 남겨둠.
- **아직 스텁** (`NotImplementedError`, 아래 크리덴셜/결정이 필요): `sourcing.py`, `image.py`,
  `localization.py`, `exposure.py`, `promo.py`, `distribution.py`, `cs.py`, `master_qa.py`
- 크리덴셜/API 키 연결 (도매꾹/쿠팡/네이버, 이미지 생성, 번역, SNS 채널 등) — 전혀 없음. (쇼피 셀러센터
  로그인은 Phase 1 방식 채택으로 당장은 불필요.)
- `rulebook/country_rules.json`은 사람이 검수해야 하는 **초안(draft)** 상태입니다.
  `rulebook/category_master.json`은 실제 쇼피 템플릿(Fashion Accessories > Hair Accessories 전체
  6개 카테고리)을 파싱해 채웠고, Face Mask 카테고리까지 총 7개 카테고리가 있습니다. 그 외
  카테고리로 확장하려면 그 카테고리가 포함된 대용량업로드 템플릿을 셀러센터에서 새로 받아 파싱해야 함.
- ⚠️ **Global SKU Price(K 컬럼)의 통화/공식이 아직 확인 안 됨** — 아래 "확인 필요" 섹션 참고. 실제
  금액을 입력하기 전에 반드시 짚고 넘어가야 하는 사항입니다.

즉, **지금 이 저장소를 그대로 실행해도 아무 상품도 등록되지 않습니다** (사람이 파일을 업로드하는
마지막 클릭이 남아있고, K컬럼 통화 확인도 필요). 하지만 compliance/margin/listing(실제 템플릿 파일
생성)까지는 실제로 동작하는 상태이고, 나머지(소싱/이미지/카피/CS/노출)는 여전히 크리덴셜과 결정을
기다리는 스텁입니다.

## ⚠️ 확인 필요: Global SKU Price(K 컬럼) 통화/공식

실제 쇼피 대용량업로드 템플릿(2026-07-16 다운로드)의 K컬럼 가이드 문구를 그대로 인용하면:

> Price of Shop SKU = Global SKU Price × Marketplace Exchange Rate × Market Price Adjustment Ratio + Hidden Price
> Input your Global SKU Price here in **RMB currency**. Only positive numbers are accepted.

이건 두 가지 지점에서 이 프로젝트의 기존 전제(운영 룰북 v2)와 다릅니다.

1. **통화가 RMB(위안)로 명시되어 있음.** 운영 룰북 v2와 이 저장소의 `country_rules.json`은 지금까지
   "Base Currency: KRW, Global SKU Price = 원가(KRW)"를 전제로 했습니다. 템플릿 문구가 모든
   크로스보더 셀러에게 공통으로 뜨는 일반 안내문이라 KRSC(한국 셀러) 계정에는 실제로 적용 안 될
   수도 있지만, **확인 없이 그냥 KRW 숫자를 넣으면 안 됩니다.**
2. **공식이 다름.** 룰북 v2는 "Adjustment Rate 100%=마진0%, 130%=마진30%"라는 단순 관계로
   설명했는데, 실제 템플릿은 `Global SKU Price × Exchange Rate × Adjustment Ratio + Hidden Price`로
   되어 있어 곱셈 이후 **덧셈 항("Hidden Price")이 하나 더 있습니다.** `margin.py`의 현재 공식은
   룰북 v2 쪽(단순 관계)을 구현한 것이라, 이 "Hidden Price" 항을 반영하지 않았습니다.

**실제 판매가 시작되기 전에 사람이 직접 쇼피 셀러센터에서 소액(예: 1개) 등록으로 실제 노출가가
의도한 대로 나오는지 확인해야 합니다.** 그전까지 `margin.py`가 계산한 숫자는 "이 정도면 여유
있어 보인다"는 근사치로만 취급하고, 그대로 믿고 대량 등록하면 안 됩니다 (Day 1에 이미 한 번
이 문제로 실제 노출가가 의도한 것보다 훨씬 높게 나온 사례가 있습니다).

## 등록 방식: Phase 1 (사람이 업로드) vs Phase 2 (완전 자동화)

쇼피 로그인 자동화(브라우저자동화/Open API)는 크리덴셜·2FA·플랫폼 승인 절차가 걸려있어 당장
가장 큰 병목이었습니다. 그래서 1단계는 로그인을 아예 자동화하지 않는 방식으로 갑니다:

1. 파이프라인이 상품 데이터를 조립해 쇼피 "대용량업로드" 형식의 `.xlsx` 파일을 만든다
   (`listing.build_mass_upload_row` + `listing.generate_mass_upload_file`, 실구현 완료,
   **실제 쇼피 템플릿 파일에 채워서 검증 완료**)
2. **사람이** 그 파일을 쇼피 셀러센터에 직접 첨부해서 업로드하고, 개별 Publish 버튼을 누른다
3. 이 수동 단계 자체가 병목이 되면 (예: 매일 10개씩 반복하기 번거로워지면) 그때 브라우저자동화
   Phase 2(`mass_upload`/`publish_individually`)를 고려한다

`generate_mass_upload_file()`은 `template_path`로 실제 쇼피 대용량업로드 템플릿(.xlsx)을 받으면
그 파일의 "Template" 시트 7행부터 값을 채워 넣는다 (다른 시트/헤더는 그대로 보존됨). 이 템플릿
파일 자체가 손상된 sheetView 속성(`activePane="bottom_left"`, OOXML 표준이 아님)을 갖고 있어서
그냥 openpyxl로 열면 에러가 나는데, `_load_workbook_tolerant()`가 이걸 자동으로 감지해서 고친
사본으로 여니 신경 쓸 필요 없음. `template_path` 없이 호출하면 컬럼 문자만으로 새 엑셀을 만드는
데모 모드로 동작한다 (검증용, 실제 업로드 금지).

## 폴더 구조

```
kdailymart-automation/
├── rulebook/
│   ├── country_rules.json       # SG/MY 금지카테고리, 수수료 가정 (draft)
│   └── category_master.json     # 카테고리ID, 속성 허용값 (SG 7개 카테고리 - Hair Accessories 6종 실템플릿 파싱 + Face Mask)
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

1. **Global SKU Price(K 컬럼) 통화/공식 확인** — 위 "확인 필요" 섹션. 실제 등록 전 최우선.
2. **MY 셀러센터 계정 개설 확정** — 아직 미확인. 미개설 시 MY 관련 전 단계가 진행 불가.
3. **소싱 방식** — 도매꾹/쿠팡/네이버 자동 접근 vs 당분간 사람이 후보를 직접 찾아 전달하는 수동 방식.
4. **이미지 가공 방식** — AI 이미지 생성 API 연결 vs 사람이 편집한 이미지를 GitHub에 업로드
   (업로드 자체는 이미 가능한 토큰 있음).
5. **카테고리 확장** — 지금은 SG의 Hair Accessories 6종 + Face Mask 1종(7개)만 커버됨. 다른
   카테고리로 넓히려면 그 카테고리가 포함된 대용량업로드 템플릿을 셀러센터에서 새로 받아야 함.
6. **1개 상품으로 사람 검토 하 E2E 드라이런** — 파일 생성까지는 검증됐으니, 이제 실제로 사람이
   그 파일을 쇼피에 업로드해서 Publish까지 되는지 1개 상품으로 확인.
7. **CS/노출/홍보 반자동 운영 시작** — 크리덴셜 없이 사람이 정보를 전달하고 이 저장소의 로직이
   보조하는 방식으로 먼저 굴려보기 (README "팀 구조 ↔ agent 매핑" 참고).
8. **각 agent 스텁의 실제 로직 구현 확장 + 무인 자동화 전환** — 위 단계들이 안정화된 뒤,
   반자동 단계를 하나씩 자동화로 옮기고 master_qa 리포트를 사람에게 알리는 채널 연결.

## 참고 문서

- 설계서: `kdailymart_자동화_파이프라인_설계서_v1.md` (파이프라인 구조, 에이전트 구성)
- 운영 룰북 v2: Day 1 실전 검증 내용 (Global SKU=원가 공식, SG 4대 규제군, 검증된 카테고리 ID,
  실패 이력 등). 이 저장소의 draft 데이터는 대부분 이 문서에서 가져왔습니다.
