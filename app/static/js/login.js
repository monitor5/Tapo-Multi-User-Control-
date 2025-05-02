// static/js/login.js

(() => {
  const form = document.getElementById("loginForm");
  const alertBox = document.getElementById("loginAlert");

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

  function showAlert(msg, sec = 4) {
    alertBox.textContent = msg;
    alertBox.classList.remove("d-none");
    setTimeout(() => alertBox.classList.add("d-none"), sec * 1000);
  }
  
  // 토큰 저장 함수
  function saveToken(token) {
    localStorage.setItem('access_token', token);
    
    // 토큰을 쿠키에도 저장 (백엔드에서 접근 가능하도록)
    document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Strict`;
  }

  form.addEventListener("submit", async e => {
    e.preventDefault();

    const formData = new FormData(form);
    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        body: new URLSearchParams(formData)
      });

      if (res.status === 401) {
        showAlert("아이디 또는 비밀번호가 틀렸습니다.");
        return;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      // 응답에서 토큰 추출하여 저장
      const data = await res.json();
      if (data.access_token) {
        saveToken(data.access_token);
        // 로그인 성공 → 대시보드로 이동
        location.href = "/";
      } else {
        throw new Error("토큰이 없습니다");
      }
    } catch (err) {
      console.error(err);
      showAlert("로그인 중 오류가 발생했습니다.");
    }
  });
  
  // URL 파라미터에서 expired=1 체크
  const params = new URLSearchParams(location.search);
  if (params.get('expired') === '1') {
    showAlert("로그인이 필요합니다");
  }
})();
