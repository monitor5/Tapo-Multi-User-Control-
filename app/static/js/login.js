// static/js/login.js

(() => {
  const form = document.getElementById("loginForm");
  const errorBox = document.getElementById("loginError");
  const spinner = document.getElementById("loginSpinner");

  // 페이지 로드 시 모든 이전 세션 정보 초기화
  function clearPreviousSession() {
    console.log("이전 세션 정보 삭제 중...");
    
    // 로컬 스토리지 토큰 삭제
    localStorage.removeItem('access_token');
    
    // 모든 쿠키 삭제
    document.cookie.split(";").forEach(function(c) {
      document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
    
    console.log("이전 세션 정보 삭제 완료");
  }
  
  // 페이지 로드 시 세션 초기화 실행
  clearPreviousSession();

  function showError(msg, sec = 5) {
    const spanElement = errorBox.querySelector('span');
    if (spanElement) {
      spanElement.textContent = msg;
    } else {
      errorBox.textContent = msg;
    }
    errorBox.classList.remove("d-none");
    setTimeout(() => errorBox.classList.add("d-none"), sec * 1000);
  }
  
  function hideError() {
    errorBox.classList.add("d-none");
  }
  
  // 토큰 저장 함수
  function saveToken(token) {
    localStorage.setItem('access_token', token);
    
    // 토큰을 쿠키에도 저장 (백엔드에서 접근 가능하도록)
    document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Strict`;
  }

  form.addEventListener("submit", async e => {
    e.preventDefault();
    
    // 이전 에러 메시지 숨기기
    hideError();
    
    // 로딩 스피너 표시
    spinner.classList.remove("d-none");
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    const formData = new FormData(form);
    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        body: new URLSearchParams(formData)
      });

      const data = await res.json();
      console.log("서버 응답:", res.status, data);

      if (res.status === 401) {
        showError("❌ 아이디 또는 비밀번호가 올바르지 않습니다.");
        return;
      }
      
      if (res.status === 422) {
        showError("❌ 입력 정보를 확인해주세요.");
        return;
      }
      
      // JSON 응답에 detail이 있으면 에러 메시지로 처리
      if (data.detail) {
        showError(`❌ ${data.detail}`);
        return;
      }
      
      if (!res.ok) {
        throw new Error(`서버 오류 (HTTP ${res.status})`);
      }

      // 응답에서 토큰 추출하여 저장
      if (data.access_token) {
        saveToken(data.access_token);
        // 로그인 성공 → 대시보드로 이동
        location.href = "/";
      } else {
        throw new Error("토큰이 없습니다");
      }
    } catch (err) {
      console.error("로그인 오류:", err);
      showError(`❌ 로그인 중 오류가 발생했습니다: ${err.message}`);
    } finally {
      // 로딩 스피너 숨기기
      spinner.classList.add("d-none");
      submitBtn.disabled = false;
    }
  });
  
  // URL 파라미터에서 expired=1 체크
  const params = new URLSearchParams(location.search);
  if (params.get('expired') === '1') {
    showError("⚠️ 로그인이 만료되었습니다. 다시 로그인해주세요.");
  }
})();
