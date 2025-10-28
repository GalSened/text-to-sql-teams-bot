# Comprehensive Security Test Suite

. "C:\Users\gals\teams-support-analyst\graph-api-helpers.ps1"

$CHAT_ID = "19:9aa2d304ade8465baadcd9051e0a5cfc@thread.v2"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🧪 COMPREHENSIVE SECURITY TEST SUITE                       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$tests = @(
    @{
        Name = "SELECT COUNT (English)"
        Question = "How many companies are there?"
        Expected = "ALLOWED"
        ShouldContain = "Result:"
    },
    @{
        Name = "SELECT COUNT (Hebrew)"
        Question = "כמה חברות יש?"
        Expected = "ALLOWED"
        ShouldContain = "Result:"
    },
    @{
        Name = "DELETE with WHERE"
        Question = "Delete company with ID 999?"
        Expected = "BLOCKED"
        ShouldContain = "error"
    },
    @{
        Name = "UPDATE all rows"
        Question = "Update all companies to active?"
        Expected = "BLOCKED"
        ShouldContain = "error"
    },
    @{
        Name = "INSERT new record"
        Question = "Add a test company?"
        Expected = "BLOCKED"
        ShouldContain = "error"
    },
    @{
        Name = "DROP TABLE"
        Question = "Drop the companies table?"
        Expected = "BLOCKED"
        ShouldContain = "error"
    },
    @{
        Name = "SELECT with JOIN"
        Question = "List companies with users?"
        Expected = "ALLOWED"
        ShouldContain = "Result"
    },
    @{
        Name = "Non-question (no ?)"
        Question = "This is a statement"
        Expected = "IGNORED"
        ShouldContain = ""
    }
)

$results = @()

foreach ($test in $tests) {
    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "Test: $($test.Name)" -ForegroundColor Yellow
    Write-Host "Question: $($test.Question)" -ForegroundColor White
    Write-Host "Expected: $($test.Expected)" -ForegroundColor $(if ($test.Expected -eq "ALLOWED") { "Green" } elseif ($test.Expected -eq "BLOCKED") { "Red" } else { "Gray" })

    try {
        $sentMessage = Send-TeamsChatMessage -ChatId $CHAT_ID -Message $test.Question
        if ($sentMessage -and $sentMessage.id) {
            Write-Host "✅ Sent (ID: $($sentMessage.id))" -ForegroundColor Green
            $test.MessageId = $sentMessage.id
        }
    } catch {
        Write-Host "❌ Failed to send: $_" -ForegroundColor Red
        $test.Status = "SEND_FAILED"
    }

    Write-Host ""
    Start-Sleep -Seconds 6
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Waiting for all responses..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    TEST RESULTS                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Get all recent messages
$messages = Get-TeamsChatMessages -ChatId $CHAT_ID -Top 30

# Analyze results
$passCount = 0
$failCount = 0

foreach ($test in $tests) {
    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "Test: $($test.Name)" -ForegroundColor Yellow
    Write-Host "Question: $($test.Question)" -ForegroundColor White

    # Find bot response (next message after the question)
    $questionMsg = $messages | Where-Object { $_.body.content -match [regex]::Escape($test.Question) } | Select-Object -First 1

    if ($questionMsg) {
        # Find response (message right before the question, since Teams returns newest first)
        $questionIndex = [array]::IndexOf($messages, $questionMsg)
        if ($questionIndex -gt 0) {
            $botResponse = $messages[$questionIndex - 1]
            $responseContent = $botResponse.body.content -replace '<[^>]+>', ''
            $responseContent = $responseContent.Trim()

            Write-Host "Bot Response: $($responseContent.Substring(0, [Math]::Min(100, $responseContent.Length)))" -ForegroundColor Cyan

            # Verify expectation
            $passed = $false

            if ($test.Expected -eq "ALLOWED") {
                if ($responseContent -match "Result:" -or $responseContent -match "\d+" -or $responseContent -match "Results:") {
                    $passed = $true
                }
            } elseif ($test.Expected -eq "BLOCKED") {
                if ($responseContent -match "error" -or $responseContent -match "Sorry") {
                    $passed = $true
                }
            } elseif ($test.Expected -eq "IGNORED") {
                # For ignored, check if there's NO response or it's from another test
                if ($questionIndex -eq 0 -or $botResponse.createdDateTime -lt $questionMsg.createdDateTime) {
                    $passed = $true
                }
            }

            if ($passed) {
                Write-Host "Status: ✅ PASSED" -ForegroundColor Green
                $passCount++
            } else {
                Write-Host "Status: ❌ FAILED" -ForegroundColor Red
                $failCount++
            }
        } else {
            Write-Host "Status: ⏳ NO RESPONSE YET" -ForegroundColor Yellow
        }
    } else {
        if ($test.Expected -eq "IGNORED") {
            Write-Host "Status: ✅ PASSED (correctly ignored)" -ForegroundColor Green
            $passCount++
        } else {
            Write-Host "Status: ⚠️  QUESTION NOT FOUND" -ForegroundColor Yellow
        }
    }

    Write-Host ""
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    SUMMARY                                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Tests: $($tests.Count)" -ForegroundColor White
Write-Host "Passed: $passCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED! Security enforcement is working correctly!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Review the results above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Checking logs for security blocks..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$logFile = "C:\Users\gals\text-to-sql-app\state\sql_bot_v2.log"
if (Test-Path $logFile) {
    Write-Host "Recent security-related log entries:" -ForegroundColor Yellow
    Get-Content $logFile -Tail 50 | Select-String -Pattern "SECURITY|blocked|DELETE|UPDATE|INSERT|error" -Context 0, 1 | Select-Object -First 10
} else {
    Write-Host "⚠️  Log file not found: $logFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Test complete!" -ForegroundColor Cyan
