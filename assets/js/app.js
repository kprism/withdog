(()=>{const slides=[...document.querySelectorAll('.hero-slide')],slideNo=document.querySelector('#slideNo'),pauseBtn=document.querySelector('#pauseBtn');let current=0,playing=true,timer;function show(index){current=(index+slides.length)%slides.length;slides.forEach((s,i)=>s.classList.toggle('active',i===current));if(slideNo)slideNo.textContent=current+1;}function start(){clearInterval(timer);timer=setInterval(()=>show(current+1),5000);}document.querySelectorAll('[data-dir]').forEach(btn=>btn.addEventListener('click',()=>{show(current+Number(btn.dataset.dir));if(playing)start();}));pauseBtn?.addEventListener('click',()=>{playing=!playing;pauseBtn.textContent=playing?'Ⅱ':'▶';playing?start():clearInterval(timer);});document.querySelector('.mobile-menu')?.addEventListener('click',()=>document.querySelector('.quick-nav')?.scrollIntoView({behavior:'smooth'}));if(!document.querySelector('link[href*="auth-modal.css"]')){const l=document.createElement('link');l.rel='stylesheet';l.href='./assets/css/auth-modal.css?v=20261008-terms-v1';document.head.appendChild(l);}const wrap=document.createElement('div');wrap.innerHTML=`<div class="auth-overlay" id="authOverlay"><div class="auth-modal"><header class="auth-head"><h2 id="authTitle">로그인</h2><button class="auth-close" id="authClose">×</button></header><nav class="auth-tabs"><button class="auth-tab" data-auth="login">로그인</button><button class="auth-tab" data-auth="member">회원가입</button><button class="auth-tab" data-auth="partner">제휴업체 등록</button></nav><div class="auth-body"><section class="auth-panel" data-panel="login"><form class="auth-form"><label>이메일<input type="email" placeholder="example@email.com"></label><label>비밀번호<input type="password"></label><button class="auth-submit">로그인</button><p class="auth-message"></p></form></section><section class="auth-panel" data-panel="member"><form class="auth-form"><label>이름<input placeholder="홍길동"></label><div class="auth-grid"><label>생년월일<input placeholder="예) 1999.01.20"></label><label>성별<select><option>남성</option><option>여성</option></select></label></div><label>전화번호<input placeholder="010-0000-0000"></label><label>이메일 (로그인 아이디로 사용)<input type="email" placeholder="example@email.com"></label><div class="auth-grid"><label>비밀번호<input type="password"></label><label>비밀번호 확인<input type="password"></label></div><div class="kakao-address"><label>주소</label><div class="postcode-row"><input data-postcode readonly placeholder="우편번호"><button type="button" class="address-search-btn" data-address-search>주소검색</button></div><input data-road-address readonly placeholder="도로명 또는 지번 주소"><input data-address-detail placeholder="상세주소를 입력하세요"></div><div class="terms-consent"><label class="auth-check terms-select-all"><input type="checkbox" data-agree-all><span>모두선택</span></label><div class="term-item"><label class="auth-check"><input type="checkbox" data-agreement="privacy"><span><b>[필수]</b> <button type="button" class="term-link" data-term-toggle="privacy" aria-expanded="false">개인정보처리방침</button> 동의</span></label><div class="term-detail" data-term-panel="privacy" hidden><b>개인정보처리방침</b><p>협회는 회원가입 및 회원관리, 본인확인, 회원증 발급과 서비스 제공을 위해 성명, 생년월일, 성별, 연락처, 이메일, 주소 등 가입 과정에서 입력한 정보를 수집·이용합니다.</p><p>수집된 정보는 회원 탈퇴 시까지 보관하는 것을 원칙으로 하며, 관계 법령에 따라 보존이 필요한 정보는 해당 기간 동안 별도 보관할 수 있습니다. 개인정보 수집·이용에 동의하지 않을 수 있으나, 필수정보 동의를 거부할 경우 회원가입이 제한될 수 있습니다.</p></div></div><div class="term-item"><label class="auth-check"><input type="checkbox" data-agreement="terms"><span><b>[필수]</b> <button type="button" class="term-link" data-term-toggle="terms" aria-expanded="false">웹사이트 이용약관</button> 동의</span></label><div class="term-detail" data-term-panel="terms" hidden><b>웹사이트 이용약관</b><p>회원은 정확한 정보를 제공하고 본인의 계정을 안전하게 관리해야 하며, 타인의 권리를 침해하거나 서비스 운영을 방해하는 행위를 해서는 안 됩니다.</p><p>협회는 서비스 품질 개선이나 운영상 필요에 따라 웹사이트의 일부 기능과 콘텐츠를 변경할 수 있으며, 중요한 변경사항은 가능한 범위에서 사전에 안내합니다.</p></div></div><div class="term-item"><label class="auth-check"><input type="checkbox" data-agreement="rules"><span><b>[필수]</b> <button type="button" class="term-link" data-term-toggle="rules" aria-expanded="false">[협회] 회원규칙</button> 동의</span></label><div class="term-detail" data-term-panel="rules" hidden><b>경상남도 반려견 협회 회원규칙</b><p>회원은 협회의 목적과 운영질서를 존중하고 회원정보를 사실대로 유지하며, 협회와 다른 회원의 명예 또는 권익을 침해하는 행위를 하지 않아야 합니다.</p><p>정회원 혜택과 온라인 회원증은 정해진 연회비 및 회원정책에 따라 제공되며, 연회비는 1년 단위로 갱신됩니다. 회원은 탈퇴를 요청할 수 있으며, 이미 납부한 연회비는 안내된 환불정책에 따릅니다.</p></div></div></div><label class="auth-check"><input type="checkbox" data-regular-member><span><b>[선택]</b> 가입과 함께 연회비를 납부하고 정회원 혜택 및 회원증을 발급받고 싶습니다.</span></label><div class="fee-box"><strong>💳 연회비 안내</strong><h3>연회비 30,000원</h3><p>가입 후 아래 계좌로 연회비를 입금해주시면, <b>1년 유효기간</b>의 온라인 회원증이 마이페이지에 자동 발급됩니다.</p><p class="refund-note">가입 후 환불은 불가합니다. 1년마다 갱신되며, 별도 연락 없을 시 자동갱신 됩니다.</p><div class="account">입금계좌 : 농협 351-2027-0000-43<br>(예금주 : 경상남도 반려견 협회)</div><a class="benefit-link" href="benefits.html">🎁 회원 혜택 자세히 보기 →</a></div><button class="auth-submit">회원가입</button><p class="auth-message"></p></form></section><section class="auth-panel" data-panel="partner"><form class="auth-form"><div class="auth-note">동물병원·미용센터·용품점 등 반려동물 관련 업체의 제휴 신청 폼입니다.</div><label>업체명<input placeholder="예) 경남동물병원"></label><div class="auth-grid"><label>업종<select><option>동물병원</option><option>미용센터</option><option>용품점</option></select></label><label>대표자명<input></label></div><label>연락처<input placeholder="010-0000-0000"></label><label>이메일<input type="email"></label><label>업체 주소<input></label><label>제휴 제안 내용<textarea></textarea></label><button class="auth-submit">제휴 신청하기</button><p class="auth-message"></p></form></section></div></div></div>`;document.body.appendChild(wrap.firstElementChild);const overlay=document.getElementById('authOverlay'),title=document.getElementById('authTitle'),tabs=[...overlay.querySelectorAll('.auth-tab')],panels=[...overlay.querySelectorAll('.auth-panel')],authBody=overlay.querySelector('.auth-body');function activate(type){tabs.forEach(t=>t.classList.toggle('active',t.dataset.auth===type));panels.forEach(p=>p.classList.toggle('active',p.dataset.panel===type));title.textContent=type==='login'?'로그인':type==='member'?'회원가입':'제휴업체 등록';authBody.scrollTop=0;}function openAuth(type){activate(type);overlay.classList.add('open');document.body.style.overflow='hidden';}function closeAuth(){overlay.classList.remove('open');document.body.style.overflow='';}tabs.forEach(t=>t.addEventListener('click',()=>activate(t.dataset.auth)));document.getElementById('authClose').addEventListener('click',closeAuth);overlay.addEventListener('mousedown',e=>{if(e.target===overlay)closeAuth();});document.addEventListener('keydown',e=>{if(e.key==='Escape')closeAuth();});

function loadDaumPostcode(){
    if(window.daum?.Postcode) return Promise.resolve();
    return new Promise((resolve,reject)=>{
        const existing=document.querySelector('script[data-daum-postcode]');
        if(existing){existing.addEventListener('load',resolve,{once:true});existing.addEventListener('error',reject,{once:true});return;}
        const script=document.createElement('script');
        script.src='https://t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js';
        script.async=true;script.dataset.daumPostcode='1';script.onload=resolve;script.onerror=reject;document.head.appendChild(script);
    });
}

overlay.addEventListener('click',async e=>{
    const button=e.target.closest('[data-address-search]');
    if(!button)return;
    try{
        await loadDaumPostcode();
        new daum.Postcode({oncomplete(data){
            const form=button.closest('form');
            const postcode=form.querySelector('[data-postcode]');
            const address=form.querySelector('[data-road-address]');
            const detail=form.querySelector('[data-address-detail]');
            postcode.value=data.zonecode||'';
            address.value=data.roadAddress||data.jibunAddress||'';
            address.dataset.sido=data.sido||'';
            address.dataset.sigungu=data.sigungu||'';
            detail.focus();
        }}).open();
    }catch(_){alert('주소 검색 서비스를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.');}
});

overlay.addEventListener('change', e=>{
    if(e.target.matches('[data-agree-all]')){
        const checked=e.target.checked;
        overlay.querySelectorAll('[data-agreement]').forEach(box=>{box.checked=checked;});
        return;
    }
    if(e.target.matches('[data-agreement]')){
        const boxes=[...overlay.querySelectorAll('[data-agreement]')];
        const all=overlay.querySelector('[data-agree-all]');
        if(all){
            const count=boxes.filter(box=>box.checked).length;
            all.checked=count===boxes.length;
            all.indeterminate=count>0 && count<boxes.length;
        }
    }
});

overlay.addEventListener('click',e=>{
    const toggle=e.target.closest('[data-term-toggle]');
    if(!toggle)return;
    e.preventDefault();
    e.stopPropagation();
    const key=toggle.dataset.termToggle;
    const panel=overlay.querySelector('[data-term-panel="'+key+'"]');
    if(!panel)return;
    const opening=panel.hidden;
    overlay.querySelectorAll('[data-term-panel]').forEach(item=>{item.hidden=true;});
    overlay.querySelectorAll('[data-term-toggle]').forEach(item=>item.setAttribute('aria-expanded','false'));
    panel.hidden=!opening;
    toggle.setAttribute('aria-expanded',opening?'true':'false');
});

/* === CSRF SUPPORT === */

function getCookie(name){
    let cookieValue = null;

    if(document.cookie && document.cookie !== ''){
        const cookies = document.cookie.split(';');

        for(let cookie of cookies){
            cookie = cookie.trim();

            if(cookie.startsWith(name + '=')){
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}


async function ensureCsrfCookie(){
    let token = getCookie('csrftoken');

    if(token){
        return token;
    }

    const response = await fetch('/api/csrf/', {
        method: 'GET',
        credentials: 'same-origin',
        cache: 'no-store'
    });

    if(!response.ok){
        throw new Error(
            '보안 토큰을 발급받지 못했습니다.'
        );
    }

    token = getCookie('csrftoken');

    if(!token){
        throw new Error(
            '보안 토큰 쿠키를 확인할 수 없습니다.'
        );
    }

    return token;
}


/* === REAL AUTH SUBMIT === */

function showJoinSuccess(email){
    closeAuth();

    const old = document.getElementById('joinSuccessOverlay');
    if(old) old.remove();

    const success = document.createElement('div');
    success.id = 'joinSuccessOverlay';
    success.className = 'join-success-overlay';

    success.innerHTML = `
      <div class="join-success-modal">
        <div class="join-success-icon">🎉</div>
        <h2>가입을 축하드립니다.</h2>
        <p>
          경상남도 반려견 협회 회원가입이<br>
          정상적으로 완료되었습니다.
        </p>
        <div class="join-success-email"></div>
        <button type="button" class="join-success-login">
          로그인
        </button>
      </div>
    `;

    success.querySelector('.join-success-email').textContent = email;

    document.body.appendChild(success);
    document.body.style.overflow = 'hidden';

    success.querySelector('.join-success-login')
      .addEventListener('click', () => {
          success.remove();
          document.body.style.overflow = '';
          openAuth('login');

          const loginEmail = overlay.querySelector(
              '[data-panel="login"] input[type="email"]'
          );

          if(loginEmail) loginEmail.value = email;
      });
}


overlay.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', async e => {
        e.preventDefault();

        const panel = form.closest('.auth-panel');
        const type = panel?.dataset.panel;
        const msg = form.querySelector('.auth-message');

        // 실제 회원 로그인
        if(type === 'login'){
            const inputs = form.querySelectorAll('input');
            const email = inputs[0]?.value.trim() || '';
            const password = inputs[1]?.value || '';

            if(!email || !password){
                if(msg) msg.textContent =
                    '이메일과 비밀번호를 입력해 주세요.';
                return;
            }

            const button = form.querySelector('.auth-submit');
            const original = button.textContent;

            button.disabled = true;
            button.textContent = '로그인 중...';
            if(msg) msg.textContent = '';

            try{
                const csrfToken = await ensureCsrfCookie();

                const response = await fetch('/api/member-login/', {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        email,
                        password
                    })
                });

                let data = {};

                try{
                    data = await response.json();
                }catch(_){}

                if(!response.ok || !data.ok){
                    throw new Error(
                        data.message || '로그인에 실패했습니다.'
                    );
                }

                form.reset();
                closeAuth();

                await refreshMemberSession();
if(location.hash==='#join') setTimeout(()=>openAuth('member'),0);

            }catch(error){
                if(msg){
                    msg.textContent =
                        error.message || '로그인에 실패했습니다.';
                }
            }finally{
                button.disabled = false;
                button.textContent = original;
            }

            return;
        }

        // 제휴업체 등록은 별도 구현
        if(type === 'partner'){
            if(msg){
                msg.textContent =
                    '제휴 신청 기능은 다음 단계에서 연결합니다.';
            }
            return;
        }

        if(type !== 'member') return;

        const inputs = form.querySelectorAll('input');
        const selects = form.querySelectorAll('select');

        const name = inputs[0]?.value.trim() || '';
        const birth_date = inputs[1]?.value.trim() || '';
        const phone = inputs[2]?.value.trim() || '';
        const email = inputs[3]?.value.trim() || '';
        const password = inputs[4]?.value || '';
        const password2 = inputs[5]?.value || '';
        const roadAddress = form.querySelector('[data-road-address]');
        const detailAddress = form.querySelector('[data-address-detail]');
        const postcode = form.querySelector('[data-postcode]')?.value.trim() || '';
        const baseAddress = roadAddress?.value.trim() || '';
        const detailValue = detailAddress?.value.trim() || '';
        const address_detail = [baseAddress, detailValue].filter(Boolean).join(' ');

        const privacy = form.querySelector('[data-agreement="privacy"]')?.checked || false;
        const termsAgreed = form.querySelector('[data-agreement="terms"]')?.checked || false;
        const rulesAgreed = form.querySelector('[data-agreement="rules"]')?.checked || false;
        const regular = form.querySelector('[data-regular-member]')?.checked || false;

        const genderText = selects[0]?.value || '';
        const region = [roadAddress?.dataset.sido, roadAddress?.dataset.sigungu].filter(Boolean).join(' ') || baseAddress.split(' ').slice(0,2).join(' ');

        let gender = '';
        if(genderText === '남성') gender = 'M';
        else if(genderText === '여성') gender = 'F';
        else if(genderText === '기타') gender = 'O';

        if(!name || !phone || !email || !password){
            if(msg) msg.textContent =
                '필수 정보를 모두 입력해 주세요.';
            return;
        }

        if(!baseAddress){
            if(msg) msg.textContent = '주소검색을 눌러 주소를 선택해 주세요.';
            return;
        }

        if(password !== password2){
            if(msg) msg.textContent =
                '비밀번호가 서로 일치하지 않습니다.';
            return;
        }

        if(password.length < 6){
            if(msg) msg.textContent =
                '비밀번호는 6자 이상 입력해 주세요.';
            return;
        }

        if(!privacy || !termsAgreed || !rulesAgreed){
            if(msg) msg.textContent =
                '개인정보처리방침, 웹사이트 이용약관, 협회 회원규칙에 모두 동의해 주세요.';
            return;
        }

        const button = form.querySelector('.auth-submit');
        const original = button.textContent;

        button.disabled = true;
        button.textContent = '가입 처리 중...';

        if(msg) msg.textContent = '';

        try{
            const csrfToken = await ensureCsrfCookie();

            const response = await fetch('/api/member-register/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    name,
                    birth_date,
                    gender,
                    phone,
                    email,
                    password,
                    region,
                    address_detail,
                    privacy_agreed: privacy,
                    regular_member_requested: regular
                })
            });

            let data = {};

            try{
                data = await response.json();
            }catch(_){}

            if(!response.ok || !data.ok){
                throw new Error(
                    data.message || '회원가입에 실패했습니다.'
                );
            }

            form.reset();
            if(data.payment_required && data.payment){
                try{
                    const clientKey=data.payment.client_key || '';
                    const isV1Key=/^(test|live)_ck_/.test(clientKey);
                    const sdkSrc=isV1Key ? 'https://js.tosspayments.com/v1/payment' : 'https://js.tosspayments.com/v2/standard';
                    if(!window.TossPayments){
                        await new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=sdkSrc;s.onload=resolve;s.onerror=reject;document.head.appendChild(s);});
                    }
                    const tossPayments=TossPayments(clientKey);
                    const common={amount:data.payment.amount,orderId:data.payment.order_id,orderName:data.payment.order_name,customerName:data.payment.customer_name,customerEmail:data.payment.customer_email,successUrl:location.origin+'/api/payments/success/',failUrl:location.origin+'/api/payments/fail/'};
                    if(isV1Key){
                        await tossPayments.requestPayment('카드',common);
                    }else{
                        const payment=tossPayments.payment({customerKey:TossPayments.ANONYMOUS});
                        await payment.requestPayment({method:'CARD',amount:{currency:'KRW',value:data.payment.amount},orderId:data.payment.order_id,orderName:data.payment.order_name,customerName:data.payment.customer_name,customerEmail:data.payment.customer_email,successUrl:common.successUrl,failUrl:common.failUrl});
                    }
                }catch(error){
                    if(msg) msg.textContent=error?.message || '결제창을 열지 못했습니다.';
                }
            }else{
                showJoinSuccess(data.email || email);
                if(data.payment_message && msg) msg.textContent=data.payment_message;
            }

        }catch(error){
            if(msg){
                msg.textContent =
                    error.message || '회원가입에 실패했습니다.';
            }
        }finally{
            button.disabled = false;
            button.textContent = original;
        }
    });
});


// ============================================================
// MEMBER SESSION / HEADER
// ============================================================

const headerActions = document.querySelector('.header-actions');

function escapeMemberHtml(value){
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function renderGuestHeader(){
    if(!headerActions) return;

    headerActions.innerHTML = `
        <button type="button" class="auth-link" data-member-login>로그인</button>
        <button type="button" class="auth-link auth-link--accent" data-member-join>회원가입</button>
    `;

    headerActions
        .querySelector('[data-member-login]')
        ?.addEventListener('click', () => openAuth('login'));

    headerActions
        .querySelector('[data-member-join]')
        ?.addEventListener('click', () => openAuth('member'));
}

function renderMemberHeader(user){
    if(!headerActions) return;

    const name = escapeMemberHtml(
        user?.name || user?.email || '회원'
    );

    headerActions.innerHTML = `
        <span class="member-welcome" style="font-weight:700;white-space:nowrap">${name}님</span>
        <button type="button" class="auth-link auth-link--mypage" data-member-mypage>마이페이지</button>
        <button type="button" class="auth-link auth-link--accent" data-member-logout>로그아웃</button>
    `;

    headerActions
        .querySelector('[data-member-mypage]')
        ?.addEventListener('click', () => {
            openMemberMyPage();
        });

    headerActions
        .querySelector('[data-member-logout]')
        ?.addEventListener('click', logoutMember);
}

async function openMemberMyPage(){
 try{
  const response=await fetch('/api/member-mypage/',{credentials:'same-origin',cache:'no-store'}),data=await response.json();if(!response.ok||!data.ok)throw new Error(data.message||'마이페이지를 불러오지 못했습니다.');
  const u=data.user,old=document.getElementById('memberMyPage');if(old)old.remove();const el=document.createElement('div');el.id='memberMyPage';el.className='member-mypage-overlay';
  let card='<div class="member-status-box">현재 회원구분: '+escapeMemberHtml(u.membership_status)+'</div>';
  if(u.membership_status==='regular')card='<div class="digital-member-card"><small>NO '+escapeMemberHtml(u.member_no)+'</small><h2>경상남도 반려견협회 정회원증</h2><h3>'+escapeMemberHtml(u.name)+'</h3><dl><div><dt>생년월일</dt><dd>'+escapeMemberHtml(u.birth_date)+'</dd></div><div><dt>주소</dt><dd>'+escapeMemberHtml(u.address_short)+'</dd></div><div><dt>연락처</dt><dd>'+escapeMemberHtml(u.phone)+'</dd></div><div><dt>성별</dt><dd>'+escapeMemberHtml(u.gender)+'</dd></div></dl><b>경상남도 반려견협회</b></div><p class="member-card-guide">해당 업체에서 회원증을 제시하면 회원혜택을 받을 수 있습니다.</p><div class="member-share-actions"><button type="button" data-share-card>카카오톡/공유</button><a data-email-card>이메일로 보내기</a></div>';
  el.innerHTML='<div class="member-mypage-modal"><button class="mypage-close" type="button">×</button><h2>마이페이지</h2>'+card+'<button class="member-withdraw-btn" type="button">회원탈퇴</button></div>';document.body.appendChild(el);document.body.style.overflow='hidden';
  el.querySelector('.mypage-close').onclick=()=>{el.remove();document.body.style.overflow=''};
  el.querySelector('[data-share-card]')?.addEventListener('click',async()=>{const share={title:'경상남도 반려견협회 회원증',text:u.name+'님의 경상남도 반려견협회 온라인 회원증',url:location.href};if(navigator.share){try{await navigator.share(share)}catch(_){}}else{await navigator.clipboard.writeText(location.href);alert('회원증 페이지 주소를 복사했습니다. 카카오톡에 붙여넣어 주세요.')}});
  const email=el.querySelector('[data-email-card]');if(email)email.href='mailto:'+encodeURIComponent(u.email)+'?subject='+encodeURIComponent('경상남도 반려견협회 회원증')+'&body='+encodeURIComponent('경상남도 반려견협회 온라인 회원증은 마이페이지에서 확인할 수 있습니다. '+location.origin);
  el.querySelector('.member-withdraw-btn').onclick=async()=>{if(!confirm('회원탈퇴 시 로그인이 차단됩니다. 정말 탈퇴하시겠습니까?'))return;const csrfToken=await ensureCsrfCookie();const r=await fetch('/api/member-withdraw/',{method:'POST',credentials:'same-origin',headers:{'X-CSRFToken':csrfToken}}),d=await r.json();if(!r.ok||!d.ok){alert(d.message||'탈퇴 처리에 실패했습니다.');return}alert('회원탈퇴가 완료되었습니다.');el.remove();document.body.style.overflow='';renderGuestHeader()};
 }catch(e){alert(e.message||'마이페이지를 불러오지 못했습니다.')}
}

async function refreshMemberSession(){
    try{
        const response = await fetch(
            '/api/member-session/',
            {
                method: 'GET',
                credentials: 'same-origin',
                cache: 'no-store'
            }
        );

        const data = await response.json();

        if(
            response.ok &&
            data.ok &&
            data.authenticated &&
            data.user
        ){
            renderMemberHeader(data.user);
            return data.user;
        }

    }catch(error){
        console.error('회원 세션 확인 실패:', error);
    }

    renderGuestHeader();
    return null;
}

async function logoutMember(){
    try{
        const csrfToken = await ensureCsrfCookie();

        const response = await fetch(
            '/api/member-logout/',
            {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            }
        );

        let data = {};

        try{
            data = await response.json();
        }catch(_){}

        if(!response.ok || !data.ok){
            throw new Error(
                data.message || '로그아웃에 실패했습니다.'
            );
        }

        renderGuestHeader();

    }catch(error){
        alert(
            error.message || '로그아웃에 실패했습니다.'
        );
    }
}


// 페이지 진입 시 Django 세션 확인
refreshMemberSession();
document.querySelectorAll('a[href="#join"],a[href="/#join"],.join .btn-gold,.footer-banner .btn-red').forEach(el=>el.addEventListener('click',e=>{e.preventDefault();openAuth('member');}));document.querySelector('.quick-nav a[href="#partners"]')?.addEventListener('click',e=>{e.preventDefault();location.href='partners.html';});document.querySelector('.quick-nav a[href="#about"]')?.addEventListener('click',e=>{e.preventDefault();location.href='about.html';});document.querySelectorAll('a[href="#benefits"],.btn-dark-outline').forEach(el=>el.addEventListener('click',e=>{e.preventDefault();location.href='benefits.html';}));
// Shared reveal motion: works automatically on current and future pages using these common components.
const motionGroups=[['.quick-nav a',55],['.stat-grid article',75],['.service-grid article',90],['.featured,.news-row',55],['.join-benefits span,.join-benefits>div',70],['.footer-banner',0]];const observed=[];motionGroups.forEach(([selector,step])=>{document.querySelectorAll(selector).forEach((el,i)=>{el.classList.add('reveal-motion');el.style.transitionDelay=`${Math.min(i*step,320)}ms`;observed.push(el);});});const revealObserver=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');revealObserver.unobserve(entry.target);}});},{threshold:.12,rootMargin:'0px 0px -25px 0px'});observed.forEach(el=>revealObserver.observe(el));
// Count-up for the four headline statistics while preserving suffix text such as 만+, 개소, 명, 개.
const counters=[...document.querySelectorAll('.stat-grid strong')];const countObserver=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(!entry.isIntersecting)return;const el=entry.target;if(el.dataset.counted)return;el.dataset.counted='1';const text=el.childNodes.length?el.childNodes[0].textContent:el.textContent;const digits=text.replace(/[^0-9]/g,'');if(!digits)return;const target=Number(digits),duration=720,start=performance.now(),suffix=text.replace(/[0-9,]/g,'');const small=el.querySelector('small');function tick(now){const p=Math.min((now-start)/duration,1),eased=1-Math.pow(1-p,3),value=Math.round(target*eased);if(el.childNodes[0])el.childNodes[0].textContent=value.toLocaleString()+suffix;else el.textContent=value.toLocaleString()+suffix;if(small&&!el.contains(small))el.appendChild(small);if(p<1)requestAnimationFrame(tick);}requestAnimationFrame(tick);countObserver.unobserve(el);});},{threshold:.5});counters.forEach(el=>countObserver.observe(el));
show(0);start();

/* === MEMBER RECOVERY + BIRTH DATE AUTO FORMAT ===
   Append inside the main app.js IIFE, before the final `})();`
*/

function recoveryEscape(value){
    return String(value ?? '')
        .replaceAll('&','&amp;')
        .replaceAll('<','&lt;')
        .replaceAll('>','&gt;')
        .replaceAll('"','&quot;')
        .replaceAll("'",'&#039;');
}

async function recoveryPost(url, payload){
    const csrfToken = await ensureCsrfCookie();
    const response = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(payload)
    });
    let data = {};
    try { data = await response.json(); } catch(_){}
    if(!response.ok || !data.ok){
        throw new Error(data.message || '처리 중 오류가 발생했습니다.');
    }
    return data;
}

function installRecoveryUI(){
    const loginForm = overlay.querySelector('[data-panel="login"] form');
    if(!loginForm || loginForm.querySelector('.member-recovery-links')) return;

    const submit = loginForm.querySelector('.auth-submit');
    const links = document.createElement('div');
    links.className = 'member-recovery-links';
    links.innerHTML = `
      <button type="button" data-recovery="id">아이디 찾기</button>
      <span>|</span>
      <button type="button" data-recovery="password">비밀번호 찾기</button>
    `;
    submit.insertAdjacentElement('afterend', links);

    function openRecovery(mode){
        document.getElementById('memberRecoveryOverlay')?.remove();

        const box = document.createElement('div');
        box.id = 'memberRecoveryOverlay';
        box.className = 'member-recovery-overlay';
        box.innerHTML = `
          <div class="member-recovery-modal">
            <div class="member-recovery-head">
              <h3>${mode === 'id' ? '아이디 찾기' : '비밀번호 찾기'}</h3>
              <button type="button" class="member-recovery-close">×</button>
            </div>
            <form class="member-recovery-form">
              <label>이름<input name="name" autocomplete="name" required></label>
              <label>연락처<input name="phone" inputmode="numeric"
                placeholder="010-0000-0000" required></label>
              ${mode === 'password' ? `
                <label>이메일<input name="email" type="email"
                  placeholder="example@email.com" required></label>
                <label>새 비밀번호<input name="password" type="password"
                  minlength="6" required></label>
                <label>새 비밀번호 확인<input name="password2" type="password"
                  minlength="6" required></label>` : ''}
              <button class="auth-submit" type="submit">
                ${mode === 'id' ? '아이디 확인' : '비밀번호 변경'}
              </button>
              <p class="member-recovery-message"></p>
            </form>
          </div>`;

        document.body.appendChild(box);
        const form = box.querySelector('form');
        const msg = box.querySelector('.member-recovery-message');

        const close = () => box.remove();
        box.querySelector('.member-recovery-close').onclick = close;
        box.addEventListener('mousedown', e => {
            if(e.target === box) close();
        });

        form.addEventListener('submit', async e => {
            e.preventDefault();
            msg.className = 'member-recovery-message';
            msg.textContent = '';

            const fd = new FormData(form);
            const button = form.querySelector('.auth-submit');
            const original = button.textContent;

            if(mode === 'password' &&
               fd.get('password') !== fd.get('password2')){
                msg.textContent = '새 비밀번호가 서로 일치하지 않습니다.';
                return;
            }

            button.disabled = true;
            button.textContent = '확인 중...';

            try{
                if(mode === 'id'){
                    const data = await recoveryPost('/api/member-find-id/', {
                        name: fd.get('name'),
                        phone: fd.get('phone')
                    });
                    msg.classList.add('success');
                    msg.innerHTML =
                        '가입 아이디는 <strong>' +
                        recoveryEscape(data.email) +
                        '</strong> 입니다.';
                }else{
                    const data = await recoveryPost('/api/member-reset-password/', {
                        name: fd.get('name'),
                        phone: fd.get('phone'),
                        email: fd.get('email'),
                        password: fd.get('password')
                    });
                    msg.classList.add('success');
                    msg.textContent = data.message;
                    setTimeout(() => {
                        close();
                        const emailInput = loginForm.querySelector('input[type="email"]');
                        if(emailInput) emailInput.value = fd.get('email');
                    }, 1200);
                }
            }catch(error){
                msg.textContent = error.message || '처리 중 오류가 발생했습니다.';
            }finally{
                button.disabled = false;
                button.textContent = original;
            }
        });
    }

    links.querySelector('[data-recovery="id"]')
        .addEventListener('click', () => openRecovery('id'));
    links.querySelector('[data-recovery="password"]')
        .addEventListener('click', () => openRecovery('password'));
}

function installBirthDateFormatter(){
    const memberForm = overlay.querySelector('[data-panel="member"] form');
    if(!memberForm) return;

    const inputs = memberForm.querySelectorAll('input');
    const birth = inputs[1];
    if(!birth || birth.dataset.birthFormatter === '1') return;

    birth.dataset.birthFormatter = '1';
    birth.placeholder = '예) 19990120';
    birth.inputMode = 'numeric';
    birth.maxLength = 10;

    birth.addEventListener('input', () => {
        const digits = birth.value.replace(/\D/g, '').slice(0, 8);
        let value = digits;
        if(digits.length > 4){
            value = digits.slice(0,4) + '-' + digits.slice(4);
        }
        if(digits.length > 6){
            value = digits.slice(0,4) + '-' +
                    digits.slice(4,6) + '-' + digits.slice(6);
        }
        birth.value = value;
    });
}

installRecoveryUI();
installBirthDateFormatter();

})();