(()=>{
'use strict';

if(window.__thePetChatbotBooted){
    return;
}
window.__thePetChatbotBooted = true;

const floats = Array.from(document.querySelectorAll('.bot-float'));
floats.slice(1).forEach(node=>node.remove());
document.querySelectorAll('.bot').forEach(node=>node.remove());

const oldButton = document.getElementById('botButton');

if(!oldButton){
    return;
}

let config = null;
let busy = false;


/* ------------------------------------------------------------
   CSRF
------------------------------------------------------------ */

function getCookie(name){

    const cookies = document.cookie
        ? document.cookie.split(';')
        : [];

    for(const item of cookies){

        const cookie = item.trim();

        if(cookie.startsWith(name + '=')){
            return decodeURIComponent(
                cookie.substring(name.length + 1)
            );
        }
    }

    return '';
}


/* ------------------------------------------------------------
   ESCAPE
------------------------------------------------------------ */

function escapeHtml(value){

    const div = document.createElement('div');

    div.textContent = value || '';

    return div.innerHTML;
}


/* ------------------------------------------------------------
   PHONE
------------------------------------------------------------ */

function cleanPhone(value){

    return String(value || '')
        .replace(/[^0-9+]/g, '');
}


/* ------------------------------------------------------------
   LOAD CONFIG
------------------------------------------------------------ */

async function loadConfig(){

    const response = await fetch(
        '/api/chatbot/config/',
        {
            credentials:'same-origin',
            cache:'no-store'
        }
    );

    if(!response.ok){
        throw new Error('CONFIG');
    }

    return await response.json();
}


/* ------------------------------------------------------------
   BOOT
------------------------------------------------------------ */

async function boot(){

    try{
        config = await loadConfig();
    }catch(error){
        console.error(
            'Chatbot configuration load failed.'
        );
        return;
    }

    if(!config.enabled){

        const floatBox = oldButton.closest(
            '.bot-float'
        );

        if(floatBox){
            floatBox.style.display = 'none';
        }

        return;
    }


    /* --------------------------------------------------------
       VIDEO BUTTON
    -------------------------------------------------------- */

    oldButton.innerHTML = '';

    if(config.video_url){

        const video = document.createElement('video');

        video.src = config.video_url;
        video.autoplay = true;
        video.loop = true;
        video.muted = true;
        video.playsInline = true;

        video.setAttribute(
            'aria-hidden',
            'true'
        );

        Object.assign(
            video.style,
            {
                width:'100%',
                height:'100%',
                objectFit:'contain',
                borderRadius:'0',
                background:'transparent',
                display:'block',
                pointerEvents:'none'
            }
        );

        oldButton.appendChild(video);

        video.play().catch(()=>{});

    }else{

        oldButton.textContent = '🐕';
    }


    oldButton.setAttribute(
        'aria-label',
        config.bot_name || '챗봇 열기'
    );


    /* --------------------------------------------------------
       PANEL
    -------------------------------------------------------- */

    const panel = document.createElement('section');

    panel.className = 'association-chatbot';

    panel.innerHTML = `
        <header>
            <div class="chat-brand">
                <span class="chat-brand-icon">🐶</span>

                <div>
                    <b>${escapeHtml(
                        config.bot_name ||
                        '경상남도 반려견 협회 챗봇'
                    )}</b>

                    <small>
                        무엇이든 물어보세요 🐾
                    </small>
                </div>
            </div>

            <button
                type="button"
                class="chat-close"
                aria-label="챗봇 닫기"
            >×</button>
        </header>

        <div class="chat-body">

            <div class="chat-msg bot">
                ${escapeHtml(
                    config.greeting || ''
                ).replace(/\n/g,'<br>')}
            </div>

            <div class="chat-quick">
                <button
                    type="button"
                    data-q="협회 소개를 알려주세요"
                >
                    🏢
                    <b>협회소개</b>
                </button>

                <button
                    type="button"
                    data-q="반려견 등록 방법을 알려주세요"
                >
                    🐾
                    <b>반려견등록</b>
                </button>

                <button
                    type="button"
                    data-q="동물병원 정보를 알려주세요"
                >
                    🏥
                    <b>동물병원 찾기</b>
                </button>

                <button
                    type="button"
                    data-q="회원가입 방법을 알려주세요"
                >
                    💳
                    <b>회원가입</b>
                </button>
            </div>

        </div>

        <form class="chat-input">

            <input
                aria-label="챗봇 질문"
                maxlength="1500"
                autocomplete="off"
                placeholder="궁금한 내용을 입력하세요"
            >

            <button
                type="submit"
                aria-label="질문 보내기"
            >➤</button>

        </form>
    `;

    document.body.appendChild(panel);


    const body = panel.querySelector(
        '.chat-body'
    );

    const input = panel.querySelector(
        'input'
    );

    const submitButton = panel.querySelector(
        '.chat-input button'
    );


    /* --------------------------------------------------------
       CONTACT BUTTON
       ALWAYS appended after bot answers.
    -------------------------------------------------------- */

    function addContactButton(){

        const wrap = document.createElement('div');

        wrap.className = 'chat-contact-wrap';

        const link = document.createElement('a');

        link.className = 'chat-contact-button';

        link.href = (
            'tel:' +
            cleanPhone(config.contact_phone)
        );

        link.textContent = (
            config.contact_button_text ||
            '☎ 협회 문의하기'
        );

        wrap.appendChild(link);
        body.appendChild(wrap);
    }


    /* 첫 인사말에도 문의 버튼 고정 */
    addContactButton();


    function scrollBottom(){

        body.scrollTop = body.scrollHeight;
    }


    function addUserMessage(text){

        const node = document.createElement('div');

        node.className = 'chat-msg user';
        node.textContent = text;

        body.appendChild(node);

        scrollBottom();
    }


    function addBotMessage(text){

        const node = document.createElement('div');

        node.className = 'chat-msg bot';
        node.textContent = text;

        body.appendChild(node);

        /*
         * AI 답변 내용과 무관하게
         * 문의 버튼은 UI가 강제로 붙인다.
         */
        addContactButton();

        scrollBottom();
    }


    function addThinking(){

        const node = document.createElement('div');

        node.className = 'chat-msg bot chat-thinking';
        node.textContent = '답변을 준비하고 있어요...';

        body.appendChild(node);

        scrollBottom();

        return node;
    }


    async function ask(question){

        if(busy){
            return;
        }

        busy = true;

        input.disabled = true;
        submitButton.disabled = true;

        addUserMessage(question);

        const thinking = addThinking();

        try{

            const response = await fetch(
                '/api/chatbot/message/',
                {
                    method:'POST',

                    credentials:'same-origin',

                    headers:{
                        'Content-Type':
                            'application/json',

                        'X-CSRFToken':
                            getCookie('csrftoken')
                    },

                    body:JSON.stringify({
                        message:question
                    })
                }
            );

            const data = await response.json();

            thinking.remove();

            if(
                !response.ok ||
                !data.ok
            ){
                addBotMessage(
                    data.error ||
                    '답변을 불러오지 못했습니다.'
                );
            }else{
                addBotMessage(
                    data.answer ||
                    '답변을 생성하지 못했습니다.'
                );
            }

        }catch(error){

            thinking.remove();

            addBotMessage(
                '서버와 연결하지 못했습니다. 잠시 후 다시 이용해주세요.'
            );

        }finally{

            busy = false;

            input.disabled = false;
            submitButton.disabled = false;

            input.focus();
        }
    }


    /* --------------------------------------------------------
       EVENTS
    -------------------------------------------------------- */

    oldButton.addEventListener(
        'click',
        ()=>{
            panel.classList.add('open');

            setTimeout(
                ()=>input.focus(),
                50
            );
        }
    );


    panel.querySelector(
        '.chat-close'
    ).addEventListener(
        'click',
        ()=>{
            panel.classList.remove('open');
        }
    );


    panel.querySelectorAll(
        '[data-q]'
    ).forEach(
        button=>{
            button.addEventListener(
                'click',
                ()=>{
                    ask(
                        button.dataset.q
                    );
                }
            );
        }
    );


    panel.querySelector(
        'form'
    ).addEventListener(
        'submit',
        event=>{

            event.preventDefault();

            const question = input.value.trim();

            if(!question){
                return;
            }

            input.value = '';

            ask(question);
        }
    );
}


boot();

})();
