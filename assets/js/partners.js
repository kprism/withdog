(function () {
    'use strict';

    var state = {
        all: [],
        categories: [],
        cities: [],
        category: '',
        city: '',
        q: '',
        map: null,
        markers: []
    };

    var cards = document.getElementById('cards');
    var count = document.getElementById('count');
    var tabs = document.getElementById('tabs');
    var searchInput = document.getElementById('searchInput');
    var searchBtn = document.getElementById('searchBtn');
    var mapBox = document.getElementById('kakaoMap');
    var regions = document.getElementById('regions');


    function escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }


    function cleanCity(city) {
        city = String(city || '').trim();

        return city
            .replace(/^경상남도\s*/, '')
            .replace(/^경남\s*/, '');
    }


    function showMapMessage(message) {
        if (!mapBox) {
            return;
        }

        mapBox.classList.add('kakao-map-status');
        mapBox.innerHTML =
            '<div class="kakao-map-status-message">' +
            escapeHtml(message) +
            '</div>';
    }


    function loadKakaoMapSdk() {
        if (
            window.kakao &&
            window.kakao.maps
        ) {
            return Promise.resolve();
        }

        return fetch(
            '/api/site-settings/?_=' + Date.now(),
            {
                credentials: 'same-origin',
                cache: 'no-store'
            }
        )
            .then(function (response) {
                if (!response.ok) {
                    throw new Error(
                        'site settings HTTP ' + response.status
                    );
                }

                return response.json();
            })
            .then(function (settings) {
                var key = String(
                    settings.kakao_javascript_key || ''
                ).trim();

                if (!key) {
                    throw new Error(
                        '카카오 JavaScript 키가 등록되지 않았습니다.'
                    );
                }

                return new Promise(function (resolve, reject) {
                    var script = document.createElement('script');

                    script.dataset.kakaoMapSdk = '1';
                    script.async = true;
                    script.src =
                        'https://dapi.kakao.com/v2/maps/sdk.js' +
                        '?appkey=' + encodeURIComponent(key) +
                        '&libraries=services&autoload=false';

                    script.onload = function () {
                        if (
                            window.kakao &&
                            window.kakao.maps &&
                            typeof window.kakao.maps.load === 'function'
                        ) {
                            window.kakao.maps.load(resolve);
                            return;
                        }

                        reject(
                            new Error('카카오 지도 SDK 초기화 실패')
                        );
                    };

                    script.onerror = function () {
                        reject(
                            new Error('카카오 지도 SDK 로드 실패')
                        );
                    };

                    document.head.appendChild(script);
                });
            });
    }


    function clearMarkers() {
        state.markers.forEach(function (marker) {
            marker.setMap(null);
        });

        state.markers = [];
    }


    function initMap() {
        if (
            !mapBox ||
            !window.kakao ||
            !window.kakao.maps
        ) {
            return false;
        }

        if (!state.map) {
            mapBox.classList.remove('kakao-map-status');
            mapBox.innerHTML = '';

            state.map = new kakao.maps.Map(
                mapBox,
                {
                    center: new kakao.maps.LatLng(
                        35.2383,
                        128.6924
                    ),
                    level: 9
                }
            );
        }

        return true;
    }


    function renderMap(partners) {
        if (!initMap()) {
            return;
        }

        clearMarkers();

        var bounds = new kakao.maps.LatLngBounds();
        var markerCount = 0;

        partners.forEach(function (partner) {
            if (
                partner.latitude == null ||
                partner.longitude == null
            ) {
                return;
            }

            var position = new kakao.maps.LatLng(
                partner.latitude,
                partner.longitude
            );

            var marker = new kakao.maps.Marker({
                position: position,
                map: state.map
            });

            var info = new kakao.maps.InfoWindow({
                content:
                    '<div style="' +
                    'padding:8px 10px;' +
                    'font-size:12px;' +
                    'white-space:nowrap;' +
                    '">' +
                    '<b>' +
                    escapeHtml(partner.name) +
                    '</b><br>' +
                    escapeHtml(cleanCity(partner.city)) +
                    '</div>'
            });

            kakao.maps.event.addListener(
                marker,
                'click',
                function () {
                    info.open(state.map, marker);
                }
            );

            state.markers.push(marker);
            bounds.extend(position);
            markerCount++;
        });

        if (markerCount > 0) {
            state.map.setBounds(bounds);
        }
    }


    function renderCards(items){
    const cards = document.getElementById('cards');
    const count = document.getElementById('count');

    if(!cards) return;

    cards.innerHTML = '';

    if(count){
        count.textContent = items.length;
    }

    items.forEach(function(p){

        const card = document.createElement('article');

        card.className =
            'partner-card' +
            (p.is_ad ? ' partner-card-affiliated' : '');

        const categoryName =
            (p.category && p.category.name)
                ? p.category.name
                : (p.category_name || '');
        const city = (p.city || '').replace(/^경남\s*/, '');

        const lat = Number(p.latitude);
        const lng = Number(p.longitude);

        const hasCoordinates =
            Number.isFinite(lat) &&
            Number.isFinite(lng);

        /*
         * 매장안내
         * Kakao Map 검색 화면으로 이동.
         * 업체명 + 주소를 함께 넘겨 동명이인 가능성을 줄인다.
         */
        /*
         * 매장안내
         *
         * 1. 카카오 장소 상세 URL이 있으면 상세페이지로 바로 이동
         * 2. 상세 URL이 없으면 주소를 섞지 않고 상호명만 카카오맵에서 검색
         *
         * Kakao Local REST API와 실제 Kakao Map 웹 검색 결과가
         * 서로 다를 수 있으므로 fallback은 상호명 단독 검색을 사용한다.
         */
        const placeQuery = encodeURIComponent(
            (p.name || '').trim()
        );

        const placeUrl =
            (p.kakao_place_url || '').trim();

        /*
         * 매장안내 활성화 정책
         *
         * 협력업체이면서 카카오 상세 URL이 등록된 경우에만 활성화한다.
         * 일반업체는 과거 자동매칭 URL이 DB에 남아 있어도 비활성화한다.
         */
        const hasPlaceDetail =
            Boolean(p.is_ad && placeUrl);

        /*
         * 길찾기
         * 모바일에서는 Kakao Map 앱 딥링크를 우선 사용.
         * 좌표가 없는 경우 주소 검색으로 fallback.
         */
        const destinationName =
            encodeURIComponent(p.name || '목적지');

        const routeFallbackUrl =
            'https://map.kakao.com/?q=' + placeQuery;

        const routeUrl = hasCoordinates
            ? 'https://map.kakao.com/link/to/' +
              destinationName + ',' + lat + ',' + lng
            : routeFallbackUrl;

        const badge = p.is_ad
            ? '<span class="partner-affiliated-badge">AD</span>'
            : '';

        const discountPercent = Math.max(
            0,
            Math.min(
                100,
                Number(p.discount_percent || 0)
            )
        );

        const discountHtml =
            '<span class="partner-discount">' +
            escapeHtml(discountPercent) +
            '% 할인</span>';

        const phoneHtml = p.phone
            ? '<p class="partner-phone">☎ ' +
              escapeHtml(p.phone) +
              '</p>'
            : '';

        card.innerHTML = `
            <div class="partner-card-top">
                <div class="partner-category-line">
                    ${badge}
                    <span class="partner-category">
                        ${escapeHtml(categoryName)}
                    </span>
                </div>

                <div class="partner-card-location">
                    ${discountHtml}
                    <span class="partner-city">
                        ${escapeHtml(city)}
                    </span>
                </div>
            </div>

            <h3 class="partner-name">
                ${escapeHtml(p.name || '')}
            </h3>

            <p class="partner-address">
                ${escapeHtml(p.address || '')}
            </p>

            ${phoneHtml}

            <div class="partner-actions">
                ${
                    hasPlaceDetail
                        ? `
                <a
                    class="partner-action partner-action-place"
                    href="${placeUrl}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    매장안내
                </a>
                `
                        : `
                <span
                    class="partner-action partner-action-place partner-action-disabled"
                    aria-disabled="true"
                    title="매장 상세정보 준비중"
                >
                    매장안내
                </span>
                `
                }

                <a
                    class="partner-action partner-action-route"
                    href="${routeUrl}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    길찾기
                </a>
            </div>
        `;

        cards.appendChild(card);
    });
}


    function renderCount(partners) {
        if (count) {
            count.textContent = partners.length;
        }
    }


    function renderCategoryTabs() {
        if (!tabs || !state.categories.length) {
            return;
        }

        tabs.innerHTML = '';

        state.categories.forEach(function (category, index) {
            var button = document.createElement('button');

            button.type = 'button';
            button.dataset.category = category.code;
            button.textContent = category.name;

            if (
                state.category === category.code ||
                (!state.category && index === 0)
            ) {
                button.classList.add('active');
            }

            button.addEventListener(
                'click',
                function () {
                    state.category = category.code;

                    tabs
                        .querySelectorAll('button')
                        .forEach(function (b) {
                            b.classList.remove('active');
                        });

                    button.classList.add('active');

                    applyFilters();
                }
            );

            tabs.appendChild(button);
        });

        if (!state.category && state.categories[0]) {
            state.category = state.categories[0].code;
        }
    }


    function renderRegions() {
        if (!regions) {
            return;
        }

        regions.innerHTML = '';

        var wrap = document.createElement('div');
        wrap.className = 'region-filter';

        var all = document.createElement('button');
        all.type = 'button';
        all.textContent = '전체 지역';
        all.className = 'active';

        all.addEventListener('click', function () {
            state.city = '';

            wrap
                .querySelectorAll('button')
                .forEach(function (b) {
                    b.classList.remove('active');
                });

            all.classList.add('active');

            applyFilters();
        });

        wrap.appendChild(all);

        state.cities.forEach(function (city) {
            var button = document.createElement('button');

            button.type = 'button';
            button.textContent = cleanCity(city);

            button.addEventListener('click', function () {
                state.city = city;

                wrap
                    .querySelectorAll('button')
                    .forEach(function (b) {
                        b.classList.remove('active');
                    });

                button.classList.add('active');

                applyFilters();
            });

            wrap.appendChild(button);
        });

        regions.appendChild(wrap);
    }


    function applyFilters() {
        var q = state.q.toLowerCase();

        var result = state.all.filter(function (partner) {
            if (
                state.category &&
                partner.category.code !== state.category
            ) {
                return false;
            }

            if (
                state.city &&
                partner.city !== state.city
            ) {
                return false;
            }

            if (q) {
                var haystack = [
                    partner.name,
                    partner.address,
                    partner.phone,
                    partner.city
                ]
                    .join(' ')
                    .toLowerCase();

                if (haystack.indexOf(q) === -1) {
                    return false;
                }
            }

            return true;
        });

        renderCount(result);
        renderCards(result);
        renderMap(result);
    }


    function bindSearch() {
        function search() {
            state.q = (
                searchInput
                    ? searchInput.value
                    : ''
            ).trim();

            applyFilters();
        }

        if (searchBtn) {
            searchBtn.addEventListener(
                'click',
                search
            );
        }

        if (searchInput) {
            searchInput.addEventListener(
                'keydown',
                function (event) {
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        search();
                    }
                }
            );
        }
    }


    function loadPartners() {
        fetch(
            '/api/partners/public-map/?_=' + Date.now(),
            {
                credentials: 'same-origin',
                cache: 'no-store'
            }
        )
            .then(function (response) {
                if (!response.ok) {
                    throw new Error(
                        'HTTP ' + response.status
                    );
                }

                return response.json();
            })
            .then(function (data) {
                if (!data.ok) {
                    throw new Error(
                        'API response error'
                    );
                }

                state.all = data.partners || [];
                state.categories = data.categories || [];
                state.cities = data.cities || [];

                renderCategoryTabs();
                renderRegions();
                bindSearch();
                applyFilters();
            })
            .catch(function (error) {
                console.error(
                    'Partner API error:',
                    error
                );

                if (cards) {
                    cards.innerHTML =
                        '<div style="' +
                        'padding:40px;' +
                        'text-align:center;' +
                        'color:#c91f26;' +
                        '">' +
                        '업체 정보를 불러오지 못했습니다.' +
                        '</div>';
                }
            });
    }


    loadKakaoMapSdk()
        .catch(function (error) {
            console.error(
                'Kakao Map SDK error:',
                error
            );

            showMapMessage(
                '카카오 지도를 불러오지 못했습니다. 관리자에서 카카오 JavaScript 키와 등록 도메인을 확인해 주세요.'
            );
        })
        .then(function () {
            loadPartners();
        });

})();
