// admin.js - 관리자 페이지 JavaScript (대시보드 스타일과 통일)

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    loadUsers();
    loadPermissions(); // 권한 목록도 로드
    setupEventListeners();
});

// 이벤트 리스너 설정
function setupEventListeners() {
    // 새 사용자 생성 폼 제출
    document.getElementById('createUserForm').addEventListener('submit', function(e) {
        e.preventDefault();
        createUser();
    });

    // 비밀번호 재설정 폼에서 비밀번호 확인
    document.getElementById('confirmPassword').addEventListener('input', function() {
        const newPassword = document.getElementById('newPasswordReset').value;
        const confirmPassword = this.value;
        
        if (newPassword !== confirmPassword) {
            this.setCustomValidity('비밀번호가 일치하지 않습니다.');
        } else {
            this.setCustomValidity('');
        }
    });
}

// 토큰 가져오기
function getToken() {
    const token = localStorage.getItem('access_token');
    console.log('토큰 조회:', token ? `${token.substring(0, 10)}...` : 'null');
    return token;
}

// API 요청 헤더 생성
function getAuthHeaders() {
    const token = getToken();
    if (!token) {
        console.error('토큰이 없습니다!');
        showAlert('error', '인증 토큰이 없습니다. 다시 로그인해주세요.');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
        return {};
    }
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
    console.log('인증 헤더 생성:', { 'Content-Type': headers['Content-Type'], 'Authorization': `Bearer ${token.substring(0, 10)}...` });
    return headers;
}

// 알림 메시지 표시 (대시보드 스타일과 유사)
function showAlert(type, message) {
    const alertId = type === 'success' ? 'alertSuccess' : 'alertError';
    const alertElement = document.getElementById(alertId);
    
    // 다른 알림 숨기기
    document.getElementById('alertSuccess').style.display = 'none';
    document.getElementById('alertError').style.display = 'none';
    
    // 메시지 표시
    alertElement.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle-fill' : 'exclamation-triangle-fill'} me-2"></i>
        ${message}
    `;
    alertElement.style.display = 'block';
    
    // 화면 상단으로 스크롤
    alertElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // 5초 후 자동 숨김
    setTimeout(() => {
        alertElement.style.display = 'none';
    }, 5000);
}

// 사용자 목록 로드
async function loadUsers() {
    console.log('📋 사용자 목록 로드 시작');
    try {
        const headers = getAuthHeaders();
        console.log('📋 사용자 목록 요청 헤더:', headers);
        
        const response = await fetch('/auth/admin/users', {
            headers: headers
        });

        console.log('📋 사용자 목록 응답 상태:', response.status, response.statusText);

        if (response.ok) {
            const data = await response.json();
            console.log('📋 사용자 목록 데이터:', data);
            console.log(`📋 총 ${data.users ? data.users.length : 0}명의 사용자 발견`);
            displayUsers(data.users);
            console.log('📋 사용자 목록 표시 완료');
        } else if (response.status === 403) {
            console.error('❌ 권한 없음:', response.status);
            showAlert('error', '관리자 권한이 필요합니다.');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            console.error('❌ 사용자 목록 로드 실패:', response.status);
            const errorData = await response.json().catch(() => ({}));
            console.log('❌ 오류 데이터:', errorData);
            showAlert('error', `사용자 목록을 불러오는데 실패했습니다. (${response.status})`);
        }
    } catch (error) {
        console.error('❌ Error loading users:', error);
        showAlert('error', `네트워크 오류가 발생했습니다: ${error.message}`);
    }
}

// 사용자 목록 표시 (대시보드 테이블 스타일과 유사)
function displayUsers(users) {
    console.log('🖥️ 사용자 목록 표시 시작:', users);
    const userList = document.getElementById('userList');
    if (!userList) {
        console.error('❌ userList 엘리먼트를 찾을 수 없습니다');
        return;
    }
    
    userList.innerHTML = '';

    if (!users || users.length === 0) {
        console.log('📋 사용자가 없습니다');
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="4" class="text-center text-muted py-4">
                <i class="bi bi-people me-2"></i>등록된 사용자가 없습니다.
            </td>
        `;
        userList.appendChild(row);
        return;
    }

    console.log(`🖥️ ${users.length}명의 사용자를 표시합니다`);
    users.forEach((user, index) => {
        console.log(`🖥️ 사용자 ${index + 1}: ${user.username} (ID: ${user.id}, 역할: ${user.role})`);
    });

    users.forEach(user => {
        const row = document.createElement('tr');
        
        const isCurrentUser = user.username === getCurrentUsername();
        const roleText = user.role === 'admin' ? '관리자' : '일반 사용자';
        const roleBadgeClass = user.role === 'admin' ? 'role-badge-admin' : 'role-badge-user';
        
        // 플러그 권한 버튼 (일반 사용자만)
        let plugPermissionButton = '';
        if (user.role !== 'admin') {
            plugPermissionButton = `<button class="btn btn-info btn-sm" onclick="openUserPermissionsModal(${user.id}, '${user.username}')" title="플러그 권한 관리">
                        <i class="bi bi-plug-fill"></i>
                    </button>`;
        }
        
        row.innerHTML = `
            <td class="fw-bold">${user.id}</td>
            <td>
                <div class="d-flex align-items-center">
                    <i class="bi bi-person-circle me-2 text-primary"></i>
                    <span class="fw-semibold">${user.username}</span>
                    ${isCurrentUser ? '<span class="badge bg-info ms-2">나</span>' : ''}
                </div>
            </td>
            <td class="text-center">
                <span class="badge ${roleBadgeClass}">${roleText}</span>
            </td>
            <td>
                <div class="action-buttons">
                    ${plugPermissionButton}
                    <button class="btn btn-warning btn-sm" onclick="openResetPasswordModal(${user.id}, '${user.username}')" title="비밀번호 재설정">
                        <i class="bi bi-key-fill"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteUser(${user.id}, '${user.username}')" 
                            ${isCurrentUser ? 'disabled' : ''} 
                            title="${isCurrentUser ? '자기 자신은 삭제할 수 없습니다' : '사용자 삭제'}">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </div>
            </td>
        `;
        
        userList.appendChild(row);
    });
}

// 현재 사용자명 가져오기 (전역 변수에서)
function getCurrentUsername() {
    return USERNAME || '';
}

// 새 사용자 생성
async function createUser() {
    const username = document.getElementById('newUsername').value.trim();
    const password = document.getElementById('newPassword').value;
    const role = document.getElementById('newRole').value;

    console.log('사용자 생성 시도:', { username, role });

    if (!username || !password) {
        showAlert('error', '사용자명과 비밀번호를 입력해주세요.');
        return;
    }

    if (username.length < 3) {
        showAlert('error', '사용자명은 3자 이상이어야 합니다.');
        return;
    }

    if (password.length < 4) {
        showAlert('error', '비밀번호는 4자 이상이어야 합니다.');
        return;
    }

    try {
        const headers = getAuthHeaders();
        console.log('요청 헤더:', headers);
        
        const requestBody = {
            username: username,
            password: password,
            role: role
        };
        console.log('요청 본문:', requestBody);

        const response = await fetch('/auth/admin/users', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(requestBody)
        });

        console.log('응답 상태:', response.status, response.statusText);

        let data;
        try {
            data = await response.json();
            console.log('응답 데이터:', data);
        } catch (jsonError) {
            console.error('JSON 파싱 오류:', jsonError);
            const responseText = await response.text();
            console.log('응답 텍스트:', responseText);
            showAlert('error', '서버 응답을 파싱할 수 없습니다.');
            return;
        }

        if (response.ok) {
            console.log('✅ 사용자 생성 성공, 사용자 목록 새로고침 시작');
            showAlert('success', `사용자 '${username}'이 성공적으로 생성되었습니다.`);
            document.getElementById('createUserForm').reset();
            
            // 사용자 목록 새로고침 - 약간의 지연 추가
            setTimeout(() => {
                console.log('🔄 사용자 목록 새로고침 실행');
                loadUsers();
            }, 500);
        } else {
            console.error('❌ 사용자 생성 실패:', response.status, data);
            showAlert('error', data.detail || `사용자 생성에 실패했습니다. (${response.status})`);
        }
    } catch (error) {
        console.error('Error creating user:', error);
        showAlert('error', `네트워크 오류가 발생했습니다: ${error.message}`);
    }
}

// 비밀번호 재설정 모달 열기
function openResetPasswordModal(userId, username) {
    document.getElementById('resetUserId').value = userId;
    document.getElementById('resetUsername').value = username;
    document.getElementById('newPasswordReset').value = '';
    document.getElementById('confirmPassword').value = '';
    
    // 커스텀 유효성 검사 메시지 초기화
    document.getElementById('confirmPassword').setCustomValidity('');
    
    const modal = new bootstrap.Modal(document.getElementById('resetPasswordModal'));
    modal.show();
}

// 비밀번호 재설정
async function resetPassword() {
    const userId = document.getElementById('resetUserId').value;
    const username = document.getElementById('resetUsername').value;
    const newPassword = document.getElementById('newPasswordReset').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (!newPassword) {
        showAlert('error', '새 비밀번호를 입력해주세요.');
        return;
    }

    if (newPassword.length < 4) {
        showAlert('error', '비밀번호는 4자 이상이어야 합니다.');
        return;
    }

    if (newPassword !== confirmPassword) {
        showAlert('error', '비밀번호가 일치하지 않습니다.');
        return;
    }

    try {
        const response = await fetch(`/auth/admin/users/${userId}/password`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert('success', data.msg);
            const modal = bootstrap.Modal.getInstance(document.getElementById('resetPasswordModal'));
            modal.hide();
        } else {
            showAlert('error', data.detail || '비밀번호 재설정에 실패했습니다.');
        }
    } catch (error) {
        console.error('Error resetting password:', error);
        showAlert('error', '네트워크 오류가 발생했습니다.');
    }
}

// 사용자 삭제
async function deleteUser(userId, username) {
    if (username === getCurrentUsername()) {
        showAlert('error', '자기 자신은 삭제할 수 없습니다.');
        return;
    }

    // 확인 대화상자 개선
    const confirmed = confirm(
        `⚠️ 사용자 삭제 확인\n\n` +
        `사용자: ${username}\n` +
        `ID: ${userId}\n\n` +
        `정말로 이 사용자를 삭제하시겠습니까?\n` +
        `이 작업은 되돌릴 수 없습니다.`
    );
    
    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`/auth/admin/users/${userId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        const data = await response.json();

        if (response.ok) {
            showAlert('success', data.msg);
            loadUsers(); // 사용자 목록 새로고침
        } else {
            showAlert('error', data.detail || '사용자 삭제에 실패했습니다.');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showAlert('error', '네트워크 오류가 발생했습니다.');
    }
}

// 플러그 권한 관리 기능들

// 전역 변수로 플러그 목록과 사용자 목록 저장
let availablePlugs = [];
let allUsers = [];

// 권한 목록 로드
async function loadPermissions() {
    console.log('🔌 플러그 권한 목록 로드 시작');
    
    const container = document.getElementById('permissionsContainer');
    if (!container) {
        console.error('❌ permissionsContainer 엘리먼트를 찾을 수 없습니다');
        return;
    }
    
    // 로딩 표시
    container.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">로딩 중...</span>
            </div>
            <div class="mt-2">권한 정보를 불러오는 중...</div>
        </div>
    `;
    
    try {
        const headers = getAuthHeaders();
        console.log('🔌 API 호출용 헤더:', headers);
        
        // 사용자별 권한 정보와 사용 가능한 플러그 목록을 병렬로 가져오기
        console.log('🔌 권한 API 호출 시작...');
        const [permissionsResponse, plugsResponse] = await Promise.all([
            fetch('/auth/admin/users/permissions', { headers }),
            fetch('/auth/admin/plugs', { headers })
        ]);
        
        console.log('🔌 권한 API 응답:', permissionsResponse.status, plugsResponse.status);

        if (permissionsResponse.ok && plugsResponse.ok) {
            const permissionsData = await permissionsResponse.json();
            const plugsData = await plugsResponse.json();
            
            allUsers = permissionsData.users;
            availablePlugs = plugsData.plugs;
            
            console.log('🔌 권한 데이터:', permissionsData);
            console.log('🔌 사용 가능한 플러그:', availablePlugs);
            
            if (!availablePlugs || availablePlugs.length === 0) {
                console.warn('⚠️ 사용 가능한 플러그가 없습니다');
                container.innerHTML = `
                    <div class="text-center text-warning py-4">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        등록된 플러그가 없습니다. 환경 설정을 확인해주세요.
                    </div>
                `;
                return;
            }
            
            displayPermissions(allUsers, availablePlugs);
        } else {
            console.error('❌ 권한 정보 로드 실패:', {
                permissionsStatus: permissionsResponse.status,
                plugsStatus: plugsResponse.status
            });
            
            // 상세 오류 정보 가져오기
            let errorMsg = '권한 정보를 불러오는데 실패했습니다.';
            try {
                if (!permissionsResponse.ok) {
                    const permError = await permissionsResponse.json();
                    errorMsg += ` 권한 API 오류: ${permError.detail || permissionsResponse.status}`;
                }
                if (!plugsResponse.ok) {
                    const plugError = await plugsResponse.json();
                    errorMsg += ` 플러그 API 오류: ${plugError.detail || plugsResponse.status}`;
                }
            } catch (e) {
                console.error('오류 정보 파싱 실패:', e);
            }
            
            container.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="bi bi-exclamation-circle me-2"></i>
                    ${errorMsg}
                </div>
            `;
            showAlert('error', errorMsg);
        }
    } catch (error) {
        console.error('❌ 권한 정보 로드 에러:', error);
        const errorMsg = `권한 정보 로드 중 오류: ${error.message}`;
        container.innerHTML = `
            <div class="text-center text-danger py-4">
                <i class="bi bi-x-circle me-2"></i>
                ${errorMsg}
            </div>
        `;
        showAlert('error', errorMsg);
    }
}

// 권한 정보 표시
function displayPermissions(users, plugs) {
    console.log('🖥️ 권한 정보 표시 시작:', users, plugs);
    const container = document.getElementById('permissionsContainer');
    
    if (!container) {
        console.error('❌ permissionsContainer 엘리먼트를 찾을 수 없습니다');
        return;
    }
    
    if (!plugs || plugs.length === 0) {
        console.log('⚠️ 플러그가 없습니다:', plugs);
        container.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-plug me-2"></i>등록된 플러그가 없습니다.
            </div>
        `;
        return;
    }
    
    if (!users || users.length === 0) {
        console.log('⚠️ 사용자가 없습니다:', users);
        container.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-people me-2"></i>등록된 사용자가 없습니다.
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive">';
    html += '<table class="table table-hover align-middle">';
    html += '<thead class="table-light">';
    html += '<tr><th style="width:20%">사용자</th>';
    
    // 플러그 이름을 헤더로 추가
    plugs.forEach(plug => {
        html += `<th class="text-center" style="width:${80/plugs.length}%">${plug.name}</th>`;
    });
    
    html += '</tr></thead><tbody>';
    
    // 각 사용자별로 행 생성
    users.forEach(user => {
        if (user.role === 'admin') return; // 관리자는 표시하지 않음
        
        html += '<tr>';
        html += `<td><span class="fw-semibold">${user.username}</span><br><small class="text-muted">ID: ${user.id}</small></td>`;
        
        // 각 플러그에 대해 권한 체크박스 생성
        plugs.forEach(plug => {
            const hasPermission = user.allowed_plugs.includes(plug.name);
            const checkboxId = `perm_${user.id}_${plug.name}`;
            
            html += `<td class="text-center">
                <input type="checkbox" class="form-check-input" 
                       id="${checkboxId}" 
                       ${hasPermission ? 'checked' : ''}
                       onchange="togglePermission(${user.id}, '${plug.name}', this.checked)">
            </td>`;
        });
        
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    
    // 관리자 사용자들 표시 (참고용)
    const adminUsers = users.filter(user => user.role === 'admin');
    if (adminUsers.length > 0) {
        html += '<div class="mt-3 p-3 bg-light rounded">';
        html += '<h6 class="mb-2"><i class="bi bi-shield-fill-check me-2"></i>관리자 (모든 플러그 접근 가능)</h6>';
        adminUsers.forEach(admin => {
            html += `<span class="badge bg-success me-2">${admin.username}</span>`;
        });
        html += '</div>';
    }
    
    container.innerHTML = html;
    console.log('🖥️ 권한 정보 표시 완료');
}

// 권한 토글 (체크박스 변경 시 호출)
async function togglePermission(userId, plugName, grant) {
    console.log(`🔄 권한 ${grant ? '부여' : '회수'}: 사용자 ID ${userId}, 플러그 ${plugName}`);
    
    try {
        const headers = getAuthHeaders();
        const requestBody = {
            user_id: userId,
            plug_name: plugName
        };
        
        const url = grant ? '/auth/admin/permissions/grant' : '/auth/admin/permissions/revoke';
        const method = grant ? 'POST' : 'DELETE';
        
        const response = await fetch(url, {
            method: method,
            headers: headers,
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log(`✅ 권한 ${grant ? '부여' : '회수'} 성공:`, data.msg);
            showAlert('success', data.msg);
            
            // 권한 목록 새로고침
            setTimeout(() => {
                loadPermissions();
            }, 500);
        } else {
            console.error(`❌ 권한 ${grant ? '부여' : '회수'} 실패:`, data.detail);
            showAlert('error', data.detail || `권한 ${grant ? '부여' : '회수'}에 실패했습니다.`);
            
            // 체크박스 상태 되돌리기
            const checkbox = document.getElementById(`perm_${userId}_${plugName}`);
            if (checkbox) {
                checkbox.checked = !grant;
            }
        }
    } catch (error) {
        console.error(`❌ 권한 ${grant ? '부여' : '회수'} 에러:`, error);
        showAlert('error', `네트워크 오류: ${error.message}`);
        
        // 체크박스 상태 되돌리기
        const checkbox = document.getElementById(`perm_${userId}_${plugName}`);
        if (checkbox) {
            checkbox.checked = !grant;
        }
    }
}

// 사용자별 플러그 권한 모달 열기
async function openUserPermissionsModal(userId, username) {
    console.log(`🔧 사용자 권한 모달 열기: ${username} (ID: ${userId})`);
    
    // 모달 정보 설정
    document.getElementById('modalUserId').value = userId;
    document.getElementById('modalUsername').textContent = username;
    
    // 플러그 목록과 현재 사용자 권한 로드
    try {
        const headers = getAuthHeaders();
        
        // 플러그 목록과 사용자 권한을 병렬로 가져오기
        const [plugsResponse, permissionsResponse] = await Promise.all([
            fetch('/auth/admin/plugs', { headers }),
            fetch('/auth/admin/users/permissions', { headers })
        ]);
        
        if (plugsResponse.ok && permissionsResponse.ok) {
            const plugsData = await plugsResponse.json();
            const permissionsData = await permissionsResponse.json();
            
            // 현재 사용자의 권한 찾기
            const currentUser = permissionsData.users.find(user => user.id === parseInt(userId));
            const userPermissions = currentUser ? currentUser.allowed_plugs : [];
            
            console.log(`🔧 사용자 ${username}의 현재 권한:`, userPermissions);
            
            // 플러그 체크박스 생성
            displayUserPlugsList(plugsData.plugs, userPermissions, userId);
            
            // 모달 표시
            const modal = new bootstrap.Modal(document.getElementById('userPermissionsModal'));
            modal.show();
            
        } else {
            console.error('❌ 플러그 목록 또는 권한 정보 로드 실패');
            showAlert('error', '플러그 정보를 불러오는데 실패했습니다.');
        }
    } catch (error) {
        console.error('❌ 권한 모달 데이터 로드 에러:', error);
        showAlert('error', `데이터 로드 중 오류: ${error.message}`);
    }
}

// 사용자별 플러그 목록 표시
function displayUserPlugsList(plugs, userPermissions, userId) {
    console.log('🔧 사용자별 플러그 목록 표시:', plugs, userPermissions);
    
    const container = document.getElementById('userPlugsList');
    
    if (!container) {
        console.error('❌ userPlugsList 엘리먼트를 찾을 수 없습니다');
        return;
    }
    
    if (plugs.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-3">
                <i class="bi bi-plug me-2"></i>등록된 플러그가 없습니다.
            </div>
        `;
        return;
    }
    
    let html = '<div class="row">';
    
    plugs.forEach((plug, index) => {
        const hasPermission = userPermissions.includes(plug.name);
        const checkboxId = `userPlug_${userId}_${plug.name}`;
        
        html += `
            <div class="col-md-6 mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" 
                           id="${checkboxId}" 
                           value="${plug.name}"
                           ${hasPermission ? 'checked' : ''}>
                    <label class="form-check-label fw-semibold" for="${checkboxId}">
                        <i class="bi bi-plug me-2"></i>${plug.name}
                        <small class="text-muted d-block">${plug.ip}</small>
                    </label>
                </div>
            </div>
        `;
        
        // 2개씩 한 줄에 표시
        if ((index + 1) % 2 === 0) {
            html += '</div><div class="row">';
        }
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    console.log('🔧 플러그 목록 표시 완료');
}

// 사용자 권한 저장
async function saveUserPermissions() {
    const userId = document.getElementById('modalUserId').value;
    const username = document.getElementById('modalUsername').textContent;
    
    console.log(`💾 사용자 권한 저장 시작: ${username} (ID: ${userId})`);
    
    // 현재 체크된 플러그들 수집
    const checkboxes = document.querySelectorAll('#userPlugsList input[type="checkbox"]');
    const selectedPlugs = [];
    const unselectedPlugs = [];
    
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedPlugs.push(checkbox.value);
        } else {
            unselectedPlugs.push(checkbox.value);
        }
    });
    
    console.log('💾 선택된 플러그:', selectedPlugs);
    console.log('💾 선택 해제된 플러그:', unselectedPlugs);
    
    try {
        const headers = getAuthHeaders();
        let successCount = 0;
        let errorCount = 0;
        const errors = [];
        
        // 현재 사용자의 권한 가져오기
        const permissionsResponse = await fetch('/auth/admin/users/permissions', { headers });
        if (permissionsResponse.ok) {
            const permissionsData = await permissionsResponse.json();
            const currentUser = permissionsData.users.find(user => user.id === parseInt(userId));
            const currentPermissions = currentUser ? currentUser.allowed_plugs : [];
            
            // 새로 부여할 권한들 (현재 없는데 선택된 것들)
            const toGrant = selectedPlugs.filter(plug => !currentPermissions.includes(plug));
            
            // 회수할 권한들 (현재 있는데 선택 해제된 것들)
            const toRevoke = currentPermissions.filter(plug => !selectedPlugs.includes(plug));
            
            console.log('💾 부여할 권한:', toGrant);
            console.log('💾 회수할 권한:', toRevoke);
            
            // 권한 부여
            for (const plugName of toGrant) {
                try {
                    const response = await fetch('/auth/admin/permissions/grant', {
                        method: 'POST',
                        headers: headers,
                        body: JSON.stringify({
                            user_id: parseInt(userId),
                            plug_name: plugName
                        })
                    });
                    
                    if (response.ok) {
                        successCount++;
                        console.log(`✅ ${plugName} 권한 부여 성공`);
                    } else {
                        const errorData = await response.json();
                        errors.push(`${plugName} 부여 실패: ${errorData.detail}`);
                        errorCount++;
                    }
                } catch (error) {
                    errors.push(`${plugName} 부여 에러: ${error.message}`);
                    errorCount++;
                }
            }
            
            // 권한 회수
            for (const plugName of toRevoke) {
                try {
                    const response = await fetch('/auth/admin/permissions/revoke', {
                        method: 'DELETE',
                        headers: headers,
                        body: JSON.stringify({
                            user_id: parseInt(userId),
                            plug_name: plugName
                        })
                    });
                    
                    if (response.ok) {
                        successCount++;
                        console.log(`✅ ${plugName} 권한 회수 성공`);
                    } else {
                        const errorData = await response.json();
                        errors.push(`${plugName} 회수 실패: ${errorData.detail}`);
                        errorCount++;
                    }
                } catch (error) {
                    errors.push(`${plugName} 회수 에러: ${error.message}`);
                    errorCount++;
                }
            }
            
            // 결과 표시
            if (errorCount === 0) {
                showAlert('success', `사용자 ${username}의 플러그 권한이 성공적으로 업데이트되었습니다.`);
                
                // 모달 닫기
                const modal = bootstrap.Modal.getInstance(document.getElementById('userPermissionsModal'));
                modal.hide();
                
                // 권한 목록 새로고침
                setTimeout(() => {
                    loadPermissions();
                    loadUsers(); // 사용자 목록도 새로고침
                }, 500);
                
            } else {
                console.error('💾 권한 저장 중 일부 오류:', errors);
                showAlert('error', `권한 업데이트 중 일부 오류가 발생했습니다. 성공: ${successCount}, 실패: ${errorCount}`);
            }
        }
        
    } catch (error) {
        console.error('💾 권한 저장 에러:', error);
        showAlert('error', `권한 저장 중 오류가 발생했습니다: ${error.message}`);
    }
}

// 로그아웃 (이미 템플릿에서 처리됨)
function logout() {
    localStorage.removeItem('access_token');
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = '/login';
} 