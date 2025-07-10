# Tapo Control Management Script - PowerShell Version
# Usage: .\manage.ps1 [dev|prod] [start|stop|restart|logs|build]
# SSL/HTTPS is handled by Synology Domain Certificate

param(
    [string]$Environment = "",
    [string]$Command = "start"
)

# Color functions
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    
    switch ($Color) {
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Blue" { Write-Host $Message -ForegroundColor Blue }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        default { Write-Host $Message }
    }
}

# Load environment variables from .env file
function Load-EnvFile {
    if (Test-Path ".env") {
        Get-Content ".env" | ForEach-Object {
            if ($_ -match "^([^#][^=]+)=(.*)$") {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
            }
        }
    }
}

# Set default port values
function Set-DefaultPorts {
    if (-not $env:NGINX_HTTP_PORT) { $env:NGINX_HTTP_PORT = "84" }
    if (-not $env:ADMINER_PORT) { $env:ADMINER_PORT = "8081" }
}

function Show-Banner {
    Write-ColorOutput "╔══════════════════════════════════════════╗" "Blue"
    Write-ColorOutput "║           TAPO CONTROL                   ║" "Blue"
    Write-ColorOutput "║        Smart Plug Management             ║" "Blue"
    Write-ColorOutput "║     (SSL handled by Synology)            ║" "Blue"
    Write-ColorOutput "╚══════════════════════════════════════════╝" "Blue"
}

function Show-URLs {
    param([string]$Environment)
    
    Write-ColorOutput "Access URLs:" "Green"
    Write-ColorOutput "   Nginx HTTP:   http://localhost:$($env:NGINX_HTTP_PORT)" "Yellow"
    Write-ColorOutput "   FastAPI:      http://localhost:5011" "Yellow"
    
    if ($Environment -eq "dev") {
        Write-ColorOutput "   Database:     http://localhost:$($env:ADMINER_PORT)" "Yellow"
    }
    
    Write-ColorOutput ""
    Write-ColorOutput "Configure Synology Reverse Proxy to point to:" "Cyan"
    Write-ColorOutput "   Source (HTTPS): your-domain.com:443" "Cyan"  
    Write-ColorOutput "   Target (HTTP):  localhost:$($env:NGINX_HTTP_PORT)" "Cyan"
}

function Start-Services {
    param([string]$Environment)
    
    Show-Banner
    Write-ColorOutput "Starting Tapo Control ($Environment mode)..." "Green"
    
    if ($Environment -eq "dev") {
        $env:COMPOSE_PROFILES = "dev"
        docker-compose up -d
    } else {
        docker-compose up -d --scale adminer=0
    }
    
    Write-ColorOutput "Services started!" "Green"
    Show-URLs $Environment
}

function Stop-Services {
    Write-ColorOutput "Stopping Tapo Control..." "Yellow"
    docker-compose down
    Write-ColorOutput "Services stopped!" "Green"
}

function Show-Logs {
    param([string]$Environment)
    Write-ColorOutput "Showing logs for $Environment environment..." "Blue"
    docker-compose logs -f
}

function Build-Services {
    Write-ColorOutput "Building services..." "Blue"
    docker-compose build --no-cache
    Write-ColorOutput "Build complete!" "Green"
}

function Show-Help {
    Write-ColorOutput "Usage: .\manage.ps1 [dev|prod] [start|stop|restart|logs|build]" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "Examples:"
    Write-ColorOutput "  .\manage.ps1 dev start    # Start development environment"
    Write-ColorOutput "  .\manage.ps1 prod start   # Start production environment"
    Write-ColorOutput "  .\manage.ps1 dev logs     # View development logs"
    Write-ColorOutput "  .\manage.ps1 prod stop    # Stop production environment"
    Write-ColorOutput ""
    Write-ColorOutput "Note: SSL/HTTPS is handled by Synology Domain Certificate"
}

# Main execution
Load-EnvFile
Set-DefaultPorts

if ($Environment -eq "dev" -or $Environment -eq "prod") {
    switch ($Command) {
        "start" { Start-Services $Environment }
        "stop" { Stop-Services }
        "restart" { 
            Stop-Services
            Start-Services $Environment
        }
        "logs" { Show-Logs $Environment }
        "build" { Build-Services }
        default { 
            Write-ColorOutput "Unknown command: $Command" "Red"
            Show-Help
            exit 1
        }
    }
} else {
    Show-Help
    exit 1
} 