# API 테스트 스크립트 (수정된 비밀번호)

# 1. 로그인 테스트
Write-Host "=== 로그인 테스트 ===" -ForegroundColor Green
try {
    $loginResponse = Invoke-RestMethod -Uri 'http://localhost:5011/auth/login' -Method Post -ContentType 'application/x-www-form-urlencoded' -Body 'username=admin&password=admin'
    Write-Host "로그인 성공!" -ForegroundColor Green
    Write-Host "토큰: $($loginResponse.access_token.Substring(0, 20))..." -ForegroundColor Yellow
    
    $token = $loginResponse.access_token
    $headers = @{
        'Authorization' = "Bearer $token"
        'Content-Type' = 'application/json'
    }
    
    # 2. 사용자 목록 조회 테스트
    Write-Host "`n=== 사용자 목록 조회 테스트 ===" -ForegroundColor Green
    $usersResponse = Invoke-RestMethod -Uri 'http://localhost:5011/auth/admin/users' -Method Get -Headers $headers
    Write-Host "사용자 목록 조회 성공!" -ForegroundColor Green
    Write-Host "사용자 수: $($usersResponse.users.Count)" -ForegroundColor Yellow
    
    # 3. 새 사용자 생성 테스트
    Write-Host "`n=== 새 사용자 생성 테스트 ===" -ForegroundColor Green
    $newUser = @{
        username = "testuser"
        password = "testpass"
        role = "user"
    } | ConvertTo-Json
    
    $createResponse = Invoke-RestMethod -Uri 'http://localhost:5011/auth/admin/users' -Method Post -Headers $headers -Body $newUser
    Write-Host "사용자 생성 성공!" -ForegroundColor Green
    Write-Host "생성된 사용자: $($createResponse.username)" -ForegroundColor Yellow
    
} catch {
    Write-Host "오류 발생: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $responseBody = $reader.ReadToEnd()
        Write-Host "응답 내용: $responseBody" -ForegroundColor Red
    }
} 