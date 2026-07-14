"""compliance-agent

역할: 국가별 금지/규제 카테고리 필터 (rulebook/country_rules.json 대조)
입력: 후보 리스트(sourcing-agent 출력), 판매국
출력: 승인/반려 + 사유
반려 조건: HSA/NEA/Safety Mark/CCP/할랄/NPRA 등 국가별 규제 저촉

파이프라인 순서: 2단계. 탈락분은 sourcing-agent로 반송하여 대체 후보를 요청한다.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sourcing import SourcingCandidate

Country = Literal["SG", "MY"]

RULEBOOK_PATH = Path(__file__).resolve().parent.parent / "rulebook" / "country_rules.json"


@dataclass
class ComplianceResult:
    candidate: SourcingCandidate
    approved: bool
    reason: str
    matched_rule_key: str | None = None


def load_country_rules(path: Path = RULEBOOK_PATH) -> dict:
    """rulebook/country_rules.json을 로드한다. (이 함수 자체는 실행 가능하지만, 아래 판정 로직은 미구현)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# candidate.category_hint(자유 텍스트)를 country_rules.json의 restricted_categories.key로 매핑하기
# 위한 v0 키워드 분류기. 정교한 분류기(임베딩/LLM 기반)가 생기기 전까지 쓰는 보수적 근사치다.
# 키워드가 안 걸리면 안전 카테고리 매칭도 시도하고, 그마저 없으면 기본 반려(default-deny)한다 -
# expansion_policy에서 명시한 "미조사 카테고리는 기본 반려" 원칙을 그대로 코드로 옮긴 것이다.
RESTRICTED_KEYWORDS: dict[Country, dict[str, list[str]]] = {
    "SG": {
        "health_beauty": ["뷰티", "화장품", "스킨케어", "마스크팩", "크림", "cosmetic", "beauty", "skincare", "mask pack"],
        "pesticides_insect_repellent": ["살충제", "방충제", "모기", "insect repellent", "pesticide"],
        "electronics": ["전자", "가전", "충전기", "배터리", "electronic", "charger", "battery"],
        "pet_food": ["펫푸드", "반려동물 사료", "강아지 간식", "고양이 간식", "pet food"],
        "tobacco": ["담배", "전자담배", "tobacco", "cigarette", "vape"],
    },
    "MY": {
        "food_beverage_non_halal": ["식품", "음료", "스낵", "간식", "김", "차", "food", "snack", "beverage", "drink"],
        "cosmetics": ["뷰티", "화장품", "스킨케어", "마스크팩", "cosmetic", "beauty", "skincare"],
    },
}

SAFE_KEYWORDS: dict[Country, dict[str, dict]] = {
    "SG": {
        "fashion": {"keywords": ["패션", "의류", "옷", "신발", "양말", "fashion", "clothing", "shoes", "socks"], "label_match": "패션 (의류"},
        "fashion_accessories": {"keywords": ["헤어핀", "헤어클립", "가방", "주얼리", "액세서리", "hair clip", "hair pin", "jewelry", "bag"], "label_match": "패션 액세서리"},
        "home_living": {"keywords": ["홈리빙", "주방", "수납", "생활용품", "home", "kitchen", "storage"], "label_match": "홈&리빙"},
        "stationery_hobby": {"keywords": ["문구", "취미", "stationery", "hobby"], "label_match": "문구"},
        "processed_food": {"keywords": ["가공식품", "포장 스낵", "김", "seaweed", "snack"], "label_match": "가공식품"},
        "sports": {"keywords": ["스포츠", "운동", "sports", "fitness"], "label_match": "스포츠"},
        "toys": {"keywords": ["완구", "장난감", "toy"], "label_match": "완구"},
    },
    "MY": {
        "fashion": {"keywords": ["패션", "의류", "옷", "신발", "양말", "fashion", "clothing", "shoes", "socks"], "label_match": "패션"},
        "home_living": {"keywords": ["홈리빙", "주방", "수납", "home", "kitchen", "storage"], "label_match": "홈리빙"},
        "stationery_hobby": {"keywords": ["문구", "취미", "stationery", "hobby"], "label_match": "문구"},
        "sports": {"keywords": ["스포츠", "운동", "sports", "fitness"], "label_match": "스포츠"},
        "toys": {"keywords": ["완구", "장난감", "toy"], "label_match": "완구"},
    },
}


def check_candidate(candidate: SourcingCandidate, country: Country, rules: dict) -> ComplianceResult:
    """후보 상품 하나를 국가별 규제와 대조하여 승인/반려를 판정한다 (v0 키워드 분류기).

    판정 순서:
    1. category_hint가 RESTRICTED_KEYWORDS에 걸리면 즉시 반려 (규제 사유는 country_rules.json에서 조회).
    2. 안 걸리면 SAFE_KEYWORDS로 안전 카테고리 매칭을 시도하고, country_rules.json의 해당
       safe_categories 항목이 verified=true일 때만 승인한다 (MY처럼 verified=false인 국가는
       키워드가 맞아도 아직 승인하지 않는다 - expansion_policy 3번 항목).
    3. 둘 다 안 걸리면 기본 반려(unknown_regulation_unverified) - "조사 안 된 카테고리는 반려"
       원칙(expansion_policy)의 코드 구현이다.

    TODO(정식 운영 전 필요 사항):
    - 이 키워드 매칭은 v0 근사치다. 실제 후보가 쌓이면 "마스크팩"처럼 뻔한 케이스 밖의 애매한
      상품(예: 손소독제 - 화장품/의약외품 경계)이 나올 텐데, 이런 건 키워드로 못 거른다.
      임베딩 기반 분류 또는 LLM 판단으로 교체하거나, 최소한 애매하면 사람 검수로 넘기는
      confidence 임계치를 추가해야 한다.
    - MY 할랄 인증 여부는 이 함수가 판정하지 않는다 (food_beverage_non_halal 키워드에 걸리면
      무조건 반려). 할랄 인증서가 실제로 확인된 상품을 예외 승인하려면 candidate에
      halal_certified 같은 필드가 추가되고, 그 근거(인증서 이미지/번호)를 사람이 확인하는
      절차가 먼저 있어야 한다.
    - country_rules.json 자체가 draft이므로, 키워드/카테고리가 늘어날 때마다
      RESTRICTED_KEYWORDS/SAFE_KEYWORDS도 함께 갱신해야 한다 (둘이 따로 놀면 분류가 틀어짐).
    """
    hint = candidate.category_hint.lower()

    for restricted_key, keywords in RESTRICTED_KEYWORDS.get(country, {}).items():
        if any(kw.lower() in hint for kw in keywords):
            rule = next(
                (r for r in rules["countries"][country]["restricted_categories"] if r["key"] == restricted_key),
                None,
            )
            reason = rule["reason"] if rule else f"{restricted_key} 규제 카테고리로 분류됨"
            return ComplianceResult(candidate=candidate, approved=False, reason=reason, matched_rule_key=restricted_key)

    for safe_key, spec in SAFE_KEYWORDS.get(country, {}).items():
        if any(kw.lower() in hint for kw in spec["keywords"]):
            entry = next(
                (s for s in rules["countries"][country]["safe_categories"] if spec["label_match"] in s["label"]),
                None,
            )
            if entry and entry.get("verified"):
                return ComplianceResult(
                    candidate=candidate, approved=True,
                    reason=f"안전 카테고리로 확인됨: {entry['label']}", matched_rule_key=safe_key,
                )
            return ComplianceResult(
                candidate=candidate, approved=False,
                reason=f"카테고리는 매칭되었으나 이 국가에서 아직 검증되지 않음(verified=false): {safe_key}",
                matched_rule_key=safe_key,
            )

    return ComplianceResult(
        candidate=candidate, approved=False,
        reason="규제 확인이 안 된 카테고리는 기본 반려 (expansion_policy 참고 - 조사 후 재시도)",
        matched_rule_key=None,
    )


def filter_candidates(candidates: list[SourcingCandidate], country: Country) -> list[ComplianceResult]:
    """후보 리스트 전체를 국가별로 필터링한다."""
    rules = load_country_rules()
    return [check_candidate(c, country, rules) for c in candidates]
