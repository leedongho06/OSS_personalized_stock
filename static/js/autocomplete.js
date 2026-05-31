(() => {
    // 1단계에서 분리한 JSON 데이터를 저장할 변수
    let COMPANIES = [];

    // Tag 상태 및 엘리먼트 정의
    const MAX = 10;
    let tags = [];

    const acWrap    = document.querySelector('.ac-wrap');
    const field     = document.getElementById('tag-field');
    const textInput = document.getElementById('tag-text');
    const countEl   = document.getElementById('tag-count');
    const resetBtn  = document.getElementById('reset-btn');
    const submitBtn = document.getElementById('submit-btn');
    const form      = document.getElementById('rec-form');

    // 태그 렌더링
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
        const atMax  = tags.length >= MAX;
        countEl.style.display  = hasTag ? '' : 'none';
        countEl.textContent    = `${tags.length}/${MAX}`;
        countEl.classList.toggle('warn', atMax);
        resetBtn.style.display = hasTag ? '' : 'none';
        submitBtn.disabled     = !hasTag;
        textInput.disabled    = atMax;
        textInput.placeholder = tags.length === 0 ? '예: 삼성전자, 카카오, 현대차…'
                              : atMax ? '' : '추가 입력…';
        field.classList.toggle('is-max', atMax);
        syncHidden();
    }

    function syncHidden() {
        form.querySelectorAll('input[name="companies"]').forEach(el => el.remove());
        tags.forEach(name => {
            const h = document.createElement('input');
            h.type = 'hidden'; h.name = 'companies'; h.value = name;
            form.appendChild(h);
        });
    }

    function addTag(raw) {
        const value = raw.trim().replace(/,+$/, '').trim();
        if (!value || tags.length >= MAX) return false;
        const idx = tags.indexOf(value);
        if (idx !== -1) {
            const pill = field.querySelectorAll('.tag-pill')[idx];
            if (pill) {
                pill.classList.remove('dup');
                void pill.offsetWidth;
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

    // Autocomplete 로직
    let acIdx = -1;          
    let acItems = [];        
    let mouseInDrop = false; 

    function filterCompanies(q) {
        if (!q) return [];
        const results = [];
        for (const c of COMPANIES) {
            if (tags.includes(c.name)) continue;  
            const ni = c.name.indexOf(q);
            const ci = c.code.startsWith(q);
            if (ni !== -1 || ci) {
                results.push({ ...c, score: ni === 0 ? 0 : 1 });
            }
        }
        results.sort((a, b) => a.score - b.score || a.name.length - b.name.length);
        return results.slice(0, 7);
    }

    function openDropdown(matches, query) {
        closeDropdown(false);
        acItems = matches;
        acIdx   = -1;

        const dd = document.createElement('div');
        dd.id = 'ac-dd';
        dd.className = 'ac-dropdown';
        dd.addEventListener('mouseenter', () => { mouseInDrop = true; });
        dd.addEventListener('mouseleave', () => { mouseInDrop = false; });

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
                
                item.addEventListener('mousedown', e => {
                    e.preventDefault();
                    mouseInDrop = true;
                });
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
            footer.innerHTML = `<kbd>↑</kbd><kbd>↓</kbd> 이동 <span class="dot">·</span> <kbd>Enter</kbd> 선택 <span class="dot">·</span> <kbd>Esc</kbd> 닫기`;
            dd.appendChild(footer);
        }

        acWrap.appendChild(dd);
    }

    function closeDropdown(resetMouse = true) {
        const dd = document.getElementById('ac-dd');
        if (dd) dd.remove();
        acIdx = -1; acItems = [];
        if (resetMouse) mouseInDrop = false;
    }

    function updateActive() {
        document.querySelectorAll('#ac-dd .ac-item').forEach((el, i) => {
            el.classList.toggle('is-active', i === acIdx);
        });
    }

    function hlText(text, query) {
        const idx = text.indexOf(query);
        if (idx === -1) return esc(text);
        return esc(text.slice(0, idx)) +
               `<mark>${esc(text.slice(idx, idx + query.length))}</mark>` +
               esc(text.slice(idx + query.length));
    }

    // 이벤트 리스너 바인딩
    textInput.addEventListener('keydown', e => {
        const ddOpen = !!document.getElementById('ac-dd');
        const itemEls = document.querySelectorAll('#ac-dd .ac-item');

        if (ddOpen) {
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
        if (mouseInDrop) return;
        closeDropdown();
    });

    field.addEventListener('click', e => {
        const btn = e.target.closest('.tag-x');
        if (btn) {
            e.stopPropagation();
            removeTag(Number(btn.dataset.i));
            const q = textInput.value.trim();
            if (q.length >= 1) openDropdown(filterCompanies(q), q);
        }
    });

    function handleFieldClick(e) {
        if (!e.target.closest('.tag-x') && !textInput.disabled) {
            textInput.focus();
        }
    }

    document.addEventListener('mousedown', e => {
        if (!acWrap.contains(e.target)) closeDropdown();
    });

    form.addEventListener('submit', e => {
        if (tags.length === 0) { e.preventDefault(); textInput.focus(); }
    });

    function esc(str) {
        return String(str)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // 인라인 HTML 호출용 전역 스코프 매핑 & JSON fetch 초기화
    window.clearTagsAll = clearTagsAll;
    window.handleFieldClick = handleFieldClick;

    // 초기 실행 시 비동기로 상장사 정보 load
    fetch('/static/js/companies.json')
        .then(response => {
            if (!response.ok) throw new Error('네트워크 응답 오류');
            return response.json();
        })
        .then(data => {
            COMPANIES = data; // 가져온 데이터를 상단 전역 배열에 할당
            render();         // 초기 렌더링 시작
        })
        .catch(error => {
            console.error('상장사 데이터를 로드하지 못했습니다:', error);
        });
