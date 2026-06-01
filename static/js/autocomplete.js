(() => {

    const COMPANIES = [
        // IT / 플랫폼
        { name: 'NAVER',             code: '035420', sector: 'IT플랫폼',   market: 'KOSPI'  },
        { name: '카카오',             code: '035720', sector: 'IT플랫폼',   market: 'KOSPI'  },
        { name: '카카오뱅크',         code: '323410', sector: '핀테크',     market: 'KOSPI'  },
        { name: '카카오페이',         code: '377300', sector: '핀테크',     market: 'KOSPI'  },
        { name: '카카오게임즈',       code: '293490', sector: '게임',       market: 'KOSDAQ' },
        // 반도체
        { name: '삼성전자',           code: '005930', sector: '반도체',     market: 'KOSPI'  },
        { name: 'SK하이닉스',         code: '000660', sector: '반도체',     market: 'KOSPI'  },
        { name: 'DB하이텍',           code: '000990', sector: '반도체',     market: 'KOSPI'  },
        { name: '한미반도체',         code: '042700', sector: '반도체',     market: 'KOSDAQ' },
        { name: '리노공업',           code: '058470', sector: '반도체',     market: 'KOSDAQ' },
        { name: '솔브레인',           code: '357780', sector: '반도체소재', market: 'KOSDAQ' },
        { name: '이오테크닉스',       code: '039030', sector: '반도체장비', market: 'KOSDAQ' },
        { name: '원익IPS',            code: '240810', sector: '반도체장비', market: 'KOSDAQ' },
        { name: '삼성전기',           code: '009150', sector: '전자부품',   market: 'KOSPI'  },
        { name: 'LG이노텍',           code: '011070', sector: '전자부품',   market: 'KOSPI'  },
        // 배터리 / 소재
        { name: 'LG에너지솔루션',     code: '373220', sector: '배터리',     market: 'KOSPI'  },
        { name: '삼성SDI',            code: '006400', sector: '배터리',     market: 'KOSPI'  },
        { name: '에코프로비엠',       code: '247540', sector: '배터리소재', market: 'KOSDAQ' },
        { name: '에코프로',           code: '086520', sector: '배터리소재', market: 'KOSDAQ' },
        { name: '포스코퓨처엠',       code: '003670', sector: '배터리소재', market: 'KOSPI'  },
        { name: '엘앤에프',           code: '066970', sector: '배터리소재', market: 'KOSDAQ' },
        // 자동차
        { name: '현대차',             code: '005380', sector: '자동차',     market: 'KOSPI'  },
        { name: '기아',               code: '000270', sector: '자동차',     market: 'KOSPI'  },
        { name: '현대모비스',         code: '012330', sector: '자동차부품', market: 'KOSPI'  },
        { name: '현대글로비스',       code: '086280', sector: '물류',       market: 'KOSPI'  },
        { name: '만도',               code: '204320', sector: '자동차부품', market: 'KOSPI'  },
        { name: '한온시스템',         code: '018880', sector: '자동차부품', market: 'KOSPI'  },
        // 바이오 / 제약
        { name: '삼성바이오로직스',   code: '207940', sector: '바이오',     market: 'KOSPI'  },
        { name: '셀트리온',           code: '068270', sector: '바이오',     market: 'KOSPI'  },
        { name: '셀트리온헬스케어',   code: '091990', sector: '바이오',     market: 'KOSDAQ' },
        { name: '한미약품',           code: '128940', sector: '제약',       market: 'KOSPI'  },
        { name: '유한양행',           code: '000100', sector: '제약',       market: 'KOSPI'  },
        { name: '종근당',             code: '185750', sector: '제약',       market: 'KOSPI'  },
        { name: '녹십자',             code: '006280', sector: '제약',       market: 'KOSPI'  },
        { name: 'SK바이오사이언스',   code: '302440', sector: '바이오',     market: 'KOSPI'  },
        { name: '알테오젠',           code: '196170', sector: '바이오',     market: 'KOSDAQ' },
        { name: 'HLB',               code: '028300', sector: '바이오',     market: 'KOSDAQ' },
        { name: '씨젠',              code: '096530', sector: '바이오',     market: 'KOSDAQ' },
        { name: '대웅제약',           code: '069620', sector: '제약',       market: 'KOSPI'  },
        // 금융 / 보험
        { name: 'KB금융',             code: '105560', sector: '금융',       market: 'KOSPI'  },
        { name: '신한지주',           code: '055550', sector: '금융',       market: 'KOSPI'  },
        { name: '하나금융지주',       code: '086790', sector: '금융',       market: 'KOSPI'  },
        { name: '우리금융지주',       code: '316140', sector: '금융',       market: 'KOSPI'  },
        { name: '기업은행',           code: '024110', sector: '금융',       market: 'KOSPI'  },
        { name: '메리츠금융지주',     code: '138040', sector: '금융',       market: 'KOSPI'  },
        { name: '삼성생명',           code: '032830', sector: '보험',       market: 'KOSPI'  },
        { name: '삼성화재',           code: '000810', sector: '보험',       market: 'KOSPI'  },
        { name: 'DB손해보험',         code: '005830', sector: '보험',       market: 'KOSPI'  },
        // 에너지 / 정유
        { name: '한국전력',           code: '015760', sector: '에너지',     market: 'KOSPI'  },
        { name: 'S-Oil',             code: '010950', sector: '정유',       market: 'KOSPI'  },
        { name: 'SK이노베이션',       code: '096770', sector: '에너지',     market: 'KOSPI'  },
        { name: 'GS',                code: '078930', sector: '에너지',     market: 'KOSPI'  },
        { name: 'KT&G',              code: '033780', sector: '담배',       market: 'KOSPI'  },
        // 철강 / 소재
        { name: 'POSCO홀딩스',        code: '005490', sector: '철강',       market: 'KOSPI'  },
        { name: '고려아연',           code: '010130', sector: '비철금속',   market: 'KOSPI'  },
        { name: '현대제철',           code: '004020', sector: '철강',       market: 'KOSPI'  },
        // 화학
        { name: 'LG화학',             code: '051910', sector: '화학',       market: 'KOSPI'  },
        { name: '롯데케미칼',         code: '011170', sector: '화학',       market: 'KOSPI'  },
        { name: '한화솔루션',         code: '009830', sector: '화학',       market: 'KOSPI'  },
        { name: '효성화학',           code: '298000', sector: '화학',       market: 'KOSPI'  },
        // 건설
        { name: '현대건설',           code: '000720', sector: '건설',       market: 'KOSPI'  },
        { name: 'GS건설',             code: '006360', sector: '건설',       market: 'KOSPI'  },
        { name: 'DL이앤씨',           code: '375500', sector: '건설',       market: 'KOSPI'  },
        { name: 'HDC현대산업개발',    code: '294870', sector: '건설',       market: 'KOSPI'  },
        // 조선
        { name: 'HD한국조선해양',     code: '009540', sector: '조선',       market: 'KOSPI'  },
        { name: '삼성중공업',         code: '010140', sector: '조선',       market: 'KOSPI'  },
        { name: '한화오션',           code: '042660', sector: '조선',       market: 'KOSPI'  },
        { name: 'HD현대',             code: '267250', sector: '조선',       market: 'KOSPI'  },
        // 전자 / 가전
        { name: 'LG전자',             code: '066570', sector: '전자',       market: 'KOSPI'  },
        // 통신
        { name: 'SK텔레콤',           code: '017670', sector: '통신',       market: 'KOSPI'  },
        { name: 'KT',                code: '030200', sector: '통신',       market: 'KOSPI'  },
        { name: 'LG유플러스',         code: '032640', sector: '통신',       market: 'KOSPI'  },
        // 엔터 / 게임
        { name: '하이브',             code: '352820', sector: '엔터',       market: 'KOSPI'  },
        { name: 'SM엔터테인먼트',     code: '041510', sector: '엔터',       market: 'KOSPI'  },
        { name: 'JYP Ent.',          code: '035900', sector: '엔터',       market: 'KOSDAQ' },
        { name: 'YG엔터테인먼트',     code: '122870', sector: '엔터',       market: 'KOSDAQ' },
        { name: '크래프톤',           code: '259960', sector: '게임',       market: 'KOSPI'  },
        { name: '엔씨소프트',         code: '036570', sector: '게임',       market: 'KOSPI'  },
        { name: '넷마블',             code: '251270', sector: '게임',       market: 'KOSPI'  },
        { name: '펄어비스',           code: '263750', sector: '게임',       market: 'KOSDAQ' },
        { name: '위메이드',           code: '112040', sector: '게임',       market: 'KOSDAQ' },
        // 유통 / 식품
        { name: '이마트',             code: '139480', sector: '유통',       market: 'KOSPI'  },
        { name: '롯데쇼핑',           code: '023530', sector: '유통',       market: 'KOSPI'  },
        { name: '신세계',             code: '004170', sector: '유통',       market: 'KOSPI'  },
        { name: 'CJ제일제당',         code: '097950', sector: '식품',       market: 'KOSPI'  },
        { name: '오리온',             code: '271560', sector: '식품',       market: 'KOSPI'  },
        { name: '농심',               code: '004370', sector: '식품',       market: 'KOSPI'  },
        // 화장품
        { name: '아모레퍼시픽',       code: '090430', sector: '화장품',     market: 'KOSPI'  },
        { name: 'LG생활건강',         code: '051900', sector: '화장품',     market: 'KOSPI'  },
        { name: '한국콜마',           code: '161890', sector: '화장품',     market: 'KOSPI'  },
        { name: '코스맥스',           code: '192820', sector: '화장품',     market: 'KOSPI'  },
        // 방산
        { name: '한국항공우주',       code: '047810', sector: '방산',       market: 'KOSPI'  },
        { name: '한화에어로스페이스', code: '012450', sector: '방산',       market: 'KOSPI'  },
        { name: '현대로템',           code: '064350', sector: '방산',       market: 'KOSPI'  },
        // 로봇
        { name: '두산로보틱스',       code: '454910', sector: '로봇',       market: 'KOSPI'  },
        { name: '레인보우로보틱스',   code: '277810', sector: '로봇',       market: 'KOSDAQ' },
        // 지주
        { name: '삼성물산',           code: '028260', sector: '지주',       market: 'KOSPI'  },
        { name: 'SK',                code: '034730', sector: '지주',       market: 'KOSPI'  },
        { name: 'LG',                code: '003550', sector: '지주',       market: 'KOSPI'  },
        { name: '한화',              code: '000880', sector: '지주',       market: 'KOSPI'  },
        { name: '롯데지주',           code: '004990', sector: '지주',       market: 'KOSPI'  },
    ];

    const MAX_TAGS = 10;

    const acWrap    = document.querySelector('.ac-wrap');
    const field     = document.getElementById('tag-field');
    const textInput = document.getElementById('tag-text');
    const countEl   = document.getElementById('tag-count');
    const resetBtn  = document.getElementById('reset-btn');
    const submitBtn = document.getElementById('submit-btn');
    const form      = document.getElementById('rec-form');

    let tags = [];

    function syncHidden() {
        form.querySelectorAll('input[name="companies"]').forEach(el => el.remove());
        tags.forEach(name => {
            const h = document.createElement('input');
            h.type = 'hidden';
            h.name = 'companies';
            h.value = name;
            form.appendChild(h);
        });
    }

    function render() {
        field.querySelectorAll('.tag-pill').forEach(el => el.remove());

        tags.forEach((name, i) => {
            const pill = document.createElement('span');
            pill.className = 'tag-pill';
            pill.innerHTML =
                `<span>${esc(name)}</span>` +
                `<button type="button" class="tag-x" data-i="${i}" aria-label="${esc(name)} 삭제">✕</button>`;
            field.insertBefore(pill, textInput);
        });

        const hasTag = tags.length > 0;
        const atMax  = tags.length >= MAX_TAGS;

        countEl.style.display  = hasTag ? '' : 'none';
        countEl.textContent    = `${tags.length}/${MAX_TAGS}`;
        countEl.classList.toggle('warn', atMax);

        resetBtn.style.display = hasTag ? '' : 'none';
        submitBtn.disabled     = !hasTag;

        textInput.disabled    = atMax;
        textInput.placeholder = tags.length === 0
            ? '예: 삼성전자, 카카오, 현대차…'
            : atMax ? '' : '추가 입력…';

        field.classList.toggle('is-max', atMax);
        syncHidden();
    }

    function addTag(raw) {
        const value = raw.trim().replace(/,+$/, '').trim();
        if (!value || tags.length >= MAX_TAGS) return false;

        const idx = tags.indexOf(value);
        if (idx !== -1) {
            const pill = field.querySelectorAll('.tag-pill')[idx];
            if (pill) {
                pill.classList.remove('dup');
                void pill.offsetWidth; // 리플로우로 애니메이션 재시작
                pill.classList.add('dup');
                setTimeout(() => pill.classList.remove('dup'), 350);
            }
            return false;
        }

        tags.push(value);
        render();
        return true;
    }

    function removeTag(i) {
        tags.splice(i, 1);
        render();
        if (!textInput.disabled) textInput.focus();
    }

    function clearTagsAll() {
        tags = [];
        render();
        textInput.focus();
    }

    let acIdx = -1;
    let acItems = [];

    function filterCompanies(query) {
        if (!query) return [];
        const results = [];
        for (const c of COMPANIES) {
            if (tags.includes(c.name)) continue;
            const ni = c.name.indexOf(query);
            const ci = c.code.startsWith(query);
            if (ni !== -1 || ci) {
                results.push({ ...c, score: ni === 0 ? 0 : 1 });
            }
        }
        results.sort((a, b) => a.score - b.score || a.name.length - b.name.length);
        return results.slice(0, 7);
    }

    function openDropdown(matches, query) {
        closeDropdown();
        acItems = matches;
        acIdx   = -1;

        const dd = document.createElement('div');
        dd.id        = 'ac-dd';
        dd.className = 'ac-dropdown';

        // 드롭다운 클릭 시 blur 이벤트 방지
        dd.addEventListener('mousedown', e => e.preventDefault());

        if (matches.length === 0) {
            dd.innerHTML = `<div class="ac-empty">일치하는 기업이 없습니다</div>`;
        } else {
            matches.forEach((c, i) => {
                const item = document.createElement('div');
                item.className = 'ac-item';
                item.innerHTML =
                    `<span class="ac-name">${hlText(c.name, query)}</span>` +
                    `<span class="ac-code">${esc(c.code)}</span>` +
                    `<span class="ac-sector">${esc(c.sector)}</span>` +
                    `<span class="ac-market">${esc(c.market)}</span>`;

                item.addEventListener('click', () => {
                    addTag(c.name);
                    textInput.value = '';
                    closeDropdown();
                    textInput.focus();
                });
                item.addEventListener('mouseenter', () => {
                    acIdx = i;
                    updateActive();
                });
                dd.appendChild(item);
            });

            const footer = document.createElement('div');
            footer.className = 'ac-footer';
            footer.innerHTML =
                `<kbd>↑</kbd><kbd>↓</kbd> 이동 ` +
                `<span class="dot">·</span> ` +
                `<kbd>Enter</kbd> 선택 ` +
                `<span class="dot">·</span> ` +
                `<kbd>Esc</kbd> 닫기`;
            dd.appendChild(footer);
        }

        acWrap.appendChild(dd);
    }

    function closeDropdown() {
        const dd = document.getElementById('ac-dd');
        if (dd) dd.remove();
        acIdx   = -1;
        acItems = [];
    }

    function updateActive() {
        document.querySelectorAll('#ac-dd .ac-item').forEach((el, i) => {
            el.classList.toggle('is-active', i === acIdx);
        });
    }

    function hlText(text, query) {
        const idx = text.indexOf(query);
        if (idx === -1) return esc(text);
        return (
            esc(text.slice(0, idx)) +
            `<mark>${esc(text.slice(idx, idx + query.length))}</mark>` +
            esc(text.slice(idx + query.length))
        );
    }

    textInput.addEventListener('keydown', e => {
        // 한글 IME 조합 중 엔터 중복 트리거 방지
        if (e.isComposing) return;

        const isOpen  = !!document.getElementById('ac-dd');
        const itemEls = document.querySelectorAll('#ac-dd .ac-item');

        if (isOpen) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                acIdx = Math.min(acIdx + 1, itemEls.length - 1);
                updateActive();
                return;
            }
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                acIdx = Math.max(acIdx - 1, -1);
                updateActive();
                return;
            }
            if (e.key === 'Escape') {
                e.preventDefault();
                closeDropdown();
                return;
            }
            if (e.key === 'Tab' && acIdx === -1 && itemEls[0]) {
                e.preventDefault();
                itemEls[0].click();
                return;
            }
            if (e.key === 'Enter' && acIdx >= 0 && itemEls[acIdx]) {
                e.preventDefault();
                itemEls[acIdx].click();
                return;
            }
        }

        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            if (textInput.value.trim()) {
                addTag(textInput.value);
                textInput.value = '';
                closeDropdown();
            }
        } else if (e.key === 'Backspace' && textInput.value === '' && tags.length > 0) {
            removeTag(tags.length - 1);
        }
    });

    textInput.addEventListener('input', () => {
        // 쉼표 포함 붙여넣기 처리
        if (textInput.value.includes(',')) {
            const parts = textInput.value.split(',');
            parts.forEach((p, i) => { if (i < parts.length - 1) addTag(p); });
            textInput.value = parts[parts.length - 1].trimStart();
            closeDropdown();
            return;
        }

        const q = textInput.value.trim();
        if (q.length >= 1) {
            openDropdown(filterCompanies(q), q);
        } else {
            closeDropdown();
        }
    });

    textInput.addEventListener('blur', () => {
        closeDropdown();
    });

    // 태그 X 버튼 (이벤트 위임)
    field.addEventListener('click', e => {
        const btn = e.target.closest('.tag-x');
        if (!btn) return;
        e.stopPropagation();
        removeTag(Number(btn.dataset.i));
        const q = textInput.value.trim();
        if (q.length >= 1) openDropdown(filterCompanies(q), q);
    });

    // 바깥 클릭 → 드롭다운 닫기
    document.addEventListener('mousedown', e => {
        if (!acWrap.contains(e.target)) closeDropdown();
    });

    form.addEventListener('submit', e => {
        if (tags.length === 0) {
            e.preventDefault();
            textInput.focus();
        }
    });

    function esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function handleFieldClick(e) {
        if (!e.target.closest('.tag-x') && !textInput.disabled) {
            textInput.focus();
        }
    }

    window.clearTagsAll    = clearTagsAll;
    window.handleFieldClick = handleFieldClick;

    render();

})();
