import html as html_lib
import re
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

from django.core.management.base import BaseCommand


BASE = "https://www.thekkf.or.kr"

LIST_URL = (
    BASE
    + "/new_home/03_kkf_service/"
      "03_approval_2.php?gid={gid}"
)

DETAIL_URL = (
    BASE
    + "/new_home/03_kkf_service/"
      "03_approval_3.php?gid={gid}&idx={idx}"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": (
        "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    ),
}


def clean_text(value):
    if not value:
        return ""

    value = re.sub(
        r"<br\s*/?>",
        "\n",
        value,
        flags=re.I,
    )

    value = re.sub(
        r"</(?:p|div|li|tr|td|th|h\d)>",
        "\n",
        value,
        flags=re.I,
    )

    value = re.sub(
        r"<[^>]+>",
        " ",
        value,
    )

    value = html_lib.unescape(value)
    value = value.replace("\xa0", " ")

    lines = []

    for line in value.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


def one_line(value):
    return re.sub(
        r"\s+",
        " ",
        clean_text(value),
    ).strip()


def fetch(url, referer=None, timeout=25):
    headers = dict(HEADERS)

    if referer:
        headers["Referer"] = referer

    req = urllib.request.Request(
        url,
        headers=headers,
    )

    with urllib.request.urlopen(
        req,
        timeout=timeout,
    ) as response:

        raw = response.read()

        status = response.status

    # 실제 대상 사이트는 CP949가 가장 안정적
    candidates = [
        "cp949",
        "euc-kr",
        "utf-8",
    ]

    best = None
    best_score = -1

    for encoding in candidates:
        try:
            decoded = raw.decode(encoding)

        except UnicodeDecodeError:
            continue

        score = len(
            re.findall(r"[가-힣]", decoded)
        )

        if score > best_score:
            best = decoded
            best_score = score

    if best is None:
        best = raw.decode(
            "cp949",
            errors="replace",
        )

    return status, best


def attr(tag, name):
    m = re.search(
        rf'\b{name}\s*=\s*["\']([^"\']*)["\']',
        tag,
        re.I,
    )

    if not m:
        return ""

    return html_lib.unescape(
        m.group(1).strip()
    )


def parse_group_name(page, gid=None):
    """
    현재 선택된 그룹의 실제 제목/설명을 추출한다.

    구조:
      <h4>1그룹</h4>
      <div class="mt20">
        <p>쉽독 , 캐틀독 ...</p>
        <p>Sheepdogs and Cattledogs ...</p>
    """

    if gid:
        pattern = re.compile(
            rf'<h4\b[^>]*>\s*{gid}\s*그룹\s*</h4>'
            rf'\s*<div\b[^>]*class=["\'][^"\']*mt20[^"\']*["\'][^>]*>'
            rf'\s*<p\b[^>]*>(.*?)</p>'
            rf'\s*<p\b[^>]*>(.*?)</p>',
            re.I | re.S,
        )

        m = pattern.search(page)

        if m:
            ko = one_line(m.group(1))
            en = one_line(m.group(2))

            if ko and en:
                return f"{ko} / {en}"

            return ko or en

    return ""


def parse_list(page, gid, list_url):
    """
    KKF 목록의 실제 견종 카드 구조에서 직접 추출한다.

    구조:
      <li class="w25p">
        <a href="03_approval_3.php?gid=1&idx=2">
          <div class="li_img">
            <img src="...">
          </div>
          <div class="li_txt">
            <p>한글 견종명</p>
            <p>ENGLISH BREED NAME</p>
          </div>
        </a>
      </li>

    이름은 상세페이지 주변 텍스트에서 추측하지 않는다.
    목록 카드의 li_txt를 원본값으로 사용한다.
    """

    results = []
    seen = set()

    li_pattern = re.compile(
        r'<li\b[^>]*class=["\'][^"\']*w25p[^"\']*["\'][^>]*>'
        r'(.*?)'
        r'</li>',
        re.I | re.S,
    )

    for li_body in li_pattern.findall(page):

        link_match = re.search(
            r'<a\b[^>]*href=["\']'
            r'([^"\']*03_approval_3\.php[^"\']*)'
            r'["\'][^>]*>',
            li_body,
            re.I | re.S,
        )

        if not link_match:
            continue

        href = html_lib.unescape(
            link_match.group(1)
        )

        absolute_url = urllib.parse.urljoin(
            list_url,
            href,
        )

        parsed_url = urllib.parse.urlparse(
            absolute_url
        )

        query = urllib.parse.parse_qs(
            parsed_url.query
        )

        try:
            item_gid = int(
                query.get("gid", ["0"])[0]
            )
        except Exception:
            continue

        # 다른 그룹 링크가 섞이는 경우 방지
        if item_gid != gid:
            continue

        try:
            idx = str(
                int(
                    query.get(
                        "idx",
                        [""],
                    )[0]
                )
            )
        except Exception:
            continue

        if idx in seen:
            continue

        txt_match = re.search(
            r'<div\b[^>]*class=["\'][^"\']*li_txt[^"\']*["\'][^>]*>'
            r'(.*?)'
            r'</div>',
            li_body,
            re.I | re.S,
        )

        if not txt_match:
            continue

        names = re.findall(
            r'<p\b[^>]*>(.*?)</p>',
            txt_match.group(1),
            re.I | re.S,
        )

        names = [
            one_line(name)
            for name in names
            if one_line(name)
        ]

        if not names:
            continue

        name_ko = names[0]

        name_en = (
            names[1]
            if len(names) >= 2
            else ""
        )

        img_match = re.search(
            r'<img\b[^>]*src=["\']([^"\']+)["\']',
            li_body,
            re.I | re.S,
        )

        image_url = ""

        if img_match:
            image_url = urllib.parse.urljoin(
                list_url,
                html_lib.unescape(
                    img_match.group(1)
                ),
            )

        seen.add(idx)

        results.append({
            "gid": gid,
            "idx": idx,

            # 목록에서 확정한 이름
            "name_ko": name_ko,
            "name_en": name_en,

            "detail_url": absolute_url,
            "image_url": image_url,
            "anchor_text": "",
            "around_text": "",
        })

    return results



def extract_table_pairs(page):
    """
    상세페이지의 표에서
    TH/TD 또는 연속 TD 형태의 label/value를 수집한다.
    """

    pairs = {}

    rows = re.findall(
        r"<tr\b[^>]*>(.*?)</tr>",
        page,
        re.I | re.S,
    )

    for row in rows:

        cells = re.findall(
            r"<(?:th|td)\b[^>]*>(.*?)</(?:th|td)>",
            row,
            re.I | re.S,
        )

        values = [
            clean_text(cell)
            for cell in cells
        ]

        values = [
            value
            for value in values
            if value
        ]

        if len(values) < 2:
            continue

        # 2개씩 label/value로 검사
        for i in range(0, len(values) - 1):

            label = one_line(values[i])
            value = one_line(values[i + 1])

            keys = [
                "FCI",
                "원산지",
                "용도",
                "분류",
                "체고",
            ]

            if any(
                key.lower() in label.lower()
                for key in keys
            ):
                pairs[label] = value

    return pairs


def extract_heading_sections(page):
    """
    상세 설명의 제목을 기준으로 섹션을 자른다.

    사이트 HTML 구조가 일부 달라져도 버티도록
    전체 텍스트 기반으로 한 번 더 파싱한다.
    """

    text = clean_text(page)

    labels = [
        "용도",
        "연혁",
        "일반외모",
        "성격 / 습성",
        "성격/습성",
        "성격",
        "두부",
        "목",
        "몸통",
        "꼬리",
        "사지",
        "걷는 모양",
        "보행",
        "피모",
        "크기",
        "결점",
        "실격",
    ]

    # 긴 라벨 먼저
    labels = sorted(
        labels,
        key=len,
        reverse=True,
    )

    escaped = "|".join(
        re.escape(x)
        for x in labels
    )

    pattern = re.compile(
        rf"(?m)^\s*({escaped})\s*$"
    )

    matches = list(
        pattern.finditer(text)
    )

    sections = defaultdict(list)

    for i, match in enumerate(matches):

        label = match.group(1).strip()

        start = match.end()

        end = (
            matches[i + 1].start()
            if i + 1 < len(matches)
            else len(text)
        )

        value = text[start:end].strip()

        if value:
            sections[label].append(value)

    return sections


def first_section(sections, *names):
    for name in names:

        values = sections.get(name)

        if values:
            return values[0].strip()

    return ""


def parse_detail(page, item):
    text = clean_text(page)

    pairs = extract_table_pairs(page)
    sections = extract_heading_sections(page)

    # FCI 표준번호
    fci_no = ""

    m = re.search(
        r"FCI\s*(?:스탠다드|STANDARD)?\s*"
        r"(?:No\.?|NO\.?)?\s*[:.]?\s*(\d+)",
        text,
        re.I,
    )

    if m:
        fci_no = m.group(1)

    # 견종명은 목록 카드에서 이미 확정했다.
    # 상세페이지 주변 문구로 다시 추측하지 않는다.
    name_ko = item.get("name_ko", "").strip()
    name_en = item.get("name_en", "").strip()

    origin = ""
    use = ""
    classification = ""
    height = ""

    for key, value in pairs.items():

        key_one = one_line(key)

        if "원산지" in key_one and not origin:
            origin = value

        elif "용도" in key_one and not use:
            use = value

        elif (
            "분류" in key_one
            or "FCI분류" in key_one.replace(" ", "")
        ) and not classification:
            classification = value

        elif "체고" in key_one and not height:
            height = value

    # 테이블 파싱 fallback
    if not origin:
        m = re.search(
            r"원산지\s*\n([^\n]+)",
            text,
        )
        if m:
            origin = one_line(m.group(1))

    if not use:
        m = re.search(
            r"용도\s*\n([^\n]+)",
            text,
        )
        if m:
            use = one_line(m.group(1))

    if not classification:
        m = re.search(
            r"FCI\s*분류\s*\n([^\n]+(?:\n[^\n]+)?)",
            text,
            re.I,
        )
        if m:
            classification = one_line(
                m.group(1)
            )

    if not height:
        m = re.search(
            r"체고\s*\n([^\n]+(?:\n[^\n]+)?)",
            text,
        )
        if m:
            height = one_line(
                m.group(1)
            )

    height_male = ""
    height_female = ""

    male = re.search(
        r"(?:수|수컷)\s*[:：]\s*"
        r"([^,\n/]+)",
        height,
    )

    female = re.search(
        r"(?:암|암컷)\s*[:：]\s*"
        r"([^,\n/]+)",
        height,
    )

    if male:
        height_male = one_line(
            male.group(1)
        )

    if female:
        height_female = one_line(
            female.group(1)
        )

    # 상세페이지 이미지 우선
    image_url = item["image_url"]

    images = re.findall(
        r'<img\b[^>]*src=["\']([^"\']+)["\']',
        page,
        re.I,
    )

    for src in images:

        src = html_lib.unescape(src)

        if (
            "kkf_file" in src.lower()
            or "dog" in src.lower()
        ):
            image_url = urllib.parse.urljoin(
                item["detail_url"],
                src,
            )
            break

    return {
        "name_ko": name_ko,
        "name_en": name_en,
        "fci_standard_no": fci_no,
        "origin": origin,
        "use": use,
        "classification": classification,
        "height": height,
        "height_male": height_male,
        "height_female": height_female,

        "purpose_detail": first_section(
            sections,
            "용도",
        ),

        "history": first_section(
            sections,
            "연혁",
        ),

        "appearance": first_section(
            sections,
            "일반외모",
        ),

        "temperament": first_section(
            sections,
            "성격 / 습성",
            "성격/습성",
            "성격",
        ),

        "head": first_section(
            sections,
            "두부",
        ),

        "neck": first_section(
            sections,
            "목",
        ),

        "body": first_section(
            sections,
            "몸통",
        ),

        "tail": first_section(
            sections,
            "꼬리",
        ),

        "limbs": first_section(
            sections,
            "사지",
        ),

        "gait": first_section(
            sections,
            "걷는 모양",
            "보행",
        ),

        "coat": first_section(
            sections,
            "피모",
        ),

        "size_detail": first_section(
            sections,
            "크기",
        ),

        "faults": first_section(
            sections,
            "결점",
        ),

        "disqualification": first_section(
            sections,
            "실격",
        ),

        "image_url": image_url,
    }


class Command(BaseCommand):

    help = (
        "KKF 1~10그룹 견종 데이터를 분석한다. "
        "기본값은 DRY RUN이며 DB를 수정하지 않는다."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--group",
            type=int,
            help="특정 FCI 그룹만 검사",
        )

        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="그룹당 상세페이지 검사 개수 제한",
        )

        parser.add_argument(
            "--delay",
            type=float,
            default=0.12,
            help="상세페이지 요청 사이 대기시간",
        )

    def handle(self, *args, **options):

        group_option = options["group"]
        limit = options["limit"]
        delay = options["delay"]

        if group_option:

            if group_option < 1 or group_option > 10:
                raise SystemExit(
                    "--group must be between 1 and 10"
                )

            groups = [group_option]

        else:
            groups = list(range(1, 11))

        all_items = []
        failures = []
        group_counts = {}
        group_names = {}

        self.stdout.write("")
        self.stdout.write("=" * 72)
        self.stdout.write(
            " KKF BREED COLLECTOR - DRY RUN"
        )
        self.stdout.write(
            " DATABASE WILL NOT BE MODIFIED"
        )
        self.stdout.write("=" * 72)

        for gid in groups:

            list_url = LIST_URL.format(
                gid=gid
            )

            self.stdout.write("")
            self.stdout.write(
                f"[GROUP {gid}] LIST REQUEST"
            )

            try:
                status, page = fetch(
                    list_url,
                    referer=BASE + "/",
                )

            except Exception as exc:
                failures.append(
                    (
                        gid,
                        "LIST",
                        "",
                        repr(exc),
                    )
                )

                self.stdout.write(
                    self.style.ERROR(
                        f"  LIST FAILED: {exc!r}"
                    )
                )

                continue

            group_name = parse_group_name(
                page,
                gid,
            )

            group_names[gid] = group_name

            items = parse_list(
                page,
                gid,
                list_url,
            )

            group_counts[gid] = len(items)

            self.stdout.write(
                f"  HTTP       = {status}"
            )

            self.stdout.write(
                f"  GROUP NAME = {group_name or '(not parsed)'}"
            )

            self.stdout.write(
                f"  BREEDS     = {len(items)}"
            )

            target_items = (
                items[:limit]
                if limit
                else items
            )

            for number, item in enumerate(
                target_items,
                1,
            ):

                try:
                    status, detail_page = fetch(
                        item["detail_url"],
                        referer=list_url,
                    )

                    parsed = parse_detail(
                        detail_page,
                        item,
                    )

                    record = {
                        **item,
                        **parsed,
                        "detail_http": status,
                        "group_name": group_name,
                    }

                    all_items.append(record)

                    flags = []

                    if parsed["name_ko"]:
                        flags.append("KO")

                    if parsed["name_en"]:
                        flags.append("EN")

                    if parsed["image_url"]:
                        flags.append("IMG")

                    if parsed["fci_standard_no"]:
                        flags.append("FCI")

                    if parsed["history"]:
                        flags.append("HISTORY")

                    if parsed["appearance"]:
                        flags.append("APPEARANCE")

                    self.stdout.write(
                        "  "
                        + f"{number:02d}/{len(target_items):02d} "
                        + f"idx={item['idx']:<4} "
                        + f"{parsed['name_ko'][:25] or '(NO NAME)'} "
                        + f"[{','.join(flags)}]"
                    )

                except Exception as exc:

                    failures.append(
                        (
                            gid,
                            item["idx"],
                            item["detail_url"],
                            repr(exc),
                        )
                    )

                    self.stdout.write(
                        self.style.ERROR(
                            "  "
                            + f"{number:02d}/{len(target_items):02d} "
                            + f"idx={item['idx']} "
                            + f"FAILED {exc!r}"
                        )
                    )

                if delay > 0:
                    time.sleep(delay)

        self.stdout.write("")
        self.stdout.write("=" * 72)
        self.stdout.write(
            " SUMMARY"
        )
        self.stdout.write("=" * 72)

        self.stdout.write("")
        self.stdout.write(
            "LIST COUNTS"
        )

        total_listed = 0

        for gid in groups:

            count = group_counts.get(
                gid,
                0,
            )

            total_listed += count

            self.stdout.write(
                f"GROUP {gid:2d} = "
                f"{count:3d} | "
                f"{group_names.get(gid, '')}"
            )

        self.stdout.write("")
        self.stdout.write(
            f"TOTAL LISTED       = {total_listed}"
        )

        self.stdout.write(
            f"DETAIL PARSED      = {len(all_items)}"
        )

        ids = [
            item["idx"]
            for item in all_items
        ]

        duplicate_ids = [
            idx
            for idx, count in Counter(ids).items()
            if count > 1
        ]

        self.stdout.write(
            f"DUPLICATE SOURCE ID= {len(duplicate_ids)}"
        )

        if duplicate_ids:
            self.stdout.write(
                "DUPLICATES = "
                + ", ".join(
                    duplicate_ids
                )
            )

        def count_field(name):
            return sum(
                1
                for item in all_items
                if item.get(name)
            )

        self.stdout.write("")
        self.stdout.write(
            "PARSE COVERAGE"
        )

        coverage_fields = [
            "name_ko",
            "name_en",
            "image_url",
            "fci_standard_no",
            "origin",
            "use",
            "classification",
            "height",
            "history",
            "appearance",
            "temperament",
            "head",
            "neck",
            "body",
            "tail",
            "limbs",
            "gait",
            "coat",
            "faults",
            "disqualification",
        ]

        for field in coverage_fields:

            count = count_field(field)

            percentage = (
                (count / len(all_items) * 100)
                if all_items
                else 0
            )

            self.stdout.write(
                f"{field:22} "
                f"{count:4d}/{len(all_items):4d} "
                f"{percentage:6.1f}%"
            )

        self.stdout.write("")
        self.stdout.write(
            f"FAILURES = {len(failures)}"
        )

        for failure in failures[:100]:
            self.stdout.write(
                "  "
                + " | ".join(
                    str(x)
                    for x in failure
                )
            )

        self.stdout.write("")
        self.stdout.write(
            "SAMPLE RECORDS"
        )

        for item in all_items[:10]:

            self.stdout.write("")
            self.stdout.write(
                f"[{item['gid']}/{item['idx']}] "
                f"{item['name_ko']} / "
                f"{item['name_en']}"
            )

            self.stdout.write(
                f"  FCI    = {item['fci_standard_no']}"
            )

            self.stdout.write(
                f"  ORIGIN = {item['origin']}"
            )

            self.stdout.write(
                f"  USE    = {item['use'][:100]}"
            )

            self.stdout.write(
                f"  HEIGHT = {item['height'][:100]}"
            )

            self.stdout.write(
                f"  IMAGE  = {item['image_url']}"
            )

            self.stdout.write(
                f"  URL    = {item['detail_url']}"
            )

        self.stdout.write("")
        self.stdout.write("=" * 72)
        self.stdout.write(
            " DRY RUN COMPLETE"
        )
        self.stdout.write(
            " DATABASE NOT MODIFIED"
        )
        self.stdout.write("=" * 72)
