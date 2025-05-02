// static/js/dashboard.js

(() => {
  /* ─── 1. DOM 요소 캐시 ────────────────────────── */
  const tbody     = document.getElementById("plugTableBody");
  const alertBox  = document.getElementById("plugAlert");
  const logoutBtns = document.querySelectorAll("#logoutBtn");
  
  /* ─── 토큰 관리 함수 ────────────────────────────── */
  // 로컬 스토리지에서 토큰 가져오기
  const getToken = () => localStorage.getItem('access_token');
  
  // 토큰 저장
  const saveToken = (token) => localStorage.setItem('access_token', token);
  
  // 토큰 삭제
  const clearToken = () => localStorage.removeItem('access_token');
  
  // 디버깅: 현재 USERNAME 확인
  console.log("현재 로그인한 사용자:", USERNAME);
  
  // 토큰 복호화하여 실제 사용자 확인
  function decodeToken(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      return JSON.parse(jsonPayload);
    } catch (e) {
      console.error("토큰 디코딩 실패:", e);
      return {};
    }
  }
  
  // 토큰에서 사용자 정보 가져오기
  const token = getToken();
  const tokenData = token ? decodeToken(token) : {};
  const tokenUsername = tokenData.sub || "";
  
  // USERNAME과 토큰 정보가 다를 경우 (빈 문자열이거나 다른 값인 경우)
  if (!USERNAME && tokenUsername) {
    console.log(`템플릿 사용자(${USERNAME})와 토큰 사용자(${tokenUsername})가 다름, 토큰 정보 사용`);
    // 토큰 사용자 정보를 우선시
    window.REAL_USERNAME = tokenUsername; 
  } else {
    window.REAL_USERNAME = USERNAME;
  }
  
  console.log("최종 사용자 정보:", {
    template: USERNAME,
    token: tokenUsername,
    using: window.REAL_USERNAME
  });

  /* ─── 2. 로그아웃 처리 ────────────────────────── */
  logoutBtns.forEach(btn => {
    btn.addEventListener("click", async () => {
      // 서버에 로그아웃 요청
      await fetch("/auth/logout", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${getToken()}`
        }
      });
      
      // 토큰 삭제 후 로그인 페이지로
      clearToken();
      location.href = "/login";
    });
  });

  /* ─── 3. 알림 표시 util ───────────────────────── */
  function showAlert(msg, sec = 4) {
    alertBox.textContent = msg;
    alertBox.classList.remove("d-none");
    setTimeout(() => alertBox.classList.add("d-none"), sec * 1000);
  }

  /* ─── 4. Fetch + JSON 체크 util ───────────────── */
  async function fetchWithJson(url, opts = {}) {
    const token = getToken();
    
    const res = await fetch(url, {
      ...opts,
      headers: {
        "Accept": "application/json",
        "Authorization": token ? `Bearer ${token}` : undefined,
        ...(opts.headers || {})
      },
    });

    if (res.status === 401) {
      // 인증 실패 → 로그인으로
      clearToken();
      return location.href = "/login?expired=1";
    }

    if (!res.ok) {
      let err = { detail: `HTTP ${res.status}` };
      try { err = await res.json() } catch {}
      throw new Error(err.detail || err.message || `HTTP ${res.status}`);
    }

    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      throw new Error(`Invalid content-type: ${ct}`);
    }

    return res.json();
  }

  /* ─── 5. 테이블 렌더링 ───────────────────────── */
  function render(plugs) {
    try {
      tbody.innerHTML = "";
      
      if (!tbody) {
        console.error("plugTableBody 요소를 찾을 수 없습니다.");
        return;
      }
      
      // 디버깅: 플러그 데이터 확인
      console.log("플러그 목록:", plugs);
      console.log("현재 로그인 사용자 세부정보:", {
        username: window.REAL_USERNAME,
        type: typeof window.REAL_USERNAME,
        length: window.REAL_USERNAME.length,
        trimmed: window.REAL_USERNAME.trim(),
        trimmedLength: window.REAL_USERNAME.trim().length
      });

      // 플러그 데이터가 없는 경우 처리
      if (!Array.isArray(plugs) || plugs.length === 0) {
        console.warn("플러그 목록이 비어있습니다.");
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td colspan="3" class="text-center py-4">
            <div class="text-muted">등록된 플러그가 없습니다.</div>
          </td>
        `;
        tbody.append(tr);
        return;
      }

      plugs.forEach(plug => {
        const {
          name,
          status       = null,  // true/false/null
          active_users = 0,
          users        = [],
        } = plug;

        // 디버깅: users 배열의 타입과 내용 상세 확인
        console.log(`플러그 ${name} - users 배열 세부정보:`, {
          usersArray: users,
          arrayType: typeof users,
          isArray: Array.isArray(users),
          length: users.length,
          elements: users.map(u => ({ value: u, type: typeof u, length: u?.length }))
        });

        // 항상 문자열로 변환하고 공백을 제거하여 비교
        const usernameStr = String(window.REAL_USERNAME || "").trim();
        
        // 로깅 - 사용자 문자열 비교 정보
        console.log(`${name} - 사용자 비교 정보:`, {
          myUsername: usernameStr,
          usersList: users,
          userTypes: users.map(u => typeof u)
        });
        
        // 사용자 ID 측면에서 문자열로 변환하여 비교
        const iUse = Array.isArray(users) && users.some(u => {
          const userStr = String(u || "").trim();
          const isMatch = userStr === usernameStr;
          console.log(`비교: '${userStr}' vs '${usernameStr}' => ${isMatch}`);
          return isMatch;
        });
        
        console.log(`${name} - 최종 사용자 비교 결과:`, {
          username: usernameStr,
          users,
          iUse
        });
        
        // 수정된 로직: 다른 사용자가 사용 중이어도 내가 사용할 수 있도록 수정
        // locked = active_users > 0 && !iUse; // 이전 로직 - 다른 사용자가 사용 중이면 버튼 비활성화
        const locked = false; // 수정된 로직 - 항상 사용 가능
        const unknown = status === null;
        
        // 디버깅: 버튼 상태 계산 로직 확인
        console.log(`플러그 ${name} - 버튼 상태:`, {
          users,
          currentUser: usernameStr,
          iUse,
          active_users,
          locked,
          unknown,
          willBeDisabled: locked || unknown
        });
        
        const badge = unknown
          ? `<span class="badge bg-warning text-dark">?</span>`
          : `<span class="badge ${status ? "bg-success" : "bg-secondary"}">
               ${status ? "켜짐" : "꺼짐"}
             </span>`;

        // 버튼 활성화/비활성화 상태 계산 결과 명확하게 표시
        // 수정된 로직: 이미 내가 사용 중이면 "사용" 버튼 비활성화, 아니면 활성화
        const useButtonDisabled = iUse || unknown;
        // 수정된 로직: 내가 사용 중이면 "나가기" 버튼 활성화, 아니면 비활성화
        const leaveButtonDisabled = !iUse || unknown;

        // 로그 - 최종 버튼 상태
        console.log(`${name} - 최종 버튼 상태:`, {
          useButtonDisabled,
          leaveButtonDisabled
        });

        // 단순화된 버튼 구조 - div로 컨테이너 구성
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${name}</td>
          <td class="text-center">
            ${badge}
            <span class="badge bg-info ms-1">${active_users}</span>
          </td>
          <td>
            <div class="buttons-container">
              <button class="button-on" 
                      data-name="${name}" 
                      data-action="on"
                      ${useButtonDisabled ? "disabled" : ""}>
                사용
              </button>
              <button class="button-off" 
                      data-name="${name}" 
                      data-action="off"
                      ${leaveButtonDisabled ? "disabled" : ""}>
                나가기
              </button>
            </div>
          </td>
        `;
        tbody.append(tr);
      });
    } catch (err) {
      console.error("테이블 렌더링 오류:", err);
      showAlert("데이터 표시 중 오류가 발생했습니다.");
    }
  }

  /* ─── 6. 서버 요청 함수 ───────────────────────── */
  async function fetchPlugs() {
    try {
      return await fetchWithJson("/plugs/", { method: "GET" });
    } catch (err) {
      console.error("플러그 데이터 요청 실패:", err);
      throw err;
    }
  }

  async function togglePlug(name, action) {
    try {
      const enc = encodeURIComponent(name);
      return await fetchWithJson(`/plugs/${enc}/${action}`, { method: "POST" });
    } catch (err) {
      console.error(`플러그 ${name} 상태 변경 실패:`, err);
      throw err;
    }
  }

  /* ─── 7. 버튼 클릭 이벤트 ─────────────────────── */
  tbody.addEventListener("click", async e => {
    // 사용/나가기 버튼 모두 처리
    const btn = e.target.closest("button[data-name]");
    if (!btn || btn.disabled) return;

    const plugName = btn.dataset.name;
    const action = btn.dataset.action;
    
    try {
      // 버튼 비활성화 (클릭 중복 방지)
      btn.disabled = true;
      
      // API 호출
      console.log(`${plugName} 플러그 ${action === "on" ? "사용" : "나가기"} 요청 중...`);
      const result = await togglePlug(plugName, action);
      console.log(`${plugName} 플러그 상태 변경 성공:`, result);
      
      // 서버 응답의 사용자 목록을 확인
      const currentUsername = String(window.REAL_USERNAME || "").trim();
      const usersList = result.users || [];
      const amIUsingNow = usersList.some(u => String(u || "").trim() === currentUsername);
      
      console.log(`서버 응답에 따른 사용 상태:`, {
        users: usersList,
        myUsername: currentUsername,
        iUse: amIUsingNow
      });
      
      // 서버 응답에 따라 버튼 상태 업데이트
      const row = btn.closest("tr");
      const useBtn = row.querySelector("button[data-action='on']");
      const leaveBtn = row.querySelector("button[data-action='off']");
      
      if (useBtn) useBtn.disabled = amIUsingNow || (result.active_users > 0 && !amIUsingNow);
      if (leaveBtn) leaveBtn.disabled = !amIUsingNow;
      
      // 전체 데이터 다시 로드 (백그라운드)
      load();
    } catch (err) {
      console.error(`${plugName} 플러그 ${action} 요청 실패:`, err);
      showAlert(err.message);
      // 오류 발생 시 버튼 다시 활성화
      btn.disabled = false;
    }
  });

  /* ─── 8. 데이터 로드 ─────────────────────────── */
  async function load() {
    try {
      const plugs = await fetchPlugs();
      render(plugs);
    } catch (err) {
      console.error("데이터 로드 실패:", err);
      showAlert("플러그 정보를 불러오지 못했습니다.");
    }
  }

  /* ─── 9. 초기 로드 & 주기적 갱신 ─────────────── */
  // 토큰이 없으면 로그인 페이지로
  if (!getToken()) {
    location.href = "/login";
  } else {
    // 초기 로드
    load();
    // 주기적 갱신 (15초마다)
    setInterval(load, 15_000);
  }
})();
