(()=>{const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const bool=(v,n)=>v?` ${n}`:'';function youtube(url){const m=String(url||'').match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|shorts\/))([^?&/]+)/);return m?m[1]:''}function media(x,cls=''){if(x.media_type==='video_file'&&x.video)return `<video class="${cls}" playsinline${bool(x.autoplay,'autoplay')}${bool(x.muted,'muted')}${bool(x.loop,'loop')} src="${esc(x.video)}"></video>`;if(x.media_type==='video_url'&&x.video_url){const y=youtube(x.video_url);if(y)return `<iframe class="${cls}" src="https://www.youtube.com/embed/${y}?autoplay=${x.autoplay?1:0}&mute=${x.muted?1:0}&loop=${x.loop?1:0}&playlist=${y}&controls=0&playsinline=1" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`;return `<video class="${cls}" playsinline${bool(x.autoplay,'autoplay')}${bool(x.muted,'muted')}${bool(x.loop,'loop')} src="${esc(x.video_url)}"></video>`}return x.image?`<img class="${cls}" src="${esc(x.image)}" alt="${esc(x.title)}">`:''}
fetch('/api/content/?kind=hero').then(r=>r.json()).then(d=>{
 const data=d.results.sort((a,b)=>a.sort_order-b.sort_order);if(!data.length)return;
 const hero=document.querySelector('.hero'),shade=hero?.querySelector('.hero-shade'),content=hero?.querySelector('.hero-content');if(!hero||!shade||!content)return;
 hero.querySelectorAll('.hero-slide').forEach(x=>x.remove());
 const slides=data.map((x,i)=>{const el=document.createElement('div');el.className='hero-slide cms-hero-slide'+(i===0?' active':'');if(x.media_type==='image'&&x.image)el.style.setProperty('--bg',`url('${x.image}')`);else el.innerHTML=media(x,'hero-media');hero.insertBefore(el,shade);return el});
 let i=0,paused=false,timer=null;const no=document.querySelector('#slideNo'),total=document.querySelector('.slider-control>span'),pause=document.querySelector('#pauseBtn'),prev=document.querySelector('.slider-control [data-dir="-1"]'),next=document.querySelector('.slider-control [data-dir="1"]');if(total)total.textContent='/ '+slides.length;
 const setText=(el,value)=>{if(el)el.textContent=value||''};const setTitle=(el,value)=>{if(!el)return;el.innerHTML='';String(value||'').split('\n').forEach((line,k,a)=>{el.appendChild(document.createTextNode(line));if(k<a.length-1)el.appendChild(document.createElement('br'))})};
 function show(n){i=(n+slides.length)%slides.length;slides.forEach((s,k)=>{s.classList.toggle('active',k===i);const v=s.querySelector('video');if(v){if(k===i)v.play().catch(()=>{});else v.pause()}});const x=data[i];if(no)no.textContent=i+1;setText(content.querySelector('.eyebrow'),x.hero_eyebrow);setTitle(content.querySelector('h1'),x.hero_title);const metas=content.querySelectorAll('.hero-meta');setText(metas[0],x.hero_meta1);setText(metas[1],x.hero_meta2);const btns=content.querySelectorAll('.hero-buttons a');if(btns[0]){setText(btns[0],x.hero_button1_text);btns[0].href=x.hero_button1_link||'#';btns[0].style.display=x.hero_button1_text?'':'none'}if(btns[1]){setText(btns[1],x.hero_button2_text);btns[1].href=x.hero_button2_link||'#';btns[1].style.display=x.hero_button2_text?'':'none'}}
 function restart(){clearInterval(timer);if(!paused&&slides.length>1)timer=setInterval(()=>show(i+1),5000)}
 if(prev)prev.onclick=e=>{e.preventDefault();show(i-1);restart()};if(next)next.onclick=e=>{e.preventDefault();show(i+1);restart()};if(pause)pause.onclick=e=>{e.preventDefault();paused=!paused;pause.textContent=paused?'▶':'Ⅱ';restart()};show(0);restart();
}).catch(()=>{});
fetch('/api/content/?kind=intro').then(r=>r.json()).then(d=>{if(!d.results.length)return;const grid=document.querySelector('.service-grid');if(!grid)return;grid.innerHTML=d.results.map(x=>`<article>${media(x,'service-media')}<div><em>${esc(x.label)}</em><h3>${esc(x.title)}</h3><p>${esc(x.body)}</p></div></article>`).join('');grid.querySelectorAll('video[autoplay]').forEach(v=>v.play().catch(()=>{}))}).catch(()=>{});
fetch('/api/content/?kind=notice').then(r=>r.json()).then(d=>{if(!d.results.length)return;const box=document.querySelector('.news-cols>div');if(!box)return;const head=box.querySelector('header');box.innerHTML='';box.appendChild(head);d.results.slice(0,5).forEach(x=>{const a=document.createElement('a');a.className='news-row';a.href='board.html?tab=notice';a.innerHTML=`<em>공지</em><span>${esc(x.title)}</span><small>${esc(x.created_at)}</small>`;box.appendChild(a)})}).catch(()=>{});
fetch('/api/content/?kind=popup').then(r=>r.json()).then(d=>{const x=d.results[0];if(!x)return;const wrap=document.createElement('div');wrap.style.cssText='position:fixed;inset:0;background:#0008;z-index:99999;display:grid;place-items:center;padding:20px';wrap.innerHTML=`<div style="width:min(520px,94vw);background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 25px 80px #0006"><div style="position:relative">${media(x,'popup-media')}<button data-close style="position:absolute;right:12px;top:12px;border:0;border-radius:50%;width:36px;height:36px;font-size:20px;cursor:pointer">×</button></div><div style="padding:24px"><h2 style="margin:0 0 10px">${esc(x.title)}</h2><p style="white-space:pre-line;color:#666">${esc(x.body)}</p>${x.link?`<a href="${esc(x.link)}" style="display:inline-block;background:#c91f26;color:#fff;padding:11px 16px;border-radius:8px;text-decoration:none">자세히 보기</a>`:''}</div></div>`;document.body.appendChild(wrap);wrap.querySelector('[data-close]').onclick=()=>wrap.remove();wrap.onclick=e=>{if(e.target===wrap)wrap.remove()}}).catch(()=>{})})();


/* === SITE SETTINGS CMS === */
(()=>{fetch('/api/site-settings/').then(r=>{if(!r.ok)throw new Error('site settings API');return r.json()}).then(x=>{const brand=document.querySelector('.site-header .brand');if(brand){const icon=brand.querySelector('.brand-dog');if(icon&&x.logo){icon.innerHTML='';const img=document.createElement('img');img.src=x.logo;img.alt=x.site_name||'로고';icon.appendChild(img)}const title=brand.querySelector('b'),sub=brand.querySelector('small');if(title&&x.site_name)title.textContent=x.site_name;if(sub)sub.textContent=x.site_subtitle||''}if(x.site_name)document.title=x.site_name}).catch(err=>console.warn('사이트 설정을 불러오지 못했습니다.',err))})();


/* =========================================================
   INTRO NOTICE / ASSOCIATION NEWS
   ========================================================= */

(function () {

    function escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function renderIntroNews(targetId, posts) {

        const target = document.getElementById(targetId);

        if (!target) {
            return;
        }

        if (!Array.isArray(posts) || posts.length === 0) {
            target.innerHTML =
                '<p class="intro-news-empty">' +
                '등록된 게시물이 없습니다.' +
                '</p>';

            return;
        }

        target.innerHTML = posts.map(function (post) {

            return (
                '<a class="intro-news-item" href="' +
                escapeHtml(post.url) +
                '">' +

                    '<span class="intro-news-category">' +
                    escapeHtml(post.category) +
                    '</span>' +

                    '<strong class="intro-news-title">' +
                    escapeHtml(post.title) +
                    '</strong>' +

                    '<time class="intro-news-date">' +
                    escapeHtml(post.date) +
                    '</time>' +

                '</a>'
            );

        }).join('');
    }

    function loadIntroNews() {

        if (
            !document.getElementById('introNoticeList') &&
            !document.getElementById('introAssociationList')
        ) {
            return;
        }

        fetch('/api/intro-news/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            },
            cache: 'no-store'
        })
        .then(function (response) {

            if (!response.ok) {
                throw new Error(
                    'HTTP ' + response.status
                );
            }

            return response.json();
        })
        .then(function (data) {

            renderIntroNews(
                'introNoticeList',
                data.notice || []
            );

            renderIntroNews(
                'introAssociationList',
                data.association || []
            );
        })
        .catch(function (error) {

            console.error(
                '[INTRO NEWS]',
                error
            );

            const notice =
                document.getElementById('introNoticeList');

            const association =
                document.getElementById('introAssociationList');

            if (notice) {
                notice.innerHTML =
                    '<p class="intro-news-empty">' +
                    '공지사항을 불러오지 못했습니다.' +
                    '</p>';
            }

            if (association) {
                association.innerHTML =
                    '<p class="intro-news-empty">' +
                    '협회 소식을 불러오지 못했습니다.' +
                    '</p>';
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener(
            'DOMContentLoaded',
            loadIntroNews
        );
    } else {
        loadIntroNews();
    }

})();
