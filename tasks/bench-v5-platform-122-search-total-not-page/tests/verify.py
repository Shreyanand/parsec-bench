#!/usr/bin/env python3
"""Harbor verifier for an authored bench scenario (contract schema "bench/v4").

Stdlib-only: this runs inside the task container, a bare ubi9 image with no
third-party packages and no network.

This file is the SOLE implementation of the bench scoring semantics. src/bench/
may build and validate an expected.json, but must never score -- a second
implementation is exactly the divergence trap that has bitten this repo three
times with hand-rolled fakes.

scripts/bench-new.py copies this file verbatim into every scenario. The tracked
original at src/bench/templates/verify.py is what the tests exercise, so the
tested file and the executed file cannot differ.
"""

import argparse
import json
import re
import sys
from pathlib import Path

CONTRACT_SCHEMA = "bench/v4"
DEFAULT_WEIGHTS = {"tool_calls": 0.4, "answer": 0.6}


def parse_transcript(text):
    """Read the stream-json transcript into (calls, answer, ok).

    Each call is (name, args). The extracted verifiers discarded `input`;
    grading arguments is the whole point of this one. Malformed lines are
    skipped so a truncated transcript still scores rather than crashing.
    """
    calls, answer, ok = [], "", False
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    args = block.get("input")
                    calls.append((
                        block.get("name", ""),
                        args if isinstance(args, dict) else {},
                    ))
        elif event.get("type") == "result":
            # Last result event wins: exactly one is written per run, but a
            # partial transcript plus a terminal error event can yield two.
            answer = event.get("result", "") or ""
            ok = event.get("subtype") == "success" and not event.get("is_error", False)
    return calls, answer, ok


# A canonical decimal spelling: no sign but "-", no leading zero, no exponent,
# no whitespace or underscores. float() accepts all of those, and would make
# "061840275391" a number equal to 61840275391.
_CANONICAL_NUMBER_RE = re.compile(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?")


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _canonical_number(text):
    """The number a string canonically spells, or None."""
    if not _CANONICAL_NUMBER_RE.fullmatch(text):
        return None
    # int for an integer spelling, so a 17-digit id is not rounded through
    # float(): float("100000000000000001") == 1e17.
    return float(text) if "." in text else int(text)


def _values_equal(want, got):
    """Compare two JSON scalars.

    Numbers compare numerically, and a numeric string equals a number: an
    agent that serialises job_id as "38627" still chose the right job, and the
    harness accepts it, so penalising that would measure serialisation style
    rather than tool use. Booleans are never equal to numbers, because
    failed_only=true and failed_only=1 are different intents.

    That tolerance applies only ACROSS types, and only to a canonical decimal
    spelling (defect 9, fixed 2026-10-09). Two strings compare exactly: a
    leading zero is part of an identifier, so "061840275391" is not
    "61840275391" and pool_id "06" is not "6" -- parsec builds the prefix
    pool-06- from one and pool-6- from the other. Before the fix both sides
    went through float(), which also accepted " 1 ", "1_000", "1e3" and "inf".
    """
    if isinstance(want, bool) or isinstance(got, bool):
        return isinstance(want, bool) and isinstance(got, bool) and want == got
    # Python compares int with int, and int with float, exactly; coercing both
    # sides through float() made 10**17 + 1 equal 10**17.
    if _is_number(want) and _is_number(got):
        return want == got
    if _is_number(want) and isinstance(got, str):
        number = _canonical_number(got)
        return number is not None and number == want
    if isinstance(want, str) and _is_number(got):
        number = _canonical_number(want)
        return number is not None and number == got
    return want == got


def _call_matches(spec, call):
    """Subset match: the name must equal, every argument the spec lists must be
    present and equal, and every key in absent_args must be missing.

    Arguments the spec omits are ignored, so an incidental max_results or
    controller does not break a correct call. absent_args exists for a trap whose
    wrong move is an *omission* rather than a wrong value -- calling
    query_babylon_catalog without a cluster (babylon.py:693). If ANY listed key
    is present the spec does not match, because cluster and sandbox_comment are
    documented alternatives and either one means the agent disambiguated.
    """
    name, args = call
    if spec.get("name", "") != name:
        return False
    for key, want in (spec.get("args") or {}).items():
        if key not in args or not _values_equal(want, args[key]):
            return False
    for key in spec.get("absent_args") or []:
        if key in args:
            return False
    return True


def _match_ordered_subsequence(expected, calls):
    """Longest ordered matching (LCS), returning the matched expected indices.

    Greedy left-to-right would be wrong: with expected [find_jobs, get_job_log]
    and an actual run of only [get_job_log], a greedy scan consumes the whole
    transcript hunting for find_jobs and reports 0 matches, hiding a call that
    is genuinely there. LCS also guarantees one actual call cannot satisfy two
    expected calls, since each step advances both cursors.
    """
    rows, columns = len(expected), len(calls)
    table = [[0] * (columns + 1) for _ in range(rows + 1)]
    for i in range(rows - 1, -1, -1):
        for j in range(columns - 1, -1, -1):
            if _call_matches(expected[i], calls[j]):
                table[i][j] = 1 + table[i + 1][j + 1]
            else:
                table[i][j] = max(table[i + 1][j], table[i][j + 1])

    matched, i, j = set(), 0, 0
    while i < rows and j < columns:
        if _call_matches(expected[i], calls[j]):
            matched.add(i)
            i += 1
            j += 1
        elif table[i + 1][j] >= table[i][j + 1]:
            i += 1
        else:
            j += 1
    return matched


def _match_exact_sequence(expected, calls):
    """All or nothing: same length, pairwise match."""
    if len(expected) != len(calls):
        return set()
    if all(_call_matches(e, c) for e, c in zip(expected, calls)):
        return set(range(len(expected)))
    return set()


def _match_unordered_subset(expected, calls):
    """Every expected call must appear, in any order. Each live call is used once.

    ordered-subsequence is right for a dependency chain: get_job_log, then
    lookup_catalog_item, then fetch_github_file only works in that order.  It is
    wrong for sibling calls with no dependency -- three providers queried for the
    same period, or get_services / get_comments / get_downtimes on one host --
    where the order is the agent's to choose and grading it measures style.
    Measured: a live run queried aws, azure, gcp against a contract listing aws,
    gcp, azure and lost a third of its tool_calls component to that alone.

    Assignment runs in descending order of how many arguments an expected call
    pins, so a loose spec cannot consume the live call a more specific sibling
    needed; ties keep authored order.  Returns matched expected indices, as the
    other matchers do, so reporting stays in authored order.
    """
    order = sorted(range(len(expected)),
                   key=lambda i: -len(expected[i].get("args") or {}))
    remaining = list(range(len(calls)))
    matched = set()
    for index in order:
        for position, call_index in enumerate(remaining):
            if _call_matches(expected[index], calls[call_index]):
                matched.add(index)
                remaining.pop(position)
                break
    return matched


def score_tool_calls(calls, spec):
    """-> (score, detail). score is matched/expected, zeroed by any forbidden hit."""
    expected = spec.get("expected") or []
    forbidden = spec.get("forbidden") or []
    match = spec.get("match", "ordered-subsequence")

    if match == "exact-sequence":
        matched = _match_exact_sequence(expected, calls)
    elif match == "unordered-subset":
        matched = _match_unordered_subset(expected, calls)
    else:
        matched = _match_ordered_subsequence(expected, calls)

    violations = [
        entry for entry in forbidden
        if any(_call_matches(entry, call) for call in calls)
    ]

    score = 1.0 if not expected else len(matched) / len(expected)
    if violations:
        score = 0.0

    detail = {
        "match": match,
        "actual": [{"name": name, "args": args} for name, args in calls],
        "unmatched_expected": [
            entry for index, entry in enumerate(expected) if index not in matched
        ],
        "forbidden_violations": violations,
    }
    return score, detail


# Glyphs that are the same text as an ASCII character (defect 10, fixed
# 2026-10-09). Agents emit U+2011 inside names ("cnv\u2011metal\u2011b"), NBSP
# between a currency and its amount, and curly apostrophes; an author writes
# ASCII. An explicit table rather than NFKC on purpose: NFKC maps "\u00b2" to
# "2" and fullwidth digits to digits, which would create digit coincidences for
# _count_present, and it still maps U+2011 to U+2010 rather than to "-".
#
# En and em dashes are deliberately NOT here. Authors enumerate "\u2014",
# "\u2013" and "--" as separate forms, and folding them would newly match 194
# forms -- 61 of them forbidden -- against ASCII-dash answers nobody measured.
_FOLD = str.maketrans({
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2212": "-",
    "\u00a0": " ", "\u202f": " ", "\u2007": " ", "\u2009": " ",
    "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"',
})


def _normalise(text):
    return text.translate(_FOLD)


# Markdown emphasis, folded only when a contract sets answer.fold_markup
# (platform-066, 2026-10-10). parsec wraps literals in backticks and bold
# throughout -- "only `vn2jx` is on **osprey**" -- which no finite list of
# substring forms can enumerate. Opt-in rather than global on purpose: folding
# every contract moved two baseline-v3 rows, cost-053 (".**" stopped hiding a
# sentence break from its excuse) and platform-006 (an honest "ran at
# `zero-touch-prod-1.0.6`" newly tripped a forbidden "at <version>"). A single
# "*" is left alone: it is a bullet, and forms enumerate it.
def _strip_markup(value):
    if isinstance(value, str):
        return value.replace("**", "").replace("`", "")
    if isinstance(value, list):
        return [_strip_markup(v) for v in value]
    if isinstance(value, dict):
        return {k: _strip_markup(v) for k, v in value.items()}
    return value


def _contains(answer, needle, ignore_case):
    """Is needle in answer? Both sides are folded (see _FOLD); the answer is
    already folded by score_answer, so folding it again is a no-op."""
    answer, needle = _normalise(answer), _normalise(needle)
    if ignore_case:
        return needle.lower() in answer.lower()
    return needle in answer


# The end of a text is a terminator (defect 8, fixed 2026-10-09). An answer is
# the join of the agent's text frames and nothing guarantees it ends in a
# newline, so a form authored with a trailing "\n" or " " as its token boundary
# -- "registration is off\n", "ticket: no " -- could never match a final line.
# Each terminator is tried at the END only, never substituted mid-text, so
# "registration is off\n" still does not match "registration is off for now".
_END_TERMINATORS = ("\n", " ")


def _contains_terminated(text, needle, ignore_case):
    return any(_contains(text + end, needle, ignore_case)
               for end in _END_TERMINATORS)


def _any_of_present(answer, item):
    """An empty any_of can never be satisfied. src/bench/contract.py rejects
    one, so reaching here with an empty list means the gate was bypassed --
    scoring it as a miss surfaces that rather than silently awarding a point."""
    ignore_case = bool(item.get("ignore_case", False))
    return any(
        _contains_terminated(answer, form, ignore_case)
        for form in item.get("any_of") or []
    )


# Sentence-ish split: ., !, ? followed by whitespace, or a newline. Deliberately
# crude and deliberately including newlines, because a markdown bullet list is
# how agents actually write these answers and an attributed bullet must not
# excuse an asserting bullet below it.
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _sentences(text):
    return [part for part in _SENTENCE_RE.split(text) if part.strip()]


# --- Polarity (defect 11, fixed 2026-10-15). A forbidden form is violated only
# where the answer ASSERTS it. Before this, every occurrence outside an
# attributed_to sentence was a violation, so a correct denial -- "not a transient
# cluster hiccup", "**In Downtime:** No", "| Ceph is out of space | ❌ False |" --
# cost the answer its point, and the cheapest way to win a trap was to stop
# mentioning the decoy at all. Three readings, tried in order on the sentence
# carrying the occurrence: a key/value field or table row whose value or verdict
# cell is a definite polarity token; a question, which asserts nothing; and a
# negation scoped to the occurrence's own clause. Measured before adoption on 371
# stored answers (v4 + v5): 11 outcomes changed, all correct on hand-labelling,
# and 0 of 6,159 forms x 7 assertion shapes newly excused. Required facts are
# deliberately NOT read this way: their forms are often field literals
# ("enable_notifications: false"), and doing so fixed nothing on the corpus while
# causing every regression measured.
#
# A negation never reaches across a clause boundary. "and" is one on purpose:
# "No retries were configured and the failure was transient" asserts transient.
_CLAUSE_BREAK_RE = re.compile(
    r"\s*(?:[;,:()|—–]|[.!?](?!\w)|\s-\s|\s--\s|=>|->|→)\s*"
    r"|\b(?:but|however|whereas|although|though|yet|instead|rather|so|"
    r"because|since|therefore|thus|hence|and|which|while|whilst)\b",
    re.IGNORECASE)
# Six tokens: "not a transient" and "no evidence the artifact server was down"
# reach; a negator on an earlier verb mostly does not.
_NEGATION_WINDOW = 6
_NEGATORS = frozenset((
    "not", "no", "never", "none", "nothing", "nobody", "neither", "nor",
    "without", "cannot", "isnt", "wasnt", "arent", "werent", "doesnt",
    "didnt", "dont", "cant", "couldnt", "wont", "wouldnt", "shouldnt",
    "hasnt", "havent", "hadnt", "aint", "lacks", "lacking",
))
# Negators that do not negate what follows: "no doubt it was transient" asserts.
_NOT_NEGATING_RE = re.compile(
    r"\b(?:not only|not just|not merely|not simply|no doubt|no question|"
    r"not surprisingly|no wonder|no surprise|nothing but|none other than|"
    r"not least|no matter|cannot rule out|can't rule out|can not rule out|"
    r"not rule out|not exclude|cannot exclude|no longer than|not until)\b",
    re.IGNORECASE)
_NEGATING_PHRASE_RE = re.compile(
    r"\b(?:rather than|instead of|ruled out|rules out|rule out|unlike|"
    r"as opposed to|far from|free of|absence of|no sign of|no evidence|"
    r"there is no|there's no|there was no)\b",
    re.IGNORECASE)
# A denial after the occurrence: "X is ruled out", "more retries do not fix".
_DENIED_AFTER_RE = re.compile(
    r"^\W*(?:is|was|are|were|has been|had been)?\s*"
    r"(?:ruled out|not the (?:cause|problem|issue|reason)|"
    r"(?:false|incorrect|wrong|unsupported|disproven|refuted|a red herring|"
    r"not supported|not the case|not what happened|not it)\b)"
    r"|^\W*(?:doesn't|does not|did not|didn't) (?:apply|hold|happen|fit)"
    r"|^\W*(?:\w+\W+){0,2}?(?:do|does|did|will|would|can|could)(?: not|n't)"
    r" (?:fix|solve|resolve|help|explain|address|change|cure)\b",
    re.IGNORECASE)
# Only questions opening with an auxiliary: a wh-question can presuppose its
# content ("Why is it that Ceph is full?"), a polar one cannot.
_POLAR_QUESTION_RE = re.compile(
    r"^[\s#>*\-\d.]*(?:is|are|was|were|do|does|did|should|could|can|will|"
    r"would|has|have|had|must)\b", re.IGNORECASE)
_VERDICT_GLYPHS = "❌✗✘✖⛔\U0001f6ab✅✔✓☑"
_DENY_VALUE_RE = re.compile(
    r"^(?:no|none|false|not|never|n/?a|0|nope|disabled|off|"
    r"ruled out|rejected|refuted|disproven|incorrect|wrong|unlikely)\b"
    r"|^[❌✗✘✖⛔\U0001f6ab]", re.IGNORECASE)
_AFFIRM_VALUE_RE = re.compile(
    r"^(?:yes|true|confirmed|correct|likely)\b|^[✅✔✓☑]",
    re.IGNORECASE)
_POLARITY_TOKEN_RE = re.compile(r"[A-Za-z0-9_']+")


def _unmarked(text):
    """Emphasis blanked to spaces, so offsets into the original stay valid."""
    return (text.replace("**", "  ").replace("__", "  ").replace("`", " ")
                .replace("’", "'"))


def _value_polarity(value, strict):
    """'deny', 'affirm' or None for a field value or a table cell. strict (a
    table cell) counts only a cell that IS a verdict -- a glyph, a short cell, or
    a verdict word then punctuation -- so an evidence cell that merely starts
    "No events found" cannot decide the row."""
    # A unit that opens a table row starts with "|" (defect 12): strip it too.
    cell = _unmarked(value).strip().strip("|").strip().strip("*_ ").lstrip("-• ").strip()
    if not cell:
        return None
    deny, affirm = _DENY_VALUE_RE.match(cell), _AFFIRM_VALUE_RE.match(cell)
    if not (deny or affirm):
        return None
    if strict:
        rest = cell[(deny or affirm).end():][:2]
        if not (cell[0] in _VERDICT_GLYPHS
                or len(_POLARITY_TOKEN_RE.findall(cell)) <= 3
                or re.match(r"\s*[—–\-,.:;(]", rest)):
            return None
    return "deny" if deny else "affirm"


def _negated_in_clause(text, start, end):
    """Is text[start:end] negated within its own clause?

    A form that opens with a negator ("nor ready", "never sent") carries its
    own polarity, and the word before it belongs to its construction ("neither
    healthy nor ready"), so only a denial after it can flip it.
    """
    plain = _unmarked(text)
    head = _POLARITY_TOKEN_RE.findall(plain[start:end])
    own = bool(head) and head[0].lower().replace("'", "") in _NEGATORS
    before, after = plain[:start], plain[end:]
    breaks = list(_CLAUSE_BREAK_RE.finditer(before))
    if breaks:
        before = before[breaks[-1].end():]
    cut = _CLAUSE_BREAK_RE.search(after)
    if cut:
        after = after[:cut.start()]
    before = _NOT_NEGATING_RE.sub(" ", before)
    words = _POLARITY_TOKEN_RE.findall(before)
    if not own:
        tokens = [w.lower().replace("'", "") for w in words]
        if any(t in _NEGATORS for t in tokens[-_NEGATION_WINDOW:]):
            return True
        if _NEGATING_PHRASE_RE.search(" ".join(words[-(_NEGATION_WINDOW + 2):])):
            return True
    return bool(_DENIED_AFTER_RE.match(after))


def _occurrence_denied(sentence, start, end, following):
    """Is the occurrence sentence[start:end] denied rather than asserted?"""
    bounds, pos = [], 0
    for cell in sentence.split("|"):
        bounds.append((pos, pos + len(cell)))
        pos += len(cell) + 1
    at = next((k for k, (a, b) in enumerate(bounds) if a <= start < b), None)
    if at is not None:
        a, b = bounds[at]
        cell = sentence[a:b]
        colon = cell.find(":")
        # "Key: value" with the occurrence in the key: the value decides.
        if (colon != -1 and min(end, b) - a <= colon + 1
                and not cell[colon + 1:colon + 3].startswith("//")):
            polarity = _value_polarity(cell[colon + 1:], strict=False)
            if polarity:
                return polarity == "deny"
        if sentence.lstrip().startswith("|"):
            if _negated_in_clause(cell, start - a, min(end, b) - a):
                return True
            verdicts = {_value_polarity(sentence[x:y], strict=True)
                        for x, y in bounds[at + 1:]} - {None}
            if verdicts:
                return verdicts == {"deny"}
            # No verdict cell in this unit: a question cell's answer sits in the
            # next unit, because the split cut the row at its "?" (defect 12).
    if sentence.rstrip().rstrip("*|").rstrip().endswith("?"):
        # The answer decides before the question's form does: "X? No." denies,
        # "Is it X? Yes." asserts; only an unanswered polar question asserts nothing.
        answer = _value_polarity(following, strict=False) if following else None
        if answer is not None:
            return answer == "deny"
        if _POLAR_QUESTION_RE.match(_unmarked(sentence).lstrip(" |")):
            return True
    return _negated_in_clause(sentence, start, end)


def _occurrences(sentence, form, ignore_case):
    """(start, end) of every occurrence of form, including one completed only by
    the end-of-sentence terminator (defect 8)."""
    hay, needle = _normalise(sentence), _normalise(form)
    if ignore_case:
        hay, needle = hay.lower(), needle.lower()
    found, i = [], hay.find(needle)
    while i != -1:
        found.append((i, i + len(needle)))
        i = hay.find(needle, i + 1)
    bare = needle.rstrip("\n ")
    if not found and bare != needle and hay.endswith(bare):
        found.append((len(hay) - len(bare), len(hay)))
    return found or [(0, len(hay))]


def _forbidden_violated(answer, item):
    """Did the answer state something it must not?

    A form's occurrence is a violation unless attributed_to is declared AND the
    sentence carrying that occurrence also carries one of its phrases. That
    separates an honest quote or refutation ("the write-up says job 90399
    failed, but it does not exist") from an assertion ("job 90399 failed on
    east"), which a plain substring test cannot -- CLAUDE.md limitation 8.
    Nor is a denied occurrence a violation (defect 11, above); every occurrence
    is read on its own, so a denial cannot license an assertion beside it.

    The exemption is per sentence, never per answer: one attributed sentence
    must not license an unattributed assertion elsewhere, which is exactly how a
    fabricator would slip through a whole-answer check.
    """
    ignore_case = bool(item.get("ignore_case", False))
    forms = item.get("none_of") or []
    excuses = [phrase for phrase in (item.get("attributed_to") or [])
               if phrase and phrase.strip()]

    sentences = _sentences(answer)
    for index, sentence in enumerate(sentences):
        following = sentences[index + 1] if index + 1 < len(sentences) else ""
        for form in forms:
            # The split drops the separator, so a sentence's end is tested as
            # a terminator too: "- mbrandt-deploy" ends a bullet, and the form
            # "mbrandt-deploy " must catch it (defect 8).
            if not _contains_terminated(sentence, form, ignore_case):
                continue
            if excuses and any(_contains(sentence, phrase, True)
                               for phrase in excuses):
                continue          # attributed here; keep checking elsewhere
            if all(_occurrence_denied(sentence, start, end, following)
                   for start, end in _occurrences(sentence, form, ignore_case)):
                continue          # denied here; keep checking elsewhere
            return True
    return False


# Word forms only up to twenty: past that, prose reliably switches to digits, and
# a longer table is surface area with no answer behind it.
_NUMBER_WORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
    15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
    19: "nineteen", 20: "twenty",
}
# "no jobs matched" is a correct way to state a count of zero.
_ZERO_WORDS = ("zero", "no", "none", "not any")
# The subset of _ZERO_WORDS that is hedging vocabulary rather than a real
# numeral -- "zero" is excluded here on purpose, it gets the same window as
# any other number word. Used only to shrink these three to a radius-1 match
# against the noun; see _count_present.
_ZERO_HEDGE_WORDS = ("no", "none", "not any")

_WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)


def _token_starts(text):
    """{character offset: token index} for every word token in text.

    Used to require that a match begins where a word begins, so `jobs` does not
    match inside `subjobs`, and to measure the count window in tokens rather
    than characters -- characters would make the window depend on how long the
    words between happen to be.
    """
    return {m.start(): index for index, m in enumerate(_WORD_RE.finditer(text))}


def _numeral_forms(value):
    """Every spelling of `value` worth accepting, longest first.

    Longest first matters: matching "no" before "none" inside "none of the jobs"
    would land on a character offset that is not a token start and be discarded,
    losing a real match.
    """
    forms = [str(value)]
    word = _NUMBER_WORDS.get(value)
    if word:
        forms.append(word)
    if value == 0:
        forms.extend(w for w in _ZERO_WORDS if w not in forms)
    return sorted(set(forms), key=len, reverse=True)


def _count_present(answer, item):
    """Is `value` stated, attached to one of `nouns`, within `window` tokens?

    This replaces v2's finite any_of list of count phrasings. That list rejected
    fully correct answers whose notation nobody anticipated -- "There are 3 AAP2
    jobs" against a list holding only "three" -- while a bare "3" could not be
    used instead because it matches inside a job id like 90203. Requiring a noun
    nearby is what makes the digit safe to accept.

    Both directions of the window count: "jobs: 3" states the same fact as
    "3 jobs".

    extra_any_of is checked first and needs no noun: it exists for phrasings with
    no numeral in them at all ("a single job", "none of them"), which the
    proximity rule cannot reach.
    """
    text_lower = _normalise(answer).lower()
    for form in item.get("extra_any_of") or []:
        if form and _normalise(form).lower() in text_lower:
            return True

    value = item.get("value")
    nouns = [_normalise(noun) for noun in (item.get("nouns") or [])
             if noun and noun.strip()]
    if value is None or not nouns:
        return False
    try:
        window = int(item.get("window", 4))
    except (TypeError, ValueError):
        window = 4

    text = text_lower
    starts = _token_starts(text)
    if not starts:
        return False

    # Each entry is (first_token_index, last_token_index, is_hedge). first ==
    # last for every single-word numeral; a hedge phrase like "not any" spans
    # two tokens, and both ends matter -- see is_hedge below.
    number_positions = []
    for form in _numeral_forms(value):
        if form.isdigit():
            # Reject a digit glued to another digit (90203, 33) or sitting inside a
            # decimal or thousands-separated number (1.3, 1,300) -- all of which
            # occur in real seed data.
            #
            # The separator has to be DIGIT-ADJACENT to disqualify. An earlier form
            # of this guard was (?<![\d.,])N(?![\d.,]), which also rejected a plain
            # sentence-ending or list comma: "the threshold is 5." and "there are 5,
            # and..." both failed, which is the phrasing sensitivity this matcher
            # exists to remove rather than reproduce. Measured while authoring
            # bench-v4-icinga-010, where a fully correct answer lost the fact.
            pattern = (r"(?<!\d)(?<![\d][.,])" + re.escape(form)
                       + r"(?!\d)(?![.,]\d)")
        else:
            pattern = r"\b" + re.escape(form) + r"\b"
        span = len(form.split())
        # "no"/"none"/"not any" are ordinary hedging vocabulary, not count
        # vocabulary: "There is no clear cause; 5 jobs failed" says *five*,
        # and "No, the jobs all succeeded" is a hedge unrelated to counting.
        # Treating them exactly like a real numeral would credit a count of
        # zero off either one, for any noun within the full window. Holding
        # them to radius 1 -- immediately adjacent to the noun -- still
        # accepts "No jobs matched" and "not any jobs" (checked against
        # whichever end of the phrase, singular or plural, sits closest to
        # the noun) while rejecting both of those false positives, whose
        # hedge word sits several tokens away from the noun it happens to
        # share a sentence with.
        is_hedge = value == 0 and form in _ZERO_HEDGE_WORDS
        for match in re.finditer(pattern, text):
            first = starts.get(match.start())
            if first is None:
                continue
            number_positions.append((first, first + span - 1, is_hedge))
    if not number_positions:
        return False

    for noun in nouns:
        noun = noun.lower()
        # A plural noun in the contract ("jobs") must also recognise its own
        # singular ("1 job"): a correct answer states the noun in whichever
        # number agrees with the value, and authoring both forms into every
        # nouns list is exactly the finite-phrasing-list trap this matcher
        # replaces. Only the trailing "s" is stripped -- this is agreement,
        # not stemming -- so a noun that is already singular is untouched.
        candidates = [noun]
        if noun.endswith("s") and len(noun) > 1:
            candidates.append(noun[:-1])
        for candidate in candidates:
            # (?!\w) requires the match to also end at a word boundary, not
            # just start at one: without it, nouns=["jobs"] (stripped to
            # "job") credits "There are 2 job_templates configured" and
            # "3 jobsomething entries", and nouns=["hosts"] (stripped to
            # "host") credits "hostname" -- a token that merely begins with
            # the noun is not the noun. \w is used here rather than this
            # file's own _WORD_RE, which treats "_" as a separator: that
            # would let "job" match the "job" half of "job_templates" as a
            # complete token and still be wrong. Requiring "not \w" after
            # the candidate rejects the underscore continuation too.
            pattern = re.escape(candidate) + r"(?!\w)"
            for match in re.finditer(pattern, text):
                index = starts.get(match.start())
                if index is None:
                    continue      # matched inside a longer word, e.g. subjobs
                for first, last, is_hedge in number_positions:
                    radius = 1 if is_hedge else window
                    if min(abs(index - first), abs(index - last)) <= radius:
                        return True
    return False


# A citation is "owner/repo" and a path close together on one line. The gap is
# bounded and newline-free on purpose: parsec's RCA playbook wants
# owner/repo:path:line, but a real answer writes "see agnosticd/agnosticd-v2,
# file ansible.cfg" just as often, while a repo in one markdown table cell and a
# path two rows later is not a citation of anything.
_CITATION_GAP_DEFAULT = 40


def _citation_present(answer, item):
    """Are this item's repo and path cited together, with a line if declared?

    Both halves are required because naming the path alone is exactly the
    ungrounded claim parsec's RCA playbook forbids, and naming the repo alone
    says nothing about where. The repo match is case-insensitive but the *owner*
    is part of it, so citing rhpds/agnosticd-v2 for a file in
    agnosticd/agnosticd-v2 does not count -- that wrong owner is the single most
    common real mistake in the trajectories.
    """
    answer = _normalise(answer)
    repo = _normalise(item.get("repo") or "").strip()
    path = _normalise(item.get("path") or "").strip()
    if not repo or not path:
        return False
    try:
        gap = int(item.get("gap", _CITATION_GAP_DEFAULT))
    except (TypeError, ValueError):
        gap = _CITATION_GAP_DEFAULT
    if gap < 0:
        gap = 0

    pattern = re.escape(repo) + r"[^\n]{0," + str(gap) + r"}?" + re.escape(path)
    matches = list(re.finditer(pattern, answer, re.IGNORECASE))
    if not matches:
        return False

    line = item.get("line")
    if line is None:
        return True
    # The line number has to follow the path, not float anywhere in the answer:
    # ":12", " line 12", " L12" all count; a 12 in the next sentence does not.
    # Every mention is tried, not only the first (defect 13, fixed 2026-10-16):
    # an honest answer often names the file once in passing and cites the line
    # at a later mention.
    line_re = re.compile(r"(?<!\d)(?<![\d][.,])" + re.escape(str(line))
                         + r"(?!\d)(?![.,]\d)")
    return any(line_re.search(answer[m.end():m.end() + 24]) for m in matches)


# The fixed category taxonomy from parsec's own RCA playbook
# (skills/aap2-job-failure-rca/SKILL.md:90-95): the operational set first, then
# the fallbacks it allows only for a novel failure. Duplicated in
# src/bench/contract.py; test_taxonomy_matches_the_verifier pins the two.
TAXONOMY = (
    "platform_failure", "connectivity_failure", "authentication_failure",
    "resource_failure", "timeout_failure", "automation_failure",
    "infrastructure_failure", "configuration", "infrastructure",
    "application_bug", "secrets", "resource", "dependency",
)

# Only these can serve as evidence that a SECOND category was named. The other
# five taxonomy members -- configuration, infrastructure, secrets, resource,
# dependency -- are ordinary English words that appear in any honest RCA prose
# ("the Ansible configuration", "a shared resource"), so scanning for them makes
# exclusive fail correct answers. Measured: a fully correct answer for
# bench-v4-platform-002 said "the execution environment's Ansible configuration"
# and lost its verdict fact to the bare member `configuration`.
#
# The cost, stated rather than hidden: when a contract's own category is one of
# those five, an answer hedging toward another of the five is not caught. That is
# the lesser error. A false negative against a correct answer is the failure class
# that retired the extracted corpus; a missed hedge is a weaker check.
TAXONOMY_EXCLUSIVE = (
    "platform_failure", "connectivity_failure", "authentication_failure",
    "resource_failure", "timeout_failure", "automation_failure",
    "infrastructure_failure", "application_bug",
)

_CONFIDENCE_WORDS = ("high", "medium", "low")


def _word_present(text, word):
    """Whole-word match, so "high" does not match "highly" and "resource" does
    not match inside "resource_failure".

    Underscores are word characters, which is what makes the second case work:
    the boundary lands where the category name actually ends.
    """
    return re.search(r"(?<![\w])" + re.escape(word) + r"(?![\w])",
                     text, re.IGNORECASE) is not None


def _verdict_present(answer, item):
    """Did the answer land on exactly this category, with a confidence?

    exclusive is the discriminating half: parsec's playbook says assign exactly
    one category, so an answer hedging across two has not produced a verdict. Only
    TAXONOMY_EXCLUSIVE counts as a second category -- see the note there for why
    the five bare-word members cannot. Substring members ("resource" inside
    "resource_failure", "infrastructure" inside "infrastructure_failure") are
    additionally excluded by whole-word matching, without which every *_failure
    verdict in an overlapping pair would be unsatisfiable.
    """
    answer = _normalise(answer)
    category = (item.get("category") or "").strip()
    if not category:
        return False
    if not _word_present(answer, category):
        return False

    if item.get("exclusive", True):
        others = [name for name in TAXONOMY_EXCLUSIVE
                  if name != category and _word_present(answer, name)]
        if others:
            return False

    if item.get("require_confidence", True):
        if not any(_word_present(answer, word) for word in _CONFIDENCE_WORDS):
            return False
    return True


def score_answer(answer, spec):
    """-> (score, detail), over one denominator of required + counts + forbidden.

    A forbidden fact is satisfied by absence and scored as a point, not as a
    penalty. That makes a fabrication trap a positively-scored item, and lets a
    largely-absence scenario score coherently.

    Know the consequence before authoring one: an answer that says nothing at
    all banks every forbidden fact for free. That is correct for a fact whose
    whole point is not being stated, but it is also why the gate computes a
    content-free floor (see src/bench/probes.py) -- a contract with many
    forbidden facts and few required ones pays a mute agent most of its answer
    weight.
    """
    required = spec.get("required") or []
    counts = spec.get("counts") or []
    citations = spec.get("citations") or []
    # A single optional object, not a list: parsec's playbook assigns exactly one
    # category per finding, so two verdicts would assert a contradiction.
    verdict = spec.get("verdict") or None
    verdicts = [verdict] if verdict else []
    forbidden = spec.get("forbidden") or []
    fold = spec.get("fold_markup") is True
    total = (len(required) + len(counts) + len(citations) + len(verdicts)
             + len(forbidden))

    # Folded once (defect 10). The end-of-answer terminator (defect 8) is
    # applied inside _any_of_present and _forbidden_violated, which try both
    # "\n" and " " there -- appending a single "\n" here would serve only the
    # newline-terminated forms. The count, citation and verdict matchers are
    # token- and regex-based and need no terminator. compute_reward's
    # completion gate still reads the raw answer, so a whitespace-only answer
    # is still empty.
    text = _normalise(answer)
    # Under fold_markup each item is matched folded but reported as authored.
    if fold:
        text = _strip_markup(text)
    view = _strip_markup if fold else (lambda item: item)

    missed = [item for item in required if not _any_of_present(text, view(item))]
    missed_counts = [item for item in counts
                     if not _count_present(text, view(item))]
    missed_citations = [item for item in citations
                        if not _citation_present(text, view(item))]
    missed_verdict = [item for item in verdicts
                      if not _verdict_present(text, view(item))]
    hit = [item for item in forbidden if _forbidden_violated(text, view(item))]

    detail = {
        "required_missed": missed,
        "required_total": len(required),
        "counts_missed": missed_counts,
        "counts_total": len(counts),
        "citations_missed": missed_citations,
        "citations_total": len(citations),
        "verdict_missed": missed_verdict,
        "verdict_total": len(verdicts),
        "forbidden_hit": hit,
        "forbidden_total": len(forbidden),
    }
    if total == 0:
        return 1.0, detail

    satisfied = ((len(required) - len(missed))
                 + (len(counts) - len(missed_counts))
                 + (len(citations) - len(missed_citations))
                 + (len(verdicts) - len(missed_verdict))
                 + (len(forbidden) - len(hit)))
    return satisfied / total, detail


def compute_reward(expected, calls, answer, ok):
    """-> (reward, detail).

    reward holds only the four scalars Harbor reads. Everything a human needs
    to understand the number goes in detail, written alongside as
    reward-detail.json: the extracted verifier reported a bare 0.625 with no
    way to see which check failed, and that cost real debugging time.
    """
    completion = expected.get("completion", {})
    gate = 1.0
    if completion.get("status", "ok") == "ok" and not ok:
        gate = 0.0
    if completion.get("nonempty_answer", True) and not answer.strip():
        gate = 0.0

    tool_score, tool_detail = score_tool_calls(calls, expected.get("tool_calls") or {})
    answer_score, answer_detail = score_answer(answer, expected.get("answer") or {})

    weights = expected.get("weights") or {}
    weight_tool = float(weights.get("tool_calls", DEFAULT_WEIGHTS["tool_calls"]))
    weight_answer = float(weights.get("answer", DEFAULT_WEIGHTS["answer"]))
    combined = weight_tool * tool_score + weight_answer * answer_score

    reward = {
        "reward": round(gate * combined, 6),
        "completion": gate,
        "tool_calls": round(tool_score, 6),
        "answer": round(answer_score, 6),
    }
    detail = {
        "gate": gate,
        "weights": {"tool_calls": weight_tool, "answer": weight_answer},
        "tool_calls": tool_detail,
        "answer": answer_detail,
    }
    return reward, detail


def _read_logs(agent_logs):
    """Concatenate every transcript file in the agent log directory.

    Globs *.jsonl and *.txt, so --out must not point at --agent-logs: a second
    run would otherwise re-read its own reward.txt as transcript input.
    """
    parts = []
    for pattern in ("*.jsonl", "*.txt"):
        for path in sorted(agent_logs.glob(pattern)):
            parts.append(path.read_text(errors="replace"))
    return "\n".join(parts)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", default="/tests/expected.json")
    parser.add_argument("--agent-logs", default="/logs/agent")
    parser.add_argument("--out", default="/logs/verifier")
    args = parser.parse_args(argv)

    expected = json.loads(Path(args.expected).read_text())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    schema = expected.get("schema")
    if schema != CONTRACT_SCHEMA:
        # Refuse to score rather than write a misleading 0. A contract this
        # verifier cannot read is a bypassed authoring gate, not a bad agent
        # run, and reporting it as 0 would invert that conclusion -- the same
        # unscoreable-is-not-zero rule src/corpus/ already follows.
        message = f"expected contract schema {CONTRACT_SCHEMA!r}, got {schema!r}"
        (out / "reward-detail.json").write_text(
            json.dumps({"error": message}, indent=2))
        print(f"verify.py: {message}", file=sys.stderr)
        return 2

    calls, answer, ok = parse_transcript(_read_logs(Path(args.agent_logs)))
    reward, detail = compute_reward(expected, calls, answer, ok)

    (out / "reward.json").write_text(json.dumps(reward, indent=2))
    (out / "reward.txt").write_text(str(reward["reward"]))
    (out / "reward-detail.json").write_text(
        json.dumps(detail, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
